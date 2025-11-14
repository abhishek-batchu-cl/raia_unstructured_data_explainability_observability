"""
Event Ingestion API for RAIA Platform
Receives events from agentic AI solutions running anywhere (cloud/on-premise)
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/events", tags=["Event Ingestion"])


# ============================================================================
# Models
# ============================================================================

class Event(BaseModel):
    """Event model for ingestion"""
    event_id: str = Field(..., description="Unique event ID")
    event_type: str = Field(..., description="Type of event (query_received, retrieval_completed, etc.)")
    timestamp: str = Field(..., description="ISO format timestamp")
    tenant: str = Field(..., description="Tenant identifier")
    project: str = Field(..., description="Project identifier")
    agent_id: str = Field(..., description="Agent identifier")
    session_id: str = Field(..., description="Session identifier")
    run_id: str = Field(..., description="Run identifier")
    data: Dict[str, Any] = Field(..., description="Event-specific data")


class EventBatch(BaseModel):
    """Batch of events for bulk ingestion"""
    events: List[Event]


class EventResponse(BaseModel):
    """Response after event ingestion"""
    status: str
    event_id: str
    message: Optional[str] = None


class BatchResponse(BaseModel):
    """Response after batch ingestion"""
    status: str
    processed: int
    failed: int
    results: List[Dict[str, Any]]


# ============================================================================
# Authentication
# ============================================================================

async def verify_api_key(authorization: Optional[str] = Header(None)):
    """Verify API key from Authorization header"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")

    api_key = authorization.replace("Bearer ", "")

    # TODO: Verify API key against database
    # For now, accept any non-empty key
    if not api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return api_key


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/ingest", response_model=EventResponse)
async def ingest_single_event(
    event: Event,
    api_key: str = Depends(verify_api_key)
):
    """
    Ingest a single event from an agentic AI solution

    **Event Types:**
    - `query_received`: User query received
    - `retrieval_completed`: Document retrieval completed
    - `llm_call_completed`: LLM call completed
    - `tool_executed`: Tool/function executed
    - `response_generated`: Final response generated
    - `evaluation_completed`: Evaluation metrics computed

    **Example:**
    ```python
    import requests

    event = {
        "event_id": "550e8400-e29b-41d4-a716-446655440000",
        "event_type": "query_received",
        "timestamp": "2025-01-14T12:00:00Z",
        "tenant": "acme-corp",
        "project": "customer-support",
        "agent_id": "support-agent-v1",
        "session_id": "session-123",
        "run_id": "run-456",
        "data": {
            "query": "What is the capital of France?",
            "query_length": 32
        }
    }

    response = requests.post(
        "http://localhost:8000/api/events/ingest",
        json=event,
        headers={"Authorization": "Bearer your-api-key"}
    )
    ```
    """
    try:
        # Validate event
        if not event.event_id or not event.event_type:
            raise HTTPException(status_code=400, detail="Missing required fields")

        # Store event in database
        from database import get_database
        db = get_database()

        # Create events table if not exists
        db.execute_update(
            """
            CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                tenant TEXT,
                project TEXT,
                agent_id TEXT,
                session_id TEXT,
                run_id TEXT,
                data TEXT,
                ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_run_id (run_id),
                INDEX idx_session_id (session_id),
                INDEX idx_timestamp (timestamp)
            )
            """
        )

        # Insert event
        db.execute_update(
            """
            INSERT INTO events (event_id, event_type, timestamp, tenant, project,
                                agent_id, session_id, run_id, data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.event_id,
                event.event_type,
                event.timestamp,
                event.tenant,
                event.project,
                event.agent_id,
                event.session_id,
                event.run_id,
                json.dumps(event.data)
            )
        )

        logger.info(f"Event ingested: {event.event_id} ({event.event_type})")

        # Process event asynchronously (compute metrics, update aggregations, etc.)
        # This would trigger metric computation in the background
        try:
            await process_event_background(event)
        except Exception as e:
            logger.error(f"Error processing event in background: {e}")
            # Don't fail the ingestion if background processing fails

        # Emit real-time update via WebSocket (if websocket is enabled)
        try:
            from websocket import manager as ws_manager
            await ws_manager.broadcast({
                "type": "new_event",
                "event": event.dict()
            }, channel="events")
        except Exception as e:
            logger.warning(f"Could not broadcast event via WebSocket: {e}")

        return EventResponse(
            status="success",
            event_id=event.event_id,
            message=f"Event {event.event_type} ingested successfully"
        )

    except Exception as e:
        logger.error(f"Error ingesting event: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to ingest event: {str(e)}")


@router.post("/batch", response_model=BatchResponse)
async def ingest_batch_events(
    batch: EventBatch,
    api_key: str = Depends(verify_api_key)
):
    """
    Ingest multiple events at once (better performance for high-volume scenarios)

    **Example:**
    ```python
    import requests

    batch = {
        "events": [
            {
                "event_id": "event-1",
                "event_type": "query_received",
                "timestamp": "2025-01-14T12:00:00Z",
                "tenant": "acme-corp",
                "project": "customer-support",
                "agent_id": "support-agent-v1",
                "session_id": "session-123",
                "run_id": "run-456",
                "data": {"query": "What is the capital of France?"}
            },
            {
                "event_id": "event-2",
                "event_type": "retrieval_completed",
                "timestamp": "2025-01-14T12:00:01Z",
                "tenant": "acme-corp",
                "project": "customer-support",
                "agent_id": "support-agent-v1",
                "session_id": "session-123",
                "run_id": "run-456",
                "data": {"num_retrieved": 5}
            }
        ]
    }

    response = requests.post(
        "http://localhost:8000/api/events/batch",
        json=batch,
        headers={"Authorization": "Bearer your-api-key"}
    )
    ```
    """
    results = []
    processed = 0
    failed = 0

    from database import get_database
    db = get_database()

    for event in batch.events:
        try:
            # Insert event
            db.execute_update(
                """
                INSERT INTO events (event_id, event_type, timestamp, tenant, project,
                                    agent_id, session_id, run_id, data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.event_id,
                    event.event_type,
                    event.timestamp,
                    event.tenant,
                    event.project,
                    event.agent_id,
                    event.session_id,
                    event.run_id,
                    json.dumps(event.data)
                )
            )

            results.append({
                "event_id": event.event_id,
                "status": "success"
            })
            processed += 1

        except Exception as e:
            logger.error(f"Error ingesting event {event.event_id}: {e}")
            results.append({
                "event_id": event.event_id,
                "status": "error",
                "error": str(e)
            })
            failed += 1

    # Process all events in background
    try:
        await process_batch_background(batch.events)
    except Exception as e:
        logger.error(f"Error processing batch in background: {e}")

    return BatchResponse(
        status="completed",
        processed=processed,
        failed=failed,
        results=results
    )


