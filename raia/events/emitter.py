"""
Event Emitter with production-grade features:
- Async batching
- Exponential backoff with jitter
- Circuit breaker
- Multiple transports (file, HTTP, Kafka, OTLP)
- Graceful shutdown
- Health checks
"""

import asyncio
import json
import logging
import os
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
from urllib.parse import urlparse

import aiofiles
import aiohttp

logger = logging.getLogger(__name__)


class TransportType(Enum):
    FILE = "file"
    HTTP = "http"
    KAFKA = "kafka"
    OTLP = "otlp"


class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject immediately
    HALF_OPEN = "half_open"  # Testing if recovered


@dataclass
class EmitterConfig:
    """Configuration for EventEmitter."""

    # Identity
    tenant: str
    project: str
    agent_id: str
    region: str = "us-east-1"
    deployment: str = "prod"

    # Transport
    transport: TransportType = TransportType.FILE
    file_path: Optional[str] = None
    http_endpoint: Optional[str] = None
    kafka_bootstrap_servers: Optional[str] = None
    kafka_topic: Optional[str] = "raia-events"
    api_key: Optional[str] = None

    # Batching
    batch_size: int = 100
    max_batch_bytes: int = 1_000_000  # 1 MB
    flush_interval_ms: int = 5000  # 5 seconds
    max_queue_size: int = 10000

    # Retry & Circuit Breaker
    max_retries: int = 3
    retry_base_delay_ms: int = 100
    retry_max_delay_ms: int = 10000
    circuit_failure_threshold: int = 5
    circuit_recovery_timeout_ms: int = 30000
    circuit_half_open_max_calls: int = 3

    # Security
    hmac_secret: Optional[str] = None
    enable_signing: bool = True

    # Schema
    schema_version: str = "1.0.0"
    sdk_version: str = "1.0.0"

    # LLM defaults
    llm: Optional[str] = None
    llm_version: Optional[str] = None
    seed: Optional[int] = None
    temperature: Optional[float] = None

    # Fallback
    fallback_to_file: bool = True
    fallback_file_path: str = "/tmp/raia_fallback.ndjson"

    @classmethod
    def from_env(cls) -> "EmitterConfig":
        """Load config from environment variables."""
        return cls(
            tenant=os.getenv("RAIA_TENANT", "default"),
            project=os.getenv("RAIA_PROJECT", "default"),
            agent_id=os.getenv("RAIA_AGENT_ID", "unknown"),
            region=os.getenv("RAIA_REGION", "us-east-1"),
            deployment=os.getenv("RAIA_DEPLOYMENT", "prod"),
            transport=TransportType(os.getenv("RAIA_TRANSPORT", "file")),
            file_path=os.getenv("RAIA_FILE_PATH"),
            http_endpoint=os.getenv("RAIA_HTTP_ENDPOINT"),
            kafka_bootstrap_servers=os.getenv("RAIA_KAFKA_BOOTSTRAP"),
            kafka_topic=os.getenv("RAIA_KAFKA_TOPIC", "raia-events"),
            api_key=os.getenv("RAIA_API_KEY"),
            batch_size=int(os.getenv("RAIA_BATCH_SIZE", "100")),
            max_batch_bytes=int(os.getenv("RAIA_MAX_BATCH_BYTES", "1000000")),
            flush_interval_ms=int(os.getenv("RAIA_FLUSH_INTERVAL_MS", "5000")),
            hmac_secret=os.getenv("RAIA_HMAC_SECRET"),
            enable_signing=os.getenv("RAIA_ENABLE_SIGNING", "true").lower() == "true",
            schema_version=os.getenv("RAIA_SCHEMA_VERSION", "1.0.0"),
            sdk_version=os.getenv("RAIA_SDK_VERSION", "1.0.0"),
            llm=os.getenv("RAIA_LLM"),
            llm_version=os.getenv("RAIA_LLM_VERSION"),
            seed=int(os.getenv("RAIA_SEED")) if os.getenv("RAIA_SEED") else None,
            temperature=float(os.getenv("RAIA_TEMPERATURE")) if os.getenv("RAIA_TEMPERATURE") else None,
        )


