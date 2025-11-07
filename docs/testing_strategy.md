# Testing & Validation Strategy

## 1. Unit Testing

### SDK Tests
```python
# tests/test_redactor.py
import pytest
from raia import Redactor, RedactionRule

def test_email_redaction():
    redactor = Redactor()
    event = {"message": "Contact me at john@example.com"}
    redacted, meta = redactor.redact(event)
    assert "[EMAIL_REDACTED]" in redacted["message"]
    assert meta["applied"] == True

def test_custom_pattern():
    redactor = Redactor()
    redactor.add_custom_pattern("order_id", r"ORD-\d{6}", "[ORDER_REDACTED]")
    event = {"text": "Order ORD-123456 shipped"}
    redacted, _ = redactor.redact(event)
    assert "ORD-123456" not in redacted["text"]
```

### Schema Validation Tests
```python
# tests/test_schema.py
import json
import jsonschema

def test_valid_session_start():
    with open('schemas/event_schema.json') as f:
        schema = json.load(f)

    event = {
        "event": "session_start",
        "event_id": "uuid-here",
        # ... complete event
    }
    jsonschema.validate(event, schema)  # Should not raise

def test_invalid_event_type():
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate({"event": "invalid_type"}, schema)
```

### Metrics Computation Tests
```python
# tests/test_metrics.py
def test_task_success_rate():
    events = [
        {"event": "finalized", "success": True, "constraints_met": True},
        {"event": "finalized", "success": False, "constraints_met": False},
    ]
    computer = MetricsComputer(events, {})
    assert computer._task_success_rate() == 50.0
```

## 2. Integration Testing

### End-to-End Test
```python
# tests/integration/test_e2e.py
import asyncio

async def test_full_pipeline():
    # 1. Emit event via SDK
    emitter = EventEmitter(config)
    await emitter.start()

    emitter.emit({"event": "session_start", ...})
    await emitter.flush()

    # 2. Verify ingestion service received it
    response = requests.get("http://localhost:8000/healthz")
    assert response.status_code == 200

    # 3. Query storage
    async with asyncpg.connect(DATABASE_URL) as conn:
        count = await conn.fetchval("SELECT COUNT(*) FROM raia_events")
        assert count == 1

    # 4. Compute metrics
    result = subprocess.run(
        ["python", "tools/replay_compute.py", "events.ndjson",
         "--metrics-config", "config/metrics_config.json"],
        capture_output=True
    )
    assert result.returncode == 0
```

## 3. Load Testing

### Locust Script
```python
# tests/load/locustfile.py
from locust import HttpUser, task, between

class RAIALoadTest(HttpUser):
    wait_time = between(0.1, 0.5)

    @task
    def ingest_event(self):
        event = {
            "event": "tool_call",
            "event_id": str(uuid.uuid4()),
            # ... complete event
        }
        self.client.post(
            "/ingest",
            json=[event],
            headers={"Authorization": "Bearer test_key"}
        )

# Run: locust -f locustfile.py --host http://localhost:8000
# Target: 5000 events/sec per pod
```

## 4. Chaos Testing

### Fault Injection Scenarios
1. **Network Partition**: Kill connection to Postgres/Kafka
2. **Pod Crash**: Randomly kill ingestion pods
3. **Resource Exhaustion**: Limit CPU/memory
4. **Slow Dependency**: Add latency to storage backend

```yaml
# chaos-experiment.yaml (using Chaos Mesh)
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: network-delay
spec:
  action: delay
  mode: one
  selector:
    namespaces:
      - raia
    labelSelectors:
      app: raia-ingestion
  delay:
    latency: "500ms"
  duration: "5m"
```

## 5. Replay & Determinism Tests

### Seed Stability Test
```python
def test_seed_determinism():
    events_run1 = run_agent_with_seed(seed=42)
    events_run2 = run_agent_with_seed(seed=42)

    # Same seed should produce same final answer
    final1 = [e for e in events_run1 if e["event"] == "finalized"][0]
    final2 = [e for e in events_run2 if e["event"] == "finalized"][0]
    assert final1["final_answer"] == final2["final_answer"]
```

## 6. CI/CD Quality Gates

### GitHub Actions Workflow
```yaml
# .github/workflows/quality-gate.yml
name: Quality Gate

on:
  pull_request:
  push:
    branches: [main]

jobs:
  quality-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run unit tests
        run: pytest tests/ --cov --cov-report=xml

      - name: Schema validation
        run: |
          python -m jsonschema -i schemas/event_examples.ndjson \
                                 schemas/event_schema.json

      - name: Compute metrics from test data
        run: |
          python tools/replay_compute.py tests/fixtures/events.ndjson \
            --metrics-config config/metrics_config.json \
            --output-csv metrics.csv \
            --fail-on-threshold

      - name: Block if success rate < 95%
        run: |
          success_rate=$(cat metrics.csv | grep task_success_rate | cut -d',' -f2)
          if (( $(echo "$success_rate < 95" | bc -l) )); then
            echo "FAILED: Success rate $success_rate < 95%"
            exit 1
          fi

      - name: Security scan
        run: |
          pip install bandit
          bandit -r sdk/python/ -f json -o bandit-report.json
```

## 7. Security Testing

### SAST (Static Analysis)
- Python: `bandit`, `semgrep`
- TypeScript: `eslint-plugin-security`

### DAST (Dynamic Analysis)
- OWASP ZAP scan on ingestion API
- Test for SQL injection, XSS (though API is JSON-only)

### Dependency Scanning
```bash
# Python
pip-audit

# Node.js
npm audit

# Docker images
trivy image raia/ingestion:latest
```

## 8. Regression Testing

Store baseline metrics and compare new runs:
```python
# tests/regression/test_baseline.py
def test_no_regression():
    baseline = load_metrics("tests/regression/baseline_metrics.json")
    current = compute_metrics_from_test_data()

    for metric, value in current.items():
        if metric in baseline:
            delta_pct = abs((value - baseline[metric]) / baseline[metric]) * 100
            assert delta_pct < 5, f"{metric} regressed by {delta_pct}%"
```

## Test Coverage Targets

- Unit tests: ≥ 80% code coverage
- Integration tests: Cover all API endpoints
- Load tests: Sustain target throughput for 1 hour
- Chaos tests: System recovers within 2 minutes
