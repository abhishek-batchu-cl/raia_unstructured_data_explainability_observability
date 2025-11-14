"""
Complete Example: Agentic AI Solution with RAIA Instrumentation

This example shows how to instrument a real agentic AI solution
(using LangChain) with RAIA to track all metrics and display them
in the dashboard.

This can run anywhere: AWS Lambda, EC2, GCP Cloud Run, Azure Functions,
Docker container, or local machine.
"""

import os
import sys
from typing import List, Dict
from datetime import datetime
import time

# Add parent directory to path to import raia_client
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from backend.raia_client import RAIAClient, RAIAConfig, RAIARun


# ============================================================================
# Mock Components (replace with your real implementation)
# ============================================================================

class MockRetriever:
    """Mock document retriever (replace with your actual retriever)"""

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """Retrieve documents (mock implementation)"""
        print(f"  → Retrieving documents for: '{query}'")
        time.sleep(0.1)  # Simulate retrieval time

        # Mock retrieved documents
        if "France" in query or "Paris" in query:
            return [
                {
                    "id": "doc_france_001",
                    "content": "Paris is the capital and most populous city of France. It has an estimated population of 2.16 million.",
                    "score": 0.95,
                    "metadata": {"source": "wikipedia", "date": "2024-01-01"}
                },
                {
                    "id": "doc_france_002",
                    "content": "France is a country in Western Europe. It is bordered by Belgium, Luxembourg, Germany, Switzerland, Italy, and Spain.",
                    "score": 0.87,
                    "metadata": {"source": "encyclopedia", "date": "2024-01-01"}
                },
                {
                    "id": "doc_paris_001",
                    "content": "The city of Paris contains numerous iconic landmarks including the Eiffel Tower, Notre-Dame Cathedral, and the Louvre Museum.",
                    "score": 0.82,
                    "metadata": {"source": "travel_guide", "date": "2024-01-01"}
                }
            ]
        else:
            return [
                {
                    "id": "doc_general_001",
                    "content": "General information document.",
                    "score": 0.65,
                    "metadata": {"source": "general", "date": "2024-01-01"}
                }
            ]


class MockLLM:
    """Mock LLM (replace with your actual LLM: OpenAI, Anthropic, etc.)"""

    def __init__(self, model_name: str = "gpt-4"):
        self.model_name = model_name

    def generate(self, prompt: str) -> tuple[str, int, float]:
        """Generate response (mock implementation)"""
        print(f"  → Calling LLM: {self.model_name}")
        time.sleep(0.2)  # Simulate LLM latency

        # Mock response based on prompt
        if "capital of France" in prompt:
            response = "Based on the provided context, the capital of France is Paris. Paris is the most populous city in France with an estimated population of 2.16 million people."
            tokens = 45
        else:
            response = "I can provide information based on the context provided."
            tokens = 15

        latency_ms = 200.0
        return response, tokens, latency_ms


class MockTool:
    """Mock tool/function (replace with your actual tools)"""

    @staticmethod
    def calculator(expression: str) -> float:
        """Simple calculator tool"""
        print(f"  → Using tool: calculator({expression})")
        try:
            result = eval(expression)
            return result
        except:
            return None


# ============================================================================
# Agentic AI Solution with RAIA Instrumentation
# ============================================================================

