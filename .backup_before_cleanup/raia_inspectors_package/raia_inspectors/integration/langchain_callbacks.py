"""
RAIA Inspectors - LangChain Integration

Helpers for integrating RAIA inspectors with LangChain.
"""

import logging
from typing import Optional

from ..execution_inspector import RAIAExecutionInspector
from ..storage.base import BaseRAIAStorage


logger = logging.getLogger(__name__)


def create_inspector_callback(
    run_id: Optional[str] = None,
    session_id: Optional[str] = None,
    agent_name: Optional[str] = None,
    graph_name: Optional[str] = None,
    storage: Optional[BaseRAIAStorage] = None
) -> RAIAExecutionInspector:
    """
    Create a RAIA execution inspector callback for LangChain.

    Convenience function for creating inspector callbacks with common parameters.

    Args:
        run_id: Run ID (auto-generated if None)
        session_id: Session ID (optional)
        agent_name: Agent name (optional)
        graph_name: Graph name (optional)
        storage: Storage backend (uses global config if None)

    Returns:
        RAIAExecutionInspector instance ready to use as a LangChain callback

    Example:
        from raia_inspectors.integration import create_inspector_callback

        inspector = create_inspector_callback(
            agent_name="my_agent",
            session_id="session_123"
        )

        result = chain.invoke(
            {"question": "What is the capital of France?"},
            config={"callbacks": [inspector]}
        )

        # Query metrics
        run = inspector.storage.get_run(inspector.run_id)
        metrics = inspector.storage.get_node_metrics_for_run(inspector.run_id)
    """
    inspector = RAIAExecutionInspector(
        storage=storage,
        run_id=run_id,
        session_id=session_id,
        agent_name=agent_name,
        graph_name=graph_name
    )

    logger.info(f"Created inspector callback: run_id={inspector.run_id}, agent={agent_name}")
    return inspector
