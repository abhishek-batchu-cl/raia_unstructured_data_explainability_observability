# RAIA - Complete Feature List

## 📋 Overview

RAIA (Responsible AI Analytics & Agent Evaluation) is a comprehensive evaluation framework providing:
- **Agent Evaluation** - Track execution, behavior, performance
- **RAG Evaluation** - Evaluate retrieval and generation quality
- **Explainability** - Attribution tracking and reasoning traces (like SHAP/LIME for AI)
- **What-If Analysis** - Counterfactual scenarios and optimization
- **Comparison & Reporting** - A/B/C testing and comprehensive reports

---

## 🎯 Core Modules

### 1. Agent Evaluation (`raia.inspectors`)

Complete agent lifecycle tracking and analysis.

#### **RAIAExecutionInspector**
Tracks agent execution and performance metrics.

**Features:**
- ✅ **Run tracking** - Start/end time, status, total latency
- ✅ **Node execution metrics** - Per-node latency, tokens, cost
- ✅ **LLM call tracking** - Token usage, cost, latency
- ✅ **Tool execution tracking** - Tool calls, success/failure
- ✅ **Error tracking** - Errors, retries, recovery
- ✅ **Task completion** - Goal achievement, completion rate
- ✅ **Streaming metrics** - Time-to-first-token, tokens/second

**Metrics Tracked:**
- Total latency (ms)
- Token usage (prompt + completion)
- Cost (USD)
- Success/failure status
- Error count & retry count
- Time-to-first-token
- Tokens per second
- Task completion rate

**Use Cases:**
- Performance monitoring
- Cost tracking
- Latency optimization
- Error analysis

---

#### **RAIABehaviorInspector**
Analyzes agent behavior patterns and decision quality.

**Features:**
- ✅ **Loop detection** - Identify infinite loops and redundant cycles
- ✅ **Redundancy analysis** - Detect duplicate tool calls
- ✅ **Path analysis** - Suboptimal path detection
- ✅ **Decision tracking** - Critical decision points
- ✅ **State transitions** - Agent state change tracking
- ✅ **Pattern detection** - Behavioral patterns over time

**Metrics Tracked:**
- Loop count & redundancy score
- Decision quality score
- Path efficiency score
- State transition count
- Pattern anomalies

**Use Cases:**
- Debugging agent behavior
- Optimizing agent graphs
- Detecting inefficiencies
- Quality assurance

---

#### **RAIASemanticInspector**
Evaluates semantic quality of outputs.

**Features:**
- ✅ **Semantic scoring** - Output quality evaluation
- ✅ **Custom evaluators** - Pluggable evaluation functions
- ✅ **LLM-based evaluation** - Use LLMs as judges
- ✅ **Multi-criteria scoring** - Relevance, coherence, accuracy
- ✅ **Historical tracking** - Quality trends over time

**Metrics Tracked:**
- Semantic quality score (0-1)
- Relevance score
- Coherence score
- Accuracy score
- Custom metric scores

**Use Cases:**
- Output quality assessment
- A/B testing for prompts
- Model comparison
- Quality regression testing

---

### 2. RAG Evaluation (`raia.inspectors.RAIARAGInspector`)

Complete RAG pipeline evaluation with retrieval and generation metrics.

#### **Retrieval Metrics**
Track document retrieval quality and performance.

**Methods:**
- `track_retrieval()` - Track retrieval metrics

**Metrics Tracked:**
- Number of documents retrieved
- Relevance scores per document
- Retrieval latency (ms)
- Precision@K
- Recall@K
- Mean Reciprocal Rank (MRR)
- NDCG (Normalized Discounted Cumulative Gain)

**Use Cases:**
- Evaluate retrieval quality
- Optimize vector search
- Compare embedding models
- A/B test retrieval strategies

---

#### **Answer Quality Metrics**
Evaluate generated answer quality and faithfulness.

**Methods:**
- `track_answer_quality()` - Track answer quality metrics

**Metrics Tracked:**
- Answer relevance (how relevant to query)
- Answer completeness (covers all aspects)
- Answer faithfulness (grounded in context)
- Hallucination score (unsupported content)
- Generation latency (ms)
- Conciseness score
- Clarity score

**Use Cases:**
- Evaluate LLM output quality
- Detect hallucinations
- Compare prompts/models
- Quality monitoring

---

#### **Vector Index Health**
Monitor vector database health and performance.

**Methods:**
- `track_index_health()` - Track vector index metrics

**Metrics Tracked:**
- Total document count
- Index size (bytes)
- Average vector dimensionality
- Index build time
- Query latency (ms)
- Memory usage
- Index freshness

