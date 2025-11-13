# RAIA Inspectors

**Behavior & Performance Analysis for AI Agents**

A production-quality Python library for analyzing how well LangChain and LangGraph agents execute, complementing traditional event logging with behavioral intelligence and performance insights.

---

## 🎯 What is RAIA Inspectors?

RAIA Inspectors is a specialized observability library that goes beyond logging *what* happened to analyze *how well* it happened. It provides:

- **Execution Metrics**: Latency, token usage, cost tracking per node and run
- **Behavior Analysis**: Loop detection, redundant operations, suboptimal paths
- **Semantic Evaluation**: Pluggable quality scoring (hallucination risk, adherence, etc.)
- **SQLite Storage**: Persistent metrics with queryable insights

---

## 🔍 RAIA Inspectors vs LangSmith / LangChain

| Feature | LangSmith / LangChain | RAIA Inspectors |
|---------|----------------------|-----------------|
| **Purpose** | Event tracing & logging | Behavior & performance analysis |
| **Focus** | **WHAT** happened | **HOW WELL** it happened |
| **Data Captured** | Events, inputs, outputs | Metrics, patterns, quality scores |
| **Primary Use Case** | Debugging, tracing | Performance optimization, quality assurance |
| **Behavioral Insights** | ❌ | ✅ Loop detection, redundancy, path analysis |
| **Performance Metrics** | ❌ | ✅ Per-node latency, cost, token efficiency |
| **Semantic Evaluation** | ❌ | ✅ Pluggable quality scorers |
| **Storage** | Cloud-based | Local SQLite (portable) |

### Why Both?

- **LangSmith**: Understand the execution flow, debug issues, trace events
- **RAIA Inspectors**: Measure efficiency, detect patterns, score quality, optimize performance

They are **complementary**, not competitive. Use LangSmith for development and debugging; use RAIA Inspectors for production monitoring and continuous improvement.

---

## 🚀 Quick Start

### Installation

```bash
# From the raia_inspectors directory
pip install -e .

# Or install dependencies manually
pip install pydantic
pip install langchain  # Optional, for LangChain integration
pip install langgraph  # Optional, for LangGraph integration
```

### LangChain Example

```python
from raia_inspectors import RAIAExecutionInspector

# Create inspector
inspector = RAIAExecutionInspector(agent_name="my_agent")

# Use as LangChain callback
result = chain.invoke(
    {"question": "What is the capital of France?"},
    config={"callbacks": [inspector]}
)

# Query metrics
run = inspector.storage.get_run(inspector.run_id)
print(f"Total latency: {run.total_latency_ms}ms")
print(f"Total tokens: {run.total_tokens_prompt + run.total_tokens_completion}")

node_metrics = inspector.storage.get_node_metrics_for_run(inspector.run_id)
for metric in node_metrics:
    print(f"{metric.node_name}: {metric.latency_ms}ms")
```

### LangGraph Example

```python
from raia_inspectors.integration import stream_with_inspection

# Stream graph with automatic inspection
for event in stream_with_inspection(
    graph,
    {"input": "Hello"},
    agent_name="my_graph_agent"
):
    print(event)

# Metrics and behavioral signals are automatically saved
```

---

## 📊 Core Features

### 1. Execution Inspector

Captures performance metrics via LangChain callbacks:

- **Per-run metrics**: Total latency, tokens, cost
- **Per-node metrics**: LLM calls, tool executions, chains
- **Error tracking**: Failures, retries, error messages
- **Cost estimation**: Token-based cost calculation

```python
from raia_inspectors import RAIAExecutionInspector

inspector = RAIAExecutionInspector(
    agent_name="medical_agent",
    session_id="session_123"
)

# Use with any LangChain chain or agent
result = agent.invoke(input, config={"callbacks": [inspector]})
```

### 2. Behavior Inspector

Detects problematic patterns in LangGraph executions:

- **Loop detection**: Repeated node sequences
- **Redundant operations**: Same tool called multiple times
- **Suboptimal paths**: Too many nodes for simple queries
- **State inconsistencies**: Conflicting state values

```python
from raia_inspectors import RAIABehaviorInspector

inspector = RAIABehaviorInspector()

for event in graph.stream(input, stream_mode="updates"):
    inspector.process_event(run_id, event)

inspector.finalize_run(run_id)

# Query detected patterns
signals = storage.get_signals_for_run(run_id)
for signal in signals:
    print(f"{signal.signal_type}: {signal.message}")
```

### 3. Semantic Inspector

Pluggable interface for quality evaluation:

```python
from raia_inspectors import RAIASemanticInspector, DummySemanticEvaluator

# Use built-in dummy evaluator or implement your own
evaluator = DummySemanticEvaluator()
inspector = RAIASemanticInspector(evaluator=evaluator)

scores = inspector.evaluate_step(
    run_id="run_123",
    node_name="answer_node",
    state_after={"answer": "Paris is the capital of France"}
)

for score in scores:
    print(f"{score.dimension}: {score.score:.2f}")
```

### 4. SQLite Storage

Persistent, queryable storage:

