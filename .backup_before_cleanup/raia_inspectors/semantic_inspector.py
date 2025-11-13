"""
RAIA Inspectors - Semantic Inspector

Pluggable interface for semantic quality evaluation.

Provides a protocol for implementing custom semantic evaluators
without hard-wiring to specific LLM providers.
"""

import logging
from typing import Any, Dict, List, Optional, Protocol

from .metrics_base import RAIAInspectorBase
from .storage.base import BaseRAIAStorage
from .models import RAIASemanticScore


logger = logging.getLogger(__name__)


class SemanticEvaluator(Protocol):
    """
    Protocol for semantic evaluators.

    Implementations should evaluate agent steps and return semantic scores.
    """

    def evaluate_step(
        self,
        *,
        run_id: str,
        node_name: str,
        state_before: Optional[Dict[str, Any]] = None,
        state_after: Optional[Dict[str, Any]] = None,
        messages: Optional[List[Dict[str, Any]]] = None
    ) -> List[RAIASemanticScore]:
        """
        Evaluate a single step in the agent execution.

        Args:
            run_id: Unique run identifier
            node_name: Name of the node being evaluated
            state_before: Agent state before the step
            state_after: Agent state after the step
            messages: Messages/outputs from the step

        Returns:
            List of RAIASemanticScore instances
        """
        ...


class RAIASemanticInspector(RAIAInspectorBase):
    """
    Manages semantic evaluation using pluggable evaluators.

    Does NOT implement evaluation logic itself - delegates to
    user-provided SemanticEvaluator implementations.

    Usage:
        # Define a custom evaluator
        class MyEvaluator:
            def evaluate_step(self, *, run_id, node_name, state_before, state_after, messages):
                # Custom evaluation logic
                return [
                    RAIASemanticScore(
                        run_id=run_id,
                        node_name=node_name,
                        dimension="hallucination_risk",
                        score=0.15,
                        explanation="Response is well-grounded"
                    )
                ]

        # Use the inspector
        inspector = RAIASemanticInspector(evaluator=MyEvaluator())
        scores = inspector.evaluate_step(
            run_id="run_123",
            node_name="answer_node",
            state_after={"answer": "The sky is blue"}
        )
    """

    def __init__(
        self,
        evaluator: Optional[SemanticEvaluator] = None,
        storage: Optional[BaseRAIAStorage] = None,
        auto_save: bool = True
    ):
        """
        Initialize semantic inspector.

        Args:
            evaluator: SemanticEvaluator implementation (optional)
            storage: Storage backend (uses global config if None)
            auto_save: Automatically save scores to storage
        """
        super().__init__(storage=storage)
        self.evaluator = evaluator
        self.auto_save = auto_save

        if evaluator is None:
            logger.warning("No evaluator provided. Semantic evaluation will be disabled.")

    def evaluate_step(
        self,
        run_id: str,
        node_name: str,
        state_before: Optional[Dict[str, Any]] = None,
        state_after: Optional[Dict[str, Any]] = None,
        messages: Optional[List[Dict[str, Any]]] = None
    ) -> List[RAIASemanticScore]:
        """
        Evaluate a single step using the configured evaluator.

        Args:
            run_id: Unique run identifier
            node_name: Name of the node being evaluated
            state_before: Agent state before the step
            state_after: Agent state after the step
            messages: Messages/outputs from the step

        Returns:
            List of RAIASemanticScore instances
        """
        if self.evaluator is None:
            logger.debug("No evaluator configured, skipping semantic evaluation")
            return []

        try:
            scores = self.evaluator.evaluate_step(
                run_id=run_id,
                node_name=node_name,
                state_before=state_before,
                state_after=state_after,
                messages=messages
            )

            # Auto-save if enabled
            if self.auto_save:
                for score in scores:
                    self.storage.save_semantic_score(score)
                logger.debug(f"Saved {len(scores)} semantic scores for {node_name} in run {run_id}")

            return scores

        except Exception as e:
            logger.error(f"Error during semantic evaluation: {e}", exc_info=True)
            return []

    def evaluate_run(
        self,
        run_id: str,
        steps: List[Dict[str, Any]]
    ) -> List[RAIASemanticScore]:
        """
        Evaluate multiple steps in a run.

        Args:
            run_id: Unique run identifier
            steps: List of step dictionaries, each containing:
                   - node_name: str
                   - state_before: dict (optional)
                   - state_after: dict (optional)
                   - messages: list (optional)

        Returns:
            List of all RAIASemanticScore instances
        """
        all_scores = []

        for step in steps:
            scores = self.evaluate_step(
                run_id=run_id,
                node_name=step.get("node_name", "unknown"),
                state_before=step.get("state_before"),
                state_after=step.get("state_after"),
                messages=step.get("messages")
            )
            all_scores.extend(scores)

        logger.info(f"Evaluated {len(steps)} steps, generated {len(all_scores)} scores for run {run_id}")
        return all_scores


