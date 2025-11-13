"""
Responsible AI Analytics & Agent Evaluation (RAIA) - Unified Python SDK

Complete production-grade instrumentation and evaluation framework for agentic systems.

## Two Complementary Systems:

### 1. Event Logging (RAIA Events)
Production-grade event logging with:
- Async batching and circuit breaker
- Multiple transports (file, HTTP, Kafka, OTLP)
- PII/PHI redaction and HMAC signing
- Deterministic replay capabilities

### 2. Behavioral Analysis (RAIA Inspectors)
Performance and pattern analysis with:
- Execution metrics (latency, tokens, cost)
- Behavioral pattern detection (loops, redundancy)
- Semantic evaluation framework
- Real-time observability

## Quick Start:

```python
from raia import EventEmitter, EmitterConfig
from raia.inspectors import RAIAExecutionInspector, RAIABehaviorInspector

# Event logging
config = EmitterConfig.from_env()
emitter = EventEmitter(config)
await emitter.start()

# Behavioral analysis
exec_inspector = RAIAExecutionInspector(agent_name="my_agent")
behavior_inspector = RAIABehaviorInspector()
```

"""

__version__ = "1.0.0"

# Event Logging Components
from .events.emitter import EventEmitter, EmitterConfig, TransportType, CircuitState
from .events.redactor import Redactor, RedactionRule
from .events.signer import EventSigner

# Inspector Components
from .inspectors.execution import RAIAExecutionInspector
from .inspectors.behavior import RAIABehaviorInspector
from .inspectors.semantic import RAIASemanticInspector, SemanticEvaluator
from .inspectors.rag import RAIARAGInspector

# Data Models
from .models import (
    RAIAAgentRun,
    RAIANodeMetrics,
    RAIAFunctionalSignal,
    RAIASemanticScore,
    # RAG Evaluation Models
    RAIARetrievalMetrics,
    RAIAAnswerQualityMetrics,
    RAIAEmbeddingDriftMetrics,
    RAIAVectorIndexHealth,
    RAIAPipelineMetrics,
)

# Explainability Models
from .models_explainability import (
    Attribution,
    RAIAAttributionMap,
    ReasoningStep,
    RAIAReasoningTrace,
    AlternativeAction,
    RAIAAgentDecision,
)

# What-If Analysis Models
from .models_whatif import (
    RAIACounterfactualScenario,
    ParameterSensitivity,
    RAIASensitivityAnalysis,
    RAIAOptimizationRecommendation,
)

# Comparison & Reporting Models
from .models_comparison import (
    RunComparison,
    EvaluationReport,
    BatchEvaluationResult,
)

# Storage
from .storage.base import BaseRAIAStorage
from .storage.sqlite import SQLiteRAIAStorage

# Configuration
from .config import RAIAConfig, get_raia_config, set_raia_config

# Utilities
from .utils import RAIAComparator

# Integrations (optional - require LangChain)
try:
    from .integrations.langchain import (
        LangChainCallbackHandler,
        LangChainExecutionInspector,
        instrumented_tool,
    )
    from .integrations.langgraph import stream_with_inspection
    _LANGCHAIN_AVAILABLE = True
except ImportError:
    # LangChain not available - integrations won't be exported
    _LANGCHAIN_AVAILABLE = False
    LangChainCallbackHandler = None
    LangChainExecutionInspector = None
    instrumented_tool = None
    stream_with_inspection = None

__all__ = [
    # Version
    "__version__",
    # Event Logging
    "EventEmitter",
    "EmitterConfig",
    "TransportType",
    "CircuitState",
    "Redactor",
    "RedactionRule",
    "EventSigner",
    # Inspectors
    "RAIAExecutionInspector",
    "RAIABehaviorInspector",
    "RAIASemanticInspector",
    "SemanticEvaluator",
    "RAIARAGInspector",
    # Models
    "RAIAAgentRun",
    "RAIANodeMetrics",
    "RAIAFunctionalSignal",
    "RAIASemanticScore",
    # RAG Evaluation Models
    "RAIARetrievalMetrics",
    "RAIAAnswerQualityMetrics",
    "RAIAEmbeddingDriftMetrics",
    "RAIAVectorIndexHealth",
    "RAIAPipelineMetrics",
    # Explainability Models
    "Attribution",
    "RAIAAttributionMap",
    "ReasoningStep",
    "RAIAReasoningTrace",
    "AlternativeAction",
    "RAIAAgentDecision",
    # What-If Analysis Models
    "RAIACounterfactualScenario",
    "ParameterSensitivity",
    "RAIASensitivityAnalysis",
    "RAIAOptimizationRecommendation",
    # Comparison & Reporting Models
    "RunComparison",
    "EvaluationReport",
    "BatchEvaluationResult",
    # Storage
    "BaseRAIAStorage",
    "SQLiteRAIAStorage",
    # Configuration
    "RAIAConfig",
    "get_raia_config",
    "set_raia_config",
    # Utilities
    "RAIAComparator",
    # Integrations
    "LangChainCallbackHandler",
    "LangChainExecutionInspector",
    "instrumented_tool",
    "stream_with_inspection",
]
