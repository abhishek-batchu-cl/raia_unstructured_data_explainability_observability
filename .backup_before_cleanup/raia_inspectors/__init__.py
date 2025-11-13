"""
RAIA Inspectors - Behavior & Performance Analysis for AI Agents

A production-quality library for analyzing LangChain and LangGraph agents.

Key Features:
- Execution metrics: latency, token usage, cost tracking
- Behavior analysis: loop detection, redundant operations, suboptimal paths
- Semantic evaluation: pluggable quality scoring
- SQLite storage: persistent metrics and signals

Positioning:
- LangSmith: Traces WHAT happened (events and logs)
- RAIA Inspectors: Analyzes HOW WELL it happened (performance and behavior)

Quick Start:

    from raia_inspectors import RAIAExecutionInspector

    # For LangChain
    inspector = RAIAExecutionInspector(agent_name="my_agent")
    result = chain.invoke(
        {"question": "Hello"},
        config={"callbacks": [inspector]}
    )

    # For LangGraph
    from raia_inspectors.integration import stream_with_inspection

    for event in stream_with_inspection(graph, {"input": "Hello"}):
        print(event)
"""

__version__ = "1.0.0"

# Core models
from .models import (
    RAIAAgentRun,
    RAIANodeMetrics,
    RAIAFunctionalSignal,
    RAIASemanticScore
)

# Storage
from .storage import BaseRAIAStorage, SQLiteRAIAStorage

# Configuration
from .config import RAIAConfig, get_raia_config, set_raia_config

# Inspectors
from .execution_inspector import RAIAExecutionInspector
from .behavior_inspector import RAIABehaviorInspector
from .semantic_inspector import (
    RAIASemanticInspector,
    SemanticEvaluator,
    DummySemanticEvaluator,
    LLMSemanticEvaluatorTemplate
)

# Integration helpers
from .integration import create_inspector_callback, stream_with_inspection

__all__ = [
    # Version
    "__version__",

    # Models
    "RAIAAgentRun",
    "RAIANodeMetrics",
    "RAIAFunctionalSignal",
    "RAIASemanticScore",

    # Storage
    "BaseRAIAStorage",
    "SQLiteRAIAStorage",

    # Configuration
    "RAIAConfig",
    "get_raia_config",
    "set_raia_config",

    # Inspectors
    "RAIAExecutionInspector",
    "RAIABehaviorInspector",
    "RAIASemanticInspector",
    "SemanticEvaluator",
    "DummySemanticEvaluator",
    "LLMSemanticEvaluatorTemplate",

    # Integration
    "create_inspector_callback",
    "stream_with_inspection",
]