# Example stub evaluator for testing/demonstration
class DummySemanticEvaluator:
    """
    Dummy evaluator for testing purposes.

    Returns random/placeholder scores.
    """

    def evaluate_step(
        self,
        *,
        run_id: str,
        node_name: str,
        state_before: Optional[Dict[str, Any]] = None,
        state_after: Optional[Dict[str, Any]] = None,
        messages: Optional[List[Dict[str, Any]]] = None
    ) -> List[RAIASemanticScore]:
        """
        Generate dummy semantic scores.
        """
        import random

        scores = []

        # Hallucination risk
        scores.append(RAIASemanticScore(
            run_id=run_id,
            node_name=node_name,
            dimension="hallucination_risk",
            score=random.uniform(0.1, 0.3),
            explanation="Dummy evaluation: randomly generated score"
        ))

        # Instruction adherence
        scores.append(RAIASemanticScore(
            run_id=run_id,
            node_name=node_name,
            dimension="instruction_adherence",
            score=random.uniform(0.7, 0.95),
            explanation="Dummy evaluation: randomly generated score"
        ))

        return scores


# Example LLM-based evaluator template (requires user to provide LLM)
class LLMSemanticEvaluatorTemplate:
    """
    Template for LLM-based semantic evaluation.

    Users should implement the _call_llm method with their preferred LLM.
    """

    def __init__(self, llm_callable=None):
        """
        Initialize LLM evaluator.

        Args:
            llm_callable: Function that takes a prompt and returns LLM response
                         Signature: (prompt: str) -> str
        """
        self.llm_callable = llm_callable

    def _call_llm(self, prompt: str) -> str:
        """
        Call LLM with prompt.

        Override this method or provide llm_callable in __init__.
        """
        if self.llm_callable:
            return self.llm_callable(prompt)
        raise NotImplementedError("Provide llm_callable or override _call_llm")

    def evaluate_step(
        self,
        *,
        run_id: str,
        node_name: str,
        state_before: Optional[Dict[str, Any]] = None,
        state_after: Optional[Dict[str, Any]] = None,
        messages: Optional[List[Dict[str, Any]]] = None
    ) -> List[RAIASemanticScore]:
        """
        Evaluate using LLM.
        """
        # Build evaluation prompt
        prompt = self._build_evaluation_prompt(
            node_name=node_name,
            state_before=state_before,
            state_after=state_after,
            messages=messages
        )

        # Call LLM
        try:
            response = self._call_llm(prompt)
            scores = self._parse_llm_response(run_id, node_name, response)
            return scores
        except Exception as e:
            logger.error(f"LLM evaluation failed: {e}")
            return []

    def _build_evaluation_prompt(
        self,
        node_name: str,
        state_before: Optional[Dict[str, Any]],
        state_after: Optional[Dict[str, Any]],
        messages: Optional[List[Dict[str, Any]]]
    ) -> str:
        """Build LLM prompt for evaluation."""
        prompt = f"""Evaluate the following agent step: {node_name}

State before: {state_before}
State after: {state_after}
Messages: {messages}

Evaluate on these dimensions:
1. Hallucination risk (0-1, lower is better)
2. Instruction adherence (0-1, higher is better)
3. Clarity (0-1, higher is better)

Respond in JSON format:
{{
    "hallucination_risk": {{"score": 0.15, "explanation": "..."}},
    "instruction_adherence": {{"score": 0.92, "explanation": "..."}},
    "clarity": {{"score": 0.88, "explanation": "..."}}
}}
"""
        return prompt

    def _parse_llm_response(
        self,
        run_id: str,
        node_name: str,
        response: str
    ) -> List[RAIASemanticScore]:
        """Parse LLM response into semantic scores."""
        import json

        try:
            data = json.loads(response)
            scores = []

            for dimension, info in data.items():
                if isinstance(info, dict) and "score" in info:
                    scores.append(RAIASemanticScore(
                        run_id=run_id,
                        node_name=node_name,
                        dimension=dimension,
                        score=float(info["score"]),
                        explanation=info.get("explanation")
                    ))

            return scores
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return []