**Use Cases:**
- Monitor vector DB performance
- Capacity planning
- Performance optimization
- Health monitoring

---

#### **Pipeline Metrics**
End-to-end RAG pipeline tracking.

**Methods:**
- `track_pipeline()` - Track complete pipeline execution

**Metrics Tracked:**
- Total pipeline latency
- Retrieval time
- Generation time
- Post-processing time
- Total cost
- Success/failure status

**Use Cases:**
- End-to-end performance monitoring
- Bottleneck identification
- Cost tracking
- SLA monitoring

---

### 3. Explainability Features (NEW!)

Adapted from SHAP/LIME for RAG and Agentic AI.

#### **Attribution Tracking**
Like SHAP for RAG - which documents influenced which answer parts.

**Methods:**
- `track_attribution()` - Track document → answer mappings

**Data Models:**
- `Attribution` - Single attribution (answer span → source document)
- `RAIAAttributionMap` - Complete attribution map

**Metrics Tracked:**
- Attributions (document → answer span mappings)
- Overall confidence
- Faithfulness score
- Hallucination score
- Context efficiency (% context used)
- Unique sources used
- Primary source identification

**Features:**
- ✅ Span-level attribution (character offsets)
- ✅ Confidence scores per attribution
- ✅ Similarity scores
- ✅ Context efficiency tracking
- ✅ Primary source identification

**Use Cases:**
- Explain where answers come from
- Identify unused context
- Detect hallucinations
- Improve context selection

---

#### **Reasoning Traces**
Like LIME for agents - step-by-step process explanation.

**Methods:**
- `track_reasoning()` - Track step-by-step reasoning

**Data Models:**
- `ReasoningStep` - Single reasoning step
- `RAIAReasoningTrace` - Complete reasoning trace

**Metrics Tracked:**
- Reasoning steps (ordered list)
- Per-step latency and success
- Reasoning quality score
- Logical consistency
- Total steps
- Successful/failed steps
- Bottleneck step identification

**Step Information:**
- Step number, name, type
- Description and rationale
- Confidence score
- Inputs and outputs
- Start/end time
- Latency
- Success/failure

**Use Cases:**
- Debug agent reasoning
- Understand decision process
- Identify bottlenecks
- Quality assurance

---

#### **Agent Decision Tracking**
Track critical decision points in agent execution.

**Methods:**
- `track_agent_decision()` - Track agent decisions

**Data Models:**
- `AlternativeAction` - Alternative action considered
- `RAIAAgentDecision` - Complete decision record

**Metrics Tracked:**
- Decision type (tool, path, strategy)
- Action taken
- Alternatives considered
- Decision confidence
- Rationale
- Decision latency

**Use Cases:**
- Understand agent choices
- Evaluate decision quality
- Compare alternatives
- Improve decision logic

---

### 4. What-If Analysis (NEW!)

Counterfactual scenario simulation and optimization.

#### **Counterfactual Scenarios**
Simulate "What would happen if we changed X?"

**Methods:**
- `simulate_scenario()` - Simulate configuration changes

**Data Models:**
- `RAIACounterfactualScenario` - Complete scenario analysis

**Scenario Types (8 types):**
1. **retrieval** - Different document selection
2. **context** - More/less context
3. **tool_selection** - Different tools
4. **agent_path** - Different graph paths
5. **parameter** - Hyperparameter changes
6. **drift_simulation** - Embedding drift impact
7. **cost_optimization** - Cost reduction strategies
8. **quality_optimization** - Quality improvement strategies

**Metrics Calculated:**
- Quality delta (% change)
- Latency delta (% change)
- Cost delta (% change)
- Improvement flag
- Recommendation (adopt/reject/test_further/conditional)
- Recommendation rationale
- Confidence score
- Pros and cons

**Use Cases:**
- Proactive optimization
- Cost reduction
- Quality improvement
- Risk-free experimentation

---

#### **Parameter Sensitivity Analysis**
Understand which parameters have the most impact.

**Data Models:**
- `ParameterSensitivity` - Single parameter impact
- `RAIASensitivityAnalysis` - Complete analysis

**Metrics Tracked:**
- Parameter name and value range
- Sensitivity score (0-1)
- Impact on quality/latency/cost
- Most/least sensitive parameters
- Suggested tuning ranges

**Use Cases:**
- Identify critical parameters
- Focus optimization efforts
- Understand parameter interactions
- Guide hyperparameter tuning

---

#### **Optimization Recommendations**
AI-powered actionable recommendations.

**Data Models:**
- `RAIAOptimizationRecommendation`

