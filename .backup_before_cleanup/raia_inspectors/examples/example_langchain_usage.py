"""
RAIA Inspectors - LangChain Example

Demonstrates how to use RAIAExecutionInspector with a simple LangChain agent.
"""

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

from raia_inspectors import (
    RAIAExecutionInspector,
    SQLiteRAIAStorage,
    RAIAConfig,
    set_raia_config
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


def run_langchain_example():
    """Run a complete LangChain example with RAIA inspection."""

    if not LANGCHAIN_AVAILABLE:
        print("Please install langchain: pip install langchain")
        return

    print("=" * 80)
    print("RAIA Inspectors - LangChain Example")
    print("=" * 80)
    print()

    # 1. Configure RAIA
    print("1. Configuring RAIA storage...")
    storage = SQLiteRAIAStorage(db_path="langchain_example.db")
    config = RAIAConfig(default_storage=storage, app_name="langchain_demo", environment="dev")
    set_raia_config(config)
    print("   ✓ Storage configured\n")

    # 2. Create tools
    print("2. Creating tools...")
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

    # 3. Create LLM (using FakeListLLM for demo)
    print("3. Creating LLM...")
    responses = [
        "I should search for information about Paris",
        "Action: Search\nAction Input: capital of France",
        "Final Answer: The capital of France is Paris.",
    ]
    llm = FakeListLLM(responses=responses)
    print("   ✓ LLM created\n")

    # 4. Create agent (using simple prompt instead of hub.pull for reliability)
    print("4. Creating agent...")
    from langchain.prompts import PromptTemplate

    template = """Answer the following question: {input}

You have access to these tools:
{tools}

Use the following format:
Thought: think about what to do
Action: the action to take (one of [{tool_names}])
Action Input: the input to the action
Observation: the result of the action
... (repeat Thought/Action/Action Input/Observation as needed)
Thought: I now know the final answer
Final Answer: the final answer

Question: {input}
{agent_scratchpad}"""

    prompt = PromptTemplate.from_template(template)

    # Simple chain instead of full agent for demo
    from langchain.chains import LLMChain

    chain = LLMChain(llm=llm, prompt=PromptTemplate.from_template("{input}"))
    print("   ✓ Chain created\n")

    # 5. Create RAIA inspector
    print("5. Creating RAIA inspector...")
    inspector = RAIAExecutionInspector(
        storage=storage,
        agent_name="langchain_demo_agent",
        session_id="demo_session_001"
    )
    print(f"   ✓ Inspector created with run_id: {inspector.run_id}\n")

    # 6. Run the chain with inspector
    print("6. Running chain with RAIA inspection...")
    print("-" * 80)

    try:
        result = chain.invoke(
            {"input": "What is the capital of France?"},
            config={"callbacks": [inspector], "tags": ["demo", "geography"]}
        )
        print(f"Result: {result}")
    except Exception as e:
        logger.error(f"Error during execution: {e}", exc_info=True)

    print("-" * 80)
    print()

    # 7. Query and display metrics
    print("7. Querying metrics from storage...")
    print("=" * 80)

    # Get run summary
    run = storage.get_run(inspector.run_id)
    if run:
        print(f"\n📊 Run Summary:")
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
        print(f"\n📈 Node Metrics ({len(node_metrics)} nodes):")
        for metric in node_metrics:
            status = "✓" if metric.success else "✗"
            print(f"   {status} {metric.node_name} ({metric.node_type}): {metric.latency_ms:.2f}ms")
            if not metric.success:
                print(f"      Error: {metric.error_message}")

    # Get signals
    signals = storage.get_signals_for_run(inspector.run_id)
    if signals:
        print(f"\n⚠️  Behavioral Signals ({len(signals)}):")
        for signal in signals:
            print(f"   [{signal.severity.upper()}] {signal.signal_type}: {signal.message}")
    else:
        print(f"\n✓ No behavioral signals detected")

    # Get semantic scores
    scores = storage.get_semantic_scores_for_run(inspector.run_id)
    if scores:
        print(f"\n🎯 Semantic Scores ({len(scores)}):")
        for score in scores:
            print(f"   {score.dimension}: {score.score:.2f}")
            if score.explanation:
                print(f"      {score.explanation}")
    else:
        print(f"\n   (No semantic evaluation performed)")

    print("\n" + "=" * 80)
    print("✓ Example completed successfully!")
    print(f"📁 Database saved to: langchain_example.db")
    print("=" * 80)


if __name__ == "__main__":
    run_langchain_example()