class AgenticAIWithRAIA:
    """
    Example agentic AI solution with RAIA instrumentation

    This demonstrates how to instrument your existing agentic AI solution
    to send metrics to RAIA platform.
    """

    def __init__(self, raia_config: RAIAConfig):
        """
        Initialize agentic AI solution

        Args:
            raia_config: RAIA configuration
        """
        # Initialize RAIA client
        self.raia = RAIAClient(raia_config)

        # Initialize your AI components
        self.retriever = MockRetriever()
        self.llm = MockLLM(model_name="gpt-4")
        self.tools = {
            "calculator": MockTool.calculator
        }

        print(f"✓ Initialized AgenticAI with RAIA instrumentation")
        print(f"  RAIA Platform: {raia_config.api_url}")
        print(f"  Tenant: {raia_config.tenant}")
        print(f"  Project: {raia_config.project}")
        print(f"  Agent: {raia_config.agent_id}")
        print()

    def process_query(self, query: str, use_tools: bool = False) -> str:
        """
        Process a user query with full RAIA instrumentation

        Args:
            query: User query
            use_tools: Whether to use tools in this run

        Returns:
            Final response
        """
        print(f"{'='*80}")
        print(f"Processing Query: \"{query}\"")
        print(f"{'='*80}")

        start_time = time.time()

        # Use RAIA context manager for automatic run management
        with RAIARun(self.raia, query=query, metadata={"use_tools": use_tools}) as raia:

            # Step 1: Retrieval
            print("\n[1] Retrieval Phase")
            retrieval_start = time.time()
            retrieved_docs = self.retriever.retrieve(query, top_k=5)
            retrieval_time_ms = (time.time() - retrieval_start) * 1000

            raia.log_retrieval(
                query=query,
                retrieved_docs=retrieved_docs,
                top_k=5,
                retrieval_time_ms=retrieval_time_ms
            )
            print(f"  ✓ Retrieved {len(retrieved_docs)} documents")
            print(f"  ✓ Logged to RAIA")

            # Step 2: Build context and prompt
            print("\n[2] LLM Call Phase")
            context = "\n\n".join([
                f"[Document {i+1}]\n{doc['content']}"
                for i, doc in enumerate(retrieved_docs[:3])
            ])

            prompt = f"""Based on the following context, answer the question.

Context:
{context}

Question: {query}

Answer:"""

            # Step 3: LLM call
            llm_start = time.time()
            response, tokens, llm_latency = self.llm.generate(prompt)
            llm_time_ms = (time.time() - llm_start) * 1000

            raia.log_llm_call(
                prompt=prompt,
                response=response,
                model=self.llm.model_name,
                tokens_used=tokens,
                latency_ms=llm_latency
            )
            print(f"  ✓ LLM call completed")
            print(f"  ✓ Logged to RAIA")

            # Step 4: Tool usage (optional)
            if use_tools:
                print("\n[3] Tool Usage Phase")
                tool_result = self.tools["calculator"]("2 + 2")

                raia.log_tool_usage(
                    tool_name="calculator",
                    tool_input={"expression": "2 + 2"},
                    tool_output=tool_result,
                    success=True
                )
                print(f"  ✓ Tool executed: calculator(2 + 2) = {tool_result}")
                print(f"  ✓ Logged to RAIA")

            # Step 5: Final response
            print("\n[4] Response Phase")
            total_time_ms = (time.time() - start_time) * 1000
            sources = [doc["id"] for doc in retrieved_docs[:3]]

            raia.log_response(
                response=response,
                sources=sources,
                confidence=0.92,
                response_time_ms=total_time_ms
            )
            print(f"  ✓ Response generated")
            print(f"  ✓ Logged to RAIA")

            # Step 6: Evaluation (if you have ground truth)
            # In production, this might come from human feedback or test sets
            print("\n[5] Evaluation Phase (optional)")
            raia.log_evaluation(
                ground_truth="Paris",
                relevance_score=0.95,
                faithfulness_score=0.93,
                correctness_score=0.98,
                hallucination_score=0.05
            )
            print(f"  ✓ Evaluation logged to RAIA")

        # Context manager automatically calls end_run()

        print(f"\n{'='*80}")
        print(f"✓ Query processed successfully in {total_time_ms:.0f}ms")
        print(f"✓ All metrics sent to RAIA platform")
        print(f"✓ Check dashboard at: http://localhost:5173")
        print(f"{'='*80}\n")

        return response


# ============================================================================
# Main Execution
# ============================================================================

def main():
    """
    Main execution - demonstrates how to use RAIA in your agentic AI solution
    """
    print("\n" + "="*80)
    print("AGENTIC AI WITH RAIA INSTRUMENTATION - COMPLETE EXAMPLE")
    print("="*80 + "\n")

    # Step 1: Configure RAIA
    print("[SETUP] Configuring RAIA connection...")
    raia_config = RAIAConfig(
        # RAIA platform URL (change to your deployment)
        api_url=os.getenv("RAIA_API_URL", "http://localhost:8000"),

        # API key for authentication
        api_key=os.getenv("RAIA_API_KEY", "demo-api-key"),

        # Your organization/company identifier
        tenant=os.getenv("RAIA_TENANT", "acme-corporation"),

        # Project identifier
        project=os.getenv("RAIA_PROJECT", "customer-support-bot"),

        # Agent identifier
        agent_id=os.getenv("RAIA_AGENT_ID", "support-agent-v1"),

        # Connection settings
        timeout=5,
        enable_logging=True
    )
    print("✓ RAIA configured\n")

    # Step 2: Initialize your agentic AI solution with RAIA
    print("[SETUP] Initializing Agentic AI solution...")
    agent = AgenticAIWithRAIA(raia_config)

    # Step 3: Process queries (this simulates your production workload)
    print("[EXECUTION] Processing queries...\n")

    # Query 1: Simple RAG query
    query1 = "What is the capital of France?"
    response1 = agent.process_query(query1, use_tools=False)
    print(f"Response: {response1}\n")

    # Small delay between queries
    time.sleep(1)

    # Query 2: Query with tool usage
    query2 = "What is the population of Paris plus 2?"
    response2 = agent.process_query(query2, use_tools=True)
    print(f"Response: {response2}\n")

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"✓ Processed 2 queries")
    print(f"✓ All events sent to RAIA platform")
    print(f"✓ Metrics computed and stored")
    print(f"\n📊 View metrics in RAIA dashboard:")
    print(f"   → Frontend: http://localhost:5173")
    print(f"   → API Docs: http://localhost:8000/docs")
    print(f"   → Metrics: http://localhost:8000/api/metrics/dashboard")
    print(f"\n💡 In production, this can run:")
    print(f"   • AWS Lambda / EC2 / ECS")
    print(f"   • GCP Cloud Run / Compute Engine")
    print(f"   • Azure Functions / App Service")
    print(f"   • Docker containers")
    print(f"   • Kubernetes pods")
    print(f"   • On-premise servers")
    print("="*80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Interrupted by user")
    except Exception as e:
        print(f"\n\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
