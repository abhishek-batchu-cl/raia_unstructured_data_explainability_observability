"""
LangChain/LangGraph integration for automatic instrumentation.
"""

import functools
import time
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

try:
    from langchain.callbacks.base import BaseCallbackHandler
    from langchain.schema import AgentAction, AgentFinish, LLMResult

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    BaseCallbackHandler = object


class LangChainCallbackHandler(BaseCallbackHandler):
    """
    LangChain callback handler that emits RAIA events.
    """

    def __init__(self, emitter: "EventEmitter", session_id: Optional[str] = None, agent_id: Optional[str] = None):
        """
        Initialize callback handler.

        Args:
            emitter: EventEmitter instance
            session_id: Session ID (generated if not provided)
            agent_id: Agent ID (uses emitter config if not provided)
        """
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("langchain not installed. Install with: pip install langchain")

        self.emitter = emitter
        self.session_id = session_id or str(uuid.uuid4())
        self.run_id = str(uuid.uuid4())
        self.agent_id = agent_id or emitter.config.agent_id

        self._start_time = None
        self._tool_start_times = {}
        self._llm_start_times = {}

    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        **kwargs: Any,
    ) -> None:
        """Run when chain starts."""
        self._start_time = time.time()

        # Emit session_start event
        self.emitter.emit(
            {
                "event": "session_start",
                "session_id": self.session_id,
                "run_id": self.run_id,
                "agent_id": self.agent_id,
                "user_id": inputs.get("user_id", "unknown"),
                "task": inputs.get("input", str(inputs)),
                "domain": inputs.get("domain", "general"),
                "constraints": inputs.get("constraints", []),
            }
        )

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Run when chain ends."""
        latency_ms = (time.time() - self._start_time) * 1000 if self._start_time else 0

        # Emit finalized event
        self.emitter.emit(
            {
                "event": "finalized",
                "session_id": self.session_id,
                "run_id": self.run_id,
                "agent_id": self.agent_id,
                "final_answer": outputs.get("output", str(outputs)),
                "success": True,
                "constraints_met": True,  # Could be enhanced with constraint checking
                "latency_ms": latency_ms,
            }
        )

    def on_chain_error(self, error: Exception, **kwargs: Any) -> None:
        """Run when chain errors."""
        self.emitter.emit(
            {
                "event": "error",
                "session_id": self.session_id,
                "run_id": self.run_id,
                "agent_id": self.agent_id,
                "error_type": "internal_error",
                "error_message": str(error),
                "recoverable": False,
            }
        )

    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        **kwargs: Any,
    ) -> None:
        """Run when LLM starts."""
        run_id = kwargs.get("run_id", str(uuid.uuid4()))
        self._llm_start_times[run_id] = time.time()

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Run when LLM ends."""
        run_id = kwargs.get("run_id")
        start_time = self._llm_start_times.pop(run_id, None)
        latency_ms = (time.time() - start_time) * 1000 if start_time else 0

        # Extract token usage if available
        token_usage = {}
        if hasattr(response, "llm_output") and response.llm_output:
            if "token_usage" in response.llm_output:
                token_usage = response.llm_output["token_usage"]

        # For plan creation, check if this looks like a planning step
        generation = response.generations[0][0] if response.generations else None
        text = generation.text if generation else ""

        # Simple heuristic: if output contains structured plan indicators
        if any(indicator in text.lower() for indicator in ["step 1", "plan:", "steps:", "first,"]):
            self.emitter.emit(
                {
                    "event": "plan_created",
                    "session_id": self.session_id,
                    "run_id": self.run_id,
                    "agent_id": self.agent_id,
                    "plan": {"steps": [], "rationale": text},  # Simplified
                    "plan_depth": text.count("step"),  # Rough estimate
                    "revision_count": 0,
                    "latency_ms": latency_ms,
                    "token_usage": token_usage,
                }
            )

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        **kwargs: Any,
    ) -> None:
        """Run when tool starts."""
        run_id = kwargs.get("run_id", str(uuid.uuid4()))
        self._tool_start_times[run_id] = time.time()

        tool_name = serialized.get("name", "unknown_tool")

        self.emitter.emit(
            {
                "event": "tool_call",
                "event_id": run_id,
                "session_id": self.session_id,
                "run_id": self.run_id,
                "agent_id": self.agent_id,
                "tool_name": tool_name,
                "tool_args": {"input": input_str},
                "is_retry": False,
                "retry_count": 0,
            }
        )

    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """Run when tool ends."""
        run_id = kwargs.get("run_id")
        start_time = self._tool_start_times.pop(run_id, None)
        latency_ms = (time.time() - start_time) * 1000 if start_time else 0

        self.emitter.emit(
            {
                "event": "observation",
                "session_id": self.session_id,
                "run_id": self.run_id,
                "agent_id": self.agent_id,
                "parent_event_id": run_id,
                "observation": output,
                "success": True,
                "grounded": False,  # Would need evidence tracking
                "latency_ms": latency_ms,
            }
        )

    def on_tool_error(self, error: Exception, **kwargs: Any) -> None:
        """Run when tool errors."""
        run_id = kwargs.get("run_id")

        self.emitter.emit(
            {
                "event": "observation",
                "session_id": self.session_id,
                "run_id": self.run_id,
                "agent_id": self.agent_id,
                "parent_event_id": run_id,
                "observation": f"Tool error: {str(error)}",
                "success": False,
                "error_type": "other",
            }
        )

    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> None:
        """Run on agent action (useful for ReAct agents)."""
        # Already handled by on_tool_start in most cases
        pass

    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> None:
        """Run on agent finish."""
        # Already handled by on_chain_end
        pass


