# RAIA Quick Start Guide

## 5-Minute Setup

### 1. Install SDK

**Python**:
```bash
pip install raia
# Or from source:
cd sdk/python && pip install -e .
```

**TypeScript/JavaScript**:
```bash
npm install @raia/sdk
# Or:
yarn add @raia/sdk
```

### 2. Start Ingestion Service (Local Dev)

```bash
# Using Docker Compose
cd services/ingestion
docker-compose up -d

# Or run locally
pip install -r requirements.txt
export RAIA_STORAGE_BACKEND=file
export RAIA_FILE_PATH=/tmp/raia_events.ndjson
export RAIA_REQUIRE_API_KEY=false  # Dev only!
python main.py
```

Service will be available at `http://localhost:8000`

### 3. Instrument Your Agent

**Python (Basic)**:
```python
import asyncio
from raia import EventEmitter, EmitterConfig

async def main():
    # Configure
    config = EmitterConfig(
        tenant="my-company",
        project="my-project",
        agent_id="my-agent-v1.0",
        transport="http",
        endpoint="http://localhost:8000/ingest",
    )

    # Initialize
    emitter = EventEmitter(config)
    await emitter.start()

    try:
        # Emit events
        session_id = "sess_123"
        emitter.emit({
            "event": "session_start",
            "session_id": session_id,
            "run_id": "run_456",
            "agent_id": "my-agent-v1.0",
            "user_id": "user_789",
            "task": "Answer user question",
            "domain": "general",
            "env": {},  # Auto-enriched
        })

        # ... emit more events as your agent runs

        await emitter.flush()
    finally:
        await emitter.shutdown()

asyncio.run(main())
```

**Python (LangChain Integration)**:
```python
from langchain.agents import AgentExecutor
from raia.integrations.langchain import LangChainCallbackHandler

callback = LangChainCallbackHandler(emitter=emitter)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    callbacks=[callback]
)

result = agent_executor.invoke({"input": "What is 2+2?"})
```

**TypeScript**:
```typescript
import { EventEmitter, EmitterConfig, TransportType } from '@raia/sdk';

const config: EmitterConfig = {
  tenant: 'my-company',
  project: 'my-project',
  agent_id: 'my-agent-v1.0',
  transport: TransportType.HTTP,
  endpoint: 'http://localhost:8000/ingest',
};

const emitter = new EventEmitter(config);

// Emit events
emitter.emit({
  event: 'session_start',
  session_id: 'sess_123',
  // ... rest of event
  env: {} as any,  // Auto-enriched
});

await emitter.flush();
await emitter.shutdown();
```

### 4. View Events

```bash
# File-based storage
tail -f /tmp/raia_events.ndjson

# Postgres
psql -c "SELECT event_type, COUNT(*) FROM raia_events GROUP BY event_type;"
```

### 5. Compute Metrics

```bash
python tools/replay_compute.py \
  /tmp/raia_events.ndjson \
  --metrics-config config/metrics_config.json \
  --output-csv metrics.csv

cat metrics.csv
```

## Production Checklist

Before deploying to production:

- [ ] Replace `http://` with `https://` endpoint
- [ ] Enable API key authentication (`RAIA_REQUIRE_API_KEY=true`)
- [ ] Enable HMAC signing (`RAIA_ENABLE_SIGNING=true`, set `RAIA_HMAC_SECRET`)
- [ ] Configure PII/PHI redaction for your domain
- [ ] Set up Postgres or Kafka for storage (not file-based)
- [ ] Deploy ingestion service with ≥ 2 replicas
- [ ] Configure Prometheus scraping for `/metrics` endpoint
- [ ] Set up Grafana dashboards
- [ ] Configure alerts (see `observability/prometheus_alerts.yaml`)
- [ ] Test disaster recovery (backup restore)

## Integration Checklist

When integrating RAIA into your agent:

- [ ] Emit `session_start` at the beginning of each task
- [ ] Emit `plan_created` when your agent creates a plan
- [ ] Emit `tool_call` before each tool invocation
- [ ] Emit `observation` after each tool completes
- [ ] Emit `critique` if your agent self-reflects
- [ ] Emit `correction` if your agent backtracks or revises
- [ ] Emit `escalation` when escalating to humans
- [ ] Emit `finalized` when task completes (with `success` flag)
- [ ] Emit `error` on unrecoverable errors
- [ ] Emit `policy_flag` when safety checks trigger
- [ ] Populate `evidence_refs` for grounding metrics
- [ ] Set `expected_tool` in `tool_call` for wrong tool detection

## Troubleshooting

**Events not appearing in storage:**
- Check ingestion service logs: `docker logs raia-ingestion`
- Verify API key is correct
- Check HMAC signature if enabled
- Ensure schema validation passes

**High event drop rate:**
- Increase batch size in SDK config
- Scale up ingestion pods
- Check storage backend latency

**Metrics computation fails:**
- Validate events against schema: `jsonschema -i events.ndjson event_schema.json`
- Check for required events (e.g., can't compute success rate without `finalized` events)

## Next Steps

- Read [Canonical Metrics](docs/canonical_metrics.md) to understand what's measured
- Review [Security & Compliance](docs/security_compliance.md) for production hardening
- Check [Deployment Guide](docs/deployment_scaling.md) for scaling strategies
- Explore example agents in `examples/`
