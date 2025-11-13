"""
RAIA Inspectors - LangGraph Integration

Helpers for integrating RAIA inspectors with LangGraph.
"""

import logging
import uuid
from typing import Any, Dict, Iterator, Optional

from raia.inspectors.execution import RAIAExecutionInspector
from raia.inspectors.behavior import RAIABehaviorInspector
from raia.storage.base import BaseRAIAStorage


logger = logging.getLogger(__name__)


def stream_with_inspection(
    graph,
    input_data: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None,
    run_id: Optional[str] = None,
    session_id: Optional[str] = None,
    agent_name: Optional[str] = None,
    graph_name: Optional[str] = None,
    storage: Optional[BaseRAIAStorage] = None,
    enable_execution_inspector: bool = True,
    enable_behavior_inspector: bool = True,
    stream_mode: str = "updates"
) -> Iterator[Dict[str, Any]]:
    """
    Stream LangGraph execution with RAIA inspection.

    Wraps graph.stream() to automatically:
    1. Track execution metrics (via ExecutionInspector)
    2. Detect behavioral patterns (via BehaviorInspector)
    3. Yield events to caller

    Args:
        graph: LangGraph graph instance
        input_data: Input to the graph
        config: LangGraph config (optional)
        run_id: Run ID (auto-generated if None)
        session_id: Session ID (optional)
        agent_name: Agent name (optional)
        graph_name: Graph name (optional)
        storage: Storage backend (uses global config if None)
        enable_execution_inspector: Enable execution metrics tracking
        enable_behavior_inspector: Enable behavior pattern detection
        stream_mode: LangGraph stream mode (default: "updates")

    Yields:
        LangGraph stream events

    Example:
        from langgraph.graph import StateGraph
        from raia_inspectors.integration import stream_with_inspection

        # Define your graph
        graph = StateGraph(...)
        compiled_graph = graph.compile()

        # Stream with inspection
        for event in stream_with_inspection(
            compiled_graph,
            {"input": "Hello"},
            agent_name="my_agent"
        ):
            print(event)

        # Metrics are automatically saved to storage
    """
    run_id = run_id or str(uuid.uuid4())

    # Initialize inspectors
    execution_inspector = None
    behavior_inspector = None

    if enable_execution_inspector:
        execution_inspector = RAIAExecutionInspector(
            storage=storage,
            run_id=run_id,
            session_id=session_id,
            agent_name=agent_name,
            graph_name=graph_name
        )
        logger.info(f"Execution inspector enabled for run {run_id}")

    if enable_behavior_inspector:
        behavior_inspector = RAIABehaviorInspector(storage=storage)
        logger.info(f"Behavior inspector enabled for run {run_id}")

    # Prepare config with execution inspector callback
    if config is None:
        config = {}

    if execution_inspector:
        callbacks = config.get("callbacks", [])
        callbacks.append(execution_inspector)
        config["callbacks"] = callbacks

    # Stream events
    try:
        for event in graph.stream(input_data, config=config, stream_mode=stream_mode):
            # Process with behavior inspector
            if behavior_inspector:
                behavior_inspector.process_event(run_id, event)

            # Yield to caller
            yield event

        # Finalize behavior analysis
        if behavior_inspector:
            behavior_inspector.finalize_run(run_id)
            logger.info(f"Behavior analysis finalized for run {run_id}")

    except Exception as e:
        logger.error(f"Error during graph execution: {e}", exc_info=True)
        raise


def inspect_graph_run(
    graph,
    input_data: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None,
    run_id: Optional[str] = None,
    storage: Optional[BaseRAIAStorage] = None
) -> Dict[str, Any]:
    """
    Run graph with inspection and return aggregated results.

    Convenience wrapper that collects all events and returns:
    - Final output
    - Run metrics
    - Node metrics
    - Behavioral signals
    - Semantic scores (if evaluator configured)

    Args:
        graph: LangGraph graph instance
        input_data: Input to the graph
        config: LangGraph config (optional)
        run_id: Run ID (auto-generated if None)
        storage: Storage backend (uses global config if None)

    Returns:
        Dictionary containing:
        - output: Final graph output
        - run: RAIAAgentRun
        - node_metrics: List[RAIANodeMetrics]
        - signals: List[RAIAFunctionalSignal]
        - semantic_scores: List[RAIASemanticScore]

    Example:
        from raia_inspectors.integration import inspect_graph_run

        result = inspect_graph_run(
            compiled_graph,
            {"input": "Hello"}
        )

        print(f"Output: {result['output']}")
        print(f"Total latency: {result['run'].total_latency_ms}ms")
        print(f"Signals detected: {len(result['signals'])}")
    """
    run_id = run_id or str(uuid.uuid4())

    # Collect all events
    events = []
    for event in stream_with_inspection(
        graph,
        input_data,
        config=config,
        run_id=run_id,
        storage=storage
    ):
        events.append(event)

    # Get final output (last event)
    output = events[-1] if events else None

    # Retrieve metrics from storage
    from raia.config import get_raia_config

    if storage is None:
        config_obj = get_raia_config()
        storage = config_obj.get_storage()

    run = storage.get_run(run_id)
    node_metrics = storage.get_node_metrics_for_run(run_id)
    signals = storage.get_signals_for_run(run_id)
    semantic_scores = storage.get_semantic_scores_for_run(run_id)

    return {
        "output": output,
        "run": run,
        "node_metrics": node_metrics,
        "signals": signals,
        "semantic_scores": semantic_scores
    }