**Recommendation Types:**
- Cost reduction
- Quality improvement
- Latency reduction
- Resource optimization
- Safety enhancement

**Information Provided:**
- Recommendation description
- Expected improvement (%)
- Implementation effort
- ROI estimate
- Priority (high/medium/low)
- Confidence score

**Use Cases:**
- Automated optimization suggestions
- Prioritize improvements
- ROI analysis
- Continuous improvement

---

### 5. Comparison & Reporting

Multi-run comparison and comprehensive reporting.

#### **Run Comparison**
A/B/C testing across configurations.

**Methods:**
- `compare_runs()` - Compare multiple runs side-by-side
- `print_comparison()` - Pretty print comparison results

**Data Models:**
- `RunComparison`

**Features:**
- ✅ Side-by-side metrics comparison
- ✅ Winner determination (quality/latency/cost)
- ✅ Overall winner with weighted scoring
- ✅ Variance analysis
- ✅ Winner rationale

**Metrics Compared:**
- Average quality
- Average latency
- Average cost
- Best run per dimension
- Overall winner

**Use Cases:**
- A/B/C testing
- Configuration comparison
- Model selection
- Prompt optimization

---

#### **Evaluation Reports**
Comprehensive evaluation reports with insights.

**Methods:**
- `generate_report()` - Generate comprehensive report
- `print_report()` - Pretty print report

**Data Models:**
- `EvaluationReport`

**Report Sections:**
- Summary metrics (quality, latency, cost)
- Quality breakdown (excellent/good/poor)
- Explainability metrics (faithfulness, hallucination)
- Strengths analysis
- Weaknesses analysis
- Optimization opportunities
- Actionable recommendations

**Use Cases:**
- Executive summaries
- Quality assurance reports
- Performance reviews
- Stakeholder communication

---

#### **Batch Evaluation**
Evaluate multiple runs in batch.

**Data Models:**
- `BatchEvaluationResult`

**Features:**
- ✅ Multi-run processing
- ✅ Aggregate statistics
- ✅ Winner determination across batches

**Use Cases:**
- Large-scale testing
- Regression testing
- Continuous monitoring
- Benchmark creation

---

## 🗄️ Storage & Persistence

### SQLite Storage (`raia.storage.SQLiteRAIAStorage`)

Complete SQLite-based storage with 15 tables.

#### **Core Tables:**
1. **raia_runs** - Run metadata
2. **raia_node_metrics** - Per-node execution metrics
3. **raia_functional_signals** - Tool/LLM call tracking
4. **raia_semantic_scores** - Semantic quality scores

#### **RAG Tables:**
5. **raia_retrieval_metrics** - Retrieval metrics
6. **raia_answer_quality_metrics** - Answer quality
7. **raia_vector_index_health** - Index health
8. **raia_pipeline_metrics** - Pipeline metrics
9. **raia_embedding_drift_metrics** - Embedding drift

#### **Explainability Tables:**
10. **raia_attribution_maps** - Attribution tracking
11. **raia_reasoning_traces** - Reasoning traces
12. **raia_agent_decisions** - Agent decisions

#### **What-If Tables:**
13. **raia_counterfactual_scenarios** - What-if scenarios
14. **raia_sensitivity_analyses** - Parameter sensitivity
15. **raia_optimization_recommendations** - Recommendations

**Features:**
- ✅ Foreign key constraints
- ✅ Indexes for performance
- ✅ JSON storage for complex data
- ✅ Automatic schema creation
- ✅ Query methods for all tables
- ✅ Batch operations
- ✅ Transaction support

**Use Cases:**
- Local development
- Prototyping
- Small-scale deployments
- Offline analysis

---

### Extensible Storage Interface (`raia.storage.BaseRAIAStorage`)

Abstract base class for custom storage backends.

**Supported (planned):**
- SQLite (implemented)
- PostgreSQL (interface ready)
- MongoDB (interface ready)
- Cloud storage (S3, GCS)
- Custom backends

---

## 🔌 Integrations

### LangChain Integration (`raia.integrations.langchain`)

Seamless LangChain callback integration.

**Features:**
- ✅ `LangChainCallbackHandler` - Auto-track LangChain chains
- ✅ Automatic metric extraction
- ✅ Chain lifecycle tracking
- ✅ LLM call tracking
- ✅ Tool call tracking

**Usage:**
```python
from raia.integrations import LangChainCallbackHandler

callback = LangChainCallbackHandler(
    inspector=inspector,
    run_id="my_run"
)

chain.invoke(input, config={"callbacks": [callback]})
```

---

### LangGraph Integration (`raia.integrations.langgraph`)

LangGraph stream inspection and tracking.

