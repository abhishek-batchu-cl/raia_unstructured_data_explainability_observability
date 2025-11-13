"""
Inspector Components (RAIA Inspectors)

Behavioral analysis and performance metrics for agentic systems:
- Execution Inspector: Performance metrics (latency, tokens, cost)
- Behavior Inspector: Pattern detection (loops, redundancy, suboptimal paths)
- Semantic Inspector: Quality evaluation framework
- RAG Inspector: RAG evaluation with drift detection (UNIQUE to RAIA!)
"""

from .execution import RAIAExecutionInspector
from .behavior import RAIABehaviorInspector
from .semantic import RAIASemanticInspector, SemanticEvaluator
from .rag import RAIARAGInspector

__all__ = [
    "RAIAExecutionInspector",
    "RAIABehaviorInspector",
    "RAIASemanticInspector",
    "SemanticEvaluator",
    "RAIARAGInspector",
]
