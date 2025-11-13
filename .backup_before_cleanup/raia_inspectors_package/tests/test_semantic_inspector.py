"""
Tests for SemanticInspector.
"""

import os
import tempfile

import pytest

from raia_inspectors.semantic_inspector import (
    RAIASemanticInspector,
    DummySemanticEvaluator
)
from raia_inspectors.storage.sqlite_storage import SQLiteRAIAStorage
from raia_inspectors.models import RAIASemanticScore


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def storage(temp_db):
    """Create a storage instance for testing."""
    return SQLiteRAIAStorage(db_path=temp_db)


def test_inspector_without_evaluator(storage):
    """Test inspector behavior when no evaluator is provided."""
    inspector = RAIASemanticInspector(storage=storage)

    scores = inspector.evaluate_step(
        run_id="test_run",
        node_name="test_node"
    )

    # Should return empty list
    assert scores == []


def test_inspector_with_dummy_evaluator(storage):
    """Test inspector with dummy evaluator."""
    evaluator = DummySemanticEvaluator()
    inspector = RAIASemanticInspector(
        evaluator=evaluator,
        storage=storage,
        auto_save=False  # Don't auto-save for this test
    )

    scores = inspector.evaluate_step(
        run_id="test_run",
        node_name="test_node",
        state_after={"answer": "Test answer"}
    )

    # Should return some scores
    assert len(scores) > 0
    assert all(isinstance(s, RAIASemanticScore) for s in scores)


def test_auto_save_feature(storage):
    """Test that auto-save saves scores to storage."""
    from raia_inspectors.models import RAIAAgentRun

    # Create a run first
    run = RAIAAgentRun(
        run_id="test_run_autosave",
        start_time=storage._get_connection().execute("SELECT datetime('now')").fetchone()[0],
        status="in_progress"
    )
    storage.save_run(run)

    evaluator = DummySemanticEvaluator()
    inspector = RAIASemanticInspector(
        evaluator=evaluator,
        storage=storage,
        auto_save=True
    )

    inspector.evaluate_step(
        run_id="test_run_autosave",
        node_name="test_node"
    )

    # Scores should be saved
    saved_scores = storage.get_semantic_scores_for_run("test_run_autosave")
    assert len(saved_scores) > 0


def test_evaluate_multiple_steps(storage):
    """Test evaluating multiple steps in a run."""
    from raia_inspectors.models import RAIAAgentRun

    # Create run
    run = RAIAAgentRun(
        run_id="test_run_multi",
        start_time=storage._get_connection().execute("SELECT datetime('now')").fetchone()[0],
        status="in_progress"
    )
    storage.save_run(run)

    evaluator = DummySemanticEvaluator()
    inspector = RAIASemanticInspector(
        evaluator=evaluator,
        storage=storage,
        auto_save=True
    )

    steps = [
        {"node_name": "step_1", "state_after": {"data": "test1"}},
        {"node_name": "step_2", "state_after": {"data": "test2"}},
        {"node_name": "step_3", "state_after": {"data": "test3"}},
    ]

    scores = inspector.evaluate_run("test_run_multi", steps)

    # Should have scores for all steps
    assert len(scores) >= len(steps)


def test_custom_evaluator():
    """Test using a custom evaluator."""

    class CustomEvaluator:
        def evaluate_step(self, *, run_id, node_name, **kwargs):
            return [
                RAIASemanticScore(
                    run_id=run_id,
                    node_name=node_name,
                    dimension="custom_metric",
                    score=0.99,
                    explanation="Custom evaluation"
                )
            ]

    inspector = RAIASemanticInspector(
        evaluator=CustomEvaluator(),
        auto_save=False
    )

    scores = inspector.evaluate_step(
        run_id="test_run",
        node_name="test_node"
    )

    assert len(scores) == 1
    assert scores[0].dimension == "custom_metric"
    assert scores[0].score == 0.99


def test_evaluator_error_handling(storage):
    """Test that evaluator errors are handled gracefully."""

    class BrokenEvaluator:
        def evaluate_step(self, **kwargs):
            raise ValueError("Intentional error")

    inspector = RAIASemanticInspector(
        evaluator=BrokenEvaluator(),
        storage=storage
    )

    # Should not raise, just return empty list
    scores = inspector.evaluate_step(
        run_id="test_run",
        node_name="test_node"
    )

    assert scores == []


def test_evaluator_with_all_parameters():
    """Test evaluator with all available parameters."""

    class DetailedEvaluator:
        def __init__(self):
            self.called_with = None

        def evaluate_step(self, *, run_id, node_name, state_before, state_after, messages):
            self.called_with = {
                "run_id": run_id,
                "node_name": node_name,
                "state_before": state_before,
                "state_after": state_after,
                "messages": messages
            }
            return []

    evaluator = DetailedEvaluator()
    inspector = RAIASemanticInspector(evaluator=evaluator, auto_save=False)

    inspector.evaluate_step(
        run_id="test_run",
        node_name="test_node",
        state_before={"key": "before"},
        state_after={"key": "after"},
        messages=[{"role": "user", "content": "test"}]
    )

    # Check evaluator received all parameters
    assert evaluator.called_with["run_id"] == "test_run"
    assert evaluator.called_with["state_before"] == {"key": "before"}
    assert evaluator.called_with["state_after"] == {"key": "after"}
    assert len(evaluator.called_with["messages"]) == 1
