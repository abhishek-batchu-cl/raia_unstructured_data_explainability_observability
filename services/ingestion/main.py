"""
RAIA Ingestion Service
Production-grade FastAPI service for event ingestion with:
- API key and HMAC signature verification
- Multiple storage backends (NDJSON, Postgres, Kafka)
- Prometheus metrics
- Health checks
"""

import json
import logging
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import aiofiles
from fastapi import FastAPI, Header, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from pydantic import BaseModel, ValidationError
import jsonschema

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus metrics
EVENTS_RECEIVED = Counter('raia_events_received_total', 'Total events received', ['tenant', 'project'])
EVENTS_INVALID = Counter('raia_events_invalid_total', 'Invalid events rejected', ['tenant', 'project', 'reason'])
EVENTS_STORED = Counter('raia_events_stored_total', 'Events successfully stored', ['tenant', 'project', 'backend'])
INGEST_LATENCY = Histogram('raia_ingest_latency_seconds', 'Ingestion latency', ['backend'])
SIGNATURE_FAILURES = Counter('raia_signature_verification_failures_total', 'Signature verification failures')

# Configuration from environment
CONFIG = {
    'storage_backend': os.getenv('RAIA_STORAGE_BACKEND', 'file'),  # file, postgres, kafka
    'file_path': os.getenv('RAIA_FILE_PATH', '/data/events.ndjson'),
    'postgres_url': os.getenv('RAIA_POSTGRES_URL'),
    'kafka_bootstrap': os.getenv('RAIA_KAFKA_BOOTSTRAP'),
    'kafka_topic': os.getenv('RAIA_KAFKA_TOPIC', 'raia-events'),
    'require_api_key': os.getenv('RAIA_REQUIRE_API_KEY', 'true').lower() == 'true',
    'require_signature': os.getenv('RAIA_REQUIRE_SIGNATURE', 'false').lower() == 'true',
    'api_keys': os.getenv('RAIA_API_KEYS', '').split(','),
    'hmac_secret': os.getenv('RAIA_HMAC_SECRET'),
    'schema_path': os.getenv('RAIA_SCHEMA_PATH', '../../schemas/event_schema.json'),
    'enable_validation': os.getenv('RAIA_ENABLE_VALIDATION', 'true').lower() == 'true',
}