**Features:**
- ✅ `stream_with_inspection()` - Wrap LangGraph streams
- ✅ Automatic event tracking
- ✅ Node execution tracking
- ✅ State transition tracking
- ✅ Real-time metrics

**Usage:**
```python
from raia.integrations import stream_with_inspection

async for event in stream_with_inspection(
    graph.stream(...),
    inspector=inspector,
    run_id="my_run"
):
    print(event)
```

---

## 📊 Data Models

### Core Models (`raia.models`)
- `RAIARun` - Run metadata
- `RAIANodeMetrics` - Node execution metrics
- `RAIAFunctionalSignal` - Tool/LLM call data
- `RAIASemanticScore` - Semantic quality scores

### RAG Models (`raia.models_rag`)
- `RAIARetrievalMetrics` - Retrieval metrics
- `RAIAAnswerQualityMetrics` - Answer quality
- `RAIAVectorIndexHealth` - Index health
- `RAIAPipelineMetrics` - Pipeline metrics
- `RAIAEmbeddingDriftMetrics` - Embedding drift

### Explainability Models (`raia.models_explainability`)
- `Attribution` - Single attribution
- `RAIAAttributionMap` - Complete attribution map
- `ReasoningStep` - Single reasoning step
- `RAIAReasoningTrace` - Reasoning trace
- `AlternativeAction` - Alternative action
- `RAIAAgentDecision` - Agent decision

### What-If Models (`raia.models_whatif`)
- `RAIACounterfactualScenario` - What-if scenario
- `ParameterSensitivity` - Parameter impact
- `RAIASensitivityAnalysis` - Sensitivity analysis
- `RAIAOptimizationRecommendation` - Recommendation

### Comparison Models (`raia.models_comparison`)
- `RunComparison` - Run comparison
- `EvaluationReport` - Evaluation report
- `BatchEvaluationResult` - Batch results

All models use **Pydantic v2** for type safety and validation.

---

## 🎯 Key Differentiators

### vs Traditional ML Explainability (SHAP/LIME)
- **SHAP** explains static predictions → **RAIA Attribution** explains dynamic RAG processes
- **LIME** explains local decisions → **RAIA Reasoning** explains multi-step agent reasoning
- **Feature importance** is fixed → **Document attribution** changes per query

### vs Existing RAG Tools
- **LangSmith**: Post-hoc traces → **RAIA**: Real-time explainability + what-if
- **LangFuse**: Observability only → **RAIA**: Observability + optimization + recommendations
- **Arize**: Model monitoring → **RAIA**: Full agent lifecycle with counterfactual analysis

### What Makes RAIA Unique
1. **First framework** to map documents to answer spans (attribution)
2. **Only tool** with counterfactual scenario simulation for RAG
3. **Integrated workflow**: Explainability + optimization + comparison in one framework
4. **AI-powered recommendations** with confidence scores
5. **Production-ready**: SQLite storage, LangChain/LangGraph integration, Docker support

---

## 📚 Quick Reference

### Installation
```bash
pip install -e .
```

### Quick Start
```python
from raia import RAIARAGInspector, SQLiteRAIAStorage

storage = SQLiteRAIAStorage("my_eval.db")
inspector = RAIARAGInspector(storage=storage)
```

### Demos
- `demo_quickstart.py` - 2-minute intro
- `demo_complete.py` - Complete workflow
- `demo_explainability.py` - Explainability features
- `demo_whatif.py` - What-if analysis
- `examples/realistic_rag_evaluation.py` - Production example

### Documentation
- `README.md` - Main entry point
- `QUICKSTART.md` - Quick start guide
- `docs/DELIVERY_SUMMARY.md` - Complete implementation
- `docs/UNIFIED_LIBRARY_README.md` - Unified library guide
- `docs/DOCKER_SETUP.md` - Docker deployment

---

## 🎉 Summary

RAIA provides **everything you need** for production agent and RAG evaluation:

✅ **22+ canonical metrics** across execution, behavior, RAG, and quality
✅ **Explainability** (attribution + reasoning traces)
✅ **What-If Analysis** (8 scenario types + optimization)
✅ **Comparison & Reporting** (A/B/C testing + comprehensive reports)
✅ **Storage** (SQLite with 15 tables)
✅ **Integrations** (LangChain + LangGraph)
✅ **Production-ready** (Docker, tests, documentation)

**Total Capabilities:**
- 5 Inspector modules
- 15 tracking methods
- 20+ data models
- 15 database tables
- 8 what-if scenario types
- 2 framework integrations
- 4 demo scripts
- Complete documentation

🚀 Ready for production use!
