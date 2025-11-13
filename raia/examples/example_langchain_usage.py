"""
RAIA - LangChain Example

Demonstrates how to use RAIA's unified package for both event logging
and execution inspection with LangChain agents.

This example shows:
1. Event logging for production telemetry
2. Execution inspection for performance monitoring
3. How to use both systems together for comprehensive observability
"""

import asyncio
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from langchain.llms import FakeListLLM
    from langchain.agents import AgentExecutor, create_react_agent
    from langchain.tools import Tool
    from langchain import hub
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logger.error("LangChain not installed. Install with: pip install langchain")

# Import from unified raia package
from raia import (
    # Execution Inspection
    RAIAExecutionInspector,
    SQLiteRAIAStorage,
    RAIAConfig,
    set_raia_config,
    # Event Logging (for production telemetry)
    EventEmitter,
    EmitterConfig,
    TransportType,
    Redactor,
    RedactionRule,
)


def search_tool(query: str) -> str:
    """Fake search tool for demonstration."""
    logger.info(f"Search tool called with: {query}")
    return f"Search results for '{query}': Found 3 results about {query}."


def calculator_tool(expression: str) -> str:
    """Fake calculator tool for demonstration."""
    logger.info(f"Calculator tool called with: {expression}")
    try:
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {e}"


