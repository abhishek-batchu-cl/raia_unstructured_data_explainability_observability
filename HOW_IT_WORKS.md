# How RAIA Works: From Agent Code to Metrics

## Visual Overview

```
┌─────────────────────────────────────────────────────────────────┐
│ YOUR LANGGRAPH AGENT                                            │
│                                                                 │
│  def my_agent():                                               │
│      emitter.emit({"event": "session_start", ...})  ←─────┐   │
│                                                            │   │
│      # Plan                                                │   │
│      emitter.emit({"event": "plan_created", ...})         │   │
│                                                            │   │
│      # Use tools                                           │   │
│      result = search_tool("query")                         │   │
│      emitter.emit({"event": "tool_call", ...})            RAIA
│      emitter.emit({"event": "observation", ...})           SDK
│                                                            │   │
│      # Return answer                                       │   │
│      emitter.emit({"event": "finalized", ...})            │   │
│                                                            │   │
└─────────────────────────────────────────────────────────┘   │
                                                               │
                    ┌──────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ AUTOMATIC PROCESSING                                            │
│                                                                 │
│  1. Batch Events (100 events or 1MB)                          │
│  2. Redact PII/PHI (emails, SSN, etc.)                        │
│  3. Sign with HMAC (tamper detection)                         │
│  4. Send to Ingestion Service                                 │
└─────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ INGESTION SERVICE (http://localhost:8000)                      │
│                                                                 │
│  1. Validate API key & signature                              │
│  2. Check against JSON schema                                 │
│  3. Store in database/file                                    │
│  4. Expose Prometheus metrics                                 │
└─────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ STORAGE (events.ndjson or Postgres)                           │
│                                                                 │
│  {"event":"session_start","task":"Answer question",...}       │
│  {"event":"plan_created","plan":{"steps":[...]},...}          │
│  {"event":"tool_call","tool_name":"search",...}               │
│  {"event":"observation","observation":"Result...",...}        │
│  {"event":"finalized","success":true,...}                     │
└─────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ METRICS COMPUTATION                                             │
│                                                                 │
│  python replay_compute.py events.ndjson                        │
│                                                                 │
│  Computes:                                                     │
│  ✓ Task Success Rate: 95%                                     │
│  ✓ Escalation Rate: 5%                                        │
│  ✓ P95 Latency: 2.3s                                          │
│  ✓ Cost per Success: $0.02                                    │
│  ✓ Wrong Tool Rate: 3%                                        │
│  ... 17 more metrics                                          │
└─────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ VISUALIZATION                                                   │
│                                                                 │
│  CSV/Parquet → Grafana Dashboard → Alerts                     │
│                                                                 │
│  [📊 Success Rate: 95% ✓]  [⚡ P95 Latency: 2.3s]            │
│  [💰 Cost: $0.02/task]     [⚠️  Escalations: 5%]              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Step-by-Step: What Happens Behind the Scenes

### 1. You Write Your Agent (5 lines of RAIA code)

```python
from raia import EventEmitter, EmitterConfig

# Setup (once)
config = EmitterConfig(
    tenant="your-company",
    project="your-project",
    agent_id="your-agent-v1.0",
    endpoint="http://localhost:8000/ingest"
)
emitter = EventEmitter(config)
await emitter.start()

# In your agent code (emit events as you go)
emitter.emit({"event": "session_start", "task": "...", ...})
emitter.emit({"event": "tool_call", "tool_name": "search", ...})
emitter.emit({"event": "finalized", "success": True, ...})
```

### 2. SDK Processes Events (Automatic)

**Batching**:
- Collects up to 100 events OR 1MB before sending
- Flushes every 5 seconds even if batch not full
- Reduces network overhead by 100x

**Redaction** (if configured):
```python
redactor = Redactor.for_domain('healthcare')
emitter = EventEmitter(config, redactor=redactor)

