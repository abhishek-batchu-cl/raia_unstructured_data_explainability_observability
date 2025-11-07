# Getting Started with RAIA

## For New Users: 3 Ways to Get Started

### Option 1: Fastest - Automated Demo (2 minutes)

```bash
./quickstart.sh
```

This script:
- ✅ Installs everything
- ✅ Starts services
- ✅ Runs a demo
- ✅ Shows you metrics

**Best for**: First-time users who want to see it working immediately.

---

### Option 2: Tutorial - LangGraph Integration (15 minutes)

```bash
# Read the tutorial
cat TUTORIAL.md

# Then follow along step-by-step
```

**Best for**: Developers integrating RAIA into their LangGraph agents.

**What you'll learn**:
- How to install and configure the SDK
- How to emit events from your agent
- How events flow through the system
- How to view and analyze metrics

---

### Option 3: Production - Full Deployment (1 hour)

1. Read architecture: `README.md`
2. Set up security: `docs/security_compliance.md`
3. Deploy to Kubernetes: `deploy/kubernetes/`
4. Configure monitoring: `observability/`

**Best for**: Production deployments in enterprise environments.

---

## How It Works (30-second version)

```python
# 1. Install SDK
pip install raia

# 2. Add to your agent
from raia import EventEmitter, EmitterConfig

emitter = EventEmitter(EmitterConfig(
    tenant="your-company",
    project="your-project",
    agent_id="your-agent",
    endpoint="http://localhost:8000/ingest"
))

# 3. Emit events
emitter.emit({"event": "session_start", "task": "..."})
emitter.emit({"event": "tool_call", "tool_name": "search", ...})
emitter.emit({"event": "finalized", "success": True})

# 4. Get metrics
# python tools/replay_compute.py events.ndjson
# → 22 metrics automatically computed
```

See [HOW_IT_WORKS.md](HOW_IT_WORKS.md) for detailed flow.

---

## Integration Checklist

When integrating RAIA into your agent:

### Minimal Integration (5 events)
- [ ] `session_start` - When task begins
- [ ] `tool_call` - Before each tool use
- [ ] `observation` - After each tool returns
- [ ] `finalized` - When task completes
- [ ] Add `success: bool` to finalized

### Standard Integration (7 events)
- [ ] All minimal events (above)
- [ ] `plan_created` - When agent creates a plan
- [ ] `error` - On unrecoverable errors

### Full Integration (10 events)
- [ ] All standard events (above)
- [ ] `critique` - When agent self-reflects
- [ ] `correction` - When agent backtracks
- [ ] `escalation` - When escalating to humans
- [ ] `policy_flag` - When safety checks trigger

### Quality Enhancements
- [ ] Add `evidence_refs` to observations (for grounding metrics)
- [ ] Add `expected_tool` to tool_calls (for wrong tool detection)
- [ ] Add `constraints` to session_start (for adherence tracking)
- [ ] Add `latency_ms` to all events (for performance metrics)
- [ ] Add `token_usage` and `cost` (for efficiency metrics)

---

## File Guide

**Start Here**:
- `README.md` - Framework overview
- `quickstart.sh` - One-command demo
- `TUTORIAL.md` - Hands-on LangGraph walkthrough
- `HOW_IT_WORKS.md` - Visual flow diagram

**Schemas & Config**:
- `schemas/event_schema.json` - Event definitions
- `schemas/event_examples.ndjson` - Example events
- `config/metrics_config.json` - Metric definitions

**SDK Code**:
- `sdk/python/raia/` - Python SDK
- `sdk/typescript/src/` - TypeScript SDK

**Services**:
- `services/ingestion/` - Ingestion service
- `tools/replay_compute.py` - Metrics computation

**Operations**:
- `observability/` - Prometheus alerts, SLO definitions
- `deploy/kubernetes/` - K8s manifests
- `docs/` - Detailed documentation

**Reference**:
- `VERIFICATION.md` - Working examples & verification
- `docs/canonical_metrics.md` - All 22 metrics explained
- `docs/security_compliance.md` - Security & compliance guide
- `docs/deployment_scaling.md` - Scaling strategies

