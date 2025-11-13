"""
RAIA Inspectors - Execution Inspector

Captures per-run and per-node timing and basic performance metrics via LangChain callbacks.
"""

import logging
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from raia.inspectors.base import RAIAInspectorBase
from raia.storage.base import BaseRAIAStorage


logger = logging.getLogger(__name__)


try:
    from langchain.callbacks.base import BaseCallbackHandler
    from langchain.schema import AgentAction, AgentFinish, LLMResult
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    BaseCallbackHandler = object
    # Mock types for when LangChain is not available
    class LLMResult:
        pass
    class AgentAction:
        pass
    class AgentFinish:
        pass
    logger.warning("LangChain not available. Install with: pip install langchain")


class RAIAExecutionInspector(RAIAInspectorBase, BaseCallbackHandler):
    """
    LangChain callback handler that captures execution metrics.

    Tracks:
    - Per-run timing and status
    - Per-node (LLM/tool/chain) latency and token usage
    - Errors and retries
    - Cost estimation

    Usage:
        inspector = RAIAExecutionInspector()
        result = chain.invoke(
            {"question": "Hello"},
            config={"callbacks": [inspector], "tags": ["prod"], "metadata": {"tenant": "acme"}}
        )
    """

    def __init__(
        self,
        storage: Optional[BaseRAIAStorage] = None,
        run_id: Optional[str] = None,
        session_id: Optional[str] = None,
        agent_name: Optional[str] = None,
        graph_name: Optional[str] = None
    ):
        """
        Initialize execution inspector.

        Args:
            storage: Storage backend (uses global config if None)
            run_id: Run ID (auto-generated if None)
            session_id: Session ID (optional)
            agent_name: Agent name (optional)
            graph_name: Graph name (optional)
        """
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("LangChain not installed. Install with: pip install langchain")

        super().__init__(storage=storage)

        self.run_id = run_id or str(uuid.uuid4())
        self.session_id = session_id
        self.agent_name = agent_name
        self.graph_name = graph_name

        # Tracking state
        self._start_time: Optional[float] = None
        self._llm_start_times: Dict[str, float] = {}
        self._tool_start_times: Dict[str, float] = {}
        self._chain_start_times: Dict[str, float] = {}

        # Aggregate metrics
        self._total_tokens_prompt = 0
        self._total_tokens_completion = 0
        self._total_cost_usd = 0.0

        # Retry tracking
        self._tool_retry_counts: Dict[str, int] = {}

    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        **kwargs: Any,
    ) -> None:
        """Called when chain starts."""
        run_id = kwargs.get("run_id")
        parent_run_id = kwargs.get("parent_run_id")

        # Only track top-level chain
        if parent_run_id is None:
            self._start_time = time.time()

            # Extract metadata from config
            metadata = kwargs.get("metadata", {})
            tags = kwargs.get("tags", [])
            if tags:
                metadata["tags"] = tags

            # Save run start
            self._save_run_start(
                run_id=self.run_id,
                session_id=self.session_id,
                agent_name=self.agent_name or serialized.get("name"),
                graph_name=self.graph_name,
                metadata=metadata
            )
            logger.info(f"Chain started: run_id={self.run_id}")
        else:
            # Track nested chain
            if run_id:
                self._chain_start_times[run_id] = time.time()

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Called when chain ends."""
        run_id = kwargs.get("run_id")
        parent_run_id = kwargs.get("parent_run_id")

        if parent_run_id is None and self._start_time:
            # Top-level chain - finalize run
            end_time = time.time()
            total_latency_ms = (end_time - self._start_time) * 1000

            self._save_run_end(
                run_id=self.run_id,
                status="success",
                total_latency_ms=total_latency_ms,
                total_tokens_prompt=self._total_tokens_prompt if self._total_tokens_prompt > 0 else None,
                total_tokens_completion=self._total_tokens_completion if self._total_tokens_completion > 0 else None,
                total_cost_usd=self._total_cost_usd if self._total_cost_usd > 0 else None
            )
            logger.info(f"Chain ended: run_id={self.run_id}, latency={total_latency_ms:.2f}ms")
        elif run_id and run_id in self._chain_start_times:
            # Nested chain - save as node metric
            start_time_ts = self._chain_start_times.pop(run_id)
            end_time = time.time()

            self._save_node_metrics(
                run_id=self.run_id,
                node_name=kwargs.get("name", "chain"),
                node_type="chain",
                start_time=datetime.fromtimestamp(start_time_ts),
                end_time=datetime.fromtimestamp(end_time),
                success=True
            )

    def on_chain_error(self, error: Exception, **kwargs: Any) -> None:
        """Called when chain errors."""
        parent_run_id = kwargs.get("parent_run_id")

        if parent_run_id is None and self._start_time:
            # Top-level chain error
            end_time = time.time()
            total_latency_ms = (end_time - self._start_time) * 1000

            self._save_run_end(
                run_id=self.run_id,
                status="error",
                total_latency_ms=total_latency_ms,
                metadata={"error": str(error)}
            )
            logger.error(f"Chain error: run_id={self.run_id}, error={error}")

    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        **kwargs: Any,
    ) -> None:
        """Called when LLM starts."""
        run_id = kwargs.get("run_id", str(uuid.uuid4()))
        self._llm_start_times[run_id] = time.time()
        logger.debug(f"LLM started: {run_id}")

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Called when LLM ends."""
        run_id = kwargs.get("run_id")
        if not run_id or run_id not in self._llm_start_times:
            return

        start_time_ts = self._llm_start_times.pop(run_id)
        end_time = time.time()

        # Extract token usage
        tokens_prompt = 0
        tokens_completion = 0
        cost_usd = 0.0

        if hasattr(response, "llm_output") and response.llm_output:
            token_usage = response.llm_output.get("token_usage", {})
            tokens_prompt = token_usage.get("prompt_tokens", 0)
            tokens_completion = token_usage.get("completion_tokens", 0)

            # Update totals
            self._total_tokens_prompt += tokens_prompt
            self._total_tokens_completion += tokens_completion

            # Simple cost estimation (GPT-3.5-turbo pricing)
            # This should be made configurable per model
            cost_usd = (tokens_prompt * 0.0005 + tokens_completion * 0.0015) / 1000
            self._total_cost_usd += cost_usd

        # Save node metrics
        self._save_node_metrics(
            run_id=self.run_id,
            node_name=kwargs.get("invocation_params", {}).get("model_name", "llm"),
            node_type="llm",
            start_time=datetime.fromtimestamp(start_time_ts),
            end_time=datetime.fromtimestamp(end_time),
            success=True,
            tokens_prompt=tokens_prompt if tokens_prompt > 0 else None,
            tokens_completion=tokens_completion if tokens_completion > 0 else None,
            cost_usd=cost_usd if cost_usd > 0 else None
        )

    def on_llm_error(self, error: Exception, **kwargs: Any) -> None:
        """Called when LLM errors."""
        run_id = kwargs.get("run_id")
        if run_id and run_id in self._llm_start_times:
            start_time_ts = self._llm_start_times.pop(run_id)
            end_time = time.time()

            self._save_node_metrics(
                run_id=self.run_id,
                node_name=kwargs.get("invocation_params", {}).get("model_name", "llm"),
                node_type="llm",
                start_time=datetime.fromtimestamp(start_time_ts),
                end_time=datetime.fromtimestamp(end_time),
                success=False,
                error_type="llm_error",
                error_message=str(error)
            )

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        **kwargs: Any,
    ) -> None:
        """Called when tool starts."""
        run_id = kwargs.get("run_id", str(uuid.uuid4()))
        self._tool_start_times[run_id] = time.time()

        tool_name = serialized.get("name", "unknown_tool")
        logger.debug(f"Tool started: {tool_name} ({run_id})")

    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """Called when tool ends."""
        run_id = kwargs.get("run_id")
        if not run_id or run_id not in self._tool_start_times:
            return

        start_time_ts = self._tool_start_times.pop(run_id)
        end_time = time.time()

        tool_name = kwargs.get("name", "tool")
        retry_count = self._tool_retry_counts.get(tool_name, 0)

        self._save_node_metrics(
            run_id=self.run_id,
            node_name=tool_name,
            node_type="tool",
            start_time=datetime.fromtimestamp(start_time_ts),
            end_time=datetime.fromtimestamp(end_time),
            success=True,
            retry_count=retry_count
        )

        # Reset retry count on success
        if tool_name in self._tool_retry_counts:
            del self._tool_retry_counts[tool_name]

    def on_tool_error(self, error: Exception, **kwargs: Any) -> None:
        """Called when tool errors."""
        run_id = kwargs.get("run_id")
        tool_name = kwargs.get("name", "tool")

        # Track retry
        self._tool_retry_counts[tool_name] = self._tool_retry_counts.get(tool_name, 0) + 1

        if run_id and run_id in self._tool_start_times:
            start_time_ts = self._tool_start_times.pop(run_id)
            end_time = time.time()

            self._save_node_metrics(
                run_id=self.run_id,
                node_name=tool_name,
                node_type="tool",
                start_time=datetime.fromtimestamp(start_time_ts),
                end_time=datetime.fromtimestamp(end_time),
                success=False,
                error_type="tool_error",
                error_message=str(error),
                retry_count=self._tool_retry_counts[tool_name]
            )

    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> None:
        """Called on agent action (useful for ReAct agents)."""
        # Most tracking is already done in on_tool_start
        pass

    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> None:
        """Called on agent finish."""
        # Most tracking is already done in on_chain_end
        pass
