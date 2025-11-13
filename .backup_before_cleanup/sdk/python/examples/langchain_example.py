"""
Example of using RAIA SDK with LangChain agents.
"""

import asyncio
import os
from raia import EventEmitter, EmitterConfig, Redactor, EventSigner
from raia.integrations.langchain import LangChainCallbackHandler, instrumented_tool

# Mock LangChain imports (replace with actual imports)
try:
    from langchain.agents import AgentExecutor, create_react_agent
    from langchain.prompts import PromptTemplate
    from langchain.tools import Tool
    from langchain_openai import ChatOpenAI

    LANGCHAIN_AVAILABLE = True
except ImportError:
    print("LangChain not installed. Install with: pip install langchain langchain-openai")
    LANGCHAIN_AVAILABLE = False


async def main():
    """Example integrating RAIA with LangChain."""

    if not LANGCHAIN_AVAILABLE:
        print("Skipping example - LangChain not available")
        return

    # 1. Setup RAIA emitter
    config = EmitterConfig(
        tenant="acme-corp",
        project="customer-support",
        agent_id="langchain-agent-v1.0",
        transport="file",
        file_path="/tmp/langchain_raia_events.ndjson",
        enable_signing=True,
        hmac_secret="demo-secret",
        llm="openai/gpt-4",
    )

    redactor = Redactor.for_domain("general")
    signer = EventSigner("demo-secret")
    emitter = EventEmitter(config, redactor, signer)

    await emitter.start()

    try:
        # 2. Create LangChain callback handler
        callback = LangChainCallbackHandler(emitter=emitter, agent_id="langchain-agent-v1.0")

        # 3. Define tools with instrumentation
        @instrumented_tool(emitter, "search_database")
        def search_database(query: str) -> str:
            """Search internal database."""
            # Simulate search
            return f"Found 3 results for: {query}"

        @instrumented_tool(emitter, "calculate", evidence_extractor=lambda x: [])
        def calculate(expression: str) -> str:
            """Perform calculations."""
            try:
                result = eval(expression)
                return f"Result: {result}"
            except Exception as e:
                return f"Error: {e}"

        # Create LangChain tools
        tools = [
            Tool(
                name="search_database",
                func=search_database,
                description="Search internal database for information",
            ),
            Tool(
                name="calculate",
                func=calculate,
                description="Perform mathematical calculations",
            ),
        ]

        # 4. Create LangChain agent
        llm = ChatOpenAI(model="gpt-4", temperature=0.7)

        prompt = PromptTemplate.from_template(
            """Answer the following question as best you can. You have access to these tools:

{tools}

Use this format:

Question: the input question
Thought: think about what to do
Action: the action to take (one of [{tool_names}])
Action Input: the input to the action
Observation: the result of the action
... (repeat Thought/Action/Action Input/Observation as needed)
Thought: I now know the final answer
Final Answer: the final answer

Question: {input}
{agent_scratchpad}"""
        )

        agent = create_react_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, callbacks=[callback], verbose=True)

        # 5. Run agent
        result = await agent_executor.ainvoke(
            {
                "input": "Search for information about Python, then calculate 25 * 4",
                "user_id": "demo_user",
                "domain": "general",
            }
        )

        print("\n=== Agent Result ===")
        print(result)

        # 6. Flush and check metrics
        await emitter.flush()
        print(f"\n=== Metrics ===")
        print(f"Events emitted: {emitter._events_emitted}")
        print(f"Events dropped: {emitter._events_dropped}")
        print(f"Health: {emitter.get_health()}")

    finally:
        await emitter.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
