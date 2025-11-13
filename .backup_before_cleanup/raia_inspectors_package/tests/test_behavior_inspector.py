"""
Tests for BehaviorInspector.
"""

import os
import tempfile

import pytest

from raia_inspectors.behavior_inspector import RAIABehaviorInspector
from raia_inspectors.storage.sqlite_storage import SQLiteRAIAStorage


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


@pytest.fixture
def inspector(storage):
    """Create an inspector instance for testing."""
    return RAIABehaviorInspector(storage=storage, loop_threshold=3)


def test_inspector_initialization(inspector):
    """Test that inspector initializes correctly."""
    assert inspector is not None
    assert inspector.loop_threshold == 3


def test_process_event(inspector):
    """Test processing a single event."""
    event = {"search_node": {"query": "test"}}
    inspector.process_event("run_001", event)

    # Should have tracked the event
    state = inspector._run_state["run_001"]
    assert state["total_nodes"] == 1
    assert "search_node" in state["node_sequence"]


def test_detect_simple_loop(inspector, storage):
    """Test detection of simple node repetition."""
    run_id = "run_loop_001"

    # Simulate repeated node execution
    for i in range(4):
        event = {"search_node": {"query": f"test_{i}"}}
        inspector.process_event(run_id, event)

    inspector.finalize_run(run_id)

    # Check for loop signal
    signals = storage.get_signals_for_run(run_id)
    loop_signals = [s for s in signals if s.signal_type == "loop_detected"]
    assert len(loop_signals) > 0
    assert loop_signals[0].severity in ["medium", "high"]


def test_detect_cyclic_pattern(inspector, storage):
    """Test detection of cyclic patterns."""
    run_id = "run_cycle_001"

    # Simulate A -> B -> C -> A -> B -> C pattern
    pattern = ["node_a", "node_b", "node_c"]
    for _ in range(2):
        for node in pattern:
            event = {node: {"data": "test"}}
            inspector.process_event(run_id, event)

    inspector.finalize_run(run_id)

    # Check for cycle detection
    signals = storage.get_signals_for_run(run_id)
    loop_signals = [s for s in signals if s.signal_type == "loop_detected"]
    assert len(loop_signals) > 0


def test_detect_redundant_tools(inspector, storage):
    """Test detection of redundant tool usage."""
    run_id = "run_redundant_001"

    # Simulate same tool called multiple times with similar args
    for i in range(4):
        event = {
            "search_tool": {
                "tool_name": "search",
                "tool_args": {"query": "similar query"}
            }
        }
        inspector.process_event(run_id, event)

    inspector.finalize_run(run_id)

    # Check for redundancy signal
    signals = storage.get_signals_for_run(run_id)
    redundant_signals = [s for s in signals if s.signal_type == "redundant_tool_use"]
    assert len(redundant_signals) > 0


def test_detect_suboptimal_path(inspector, storage):
    """Test detection of suboptimal execution paths."""
    run_id = "run_suboptimal_001"

    # Simulate many nodes (more than threshold)
    for i in range(15):
        event = {f"node_{i}": {"data": "test"}}
        inspector.process_event(run_id, event)

    inspector.finalize_run(run_id)

    # Check for suboptimal path signal
    signals = storage.get_signals_for_run(run_id)
    suboptimal_signals = [s for s in signals if s.signal_type == "suboptimal_path"]
    assert len(suboptimal_signals) > 0


def test_detect_info_redundancy(inspector, storage):
    """Test detection of information redundancy."""
    run_id = "run_redundancy_001"

    # Same node repeated many times
    for i in range(10):
        event = {"same_node": {"iteration": i}}
        inspector.process_event(run_id, event)

    inspector.finalize_run(run_id)

    # Check for info redundancy
    signals = storage.get_signals_for_run(run_id)
    info_signals = [s for s in signals if s.signal_type == "info_redundancy"]
    assert len(info_signals) > 0


def test_reset_run(inspector):
    """Test resetting run state."""
    run_id = "run_reset_001"

    # Process some events
    for i in range(3):
        event = {f"node_{i}": {"data": "test"}}
        inspector.process_event(run_id, event)

    # Reset
    inspector.reset_run(run_id)

    # State should be cleared
    assert run_id not in inspector._run_state


def test_finalize_clears_state(inspector):
    """Test that finalize clears run state."""
    run_id = "run_finalize_001"

    # Process events
    event = {"test_node": {"data": "test"}}
    inspector.process_event(run_id, event)

    # Finalize
    inspector.finalize_run(run_id)

    # State should be cleared
    assert run_id not in inspector._run_state


def test_no_signals_for_normal_execution(inspector, storage):
    """Test that normal execution doesn't trigger signals."""
    run_id = "run_normal_001"

    # Simulate normal execution with few nodes
    nodes = ["start", "process", "end"]
    for node in nodes:
        event = {node: {"data": "test"}}
        inspector.process_event(run_id, event)

    inspector.finalize_run(run_id)

    # Should have minimal or no signals
    signals = storage.get_signals_for_run(run_id)
    # Filter out low severity signals
    high_signals = [s for s in signals if s.severity in ["high", "critical"]]
    assert len(high_signals) == 0