```python
from raia_inspectors import SQLiteRAIAStorage

storage = SQLiteRAIAStorage(db_path="my_metrics.db")

# Query runs
run = storage.get_run("run_id")
node_metrics = storage.get_node_metrics_for_run("run_id")
signals = storage.get_signals_for_run("run_id")
semantic_scores = storage.get_semantic_scores_for_run("run_id")
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         LangChain / LangGraph           │
│              Agent Runtime              │
└──────────────┬──────────────────────────┘
               │
               │ Callbacks / Events
               ▼
┌─────────────────────────────────────────┐
│         RAIA Inspectors                 │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │   Execution Inspector            │  │
│  │   • Latency, tokens, cost        │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │   Behavior Inspector             │  │
│  │   • Loops, redundancy, paths     │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │   Semantic Inspector             │  │
│  │   • Quality scores (pluggable)   │  │
│  └──────────────────────────────────┘  │
│                                         │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         SQLite Storage                  │
│                                         │
│  • Runs          • Signals              │
│  • Node Metrics  • Semantic Scores      │
└─────────────────────────────────────────┘
```

---

## 📋 Data Models

### RAIAAgentRun
- `run_id`, `session_id`, `agent_name`, `graph_name`
- `start_time`, `end_time`, `status`
- `total_latency_ms`, `total_tokens_*`, `total_cost_usd`

### RAIANodeMetrics
- Per-node execution metrics
- `node_name`, `node_type` (llm/tool/chain/custom)
- `latency_ms`, `tokens_*`, `cost_usd`
- `success`, `error_type`, `retry_count`

### RAIAFunctionalSignal
- Behavioral pattern detection
- `signal_type`: loop_detected, redundant_tool_use, bad_tool_choice, etc.
- `severity`: low, medium, high, critical
- `message`, `metadata`

### RAIASemanticScore
- Quality evaluation
- `dimension`: hallucination_risk, instruction_adherence, clarity, etc.
- `score` (0-1), `explanation`

---

## 🧪 Running Tests

```bash
# Install pytest
pip install pytest

# Run all tests
pytest raia_inspectors/tests/

# Run specific test file
pytest raia_inspectors/tests/test_execution_inspector.py

# Run with coverage
pip install pytest-cov
pytest --cov=raia_inspectors raia_inspectors/tests/
```

---

## 📚 Examples

See the `examples/` directory:

- **example_langchain_usage.py**: Complete LangChain demo
- **example_langgraph_usage.py**: Complete LangGraph demo

Run examples:

```bash
python raia_inspectors/examples/example_langchain_usage.py
python raia_inspectors/examples/example_langgraph_usage.py
```

---

## 🔌 Custom Semantic Evaluators

Implement your own evaluator:

```python
from raia_inspectors import RAIASemanticInspector, RAIASemanticScore

class MyEvaluator:
    def evaluate_step(self, *, run_id, node_name, state_before, state_after, messages):
        # Your custom logic here
        score = self.compute_quality(state_after)

        return [
            RAIASemanticScore(
                run_id=run_id,
                node_name=node_name,
                dimension="custom_quality",
                score=score,
                explanation="Custom evaluation logic"
            )
        ]

    def compute_quality(self, state):
        # Your implementation
        return 0.85

# Use custom evaluator
inspector = RAIASemanticInspector(evaluator=MyEvaluator())
```

---

## 🤝 Integration with Existing RAIA Framework

RAIA Inspectors is designed to **complement** the existing RAIA event framework:

- **RAIA SDK**: Emits structured events (session_start, tool_call, finalized, etc.)
- **RAIA Inspectors**: Analyzes execution patterns and performance

**Both can run simultaneously:**

```python
from raia import EventEmitter
from raia.integrations.langchain import LangChainCallbackHandler
from raia_inspectors import RAIAExecutionInspector

# RAIA SDK for event logging
raia_emitter = EventEmitter(...)
raia_callback = LangChainCallbackHandler(emitter=raia_emitter)

# RAIA Inspectors for behavior analysis
inspector = RAIAExecutionInspector()

# Use both
result = chain.invoke(
    input,
    config={"callbacks": [raia_callback, inspector]}
)
```

---

## 📖 Documentation

- **README.md**: This file
- **models.py**: Data model definitions
- **storage/**: Storage implementations
- **integration/**: Helper functions for LangChain/LangGraph
- **examples/**: Complete working examples
- **tests/**: Test suite

---

## 🛠️ Configuration

```python
from raia_inspectors import RAIAConfig, set_raia_config, SQLiteRAIAStorage

# Configure storage
storage = SQLiteRAIAStorage(db_path="custom_metrics.db")

config = RAIAConfig(
    default_storage=storage,
    app_name="my_app",
    environment="production",
    enable_semantic_eval=True
)

set_raia_config(config)

# All inspectors will now use this configuration
```

---

## 🚧 Limitations & Future Work

**Current Limitations:**
- Cost estimation uses simplified model (configurable per model in future)
- Semantic evaluation requires user-provided evaluator (no built-in LLM scorer)
- Behavioral pattern detection is heuristic-based

**Roadmap:**
- PostgreSQL storage backend
- Real-time alerting on behavioral signals
- Pre-built LLM-based semantic evaluators
- Grafana dashboard integration
- Multi-run aggregation and trend analysis

---

## 📝 License

Part of the RAIA (Responsible AI Analytics & Agent Evaluation) framework.

---

## 🙋 Support

For issues, questions, or contributions, please refer to the main RAIA repository.

---

**Built with ❤️ for the AI agent community**
