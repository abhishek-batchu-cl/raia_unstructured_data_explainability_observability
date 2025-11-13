# RAIA - Responsible AI Analytics & Agent Evaluation

## ⚡ NEW: RAG Explainability & What-If Analysis

RAIA now includes advanced RAG evaluation features adapted from traditional ML explainability:

```bash
# 2-minute demo showing all features
python3 demo_quickstart.py

# Or use the quickstart script
./quickstart.sh
```

**What's included:**

🔍 **Explainability** (like SHAP/LIME for RAG)
- Attribution tracking: Which documents influenced which answer parts
- Reasoning traces: Step-by-step process capture
- Faithfulness & hallucination detection

🎯 **What-If Analysis** (counterfactual optimization)
- Simulate configuration changes before implementing
- Cost vs quality trade-off analysis
- Automatic recommendations with confidence scores

📊 **Comparison & Reporting**
- A/B/C testing across configurations
- Winner determination with rationale
- Comprehensive evaluation reports

**Quick Example:**
```python
from raia import RAIARAGInspector, SQLiteRAIAStorage

# Initialize
storage = SQLiteRAIAStorage("my_rag.db")
inspector = RAIARAGInspector(storage=storage)

# Track explainability
inspector.track_attribution(
    run_id="run_001",
    query="What causes climate change?",
    answer="Greenhouse gas emissions...",
    attributions=[...],  # Document → answer mappings
    faithfulness_score=0.97,
    hallucination_score=0.03,
)

# Run what-if analysis
scenario = inspector.simulate_scenario(
    run_id="run_001",
    scenario_name="Reduce context for cost savings",
    scenario_type="context",
    original_config={"context_tokens": 2000},
    alternative_config={"context_tokens": 1200},
    original_quality=0.93,
    original_cost_usd=0.015,
    alternative_quality=0.90,
    alternative_cost_usd=0.009,
)

print(f"Recommendation: {scenario.recommendation}")
print(f"Cost savings: {scenario.cost_delta_pct:.1f}%")
```

**📖 See [QUICKSTART.md](QUICKSTART.md) for complete RAG evaluation guide**

---

## 🚀 Quick Start - Unified Library (2 Minutes)

### NEW: All RAIA functionality is now in one unified package!

```bash
# Install the unified library
pip install -e .

# Use both event logging and behavioral analysis
from raia import (
    # Event Logging (production telemetry)
    EventEmitter, EmitterConfig,
    # Behavioral Analysis (performance metrics)
    RAIAExecutionInspector, RAIABehaviorInspector,
    # Storage
    SQLiteRAIAStorage,
    # Integrations
    LangChainCallbackHandler, stream_with_inspection,
)
```

### Docker Quick Start (Cross-Platform)
```bash
# Mac/Linux
./run.sh build && ./run.sh test

# Windows
run.bat build
run.bat test
```

**What you get:**
- 📊 22 canonical metrics (success rate, latency, cost, safety)
- 🔍 Complete event trace for every agent run
- ⚡ Real-time performance metrics (latency, tokens, cost)
- 🔁 Loop detection and redundancy analysis
- 📈 Observability via Prometheus/Grafana
- 🔒 Enterprise security (encryption, PII redaction, RBAC)

**📚 See [UNIFIED_LIBRARY_README.md](UNIFIED_LIBRARY_README.md) for complete unified library guide**

---

## 🎯 RAIA - Two Complementary Systems, One Package

The unified `raia` package provides two complementary systems:

### 1. Event Logging (`raia.events`)
**Purpose**: Production telemetry, compliance, audit trails

- Async batching with circuit breaker
- Multiple transports (file, HTTP, Kafka, OTLP)
- PII/PHI redaction and HMAC signing
- Deterministic replay capabilities

**Use for**: Compliance, audit trails, event sourcing (**WHAT** happened)

### 2. Behavioral Analysis (`raia.inspectors`)
**Purpose**: Performance optimization, quality analysis

- Per-node execution metrics (latency, tokens, cost)
- Pattern detection (loops, redundancy, suboptimal paths)
- Semantic quality evaluation framework
- SQLite-based queryable storage

**Use for**: Performance analysis, debugging (**HOW WELL** it happened)

### Using Both Together
```python
from raia import EventEmitter, EmitterConfig, RAIAExecutionInspector, SQLiteRAIAStorage
from raia.integrations import create_unified_callback

# Setup both systems
emitter = EventEmitter(EmitterConfig.from_env())
storage = SQLiteRAIAStorage("metrics.db")
await emitter.start()

# Create unified callback
callbacks = create_unified_callback(
    emitter=emitter,
    storage=storage,
    agent_name="my-agent",
    use_events=True,
    use_inspectors=True,
)

# Use in your agent
result = chain.invoke(input, config={"callbacks": callbacks})
```

