"""
RAIA Client Library
Use this in your agentic AI solution to send events to RAIA platform
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid
import requests
import json
import logging
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class RAIAConfig:
    """Configuration for RAIA client"""
    api_url: str
    api_key: str
    tenant: str
    project: str
    agent_id: str
    timeout: int = 5
    batch_size: int = 10
    enable_logging: bool = True


class RAIAClient:
    """
    RAIA Client for instrumenting agentic AI solutions

    Usage:
    ```python
    from raia_client import RAIAClient, RAIAConfig

    # Initialize client
    config = RAIAConfig(
        api_url="https://your-raia-instance.com",
        api_key="your-api-key",
        tenant="your-company",
        project="your-project",
        agent_id="your-agent"
    )
    raia = RAIAClient(config)

    # Start a run
    run_id = raia.start_run("What is the capital of France?")

    # Log retrieval
    raia.log_retrieval(
        query="What is the capital of France?",
        retrieved_docs=[
            {"id": "doc1", "content": "Paris is the capital of France", "score": 0.95},
            {"id": "doc2", "content": "France is in Europe", "score": 0.85}
        ]
    )

    # Log LLM call
    raia.log_llm_call(
        prompt="Based on the context, answer: What is the capital of France?",
        response="The capital of France is Paris.",
        model="gpt-4",
        tokens_used=45
    )

    # Log final response
    raia.log_response(
        response="The capital of France is Paris.",
        sources=["doc1", "doc2"]
    )

    # Optionally log evaluation metrics
    raia.log_evaluation(
        ground_truth="Paris",
        relevance_score=0.98,
        faithfulness_score=0.95
    )
    ```
    """

    def __init__(self, config: RAIAConfig):
        self.config = config
        self.session_id = str(uuid.uuid4())
        self.run_id = None
        self.event_queue = []

        self.api_url = config.api_url.rstrip('/')
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.api_key}"
        }

    def start_run(self, query: str, metadata: Optional[Dict] = None) -> str:
        """
        Start a new run

        Args:
            query: User query
            metadata: Optional metadata (user_id, session context, etc.)

        Returns:
            run_id: Unique run identifier
        """
        self.run_id = str(uuid.uuid4())

        event = self._create_event(
            event_type="query_received",
            data={
                "query": query,
                "query_length": len(query),
                "metadata": metadata or {}
            }
        )

        self._send_event(event)

        if self.config.enable_logging:
            logger.info(f"✓ Started run: {self.run_id}")

        return self.run_id

    def log_retrieval(
        self,
        query: str,
        retrieved_docs: List[Dict[str, Any]],
        top_k: int = None,
        retrieval_time_ms: float = None
    ):
        """
        Log document retrieval

        Args:
            query: Search query
            retrieved_docs: List of retrieved documents
                Each doc should have: id, content, score, metadata (optional)
            top_k: Number of top results (default: len(retrieved_docs))
            retrieval_time_ms: Time taken for retrieval in milliseconds
        """
        if not self.run_id:
            logger.warning("No active run. Call start_run() first.")
            return

        top_k = top_k or len(retrieved_docs)

        event = self._create_event(
            event_type="retrieval_completed",
            data={
                "query": query,
                "num_retrieved": len(retrieved_docs),
                "top_k": top_k,
                "retrieval_time_ms": retrieval_time_ms,
                "retrieved_docs": [
                    {
                        "doc_id": doc.get("id", f"doc_{i}"),
                        "content": doc.get("content", ""),
                        "score": doc.get("score", 0.0),
                        "metadata": doc.get("metadata", {})
                    }
                    for i, doc in enumerate(retrieved_docs[:top_k])
                ]
            }
        )

        self._send_event(event)

        if self.config.enable_logging:
            logger.info(f"✓ Logged retrieval: {len(retrieved_docs)} docs")

    def log_llm_call(
        self,
        prompt: str,
        response: str,
        model: str,
        tokens_used: int = None,
        latency_ms: float = None,
        temperature: float = None
    ):
        """
        Log LLM call

        Args:
            prompt: Prompt sent to LLM
            response: Response from LLM
            model: Model name (e.g., "gpt-4", "claude-3")
            tokens_used: Total tokens used
            latency_ms: API call latency in milliseconds
            temperature: Model temperature setting
        """
        if not self.run_id:
            logger.warning("No active run. Call start_run() first.")
            return

        event = self._create_event(
            event_type="llm_call_completed",
            data={
                "prompt": prompt,
                "response": response,
                "model": model,
                "tokens_used": tokens_used,
                "prompt_length": len(prompt),
                "response_length": len(response),
                "latency_ms": latency_ms,
                "temperature": temperature
            }
        )

        self._send_event(event)

        if self.config.enable_logging:
            logger.info(f"✓ Logged LLM call: {model}")

    def log_tool_usage(
        self,
        tool_name: str,
        tool_input: Dict[str, Any],
        tool_output: Any,
        success: bool = True,
        error_message: str = None
    ):
        """
        Log tool/function usage

        Args:
            tool_name: Name of the tool
            tool_input: Input parameters to the tool
            tool_output: Output from the tool
            success: Whether tool execution was successful
            error_message: Error message if tool failed
        """
        if not self.run_id:
            logger.warning("No active run. Call start_run() first.")
            return

        event = self._create_event(
            event_type="tool_executed",
            data={
                "tool_name": tool_name,
                "tool_input": tool_input,
                "tool_output": str(tool_output),
                "success": success,
                "error_message": error_message
            }
        )

        self._send_event(event)

        if self.config.enable_logging:
            logger.info(f"✓ Logged tool usage: {tool_name}")

    def log_response(
        self,
        response: str,
        sources: List[str],
        confidence: float = None,
        response_time_ms: float = None
    ):
        """
        Log final response

        Args:
            response: Final response to user
            sources: List of source document IDs used
            confidence: Confidence score (0-1)
            response_time_ms: Total response time in milliseconds
        """
        if not self.run_id:
            logger.warning("No active run. Call start_run() first.")
            return

        event = self._create_event(
            event_type="response_generated",
            data={
                "response": response,
                "response_length": len(response),
                "sources_used": sources,
                "num_sources": len(sources),
                "confidence": confidence,
                "response_time_ms": response_time_ms
            }
        )

        self._send_event(event)

        if self.config.enable_logging:
            logger.info(f"✓ Logged response: {len(response)} chars, {len(sources)} sources")

    def log_evaluation(
        self,
        ground_truth: str = None,
        relevance_score: float = None,
        faithfulness_score: float = None,
        correctness_score: float = None,
        hallucination_score: float = None
    ):
        """
        Log evaluation metrics (if ground truth is available)

        Args:
            ground_truth: Expected correct answer
            relevance_score: Relevance score (0-1)
            faithfulness_score: Faithfulness to sources score (0-1)
            correctness_score: Correctness score (0-1)
            hallucination_score: Hallucination score (0-1, lower is better)
        """
        if not self.run_id:
            logger.warning("No active run. Call start_run() first.")
            return

        event = self._create_event(
            event_type="evaluation_completed",
            data={
                "ground_truth": ground_truth,
                "relevance_score": relevance_score,
                "faithfulness_score": faithfulness_score,
                "correctness_score": correctness_score,
                "hallucination_score": hallucination_score
            }
        )

        self._send_event(event)

        if self.config.enable_logging:
            logger.info(f"✓ Logged evaluation")

    def end_run(self, success: bool = True, error_message: str = None):
        """
        End the current run

        Args:
            success: Whether the run completed successfully
            error_message: Error message if run failed
        """
        if not self.run_id:
            logger.warning("No active run.")
            return

        event = self._create_event(
            event_type="run_completed",
            data={
                "success": success,
                "error_message": error_message
            }
        )

        self._send_event(event)

        if self.config.enable_logging:
            logger.info(f"✓ Ended run: {self.run_id}")

        # Flush any queued events
        self.flush()

        # Reset run_id
        self.run_id = None

    def flush(self):
        """Flush any queued events (for batch mode)"""
        if self.event_queue:
            self._send_batch(self.event_queue)
            self.event_queue = []

    def _create_event(self, event_type: str, data: Dict[str, Any]) -> Dict:
        """Create event dictionary"""
        return {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "tenant": self.config.tenant,
            "project": self.config.project,
            "agent_id": self.config.agent_id,
            "session_id": self.session_id,
            "run_id": self.run_id,
            "data": data
        }

    def _send_event(self, event: Dict):
        """Send event to RAIA platform"""
        try:
            response = requests.post(
                f"{self.api_url}/api/events/ingest",
                json=event,
                headers=self.headers,
                timeout=self.config.timeout
            )
            response.raise_for_status()

            if self.config.enable_logging:
                logger.debug(f"Event sent: {event['event_type']}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send event: {e}")
            # In production, you might want to queue failed events for retry
            # or send to a dead-letter queue

    def _send_batch(self, events: List[Dict]):
        """Send batch of events"""
        try:
            response = requests.post(
                f"{self.api_url}/api/events/batch",
                json={"events": events},
                headers=self.headers,
                timeout=self.config.timeout * 2
            )
            response.raise_for_status()

            if self.config.enable_logging:
                logger.info(f"Batch sent: {len(events)} events")

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send batch: {e}")


# ============================================================================
# Convenience Context Manager
# ============================================================================

class RAIARun:
    """
    Context manager for RAIA runs

    Usage:
    ```python
    with RAIARun(raia, query="What is AI?") as run:
        # Log retrieval
        run.log_retrieval(...)

        # Log LLM call
        run.log_llm_call(...)

        # Log response
        run.log_response(...)

    # Run automatically ends when context exits
    ```
    """

    def __init__(self, client: RAIAClient, query: str, metadata: Optional[Dict] = None):
        self.client = client
        self.query = query
        self.metadata = metadata
        self.run_id = None

    def __enter__(self):
        self.run_id = self.client.start_run(self.query, self.metadata)
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Run failed
            self.client.end_run(success=False, error_message=str(exc_val))
        else:
            # Run succeeded
            self.client.end_run(success=True)


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    # Example configuration
    config = RAIAConfig(
        api_url="http://localhost:8000",
        api_key="demo-api-key",
        tenant="demo-company",
        project="demo-project",
        agent_id="demo-agent"
    )

    # Initialize client
    raia = RAIAClient(config)

    # Example 1: Manual run management
    print("=== Example 1: Manual Run ===")
    run_id = raia.start_run("What is the capital of France?")

    raia.log_retrieval(
        query="capital France",
        retrieved_docs=[
            {"id": "doc1", "content": "Paris is the capital of France", "score": 0.95},
            {"id": "doc2", "content": "France is in Europe", "score": 0.85}
        ]
    )

    raia.log_llm_call(
        prompt="Based on context, what is the capital of France?",
        response="The capital of France is Paris.",
        model="gpt-4",
        tokens_used=45
    )

    raia.log_response(
        response="The capital of France is Paris.",
        sources=["doc1", "doc2"]
    )

    raia.end_run(success=True)

    # Example 2: Using context manager
    print("\n=== Example 2: Context Manager ===")
    with RAIARun(raia, query="What is machine learning?") as run:
        run.log_retrieval(
            query="machine learning definition",
            retrieved_docs=[
                {"id": "ml1", "content": "ML is a subset of AI", "score": 0.9}
            ]
        )

        run.log_llm_call(
            prompt="Define machine learning",
            response="Machine learning is...",
            model="gpt-4",
            tokens_used=30
        )

        run.log_response(
            response="Machine learning is a subset of AI...",
            sources=["ml1"]
        )

    print("\n✓ Examples completed!")