---

## Common Questions

### Q: Do I need to install Postgres/Kafka?
**A**: No! For development, use file storage:
```bash
export RAIA_STORAGE_BACKEND=file
export RAIA_FILE_PATH=/tmp/events.ndjson
```

For production, Postgres or Kafka are recommended.

### Q: How much overhead does the SDK add?
**A**: ~1-2ms per event (p50), amortized to <0.1ms with batching.

### Q: Can I use this without LangChain/LangGraph?
**A**: Yes! The SDK is framework-agnostic. Just emit events:
```python
emitter.emit({"event": "session_start", ...})
```

### Q: How do I secure this for production?
**A**: Enable authentication and signing:
```python
config = EmitterConfig(
    ...,
    api_key="your-api-key",
    hmac_secret="your-secret",
    enable_signing=True
)
```

See `docs/security_compliance.md` for full guide.

### Q: What if my agent doesn't use tools?
**A**: That's fine! Just emit the events relevant to your agent:
- session_start
- plan_created (if you plan)
- finalized

### Q: How do I view metrics in real-time?
**A**: Set up Prometheus + Grafana:
```bash
cd observability
docker-compose up -d
# Open http://localhost:3000
```

Use queries from `observability/grafana_dashboard_queries.md`.

### Q: Can I add custom metrics?
**A**: Yes! The replay tool can be extended. Or query events directly:
```python
import json

with open('events.ndjson') as f:
    events = [json.loads(line) for line in f]

# Your custom metric
custom_metric = len([e for e in events if e['event'] == 'my_custom_event'])
```

### Q: Does this work with OpenAI, Anthropic, etc.?
**A**: Yes! RAIA is LLM-agnostic. Just set:
```python
config = EmitterConfig(
    ...,
    llm="anthropic/claude-3-opus",
    llm_version="2024-01-01"
)
```

---

## Support & Contributing

- **Issues**: Report at [GitHub Issues](https://github.com/your-org/raia/issues)
- **Docs**: All docs in `docs/` directory
- **Examples**: See `sdk/*/examples/`

---

## Next Steps

1. ✅ Run `./quickstart.sh` to see it working
2. ✅ Read `TUTORIAL.md` for LangGraph integration
3. ✅ Integrate into your agent (use checklist above)
4. ✅ Compute metrics: `python tools/replay_compute.py`
5. ✅ Set up monitoring (optional): `observability/`
6. ✅ Review security: `docs/security_compliance.md`

**Questions?** Check `HOW_IT_WORKS.md` for visual explanations!

---

## Quick Reference Card

```python
# === RAIA Quick Reference ===

# Setup
from raia import EventEmitter, EmitterConfig
config = EmitterConfig(tenant="co", project="proj", agent_id="agent-v1", endpoint="http://localhost:8000/ingest")
emitter = EventEmitter(config)
await emitter.start()

# Common Events
emitter.emit({"event": "session_start", "session_id": sid, "run_id": rid, "agent_id": aid, "task": "...", "domain": "general", "env": {}})
emitter.emit({"event": "plan_created", "session_id": sid, "run_id": rid, "agent_id": aid, "plan": {"steps": [...]}, "plan_depth": 3, "env": {}})
emitter.emit({"event": "tool_call", "session_id": sid, "run_id": rid, "agent_id": aid, "tool_name": "search", "tool_args": {}, "is_retry": False, "env": {}})
emitter.emit({"event": "observation", "session_id": sid, "run_id": rid, "agent_id": aid, "observation": "...", "success": True, "grounded": True, "env": {}})
emitter.emit({"event": "finalized", "session_id": sid, "run_id": rid, "agent_id": aid, "success": True, "constraints_met": True, "env": {}})

# Shutdown
await emitter.flush()
await emitter.shutdown()

# Compute Metrics
# python tools/replay_compute.py events.ndjson --metrics-config config/metrics_config.json --output-csv metrics.csv
```

Print this out and keep it handy! 📋