**Learn More:**
- 📖 [Unified Library Guide](UNIFIED_LIBRARY_README.md) - Complete guide for the unified package
- 🆚 [Framework Comparison](FRAMEWORK_COMPARISON.md) - vs LangSmith, LangFuse, Arize, etc.
- 💡 [Why RAIA?](WHY_RAIA_INSPECTORS.md) - Visual examples and use cases
- 🐳 [Docker Guide](DOCKER_GUIDE.md) - Cross-platform Docker setup

---

## Concept & Scope

**RAIA (Responsible AI Analytics & Agent Evaluation)** is a standardized, logging-first, production-grade evaluation framework for agentic systems (e.g., LangChain/LangGraph agents) designed to work across regulated and unregulated domains including healthcare, insurance, banking, retail, and public sector. Unlike post-hoc evaluation frameworks that analyze only final outputs, RAIA captures structured runtime events at every stage of agent execution—planning, tool selection, observations, critiques, corrections, and escalations—enabling deep introspection into agent behavior, reliability, safety, and efficiency.

The framework follows a library-first architecture where developers embed a lightweight instrumentation SDK into their agents to emit standardized events. These events flow through a secure, scalable ingestion pipeline into durable storage (NDJSON files, S3, Postgres, Kafka), where they can be replayed deterministically to compute canonical metrics. The system is designed with enterprise requirements at its core: encryption at rest and in transit, PII/PHI redaction, RBAC, tenant isolation, audit trails, data residency controls, GDPR/CCPA compliance hooks, and comprehensive observability via Prometheus/OpenTelemetry.

### Architecture Overview

```
┌─────────────────┐
│  Agent Runtime  │
│  (LangChain/    │
│   LangGraph)    │
└────────┬────────┘
         │ SDK (Python/TS)
         │ • Batching
         │ • Redaction
         │ • HMAC Signing
         │ • Circuit Breaker
         ▼
┌─────────────────────────────────────────┐
│         Ingestion Service               │
│  • FastAPI / HTTP / Kafka / OTLP        │
│  • Auth (API Key, HMAC, mTLS)           │
│  • Validation & Tenant Routing          │
│  • Prometheus Metrics                   │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│            Storage Layer                │
│  • NDJSON (local/S3)                    │
│  • Postgres (structured queries)        │
│  • Kafka (streaming)                    │
│  • Encryption at rest (AES-256)         │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│       Replay & Compute Engine           │
│  • Deterministic metric calculation     │
│  • Versioned schemas & prompts          │
│  • CSV/Parquet export                   │
│  • CI/CD quality gates                  │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│    Dashboards, Alerts & Analytics       │
│  • Grafana / Prometheus                 │
│  • SLO tracking & error budgets         │
│  • Domain KPI packs                     │
└─────────────────────────────────────────┘
```

### Goals
- **Runtime Observability**: Capture every agent decision point, not just final answers
- **Standardization**: Interoperable event schema and canonical metric set across all agents
- **Security & Compliance**: Enterprise-grade encryption, redaction, RBAC, audit trails, retention policies
- **Reproducibility**: Versioned schemas, deterministic replay, seed tracking
- **Operational Readiness**: SLOs, alerts, capacity planning, backpressure, disaster recovery
- **Library-First**: Embeddable SDK with minimal overhead (<2ms p50, <10ms p95)
- **Provider Agnostic**: Works with any LLM, storage backend, or observability platform

### Non-Goals
- Model leaderboards or judge-LLM scoring systems
- Subjective rubric design (can be layered on top)
- Vendor lock-in to specific clouds or databases

### Key Differentiators
1. **Logging-First**: All metrics derived from structured runtime logs, not post-hoc analysis
2. **Compliance-Ready**: Built-in PII/PHI redaction, data residency, retention, GDPR hooks
3. **Production-Grade**: Async I/O, batching, retries, circuit breakers, health checks, graceful shutdown
4. **Cross-Domain**: Generic core with domain-specific KPI packs (healthcare, finance, retail)
5. **Deterministic Replay**: Seed tracking and time normalization for reproducible evaluations
6. **Zero Trust**: HMAC-signed events, encrypted storage, RBAC, tenant isolation

## Performance Targets
- **SDK Overhead**: <2ms p50, <10ms p95 per event
- **Ingestion Throughput**: ≥5,000 events/sec per pod (2 vCPU)
- **Replay & Compute**: ≥200,000 events/minute single node
- **Latency SLO**: p95 ingest-to-storage <500ms
- **Availability**: 99.9% uptime (8.76h downtime/year)

## Quick Start
See [docs/quickstart.md](docs/quickstart.md) for integration guide.