async def run_langchain_example():
    """Run a complete LangChain example with RAIA inspection and event logging."""

    if not LANGCHAIN_AVAILABLE:
        print("Please install langchain: pip install langchain")
        return

    print("=" * 80)
    print("RAIA - LangChain Example (Event Logging + Execution Inspection)")
    print("=" * 80)
    print()

    # 1. Configure RAIA Inspector Storage
    print("1. Configuring RAIA inspector storage...")
    storage = SQLiteRAIAStorage(db_path="langchain_example.db")
    config = RAIAConfig(default_storage=storage, app_name="langchain_demo", environment="dev")
    set_raia_config(config)
    print("   ✓ Storage configured\n")

    # 2. Configure Event Emitter (for production telemetry)
    print("2. Configuring event emitter...")
    # Configure event logging with file transport
    emitter_config = EmitterConfig(
        app_name="langchain_demo",
        environment="dev",
        transport_type=TransportType.FILE,
        file_path="langchain_events.jsonl",
        batch_size=10,
        flush_interval_ms=1000,
    )

    # Add PII redaction for sensitive data
    redactor = Redactor()
    redactor.add_rule(RedactionRule(
        pattern=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        replacement="[EMAIL_REDACTED]",
        description="Email addresses"
    ))
    emitter_config.redactor = redactor

    # Create and start emitter
    emitter = EventEmitter(emitter_config)
    await emitter.start()
    print("   ✓ Event emitter started\n")

    # 3. Create tools
    print("3. Creating tools...")
    tools = [
        Tool(
            name="Search",
            func=search_tool,
            description="Useful for searching information on the internet"
        ),
        Tool(
            name="Calculator",
            func=calculator_tool,
            description="Useful for doing math calculations"
        )
    ]
    print("   ✓ Tools created\n")

    # 4. Create LLM (using FakeListLLM for demo)
    print("4. Creating LLM...")
    responses = [
        "I should search for information about Paris",
        "Action: Search\nAction Input: capital of France",
        "Final Answer: The capital of France is Paris.",
    ]
    llm = FakeListLLM(responses=responses)
    print("   ✓ LLM created\n")

    # 5. Create agent (using simple prompt instead of hub.pull for reliability)
    print("5. Creating agent...")
    from langchain.prompts import PromptTemplate
    from langchain.chains import LLMChain

    # Simple chain instead of full agent for demo
    chain = LLMChain(llm=llm, prompt=PromptTemplate.from_template("{input}"))
    print("   ✓ Chain created\n")

    # 6. Create RAIA inspector
    print("6. Creating RAIA execution inspector...")
    inspector = RAIAExecutionInspector(
        storage=storage,
        agent_name="langchain_demo_agent",
        session_id="demo_session_001"
    )
    print(f"   ✓ Inspector created with run_id: {inspector.run_id}\n")

    # 7. Run the chain with both systems
    print("7. Running chain with RAIA inspection and event logging...")
    print("-" * 80)

    try:
        # Log event: Chain execution started
        await emitter.emit({
            "event_type": "chain_execution_started",
            "run_id": inspector.run_id,
            "agent_name": "langchain_demo_agent",
            "query": "What is the capital of France?",
            "tags": ["demo", "geography"]
        })

        # Execute chain with inspector callback
        # The inspector tracks performance metrics (latency, tokens, etc.)
        result = chain.invoke(
            {"input": "What is the capital of France?"},
            config={"callbacks": [inspector], "tags": ["demo", "geography"]}
        )
        print(f"Result: {result}")

        # Log event: Chain execution completed
        await emitter.emit({
            "event_type": "chain_execution_completed",
            "run_id": inspector.run_id,
            "result": str(result),
            "status": "success"
        })

    except Exception as e:
        logger.error(f"Error during execution: {e}", exc_info=True)
        # Log error event
        await emitter.emit({
            "event_type": "chain_execution_failed",
            "run_id": inspector.run_id,
            "error": str(e),
            "status": "error"
        })

    print("-" * 80)
    print()

    # 8. Query and display metrics from inspector storage
    print("8. Querying metrics from inspector storage...")
    print("=" * 80)

    # Get run summary from inspector storage
    run = storage.get_run(inspector.run_id)
    if run:
        print(f"\n[Inspector Metrics] Run Summary:")
        print(f"   Run ID: {run.run_id}")
        print(f"   Agent: {run.agent_name}")
        print(f"   Session: {run.session_id}")
        print(f"   Status: {run.status}")
        print(f"   Duration: {run.total_latency_ms:.2f}ms" if run.total_latency_ms else "   Duration: N/A")
        if run.total_tokens_prompt:
            print(f"   Tokens (prompt): {run.total_tokens_prompt}")
        if run.total_tokens_completion:
            print(f"   Tokens (completion): {run.total_tokens_completion}")
        if run.total_cost_usd:
            print(f"   Cost: ${run.total_cost_usd:.4f}")

    # Get node metrics
    node_metrics = storage.get_node_metrics_for_run(inspector.run_id)
    if node_metrics:
        print(f"\n[Inspector Metrics] Node Metrics ({len(node_metrics)} nodes):")
        for metric in node_metrics:
            status = "✓" if metric.success else "✗"
            print(f"   {status} {metric.node_name} ({metric.node_type}): {metric.latency_ms:.2f}ms")
            if not metric.success:
                print(f"      Error: {metric.error_message}")

    # Get signals
    signals = storage.get_signals_for_run(inspector.run_id)
    if signals:
        print(f"\n[Inspector Metrics] Behavioral Signals ({len(signals)}):")
        for signal in signals:
            print(f"   [{signal.severity.upper()}] {signal.signal_type}: {signal.message}")
    else:
        print(f"\n[Inspector Metrics] No behavioral signals detected")

    # Get semantic scores
    scores = storage.get_semantic_scores_for_run(inspector.run_id)
    if scores:
        print(f"\n[Inspector Metrics] Semantic Scores ({len(scores)}):")
        for score in scores:
            print(f"   {score.dimension}: {score.score:.2f}")
            if score.explanation:
                print(f"      {score.explanation}")
    else:
        print(f"\n[Inspector Metrics] (No semantic evaluation performed)")

    # 9. Shutdown and display event logging info
    print("\n9. Shutting down event emitter...")
    await emitter.shutdown()
    print("   ✓ Event emitter shutdown complete\n")

    print("=" * 80)
    print("Example completed successfully!")
    print()
    print("Key Takeaways:")
    print("  • Inspector Storage: Performance metrics in langchain_example.db")
    print("  • Event Logging: Production events in langchain_events.jsonl")
    print()
    print("How the systems work together:")
    print("  • Inspectors: Real-time performance tracking and behavioral analysis")
    print("  • Events: Production telemetry with batching and PII redaction")
    print("  • Use inspectors for debugging, events for production monitoring")
    print("=" * 80)


if __name__ == "__main__":
    # Run the async example
    asyncio.run(run_langchain_example())