# Global storage backends
storage_backends = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic."""
    logger.info("Starting RAIA Ingestion Service")
    logger.info(f"Configuration: {CONFIG}")

    # Initialize storage backends
    if CONFIG['storage_backend'] == 'file':
        storage_backends['file'] = FileStorage(CONFIG['file_path'])
        await storage_backends['file'].initialize()

    if CONFIG['storage_backend'] == 'postgres':
        storage_backends['postgres'] = PostgresStorage(CONFIG['postgres_url'])
        await storage_backends['postgres'].initialize()

    if CONFIG['storage_backend'] == 'kafka':
        storage_backends['kafka'] = KafkaStorage(
            CONFIG['kafka_bootstrap'],
            CONFIG['kafka_topic']
        )
        await storage_backends['kafka'].initialize()

    # Load JSON schema
    if CONFIG['enable_validation']:
        global event_schema
        schema_path = Path(__file__).parent / CONFIG['schema_path']
        with open(schema_path) as f:
            event_schema = json.load(f)
        logger.info(f"Loaded event schema from {schema_path}")

    yield

    # Cleanup
    logger.info("Shutting down RAIA Ingestion Service")
    for backend in storage_backends.values():
        await backend.close()


app = FastAPI(
    title="RAIA Ingestion Service",
    version="1.0.0",
    lifespan=lifespan
)

event_schema = None


# Storage backend interfaces
class FileStorage:
    """NDJSON file storage backend."""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)

    async def initialize(self):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"File storage initialized: {self.file_path}")

    async def store(self, events: List[dict]):
        start_time = time.time()
        async with aiofiles.open(self.file_path, mode='a') as f:
            for event in events:
                await f.write(json.dumps(event) + '\n')
        INGEST_LATENCY.labels(backend='file').observe(time.time() - start_time)

    async def close(self):
        pass


class PostgresStorage:
    """PostgreSQL storage backend."""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.pool = None

    async def initialize(self):
        import asyncpg
        self.pool = await asyncpg.create_pool(self.connection_string)
        logger.info("Postgres storage initialized")

        # Create table if not exists
        async with self.pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS raia_events (
                    event_id UUID PRIMARY KEY,
                    ts TIMESTAMPTZ NOT NULL,
                    session_id UUID NOT NULL,
                    run_id UUID NOT NULL,
                    agent_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    tenant TEXT NOT NULL,
                    project TEXT NOT NULL,
                    data JSONB NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
                CREATE INDEX IF NOT EXISTS idx_session_id ON raia_events(session_id);
                CREATE INDEX IF NOT EXISTS idx_tenant_project ON raia_events(tenant, project);
                CREATE INDEX IF NOT EXISTS idx_ts ON raia_events(ts DESC);
            ''')

    async def store(self, events: List[dict]):
        start_time = time.time()
        async with self.pool.acquire() as conn:
            for event in events:
                await conn.execute(
                    '''INSERT INTO raia_events
                       (event_id, ts, session_id, run_id, agent_id, event_type, tenant, project, data)
                       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                       ON CONFLICT (event_id) DO NOTHING''',
                    event['event_id'],
                    datetime.fromisoformat(event['ts'].replace('Z', '+00:00')),
                    event['session_id'],
                    event['run_id'],
                    event['agent_id'],
                    event['event'],
                    event['env']['tenant'],
                    event['env']['project'],
                    json.dumps(event)
                )
        INGEST_LATENCY.labels(backend='postgres').observe(time.time() - start_time)

    async def close(self):
        if self.pool:
            await self.pool.close()


class KafkaStorage:
    """Kafka storage backend."""

    def __init__(self, bootstrap_servers: str, topic: str):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.producer = None

    async def initialize(self):
        from aiokafka import AIOKafkaProducer
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        await self.producer.start()
        logger.info(f"Kafka storage initialized: {self.bootstrap_servers} -> {self.topic}")

    async def store(self, events: List[dict]):
        start_time = time.time()
        for event in events:
            await self.producer.send(self.topic, value=event)
        INGEST_LATENCY.labels(backend='kafka').observe(time.time() - start_time)

    async def close(self):
        if self.producer:
            await self.producer.stop()


# Authentication
def verify_api_key(authorization: Optional[str]) -> bool:
    """Verify API key from Authorization header."""
    if not CONFIG['require_api_key']:
        return True

    if not authorization:
        return False

    # Expected format: "Bearer <api_key>"
    parts = authorization.split(' ')
    if len(parts) != 2 or parts[0] != 'Bearer':
        return False

    api_key = parts[1]
    return api_key in CONFIG['api_keys']


def verify_hmac_signature(event: dict, signature: Optional[str]) -> bool:
    """Verify HMAC signature."""
    if not CONFIG['require_signature']:
        return True

    if not signature or not CONFIG['hmac_secret']:
        return False

    from raia.signer import EventSigner
    signer = EventSigner(CONFIG['hmac_secret'])
    return signer.verify(event, signature)


# Validation
def validate_event(event: dict) -> Optional[str]:
    """Validate event against JSON schema."""
    if not CONFIG['enable_validation'] or not event_schema:
        return None

    try:
        jsonschema.validate(event, event_schema)
        return None
    except jsonschema.ValidationError as e:
        return str(e)


# API Endpoints
@app.post('/ingest')
async def ingest_events(
    request: Request,
    authorization: Optional[str] = Header(None),
):
    """
    Ingest events (NDJSON or JSON array).

    Accepts:
    - Content-Type: application/x-ndjson (one event per line)
    - Content-Type: application/json (array of events)
    """
    # Verify API key
    if not verify_api_key(authorization):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )

    # Parse events
    content_type = request.headers.get('content-type', '').lower()
    body = await request.body()

    try:
        if 'ndjson' in content_type:
            events = [json.loads(line) for line in body.decode('utf-8').strip().split('\n') if line]
        elif 'json' in content_type:
            data = json.loads(body)
            events = data if isinstance(data, list) else [data]
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported Content-Type. Use application/x-ndjson or application/json"
            )
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON: {e}"
        )

    # Process events
    valid_events = []
    for event in events:
        tenant = event.get('env', {}).get('tenant', 'unknown')
        project = event.get('env', {}).get('project', 'unknown')

        EVENTS_RECEIVED.labels(tenant=tenant, project=project).inc()

        # Verify signature if required
        signature = event.pop('_signature', None)
        if CONFIG['require_signature']:
            if not verify_hmac_signature(event, signature):
                SIGNATURE_FAILURES.inc()
                EVENTS_INVALID.labels(tenant=tenant, project=project, reason='signature').inc()
                logger.warning(f"Signature verification failed for event {event.get('event_id')}")
                continue

        # Validate schema
        validation_error = validate_event(event)
        if validation_error:
            EVENTS_INVALID.labels(tenant=tenant, project=project, reason='schema').inc()
            logger.warning(f"Schema validation failed: {validation_error}")
            continue

        valid_events.append(event)

    if not valid_events:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid events to ingest"
        )

    # Store events
    backend_name = CONFIG['storage_backend']
    backend = storage_backends.get(backend_name)

    if not backend:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Storage backend '{backend_name}' not initialized"
        )

    try:
        await backend.store(valid_events)

        # Update metrics
        for event in valid_events:
            tenant = event['env']['tenant']
            project = event['env']['project']
            EVENTS_STORED.labels(tenant=tenant, project=project, backend=backend_name).inc()

    except Exception as e:
        logger.exception(f"Failed to store events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Storage error: {e}"
        )

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            'accepted': len(valid_events),
            'rejected': len(events) - len(valid_events)
        }
    )


@app.get('/healthz')
async def health_check():
    """Health check endpoint."""
    return {'status': 'healthy'}


@app.get('/readyz')
async def readiness_check():
    """Readiness check endpoint."""
    # Check storage backend
    backend_name = CONFIG['storage_backend']
    backend = storage_backends.get(backend_name)

    if not backend:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Storage backend '{backend_name}' not ready"
        )

    return {'status': 'ready', 'backend': backend_name}


@app.get('/metrics')
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
