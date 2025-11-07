# RAIA - Responsible AI Analytics & Agent Evaluation

## 🚀 Quick Start (2 Minutes)

```bash
# 1. Run the automated setup
./quickstart.sh

# That's it! The script will:
# ✅ Install RAIA SDK
# ✅ Start ingestion service
# ✅ Run a demo agent
# ✅ Collect events and compute metrics
```

**For detailed LangGraph integration**, see [TUTORIAL.md](TUTORIAL.md) — a complete walkthrough showing how to instrument your agent.

**What you get:**
- 📊 22 canonical metrics (success rate, latency, cost, etc.)
- 🔍 Complete event trace for every agent run
- 📈 Real-time observability via Prometheus/Grafana
- 🔒 Enterprise security (encryption, redaction, RBAC)

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
