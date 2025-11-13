"""
RAIA Inspectors - Base Storage Interface

Abstract base class for storage implementations.
"""

from abc import ABC, abstractmethod
from typing import Optional
from ..models import RAIAAgentRun, RAIANodeMetrics, RAIAFunctionalSignal, RAIASemanticScore


class BaseRAIAStorage(ABC):
    """
    Abstract base class for RAIA storage backends.

    Implementations must provide methods for persisting and querying
    agent runs, node metrics, functional signals, and semantic scores.
    """

    @abstractmethod
    def save_run(self, run: RAIAAgentRun) -> None:
        """
        Save a new agent run.

        Args:
            run: RAIAAgentRun instance to save
        """
        pass

    @abstractmethod
    def update_run(self, run: RAIAAgentRun) -> None:
        """
        Update an existing agent run.

        Args:
            run: RAIAAgentRun instance with updated data
        """
        pass

    @abstractmethod
    def save_node_metrics(self, metrics: RAIANodeMetrics) -> None:
        """
        Save node metrics for a run.

        Args:
            metrics: RAIANodeMetrics instance to save
        """
        pass

    @abstractmethod
    def save_functional_signal(self, signal: RAIAFunctionalSignal) -> None:
        """
        Save a functional signal (behavioral pattern detection).

        Args:
            signal: RAIAFunctionalSignal instance to save
        """
        pass

    @abstractmethod
    def save_semantic_score(self, score: RAIASemanticScore) -> None:
        """
        Save a semantic quality score.

        Args:
            score: RAIASemanticScore instance to save
        """
        pass

    @abstractmethod
    def get_run(self, run_id: str) -> Optional[RAIAAgentRun]:
        """
        Retrieve a run by ID.

        Args:
            run_id: Unique run identifier

        Returns:
            RAIAAgentRun instance or None if not found
        """
        pass

    @abstractmethod
    def get_node_metrics_for_run(self, run_id: str) -> list[RAIANodeMetrics]:
        """
        Retrieve all node metrics for a run.

        Args:
            run_id: Unique run identifier

        Returns:
            List of RAIANodeMetrics instances
        """
        pass

    @abstractmethod
    def get_signals_for_run(self, run_id: str) -> list[RAIAFunctionalSignal]:
        """
        Retrieve all functional signals for a run.

        Args:
            run_id: Unique run identifier

        Returns:
            List of RAIAFunctionalSignal instances
        """
        pass

    @abstractmethod
    def get_semantic_scores_for_run(self, run_id: str) -> list[RAIASemanticScore]:
        """
        Retrieve all semantic scores for a run.

        Args:
            run_id: Unique run identifier

        Returns:
            List of RAIASemanticScore instances
        """
        pass