# Automatically redacts:
# john@example.com → [EMAIL_REDACTED]
# SSN 123-45-6789 → [SSN_REDACTED]
# Patient MRN-123456 → [MRN_REDACTED]
```

**Signing** (prevents tampering):
```python
signer = EventSigner(secret="your-hmac-secret")
emitter = EventEmitter(config, signer=signer)

# Each event gets: _signature: "a3f7b2c..."
```

**Circuit Breaker** (resilience):
- If ingestion fails 5 times → open circuit
- Falls back to local file
- Auto-recovers after 30 seconds

### 3. Ingestion Service Receives Events

**Request**:
```bash
POST http://localhost:8000/ingest
Content-Type: application/x-ndjson
Authorization: Bearer your-api-key

{"event":"session_start","session_id":"abc-123",...}
{"event":"tool_call","session_id":"abc-123",...}
...
```

**Processing**:
1. ✅ Validate API key
2. ✅ Verify HMAC signature
3. ✅ Check JSON schema
4. ✅ Write to storage
5. ✅ Update Prometheus metrics

**Response**:
```json
{"accepted": 10, "rejected": 0}
```

### 4. Events Are Stored

**NDJSON Format** (one event per line):
```
{"event":"session_start","event_id":"550e8400...","ts":"2025-01-15T10:30:00Z","session_id":"650e8400...","agent_id":"my-agent","task":"What is 2+2?","domain":"general","env":{"tenant":"acme","project":"demo"}}
{"event":"tool_call","event_id":"650e8400...","ts":"2025-01-15T10:30:01Z","session_id":"650e8400...","tool_name":"calculator","tool_args":{"expr":"2+2"},"latency_ms":45}
{"event":"finalized","event_id":"750e8400...","ts":"2025-01-15T10:30:02Z","session_id":"650e8400...","success":true,"total_steps":2,"latency_ms":2000}
```

**Or Postgres**:
```sql
SELECT event_type, COUNT(*)
FROM raia_events
WHERE tenant='acme'
GROUP BY event_type;

-- event_type     | count
-- session_start  |   100
-- tool_call      |   350
-- finalized      |   100
```

### 5. You Compute Metrics

```bash
python tools/replay_compute.py \
  events.ndjson \
  --metrics-config config/metrics_config.json \
  --output-csv metrics.csv
```

**What It Computes**:

| Metric | Formula | Result |
|--------|---------|--------|
| Task Success Rate | (successful finalized / total finalized) × 100 | 95% |
| Escalation Rate | (sessions with escalation / total sessions) × 100 | 5% |
| P95 Latency | 95th percentile of (finalized.ts - session_start.ts) | 2300ms |
| Wrong Tool Rate | (tool_calls with wrong tool / total tool_calls) × 100 | 3% |
| Cost per Success | SUM(cost) / COUNT(successful finalized) | $0.02 |

### 6. You View Results

**CSV**:
```csv
task_success_rate,escalation_rate,p95_latency,cost_per_success
95.0,5.0,2300.0,0.02
```

**Grafana Dashboard**:
```
┌─────────────────────────────────────────┐
│  Agent Reliability Dashboard            │
├─────────────────────────────────────────┤
│  Success Rate:  95% ████████████░       │
│  Escalations:    5% ██░░░░░░░░░░        │
│  P95 Latency: 2.3s ██████░░░░░░         │
│  Cost/Task: $0.02  █░░░░░░░░░░░         │
└─────────────────────────────────────────┘
```

**Prometheus Alert** (if configured):
```
FIRING: HighTaskFailureRate
  Success rate dropped to 85% (threshold: 90%)
  ACTION: Check recent deployments
