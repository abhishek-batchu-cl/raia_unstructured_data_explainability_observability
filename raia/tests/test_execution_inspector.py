"""
Tests for ExecutionInspector.
"""

import os
import tempfile
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from raia.inspectors.execution import RAIAExecutionInspector
from raia.storage.sqlite import SQLiteRAIAStorage


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
    return RAIAExecutionInspector(
        storage=storage,
        run_id="test_run_001",
        agent_name="test_agent"
    )


def test_inspector_initialization(inspector):
    """Test that inspector initializes correctly."""
    assert inspector is not None
    assert inspector.run_id == "test_run_001"
    assert inspector.agent_name == "test_agent"


def test_on_chain_start(inspector):
    """Test chain start callback."""
    serialized = {"name": "test_chain"}
    inputs = {"question": "Hello"}

    inspector.on_chain_start(
        serialized=serialized,
        inputs=inputs,
        parent_run_id=None
    )

    # Check run was created
    run = inspector.storage.get_run(inspector.run_id)
    assert run is not None
    assert run.status == "in_progress"


def test_on_chain_end(inspector):
    """Test chain end callback."""
    # Start chain first
    inspector.on_chain_start(
        serialized={"name": "test_chain"},
        inputs={},
        parent_run_id=None
    )

    # End chain
    inspector.on_chain_end(
        outputs={"answer": "Hello back"},
        parent_run_id=None
    )

    # Check run was updated
    run = inspector.storage.get_run(inspector.run_id)
    assert run.status == "success"
    assert run.end_time is not None
    assert run.total_latency_ms is not None


def test_on_chain_error(inspector):
    """Test chain error callback."""
    # Start chain
    inspector.on_chain_start(
        serialized={"name": "test_chain"},
        inputs={},
        parent_run_id=None
    )

    # Trigger error
    error = ValueError("Test error")
    inspector.on_chain_error(error=error, parent_run_id=None)

    # Check run was marked as error
    run = inspector.storage.get_run(inspector.run_id)
    assert run.status == "error"
    assert "Test error" in str(run.metadata.get("error", ""))


def test_on_llm_start_and_end(inspector):
    """Test LLM start and end callbacks."""
    # Start chain
    inspector.on_chain_start(
        serialized={"name": "test_chain"},
        inputs={},
        parent_run_id=None
    )

    # Start LLM
    llm_run_id = "llm_001"
    inspector.on_llm_start(
        serialized={},
        prompts=["Hello"],
        run_id=llm_run_id
    )

    # Create mock LLM result
    mock_result = MagicMock()
    mock_result.llm_output = {
        "token_usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20
        }
    }

    # End LLM
    inspector.on_llm_end(
        response=mock_result,
        run_id=llm_run_id,
        invocation_params={"model_name": "gpt-3.5-turbo"}
    )

    # Check node metrics were saved
    metrics = inspector.storage.get_node_metrics_for_run(inspector.run_id)
    assert len(metrics) == 1
    assert metrics[0].node_type == "llm"
    assert metrics[0].tokens_prompt == 10
    assert metrics[0].tokens_completion == 20
    assert metrics[0].success is True


def test_on_tool_start_and_end(inspector):
    """Test tool start and end callbacks."""
    # Start chain
    inspector.on_chain_start(
        serialized={"name": "test_chain"},
        inputs={},
        parent_run_id=None
    )

    # Start tool
    tool_run_id = "tool_001"
    inspector.on_tool_start(
        serialized={"name": "search"},
        input_str="query",
        run_id=tool_run_id
    )

    # End tool
    inspector.on_tool_end(
        output="result",
        run_id=tool_run_id,
        name="search"
    )

    # Check node metrics
    metrics = inspector.storage.get_node_metrics_for_run(inspector.run_id)
    assert len(metrics) == 1
    assert metrics[0].node_type == "tool"
    assert metrics[0].node_name == "search"
    assert metrics[0].success is True


def test_on_tool_error(inspector):
    """Test tool error callback."""
    # Start chain
    inspector.on_chain_start(
        serialized={"name": "test_chain"},
        inputs={},
        parent_run_id=None
    )

    # Start tool
    tool_run_id = "tool_002"
    inspector.on_tool_start(
        serialized={"name": "calculator"},
        input_str="1/0",
        run_id=tool_run_id
    )

    # Tool error
    error = ZeroDivisionError("division by zero")
    inspector.on_tool_error(
        error=error,
        run_id=tool_run_id,
        name="calculator"
    )

    # Check node metrics
    metrics = inspector.storage.get_node_metrics_for_run(inspector.run_id)
    assert len(metrics) == 1
    assert metrics[0].success is False
    assert metrics[0].error_type == "tool_error"
    assert "division by zero" in metrics[0].error_message


def test_token_aggregation(inspector):
    """Test that token counts are aggregated correctly."""
    # Start chain
    inspector.on_chain_start(
        serialized={"name": "test_chain"},
        inputs={},
        parent_run_id=None
    )

    # Multiple LLM calls
    for i in range(3):
        llm_run_id = f"llm_{i}"
        inspector.on_llm_start(
            serialized={},
            prompts=["test"],
            run_id=llm_run_id
        )

        mock_result = MagicMock()
        mock_result.llm_output = {
            "token_usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20
            }
        }

        inspector.on_llm_end(
            response=mock_result,
            run_id=llm_run_id,
            invocation_params={"model_name": "test-model"}
        )

    # End chain
    inspector.on_chain_end(outputs={}, parent_run_id=None)

    # Check aggregation
    run = inspector.storage.get_run(inspector.run_id)
    assert run.total_tokens_prompt == 30  # 3 * 10
    assert run.total_tokens_completion == 60  # 3 * 20
