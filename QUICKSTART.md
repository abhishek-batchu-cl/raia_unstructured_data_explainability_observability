# RAIA Quick Start Guide

Get started with RAIA in under 5 minutes!

## Installation

### Option 1: pip install (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/raia.git
cd raia

# Install RAIA
pip install -e .

# Install optional dependencies
pip install -e ".[langchain]"  # For LangChain integration
pip install -e ".[all]"          # All optional features
```

### Option 2: Docker

```bash
# Build and run with Docker
docker-compose up -d

# Access the container
docker exec -it raia_app bash
```

## Quick Example

```python
from raia import RAIARAGInspector, SQLiteRAIAStorage

# Initialize RAIA
storage = SQLiteRAIAStorage("my_rag_eval.db")
inspector = RAIARAGInspector(storage=storage)

# Track retrieval metrics
inspector.track_retrieval(
    run_id="run_001",
    query="What causes climate change?",
    retrieved_doc_ids=["doc1", "doc2", "doc3"],
    relevance_scores=[0.92, 0.87, 0.81],
    retrieval_latency_ms=45.0,
    precision_at_k=1.0,
    recall_at_k=0.85,
)

# Track answer quality
inspector.track_answer_quality(
    run_id="run_001",
    query="What causes climate change?",
    answer="Climate change is caused by...",
    answer_relevance=0.94,
    answer_faithfulness=0.97,
    hallucination_score=0.03,
    generation_latency_ms=1800.0,
)

print("✅ Metrics tracked successfully!")
```

## Run Complete Examples

### 1. Realistic RAG Evaluation

```bash
python examples/realistic_rag_evaluation.py
```

This example demonstrates:
- ✅ Complete RAG pipeline evaluation
- ✅ Multiple configuration comparison
- ✅ Explainability analysis (attribution + reasoning)
- ✅ What-if analysis for optimization
- ✅ Comprehensive reporting

### 2. Explainability Demo

```bash
python demo_explainability.py
```

Shows SHAP/LIME-style explainability for RAG:
- 📊 Attribution tracking (document → answer)
- 🔍 Reasoning traces (step-by-step process)
- 🎯 Comparison with traditional ML explainability

### 3. What-If Analysis Demo

```bash
python demo_whatif.py
```

Demonstrates counterfactual analysis:
- 💰 Cost optimization scenarios
- ⚡ Performance trade-off analysis
- 📈 ROI calculations
- 🎯 Actionable recommendations

### 4. Complete Workflow Demo

```bash
python demo_complete.py
```

End-to-end workflow showing all features together.

## Core Features

### 1. RAG Evaluation
```python
# Track retrieval quality
inspector.track_retrieval(...)

# Track answer quality
inspector.track_answer_quality(...)

# Track embedding drift
inspector.track_embedding_drift(...)

# Track vector index health
inspector.track_index_health(...)

# Track pipeline metrics
inspector.track_pipeline(...)
```

### 2. Explainability
```python
# Track attribution (which documents influenced answer)
inspector.track_attribution(
    run_id="run_001",
    query="...",
    answer="...",
    attributions=[...],  # document → answer span mappings
    faithfulness_score=0.97,
    hallucination_score=0.03,
)

# Track reasoning (step-by-step process)
inspector.track_reasoning(
    run_id="run_001",
    query="...",
    steps=[...],  # reasoning steps with timing
    reasoning_quality_score=0.93,
)
```

### 3. What-If Analysis
```python
# Simulate configuration changes
scenario = inspector.simulate_scenario(
    run_id="run_001",
    scenario_name="Reduce context size",
    scenario_type="context",
    original_config={"context_tokens": 2000},
    alternative_config={"context_tokens": 1200},
    original_quality=0.92,
    original_latency_ms=1800.0,
    original_cost_usd=0.0045,
    alternative_quality=0.90,
    alternative_latency_ms=1100.0,
    alternative_cost_usd=0.0027,
)

print(f"Recommendation: {scenario.recommendation}")
print(f"Quality delta: {scenario.quality_delta_pct:+.1f}%")
print(f"Cost delta: {scenario.cost_delta_pct:+.1f}%")
```

### 4. Comparison & Reporting
```python
from raia import RAIAComparator

comparator = RAIAComparator(storage)

# Compare multiple runs
comparison = comparator.compare_runs(
    run_ids=["run_001", "run_002", "run_003"],
    comparison_name="A/B/C Test"
)
comparator.print_comparison(comparison)

# Generate comprehensive report
report = comparator.generate_report(
    run_ids=["run_001", "run_002", "run_003"],
    report_name="Q4 2024 Evaluation"
)
comparator.print_report(report)
```

## LangChain Integration

```python
from raia.integrations.langchain import LangChainCallbackHandler
from langchain.chains import RetrievalQA

# Add RAIA callback to LangChain
callback = LangChainCallbackHandler(
    inspector=inspector,
    run_id="langchain_run_001"
)

# Use with any LangChain chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    callbacks=[callback]
)

result = qa_chain("What causes climate change?")
# Metrics automatically tracked!
```

## LangGraph Integration

```python
from raia.integrations.langgraph import stream_with_inspection

# Wrap LangGraph stream for automatic tracking
async for event in stream_with_inspection(
    graph.stream(...),
    inspector=inspector,
    run_id="langgraph_run_001"
):
    print(event)
# All metrics tracked automatically!
```

## Database Queries

```python
# Retrieve stored metrics
retrieval_metrics = inspector.get_retrieval_metrics("run_001")
answer_metrics = inspector.get_answer_quality("run_001")
attribution_maps = inspector.get_attribution_maps("run_001")
reasoning_traces = inspector.get_reasoning_traces("run_001")
scenarios = inspector.get_counterfactual_scenarios("run_001")

# Query historical data
from raia import SQLiteRAIAStorage

storage = SQLiteRAIAStorage("my_rag_eval.db")
all_runs = storage.list_runs()
run_metrics = storage.get_run("run_001")
```

## Monitoring & Dashboards

RAIA stores all metrics in SQLite, making it easy to:

1. **Query metrics programmatically**
2. **Build custom dashboards** (Grafana, Streamlit, etc.)
3. **Track performance over time**
4. **Compare configurations**
5. **Generate reports**

Example SQL query:
```sql
SELECT
    run_id,
    AVG(precision_at_k) as avg_precision,
    AVG(retrieval_latency_ms) as avg_latency
FROM raia_retrieval_metrics
WHERE created_at > datetime('now', '-7 days')
GROUP BY run_id;
```

## Next Steps

1. **Read the full documentation**: `docs/` directory
2. **Explore examples**: `examples/` directory
3. **Check tutorials**: `tutorials/` directory
4. **API Reference**: See docstrings in code

## Support

- 📖 Documentation: `docs/`
- 💬 Issues: GitHub Issues
- 📧 Email: support@example.com

## License

MIT License - see LICENSE file for details