@router.get("/stats")
async def get_ingestion_stats(api_key: str = Depends(verify_api_key)):
    """
    Get statistics about event ingestion

    Returns:
    - Total events ingested
    - Events by type
    - Events by tenant/project
    - Ingestion rate
    """
    from database import get_database
    db = get_database()

    stats = {}

    # Total events
    result = db.execute_query("SELECT COUNT(*) as total FROM events")
    stats["total_events"] = result[0]["total"] if result else 0

    # Events by type
    result = db.execute_query(
        """
        SELECT event_type, COUNT(*) as count
        FROM events
        GROUP BY event_type
        ORDER BY count DESC
        """
    )
    stats["events_by_type"] = {row["event_type"]: row["count"] for row in result}

    # Events by tenant
    result = db.execute_query(
        """
        SELECT tenant, COUNT(*) as count
        FROM events
        GROUP BY tenant
        ORDER BY count DESC
        LIMIT 10
        """
    )
    stats["top_tenants"] = {row["tenant"]: row["count"] for row in result}

    # Recent ingestion rate (events per minute in last hour)
    result = db.execute_query(
        """
        SELECT COUNT(*) as count
        FROM events
        WHERE ingested_at > datetime('now', '-1 hour')
        """
    )
    events_last_hour = result[0]["count"] if result else 0
    stats["events_per_minute_last_hour"] = round(events_last_hour / 60, 2)

    return stats


# ============================================================================
# Background Processing
# ============================================================================

async def process_event_background(event: Event):
    """
    Process event in background to compute metrics, update aggregations, etc.
    This is called asynchronously after event ingestion.
    """
    # TODO: Implement metric computation logic
    # - Update run aggregations
    # - Compute retrieval metrics (precision, recall, F1)
    # - Compute answer quality metrics (faithfulness, hallucination)
    # - Update drift detection
    # - Trigger alerts if thresholds exceeded

    logger.info(f"Processing event {event.event_id} in background")


async def process_batch_background(events: List[Event]):
    """Process multiple events in background"""
    for event in events:
        await process_event_background(event)


# ============================================================================
# Health Check
# ============================================================================

@router.get("/health")
async def event_ingestion_health():
    """Check health of event ingestion service"""
    from database import get_database

    try:
        db = get_database()
        # Try to query database
        result = db.execute_query("SELECT COUNT(*) as count FROM events LIMIT 1")

        return {
            "status": "healthy",
            "service": "event_ingestion",
            "database": "connected",
            "total_events": result[0]["count"] if result else 0
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "event_ingestion",
            "error": str(e)
        }