def instrumented_tool(
    emitter: "EventEmitter",
    tool_name: str,
    session_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    evidence_extractor: Optional[callable] = None,
):
    """
    Decorator to instrument custom tools with RAIA events.

    Args:
        emitter: EventEmitter instance
        tool_name: Name of the tool
        session_id: Session ID (optional)
        agent_id: Agent ID (optional)
        evidence_extractor: Function to extract evidence refs from tool output

    Example:
        @instrumented_tool(emitter, "search_pubmed")
        def search_pubmed(query: str) -> str:
            # Tool implementation
            return results
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate IDs
            event_id = str(uuid.uuid4())
            sid = session_id or str(uuid.uuid4())
            rid = str(uuid.uuid4())
            aid = agent_id or emitter.config.agent_id

            # Emit tool_call event
            start_time = time.time()
            emitter.emit(
                {
                    "event": "tool_call",
                    "event_id": event_id,
                    "session_id": sid,
                    "run_id": rid,
                    "agent_id": aid,
                    "tool_name": tool_name,
                    "tool_args": {"args": args, "kwargs": kwargs},
                    "is_retry": False,
                    "retry_count": 0,
                }
            )

            # Execute tool
            try:
                result = func(*args, **kwargs)
                success = True
                error_type = None
            except Exception as e:
                result = str(e)
                success = False
                error_type = "other"
                raise
            finally:
                latency_ms = (time.time() - start_time) * 1000

                # Extract evidence if extractor provided
                evidence_refs = []
                grounded = False
                if success and evidence_extractor:
                    try:
                        evidence_refs = evidence_extractor(result)
                        grounded = len(evidence_refs) > 0
                    except Exception:
                        pass

                # Emit observation event
                emitter.emit(
                    {
                        "event": "observation",
                        "session_id": sid,
                        "run_id": rid,
                        "agent_id": aid,
                        "parent_event_id": event_id,
                        "observation": str(result),
                        "success": success,
                        "error_type": error_type,
                        "grounded": grounded,
                        "evidence_refs": evidence_refs,
                        "latency_ms": latency_ms,
                    }
                )

            return result

        return wrapper

    return decorator
