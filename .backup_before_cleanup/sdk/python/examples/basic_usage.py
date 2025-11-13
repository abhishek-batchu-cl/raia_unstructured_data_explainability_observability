"""
Basic usage example for RAIA Python SDK.
"""

import asyncio
import uuid
from raia import EventEmitter, EmitterConfig, Redactor, EventSigner


async def main():
    """Basic example demonstrating SDK usage."""

    # 1. Configure emitter
    config = EmitterConfig(
        tenant="acme-corp",
        project="customer-service",
        agent_id="support-agent-v1.0",
        region="us-east-1",
        transport="file",  # Use file transport for demo
        file_path="/tmp/raia_events.ndjson",
        batch_size=10,
        flush_interval_ms=1000,
        enable_signing=True,
        hmac_secret="your-secret-key-here",
        llm="openai/gpt-4",
        seed=42,
    )

    # 2. Create redactor for PII/PHI
    redactor = Redactor.for_domain("healthcare")

    # 3. Create signer
    signer = EventSigner(secret="your-secret-key-here")

    # 4. Initialize emitter
    emitter = EventEmitter(config=config, redactor=redactor, signer=signer)

    # 5. Start background workers
    await emitter.start()

    try:
        # Example: Emit session start
        session_id = str(uuid.uuid4())
        run_id = str(uuid.uuid4())

        emitter.emit(
            {
                "event": "session_start",
                "session_id": session_id,
                "run_id": run_id,
                "agent_id": config.agent_id,
                "user_id": "user_12345",
                "task": "Patient asking about chest pain symptoms",
                "domain": "healthcare",
                "constraints": ["HIPAA compliant", "no medical advice"],
            }
        )

        # Example: Emit plan created
        emitter.emit(
            {
                "event": "plan_created",
                "session_id": session_id,
                "run_id": run_id,
                "agent_id": config.agent_id,
                "plan": {
                    "steps": [
                        {"id": "1", "description": "Gather symptoms", "tool": "ask_questions"},
                        {"id": "2", "description": "Check urgency", "tool": "triage_protocol"},
                        {"id": "3", "description": "Provide guidance", "tool": "generate_response"},
                    ],
                    "rationale": "Systematic triage approach for chest pain",
                },
                "plan_depth": 3,
                "revision_count": 0,
            }
        )

        # Example: Emit tool call
        tool_event_id = str(uuid.uuid4())
        emitter.emit(
            {
                "event": "tool_call",
                "event_id": tool_event_id,
                "session_id": session_id,
                "run_id": run_id,
                "agent_id": config.agent_id,
                "tool_name": "search_knowledge_base",
                "tool_args": {"query": "chest pain triage guidelines"},
                "is_retry": False,
                "retry_count": 0,
            }
        )

        # Example: Emit observation with evidence
        emitter.emit(
            {
                "event": "observation",
                "session_id": session_id,
                "run_id": run_id,
                "agent_id": config.agent_id,
                "parent_event_id": tool_event_id,
                "observation": "Found 3 relevant guidelines for chest pain assessment",
                "success": True,
                "grounded": True,
                "evidence_refs": [
                    {"source": "internal_kb", "id": "guideline_001", "relevance_score": 0.95},
                    {"source": "internal_kb", "id": "guideline_002", "relevance_score": 0.89},
                ],
                "latency_ms": 234.5,
            }
        )

        # Example: Emit escalation
        emitter.emit(
            {
                "event": "escalation",
                "session_id": session_id,
                "run_id": run_id,
                "agent_id": config.agent_id,
                "escalation_reason": "safety_concern",
                "escalation_target": "human",
                "context": "Symptoms suggest possible cardiac event, requires medical professional assessment",
            }
        )

        # Example: Emit finalized
        emitter.emit(
            {
                "event": "finalized",
                "session_id": session_id,
                "run_id": run_id,
                "agent_id": config.agent_id,
                "final_answer": "Based on your symptoms, please seek immediate medical attention. Escalated to physician.",
                "success": True,
                "constraints_met": True,
                "total_steps": 4,
                "total_tool_calls": 2,
                "latency_ms": 3456.7,
            }
        )

        print(f"Emitted {emitter._events_emitted} events")

        # Force flush
        await emitter.flush()
        print("Flushed all events")

        # Check health
        health = emitter.get_health()
        print(f"Health status: {health}")

    finally:
        # Graceful shutdown
        await emitter.shutdown(timeout=10.0)
        print("Emitter shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
