"""
RAIA Inspectors - Base Metrics Class

Base class providing common functionality for all inspectors.
"""

import logging
from datetime import datetime
from typing import Any, Optional

from .config import get_raia_config
from .storage.base import BaseRAIAStorage
from .models import RAIAAgentRun, RAIANodeMetrics, RAIAFunctionalSignal, RAIASemanticScore


logger = logging.getLogger(__name__)


class RAIAInspectorBase:
    """
    Base class for RAIA inspectors.

    Provides common functionality for saving runs, metrics, signals, and scores.
    """

    def __init__(self, storage: Optional[BaseRAIAStorage] = None):
        """
        Initialize inspector base.

        Args:
            storage: Storage backend (uses global config if None)
        """
        if storage is None:
            config = get_raia_config()
            storage = config.get_storage()
        self.storage = storage
        logger.debug(f"Initialized {self.__class__.__name__} with storage {storage.__class__.__name__}")

    def _save_run_start(
        self,
        run_id: str,
        session_id: Optional[str] = None,
        agent_name: Optional[str] = None,
        graph_name: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None
    ) -> RAIAAgentRun:
        """
        Create and save a new run at start time.

        Args:
            run_id: Unique run identifier
            session_id: Session ID (optional)
            agent_name: Agent name (optional)
            graph_name: Graph name (optional)
            metadata: Additional metadata (optional)

        Returns:
            RAIAAgentRun instance
        """
        run = RAIAAgentRun(
            run_id=run_id,
            session_id=session_id,
            agent_name=agent_name,
            graph_name=graph_name,
            start_time=datetime.utcnow(),
            status="in_progress",
            metadata=metadata
        )
        self.storage.save_run(run)
        logger.info(f"Started run {run_id}")
        return run

    def _save_run_end(
        self,
        run_id: str,
        status: str = "success",
        total_latency_ms: Optional[float] = None,
        total_tokens_prompt: Optional[int] = None,
        total_tokens_completion: Optional[int] = None,
        total_cost_usd: Optional[float] = None,
        metadata: Optional[dict[str, Any]] = None
    ) -> None:
        """
        Update run with end time and final metrics.

        Args:
            run_id: Unique run identifier
            status: Final status (success/error)
            total_latency_ms: Total latency in milliseconds
            total_tokens_prompt: Total prompt tokens
            total_tokens_completion: Total completion tokens
            total_cost_usd: Total cost in USD
            metadata: Additional metadata
        """
        run = self.storage.get_run(run_id)
        if run:
            run.end_time = datetime.utcnow()
            run.status = status
            run.total_latency_ms = total_latency_ms
            run.total_tokens_prompt = total_tokens_prompt
            run.total_tokens_completion = total_tokens_completion
            run.total_cost_usd = total_cost_usd
            if metadata:
                run.metadata = {**(run.metadata or {}), **metadata}
            self.storage.update_run(run)
            logger.info(f"Ended run {run_id} with status {status}")
        else:
            logger.warning(f"Run {run_id} not found for update")

    def _save_node_metrics(
        self,
        run_id: str,
        node_name: str,
        node_type: str,
        start_time: datetime,
        end_time: datetime,
        success: bool = True,
        error_type: Optional[str] = None,
        error_message: Optional[str] = None,
        retry_count: int = 0,
        tokens_prompt: Optional[int] = None,
        tokens_completion: Optional[int] = None,
        cost_usd: Optional[float] = None,
        metadata: Optional[dict[str, Any]] = None
    ) -> None:
        """
        Save node metrics.

        Args:
            run_id: Parent run ID
            node_name: Name of the node
            node_type: Type of node (llm/tool/chain/custom)
            start_time: Node start time
            end_time: Node end time
            success: Whether node succeeded
            error_type: Error type if failed
            error_message: Error message if failed
            retry_count: Number of retries
            tokens_prompt: Prompt tokens used
            tokens_completion: Completion tokens used
            cost_usd: Estimated cost
            metadata: Additional metadata
        """
        latency_ms = (end_time - start_time).total_seconds() * 1000

        metrics = RAIANodeMetrics(
            run_id=run_id,
            node_name=node_name,
            node_type=node_type,
            start_time=start_time,
            end_time=end_time,
            latency_ms=latency_ms,
            tokens_prompt=tokens_prompt,
            tokens_completion=tokens_completion,
            cost_usd=cost_usd,
            success=success,
            error_type=error_type,
            error_message=error_message,
            retry_count=retry_count,
            metadata=metadata
        )
        self.storage.save_node_metrics(metrics)
        logger.debug(f"Saved metrics for node {node_name} in run {run_id}")

    def _save_signal(
        self,
        run_id: str,
        signal_type: str,
        severity: str,
        message: str,
        node_name: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None
    ) -> None:
        """
        Save a functional signal.

        Args:
            run_id: Parent run ID
            signal_type: Type of signal
            severity: Severity level
            message: Human-readable message
            node_name: Node where signal was detected
            metadata: Additional context
        """
        signal = RAIAFunctionalSignal(
            run_id=run_id,
            node_name=node_name,
            signal_type=signal_type,
            severity=severity,
            message=message,
            metadata=metadata
        )
        self.storage.save_functional_signal(signal)
        logger.info(f"Saved signal {signal_type} ({severity}) for run {run_id}")

    def _save_semantic_score(
        self,
        run_id: str,
        dimension: str,
        score: float,
        explanation: Optional[str] = None,
        node_name: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None
    ) -> None:
        """
        Save a semantic quality score.

        Args:
            run_id: Parent run ID
            dimension: Semantic dimension being scored
            score: Score value (0-1)
            explanation: Explanation of score
            node_name: Node being evaluated
            metadata: Additional context
        """
        semantic_score = RAIASemanticScore(
            run_id=run_id,
            node_name=node_name,
            dimension=dimension,
            score=score,
            explanation=explanation,
            metadata=metadata
        )
        self.storage.save_semantic_score(semantic_score)
        logger.debug(f"Saved semantic score {dimension}={score:.2f} for run {run_id}")