```

---

## Real Example: Healthcare Triage Agent

### Your Agent Code

```python
async def triage_patient(symptoms: str):
    session_id = str(uuid.uuid4())

    # 1. Start
    emitter.emit({
        "event": "session_start",
        "session_id": session_id,
        "task": f"Triage patient with symptoms: {symptoms}",
        "domain": "healthcare",
        "constraints": ["HIPAA compliant", "no diagnosis", "escalate if urgent"]
    })

    # 2. Plan
    emitter.emit({
        "event": "plan_created",
        "session_id": session_id,
        "plan": {
            "steps": [
                {"id": "1", "description": "Check symptom severity", "tool": "severity_check"},
                {"id": "2", "description": "Search medical guidelines", "tool": "guideline_search"},
                {"id": "3", "description": "Generate triage recommendation", "tool": None}
            ]
        },
        "plan_depth": 3
    })

    # 3. Use tools
    severity = await check_severity(symptoms)
    emitter.emit({
        "event": "tool_call",
        "session_id": session_id,
        "tool_name": "severity_check",
        "tool_args": {"symptoms": "[REDACTED]"}  # Auto-redacted
    })

    emitter.emit({
        "event": "observation",
        "session_id": session_id,
        "observation": f"Severity: {severity}",
        "success": True,
        "grounded": True
    })

    # 4. If severe, escalate
    if severity == "high":
        emitter.emit({
            "event": "escalation",
            "session_id": session_id,
            "escalation_reason": "safety_concern",
            "escalation_target": "human"
        })

    # 5. Finalize
    emitter.emit({
        "event": "finalized",
        "session_id": session_id,
        "success": True,
        "constraints_met": True
    })
```

### What Gets Captured

**5 events per patient**:
1. session_start → Task + constraints
2. plan_created → 3-step plan
3. tool_call → severity_check called
4. observation → severity = "high"
5. escalation → Sent to human doctor
6. finalized → Completed with constraints met

### Metrics You Get

After 1000 patients:
- **Task Success Rate**: 98% (980/1000 completed)
- **Escalation Rate**: 15% (150/1000 escalated to doctors)
- **Safety Violation Rate**: 0% (no HIPAA breaches)
- **P95 Latency**: 3.2s (fast enough for ER)
- **Cost per Triage**: $0.03 (affordable at scale)

---

## Key Benefits

### 1. Zero Manual Logging
```python
# ❌ Before RAIA
logger.info(f"Starting session {session_id}")
logger.info(f"Plan created with {len(steps)} steps")
logger.info(f"Tool {tool_name} returned {result}")
# ... hundreds of lines of logging code

# ✅ With RAIA
emitter.emit({"event": "session_start", ...})
emitter.emit({"event": "plan_created", ...})
emitter.emit({"event": "tool_call", ...})
# Structured, validated, queryable
```

### 2. Automatic Metrics
```python
# ❌ Before: Manually count successes
success_count = 0
for log in logs:
    if "SUCCESS" in log:
        success_count += 1
success_rate = success_count / total * 100

# ✅ With RAIA: Automatic
# Just run: replay_compute.py events.ndjson
# Get 22 metrics instantly
```

### 3. Real-Time Alerts
```yaml
# Prometheus alerts auto-configured
- alert: HighFailureRate
  expr: success_rate < 90
  for: 5m
  action: page on-call
```

### 4. Compliance-Ready
```python
# PII automatically redacted
redactor = Redactor.for_domain('healthcare')
# john@example.com → [EMAIL_REDACTED]
# SSN 123-45-6789 → [SSN_REDACTED]
# Patient ID PT-12345 → [PATIENT_ID_REDACTED]

# Audit trail automatic
# Every access logged with who, what, when, from where
```

---

## Summary

**You write**: 5 lines of RAIA code
**You get**:
- 📊 22 production metrics
- 🔍 Complete trace of every decision
- 📈 Real-time dashboards
- 🚨 Automatic alerts
- 🔒 Enterprise security
- 📜 Audit logs
- 🧪 Reproducible evaluations

**No manual logging. No custom metrics. No maintenance.**

Just emit events and let RAIA handle the rest! 🎉
