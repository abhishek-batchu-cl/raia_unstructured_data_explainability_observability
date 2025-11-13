"""
RAIA - LangGraph Example

Demonstrates how to use RAIA's unified package for both event logging
and behavioral inspection with LangGraph graphs.

This example shows:
1. Event logging for production telemetry
2. Behavioral inspection for loop and pattern detection
3. How to use both systems together for comprehensive graph observability
"""

import asyncio
import logging
from typing import TypedDict, Annotated
from operator import add

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logger.error("LangGraph not installed. Install with: pip install langgraph")

# Import from unified raia package
from raia import (
    # Behavioral Inspection
    RAIABehaviorInspector,
    SQLiteRAIAStorage,
    RAIAConfig,
    set_raia_config,
    stream_with_inspection,
    # Event Logging (for production telemetry)
    EventEmitter,
    EmitterConfig,
    TransportType,
)


# Define state
class AgentState(TypedDict):
    """State for our demo agent."""
    messages: Annotated[list[str], add]
    query: str
    search_count: int
    result: str


def search_node(state: AgentState) -> AgentState:
    """Simulated search node."""
    logger.info(f"Search node executing for query: {state.get('query', 'N/A')}")

    # Simulate search
    search_result = f"Found information about: {state.get('query', 'unknown')}"

    return {
        **state,
        "messages": [f"Search: {search_result}"],
        "search_count": state.get("search_count", 0) + 1
    }


def process_node(state: AgentState) -> AgentState:
    """Simulated processing node."""
    logger.info("Process node executing")

    messages = state.get("messages", [])
    result = f"Processed {len(messages)} messages"

    return {
        **state,
        "messages": [f"Process: {result}"],
        "result": result
    }


def decide_node(state: AgentState) -> str:
    """Decision node - determines next step."""
    search_count = state.get("search_count", 0)

    # Simulate loop condition
    if search_count < 2:
        logger.info(f"Decision: Continue searching (count: {search_count})")
        return "search"
    else:
        logger.info("Decision: Proceed to process")
        return "process"


def answer_node(state: AgentState) -> AgentState:
    """Final answer node."""
    logger.info("Answer node executing")

    result = state.get("result", "No result")
    return {
        **state,
        "messages": [f"Final answer: {result}"]
    }


def create_demo_graph():
    """Create a demo LangGraph with intentional patterns for detection."""

    if not LANGGRAPH_AVAILABLE:
        raise ImportError("LangGraph not installed")

    # Create graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("search", search_node)
    workflow.add_node("decide", decide_node)
    workflow.add_node("process", process_node)
    workflow.add_node("answer", answer_node)

    # Add edges
    workflow.set_entry_point("search")
    workflow.add_edge("search", "decide")

    # Conditional edges from decide
    workflow.add_conditional_edges(
        "decide",
        lambda state: decide_node(state),
        {
            "search": "search",  # Loop back
            "process": "process"
        }
    )

    workflow.add_edge("process", "answer")
    workflow.add_edge("answer", END)

    return workflow.compile()


