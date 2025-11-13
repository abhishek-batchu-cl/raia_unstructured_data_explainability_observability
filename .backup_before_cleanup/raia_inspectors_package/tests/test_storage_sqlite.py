"""
Tests for SQLite storage implementation.
"""

import os
import tempfile
from datetime import datetime

import pytest

from raia_inspectors.storage.sqlite_storage import SQLiteRAIAStorage
from raia_inspectors.models import (
    RAIAAgentRun,
    RAIANodeMetrics,
    RAIAFunctionalSignal,
    RAIASemanticScore
)


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


def test_storage_initialization(storage):
    """Test that storage initializes and creates tables."""
    assert storage is not None
    assert os.path.exists(storage.db_path)


def test_save_and_get_run(storage):
    """Test saving and retrieving a run."""
    run = RAIAAgentRun(
        run_id="test_run_123",
        session_id="session_456",
        agent_name="test_agent",
        graph_name="test_graph",
        start_time=datetime.utcnow(),
        status="in_progress"
    )

    # Save
    storage.save_run(run)

    # Retrieve
    retrieved = storage.get_run("test_run_123")
    assert retrieved is not None
    assert retrieved.run_id == "test_run_123"
    assert retrieved.agent_name == "test_agent"
    assert retrieved.status == "in_progress"


def test_update_run(storage):
    """Test updating an existing run."""
    run = RAIAAgentRun(
        run_id="test_run_456",
        start_time=datetime.utcnow(),
        status="in_progress"
    )

    storage.save_run(run)

    # Update
    run.status = "success"
    run.end_time = datetime.utcnow()
    run.total_latency_ms = 1500.0
    storage.update_run(run)

    # Verify
    retrieved = storage.get_run("test_run_456")
    assert retrieved.status == "success"
    assert retrieved.end_time is not None
    assert retrieved.total_latency_ms == 1500.0


def test_save_node_metrics(storage):
    """Test saving and retrieving node metrics."""
    # First create a run
    run = RAIAAgentRun(
        run_id="test_run_789",
        start_time=datetime.utcnow(),
        status="in_progress"
    )
    storage.save_run(run)

    # Create metrics
    start = datetime.utcnow()
    end = datetime.utcnow()

    metrics = RAIANodeMetrics(
        run_id="test_run_789",
        node_name="test_llm",
        node_type="llm",
        start_time=start,
        end_time=end,
        latency_ms=250.5,
        tokens_prompt=100,
        tokens_completion=50,
        success=True
    )

    storage.save_node_metrics(metrics)

    # Retrieve
    retrieved_metrics = storage.get_node_metrics_for_run("test_run_789")
    assert len(retrieved_metrics) == 1
    assert retrieved_metrics[0].node_name == "test_llm"
    assert retrieved_metrics[0].latency_ms == 250.5
    assert retrieved_metrics[0].tokens_prompt == 100


def test_save_functional_signal(storage):
    """Test saving and retrieving functional signals."""
    # Create run
    run = RAIAAgentRun(
        run_id="test_run_signal",
        start_time=datetime.utcnow(),
        status="in_progress"
    )
    storage.save_run(run)

    # Create signal
    signal = RAIAFunctionalSignal(
        run_id="test_run_signal",
        node_name="search_node",
        signal_type="loop_detected",
        severity="high",
        message="Node executed 5 times",
        metadata={"count": 5}
    )

    storage.save_functional_signal(signal)

    # Retrieve
    signals = storage.get_signals_for_run("test_run_signal")
    assert len(signals) == 1
    assert signals[0].signal_type == "loop_detected"
    assert signals[0].severity == "high"
    assert signals[0].metadata["count"] == 5


def test_save_semantic_score(storage):
    """Test saving and retrieving semantic scores."""
    # Create run
    run = RAIAAgentRun(
        run_id="test_run_semantic",
        start_time=datetime.utcnow(),
        status="in_progress"
    )
    storage.save_run(run)

    # Create score
    score = RAIASemanticScore(
        run_id="test_run_semantic",
        node_name="answer_node",
        dimension="hallucination_risk",
        score=0.15,
        explanation="Well-grounded response"
    )

    storage.save_semantic_score(score)

    # Retrieve
    scores = storage.get_semantic_scores_for_run("test_run_semantic")
    assert len(scores) == 1
    assert scores[0].dimension == "hallucination_risk"
    assert scores[0].score == 0.15
    assert scores[0].explanation == "Well-grounded response"


def test_multiple_node_metrics(storage):
    """Test saving multiple node metrics for a single run."""
    run = RAIAAgentRun(
        run_id="test_run_multi",
        start_time=datetime.utcnow(),
        status="in_progress"
    )
    storage.save_run(run)

    # Save multiple metrics
    for i in range(5):
        metrics = RAIANodeMetrics(
            run_id="test_run_multi",
            node_name=f"node_{i}",
            node_type="tool",
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow(),
            latency_ms=100.0 * i,
            success=True
        )
        storage.save_node_metrics(metrics)

    # Retrieve
    all_metrics = storage.get_node_metrics_for_run("test_run_multi")
    assert len(all_metrics) == 5
    assert all_metrics[0].node_name == "node_0"
    assert all_metrics[4].node_name == "node_4"


def test_get_nonexistent_run(storage):
    """Test retrieving a run that doesn't exist."""
    result = storage.get_run("nonexistent_run")
    assert result is None


def test_get_metrics_for_nonexistent_run(storage):
    """Test retrieving metrics for a run that doesn't exist."""
    metrics = storage.get_node_metrics_for_run("nonexistent_run")
    assert metrics == []

    signals = storage.get_signals_for_run("nonexistent_run")
    assert signals == []

    scores = storage.get_semantic_scores_for_run("nonexistent_run")
    assert scores == []