@dataclass
class CircuitBreaker:
    """Circuit breaker to prevent cascading failures."""

    failure_threshold: int
    recovery_timeout_ms: int
    half_open_max_calls: int

    state: CircuitState = field(default=CircuitState.CLOSED, init=False)
    failure_count: int = field(default=0, init=False)
    last_failure_time: float = field(default=0.0, init=False)
    half_open_calls: int = field(default=0, init=False)

    def record_success(self) -> None:
        """Record successful call."""
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_calls += 1
            if self.half_open_calls >= self.half_open_max_calls:
                logger.info("Circuit breaker recovered, closing circuit")
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.half_open_calls = 0
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0

    def record_failure(self) -> None:
        """Record failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == CircuitState.HALF_OPEN:
            logger.warning("Circuit breaker failed in half-open state, reopening")
            self.state = CircuitState.OPEN
            self.half_open_calls = 0
        elif self.state == CircuitState.CLOSED:
            if self.failure_count >= self.failure_threshold:
                logger.error(f"Circuit breaker threshold reached ({self.failure_count} failures), opening circuit")
                self.state = CircuitState.OPEN

    def can_attempt(self) -> bool:
        """Check if call can be attempted."""
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            elapsed_ms = (time.time() - self.last_failure_time) * 1000
            if elapsed_ms >= self.recovery_timeout_ms:
                logger.info("Circuit breaker recovery timeout elapsed, entering half-open state")
                self.state = CircuitState.HALF_OPEN
                self.half_open_calls = 0
                return True
            return False

        if self.state == CircuitState.HALF_OPEN:
            return True

        return False


class EventEmitter:
    """
    Production-grade event emitter with batching, retries, and circuit breaker.
    """

    def __init__(
        self,
        config: EmitterConfig,
        redactor: Optional["Redactor"] = None,
        signer: Optional["EventSigner"] = None,
    ):
        self.config = config
        self.redactor = redactor
        self.signer = signer

        # State
        self._queue: asyncio.Queue = asyncio.Queue(maxsize=config.max_queue_size)
        self._batch: List[Dict[str, Any]] = []
        self._batch_bytes = 0
        self._flush_task: Optional[asyncio.Task] = None
        self._worker_task: Optional[asyncio.Task] = None
        self._shutdown = False
        self._http_session: Optional[aiohttp.ClientSession] = None

        # Circuit breaker
        self._circuit_breaker = CircuitBreaker(
            failure_threshold=config.circuit_failure_threshold,
            recovery_timeout_ms=config.circuit_recovery_timeout_ms,
            half_open_max_calls=config.circuit_half_open_max_calls,
        )

        # Metrics
        self._events_emitted = 0
        self._events_dropped = 0
        self._batches_sent = 0
        self._batches_failed = 0

        # Kafka producer (lazy init)
        self._kafka_producer = None

        logger.info(f"EventEmitter initialized: transport={config.transport.value}, agent={config.agent_id}")

    async def start(self) -> None:
        """Start background workers."""
        if self._worker_task is not None:
            logger.warning("EventEmitter already started")
            return

        logger.info("Starting EventEmitter background workers")
        self._worker_task = asyncio.create_task(self._batch_worker())
        self._flush_task = asyncio.create_task(self._periodic_flush())

        if self.config.transport == TransportType.HTTP:
            self._http_session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10),
                headers={
                    "User-Agent": f"RAIA-SDK/{self.config.sdk_version}",
                    "X-RAIA-Tenant": self.config.tenant,
                    "X-RAIA-Project": self.config.project,
                },
            )

    async def shutdown(self, timeout: float = 30.0) -> None:
        """Gracefully shutdown, flushing pending events."""
        logger.info("Shutting down EventEmitter...")
        self._shutdown = True

        # Flush remaining events
        try:
            await asyncio.wait_for(self.flush(), timeout=timeout / 2)
        except asyncio.TimeoutError:
            logger.error("Flush timeout during shutdown")

        # Cancel workers
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass

        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass

        # Close HTTP session
        if self._http_session:
            await self._http_session.close()

        # Close Kafka producer
        if self._kafka_producer:
            await self._kafka_producer.stop()

        logger.info(
            f"EventEmitter shutdown complete. Stats: emitted={self._events_emitted}, "
            f"dropped={self._events_dropped}, batches_sent={self._batches_sent}, "
            f"batches_failed={self._batches_failed}"
        )

    def emit(self, event: Dict[str, Any]) -> None:
        """
        Emit an event (non-blocking).
        Automatically enriches with env metadata, redacts, and signs.
        """
        try:
            # Enrich with env
            event = self._enrich_event(event)

            # Redact PII/PHI
            if self.redactor:
                event, redaction_metadata = self.redactor.redact(event)
                if redaction_metadata["applied"]:
                    event["redaction"] = redaction_metadata

            # Sign
            if self.signer and self.config.enable_signing:
                signature = self.signer.sign(event)
                event["_signature"] = signature

            # Add to queue (non-blocking)
            try:
                self._queue.put_nowait(event)
                self._events_emitted += 1
            except asyncio.QueueFull:
                self._events_dropped += 1
                logger.error("Event queue full, dropping event")

        except Exception as e:
            logger.exception(f"Failed to emit event: {e}")
            self._events_dropped += 1

    def _enrich_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Add standard metadata to event."""
        if "event_id" not in event:
            event["event_id"] = str(uuid.uuid4())

        if "ts" not in event:
            event["ts"] = datetime.now(timezone.utc).isoformat()

        if "env" not in event:
            event["env"] = {}

        env = event["env"]
        env.setdefault("sdk_version", self.config.sdk_version)
        env.setdefault("schema_version", self.config.schema_version)
        env.setdefault("tenant", self.config.tenant)
        env.setdefault("project", self.config.project)
        env.setdefault("region", self.config.region)
        env.setdefault("deployment", self.config.deployment)

        if self.config.llm:
            env.setdefault("llm", self.config.llm)
        if self.config.llm_version:
            env.setdefault("llm_version", self.config.llm_version)
        if self.config.seed is not None:
            env.setdefault("seed", self.config.seed)
        if self.config.temperature is not None:
            env.setdefault("temperature", self.config.temperature)

        return event

    async def flush(self) -> None:
        """Flush current batch immediately."""
        if not self._batch:
            return

        await self._send_batch(self._batch)
        self._batch = []
        self._batch_bytes = 0

    async def _batch_worker(self) -> None:
        """Worker that accumulates events into batches."""
        while not self._shutdown:
            try:
                # Wait for event with timeout
                event = await asyncio.wait_for(self._queue.get(), timeout=0.1)

                event_json = json.dumps(event)
                event_bytes = len(event_json.encode("utf-8"))

                # Check if adding this event would exceed limits
                should_flush = (
                    len(self._batch) >= self.config.batch_size
                    or self._batch_bytes + event_bytes > self.config.max_batch_bytes
                )

                if should_flush and self._batch:
                    await self._send_batch(self._batch)
                    self._batch = []
                    self._batch_bytes = 0

                self._batch.append(event)
                self._batch_bytes += event_bytes

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.exception(f"Batch worker error: {e}")
                await asyncio.sleep(1)

    async def _periodic_flush(self) -> None:
        """Periodically flush batches."""
        while not self._shutdown:
            await asyncio.sleep(self.config.flush_interval_ms / 1000)
            if self._batch:
                await self.flush()

    async def _send_batch(self, batch: List[Dict[str, Any]]) -> None:
        """Send batch with retries and circuit breaker."""
        if not self._circuit_breaker.can_attempt():
            logger.warning("Circuit breaker open, using fallback")
            await self._fallback_write(batch)
            return

        for attempt in range(self.config.max_retries + 1):
            try:
                if self.config.transport == TransportType.FILE:
                    await self._send_to_file(batch)
                elif self.config.transport == TransportType.HTTP:
                    await self._send_to_http(batch)
                elif self.config.transport == TransportType.KAFKA:
                    await self._send_to_kafka(batch)
                elif self.config.transport == TransportType.OTLP:
                    await self._send_to_otlp(batch)

                self._circuit_breaker.record_success()
                self._batches_sent += 1
                logger.debug(f"Batch sent successfully: {len(batch)} events")
                return

            except Exception as e:
                logger.warning(f"Batch send failed (attempt {attempt + 1}/{self.config.max_retries + 1}): {e}")

                if attempt < self.config.max_retries:
                    delay = min(
                        self.config.retry_base_delay_ms * (2**attempt),
                        self.config.retry_max_delay_ms,
                    )
                    # Add jitter
                    import random

                    jitter = random.uniform(0, delay * 0.1)
                    await asyncio.sleep((delay + jitter) / 1000)
                else:
                    self._circuit_breaker.record_failure()
                    self._batches_failed += 1
                    logger.error(f"Batch send failed after {self.config.max_retries} retries")

                    if self.config.fallback_to_file:
                        await self._fallback_write(batch)

    async def _send_to_file(self, batch: List[Dict[str, Any]]) -> None:
        """Write batch to NDJSON file."""
        file_path = self.config.file_path or f"/tmp/raia_{self.config.tenant}_{self.config.project}.ndjson"
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(file_path, mode="a") as f:
            for event in batch:
                await f.write(json.dumps(event) + "\n")

    async def _send_to_http(self, batch: List[Dict[str, Any]]) -> None:
        """Send batch to HTTP endpoint."""
        if not self.config.http_endpoint:
            raise ValueError("http_endpoint not configured")

        if not self._http_session:
            raise RuntimeError("HTTP session not initialized")

        headers = {}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        # Send as NDJSON
        ndjson = "\n".join(json.dumps(event) for event in batch)

        async with self._http_session.post(
            self.config.http_endpoint,
            data=ndjson,
            headers={**headers, "Content-Type": "application/x-ndjson"},
        ) as response:
            if response.status >= 400:
                text = await response.text()
                raise RuntimeError(f"HTTP {response.status}: {text}")

    async def _send_to_kafka(self, batch: List[Dict[str, Any]]) -> None:
        """Send batch to Kafka."""
        if not self.config.kafka_bootstrap_servers:
            raise ValueError("kafka_bootstrap_servers not configured")

        # Lazy init Kafka producer
        if self._kafka_producer is None:
            from aiokafka import AIOKafkaProducer

            self._kafka_producer = AIOKafkaProducer(
                bootstrap_servers=self.config.kafka_bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )
            await self._kafka_producer.start()

        for event in batch:
            await self._kafka_producer.send(self.config.kafka_topic, value=event)

    async def _send_to_otlp(self, batch: List[Dict[str, Any]]) -> None:
        """Send batch to OpenTelemetry collector."""
        # Simplified: convert events to OTLP log records
        # In production, use opentelemetry-sdk
        raise NotImplementedError("OTLP transport not yet implemented")

    async def _fallback_write(self, batch: List[Dict[str, Any]]) -> None:
        """Write to fallback file when primary transport fails."""
        logger.warning(f"Writing {len(batch)} events to fallback file")
        try:
            Path(self.config.fallback_file_path).parent.mkdir(parents=True, exist_ok=True)
            async with aiofiles.open(self.config.fallback_file_path, mode="a") as f:
                for event in batch:
                    await f.write(json.dumps(event) + "\n")
        except Exception as e:
            logger.exception(f"Fallback write failed: {e}")

    def get_health(self) -> Dict[str, Any]:
        """Get health status."""
        return {
            "status": "healthy" if self._circuit_breaker.state == CircuitState.CLOSED else "degraded",
            "circuit_state": self._circuit_breaker.state.value,
            "queue_size": self._queue.qsize(),
            "batch_size": len(self._batch),
            "events_emitted": self._events_emitted,
            "events_dropped": self._events_dropped,
            "batches_sent": self._batches_sent,
            "batches_failed": self._batches_failed,
        }

    def get_metrics(self) -> Dict[str, int]:
        """Get Prometheus-style metrics."""
        return {
            "raia_events_emitted_total": self._events_emitted,
            "raia_events_dropped_total": self._events_dropped,
            "raia_batches_sent_total": self._batches_sent,
            "raia_batches_failed_total": self._batches_failed,
            "raia_queue_size": self._queue.qsize(),
            "raia_circuit_breaker_state": 1 if self._circuit_breaker.state == CircuitState.OPEN else 0,
        }