async def run_langgraph_example():
    """Run a complete LangGraph example with RAIA inspection and event logging."""

    if not LANGGRAPH_AVAILABLE:
        print("Please install langgraph: pip install langgraph")
        return

    print("=" * 80)
    print("RAIA - LangGraph Example (Event Logging + Behavioral Inspection)")
    print("=" * 80)
    print()

    # 1. Configure RAIA Inspector Storage
    print("1. Configuring RAIA inspector storage...")
    storage = SQLiteRAIAStorage(db_path="langgraph_example.db")
    config = RAIAConfig(default_storage=storage, app_name="langgraph_demo", environment="dev")
    set_raia_config(config)
    print("   ✓ Storage configured\n")

    # 2. Configure Event Emitter (for production telemetry)
    print("2. Configuring event emitter...")
    emitter_config = EmitterConfig(
        app_name="langgraph_demo",
        environment="dev",
        transport_type=TransportType.FILE,
        file_path="langgraph_events.jsonl",
        batch_size=10,
        flush_interval_ms=1000,
    )
    emitter = EventEmitter(emitter_config)
    await emitter.start()
    print("   ✓ Event emitter started\n")

    # 3. Create graph
    print("3. Creating LangGraph...")
    graph = create_demo_graph()
    print("   ✓ Graph created\n")

    # 4. Run with inspection and event logging
    print("4. Running graph with RAIA inspection and event logging...")
    print("-" * 80)

    input_data = {
        "query": "What is machine learning?",
        "messages": [],
        "search_count": 0,
        "result": ""
    }

    run_id = None
    events = []
    node_count = 0

    try:
        # Log event: Graph execution started
        await emitter.emit({
            "event_type": "graph_execution_started",
            "graph_name": "search_decide_process",
            "agent_name": "langgraph_demo_agent",
            "input_query": input_data["query"]
        })

        # Stream graph execution with behavioral inspection
        # The inspector detects loops, redundancy, and other patterns
        for event in stream_with_inspection(
            graph,
            input_data,
            agent_name="langgraph_demo_agent",
            graph_name="search_decide_process",
            storage=storage
        ):
            print(f"Event: {event}")
            events.append(event)
            node_count += 1

            # Log event for each node execution
            await emitter.emit({
                "event_type": "node_executed",
                "node_name": str(event.get("node", "unknown")),
                "event_data": str(event)
            })

            # Capture run_id from the inspector callback
            # In production, you'd access this from the callback handler
            if run_id is None and hasattr(storage, 'last_run_id'):
                run_id = storage.last_run_id

        # Log event: Graph execution completed
        await emitter.emit({
            "event_type": "graph_execution_completed",
            "node_count": node_count,
            "status": "success"
        })

    except Exception as e:
        logger.error(f"Error during execution: {e}", exc_info=True)
        # Log error event
        await emitter.emit({
            "event_type": "graph_execution_failed",
            "error": str(e),
            "status": "error"
        })

    print("-" * 80)
    print()

    # 5. Query and display metrics from inspector storage
    print("5. Querying metrics from inspector storage...")
    print("=" * 80)

    # Get all runs (we'll get the latest)
    # For demo, we'll manually inspect the database
    # In real usage, you'd track the run_id properly

    import sqlite3
    conn = sqlite3.connect("langgraph_example.db")
    cursor = conn.cursor()

    # Get latest run
    cursor.execute("SELECT run_id FROM raia_runs ORDER BY start_time DESC LIMIT 1")
    row = cursor.fetchone()

    if row:
        run_id = row[0]
        print(f"\n[Inspector Metrics] Latest Run ID: {run_id}\n")

        # Get run summary
        run = storage.get_run(run_id)
        if run:
            print(f"[Inspector Metrics] Run Summary:")
            print(f"   Graph: {run.graph_name}")
            print(f"   Agent: {run.agent_name}")
            print(f"   Status: {run.status}")
            print(f"   Duration: {run.total_latency_ms:.2f}ms" if run.total_latency_ms else "   Duration: N/A")

        # Get node metrics
        node_metrics = storage.get_node_metrics_for_run(run_id)
        if node_metrics:
            print(f"\n[Inspector Metrics] Node Metrics ({len(node_metrics)} nodes):")
            for metric in node_metrics:
                status = "✓" if metric.success else "✗"
                print(f"   {status} {metric.node_name}: {metric.latency_ms:.2f}ms")

        # Get behavioral signals (loops, redundancy, etc.)
        signals = storage.get_signals_for_run(run_id)
        if signals:
            print(f"\n[Inspector Metrics] Behavioral Signals ({len(signals)}):")
            for signal in signals:
                print(f"   [{signal.severity.upper()}] {signal.signal_type}")
                print(f"      {signal.message}")
                if signal.metadata:
                    print(f"      Metadata: {signal.metadata}")
        else:
            print(f"\n[Inspector Metrics] No behavioral signals detected (expected loops in this demo)")

        # Get semantic scores
        scores = storage.get_semantic_scores_for_run(run_id)
        if scores:
            print(f"\n[Inspector Metrics] Semantic Scores ({len(scores)}):")
            for score in scores:
                print(f"   {score.dimension}: {score.score:.2f}")
        else:
            print(f"\n[Inspector Metrics] (No semantic evaluation performed)")

    conn.close()

    # 6. Shutdown and display event logging info
    print("\n6. Shutting down event emitter...")
    await emitter.shutdown()
    print("   ✓ Event emitter shutdown complete\n")

    print("=" * 80)
    print("Example completed successfully!")
    print()
    print("Key Takeaways:")
    print("  • Inspector Storage: Behavioral signals in langgraph_example.db")
    print("  • Event Logging: Production events in langgraph_events.jsonl")
    print()
    print("What this example demonstrates:")
    print("  • Loop detection: Search node called multiple times (behavioral inspection)")
    print("  • Node execution tracking: Performance metrics for each node")
    print("  • Event logging: Production telemetry with batching")
    print()
    print("How the systems work together:")
    print("  • Inspectors: Real-time pattern detection (loops, redundancy, stalls)")
    print("  • Events: Production telemetry with async batching and PII redaction")
    print("  • Use inspectors for debugging, events for production monitoring")
    print("=" * 80)


if __name__ == "__main__":
    # Run the async example
    asyncio.run(run_langgraph_example())
