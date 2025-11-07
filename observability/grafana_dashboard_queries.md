# Grafana Dashboard Queries for RAIA

This document provides PromQL queries for building RAIA Grafana dashboards.

## Dashboard 1: Agent Reliability Overview

### Panel: Task Success Rate (24h)
```promql
sum(rate(raia_events_stored_total{event_type="finalized", success="true"}[24h])) by (agent_id)
/
sum(rate(raia_events_stored_total{event_type="finalized"}[24h])) by (agent_id)
* 100
```

### Panel: Escalation Rate by Agent
```promql
(
  count(rate(raia_events_stored_total{event_type="escalation"}[1h])) by (agent_id)
  /
  count(rate(raia_events_stored_total{event_type="finalized"}[1h])) by (agent_id)
) * 100
```

### Panel: Safety Violations Timeline
```promql
sum(increase(raia_events_stored_total{event_type="policy_flag", severity=~"violation|critical"}[5m])) by (agent_id, policy_id)
```

### Panel: Error Rate
```promql
(
  sum(rate(raia_events_stored_total{event_type="error", recoverable="false"}[5m])) by (agent_id)
  /
  sum(rate(raia_events_stored_total{event_type="session_start"}[5m])) by (agent_id)
) * 100
```

## Dashboard 2: Performance Metrics

### Panel: P95 End-to-End Latency
```promql
histogram_quantile(0.95,
  sum(rate(raia_e2e_latency_seconds_bucket[5m])) by (le, agent_id)
) * 1000  # Convert to milliseconds
```

### Panel: P50 vs P95 Latency Comparison
```promql
# P50
histogram_quantile(0.50, sum(rate(raia_e2e_latency_seconds_bucket[5m])) by (le, agent_id)) * 1000

# P95
histogram_quantile(0.95, sum(rate(raia_e2e_latency_seconds_bucket[5m])) by (le, agent_id)) * 1000
```

### Panel: Ingestion Throughput
```promql
sum(rate(raia_events_stored_total[1m])) by (backend)
```

### Panel: Average Tokens per Success
```promql
sum(rate(raia_token_usage_total[5m])) by (agent_id)
/
sum(rate(raia_events_stored_total{event_type="finalized", success="true"}[5m])) by (agent_id)
```

## Dashboard 3: Infrastructure Health

### Panel: Service Uptime
```promql
up{job="raia-ingestion"}
```

### Panel: Queue Size
```promql
raia_queue_size
```

### Panel: Event Drop Rate
```promql
rate(raia_events_dropped_total[5m])
```

### Panel: Circuit Breaker State
```promql
raia_circuit_breaker_state  # 0 = closed (healthy), 1 = open (failing)
```

### Panel: Batch Send Latency
```promql
histogram_quantile(0.95,
  sum(rate(raia_ingest_latency_seconds_bucket[5m])) by (le, backend)
)
```

## Dashboard 4: Cost & Efficiency

### Panel: Cost per Successful Task
```promql
sum(rate(raia_cost_total[1h])) by (tenant, agent_id)
/
sum(rate(raia_events_stored_total{event_type="finalized", success="true"}[1h])) by (tenant, agent_id)
```

### Panel: Token Efficiency Trend
```promql
sum(increase(raia_token_usage_total[1h])) by (agent_id)
/
sum(increase(raia_events_stored_total{event_type="finalized", success="true"}[1h])) by (agent_id)
```

### Panel: Daily Cost by Tenant
```promql
sum(increase(raia_cost_total[24h])) by (tenant)
```

## Dashboard 5: Agent Behavior Analysis

### Panel: Wrong Tool Selection Rate
```promql
(
  count(raia_events_stored_total{event_type="tool_call", tool_name != expected_tool}[5m]) by (agent_id)
  /
  count(raia_events_stored_total{event_type="tool_call"}[5m]) by (agent_id)
) * 100
```

### Panel: Average Plan Depth
```promql
avg(raia_plan_depth{revision_count="0"}[1h]) by (agent_id)
```

### Panel: Backtrack Rate
```promql
(
  count(rate(raia_events_stored_total{event_type="correction", correction_type="backtrack"}[5m])) by (agent_id)
  /
  count(rate(raia_events_stored_total{event_type="finalized"}[5m])) by (agent_id)
) * 100
```

### Panel: Tool Call Distribution
```promql
sum(increase(raia_events_stored_total{event_type="tool_call"}[1h])) by (tool_name)
```

## Dashboard 6: SLO Tracking

### Panel: Success Rate SLO Attainment (28d)
```promql
(
  sum(rate(raia_events_stored_total{event_type="finalized", success="true"}[28d]))
  /
  sum(rate(raia_events_stored_total{event_type="finalized"}[28d]))
) * 100
```
Add threshold line at 99.9%

### Panel: Error Budget Remaining
```promql
# Error budget = allowed failures - actual failures
(0.001 * sum(increase(raia_events_stored_total{event_type="finalized"}[28d])))
-
sum(increase(raia_events_stored_total{event_type="finalized", success="false"}[28d]))
```

### Panel: Burn Rate (1h window)
```promql
(
  1 - (
    sum(rate(raia_events_stored_total{event_type="finalized", success="true"}[1h]))
    /
    sum(rate(raia_events_stored_total{event_type="finalized"}[1h]))
  )
) / 0.001  # Normalize to error budget
```

## Dashboard 7: Tenant-Specific View

### Panel: Success Rate by Tenant/Project
```promql
sum(rate(raia_events_stored_total{event_type="finalized", success="true"}[1h])) by (tenant, project)
/
sum(rate(raia_events_stored_total{event_type="finalized"}[1h])) by (tenant, project)
* 100
```

### Panel: Event Volume by Tenant
```promql
sum(rate(raia_events_stored_total[5m])) by (tenant)
```

### Panel: Cost by Tenant
```promql
sum(rate(raia_cost_total[1h])) by (tenant)
```

## Recommended Dashboard Settings

- **Time Range**: Default to last 24 hours with quick ranges (1h, 6h, 24h, 7d, 28d)
- **Refresh**: Auto-refresh every 30s for operational dashboards, 5m for analytics
- **Templating Variables**:
  - `$tenant`: Tenant filter
  - `$project`: Project filter
  - `$agent_id`: Agent filter
  - `$deployment`: Environment filter (dev/staging/prod)
- **Alerting**: Configure dashboard alerts to link to Prometheus alert rules

## Example Alert Annotations

Add these to panels for context:
```json
{
  "annotations": {
    "list": [
      {
        "datasource": "Prometheus",
        "enable": true,
        "expr": "ALERTS{alertname=\"HighTaskFailureRate\",alertstate=\"firing\"}",
        "iconColor": "red",
        "name": "Firing Alerts",
        "tagKeys": "severity,team"
      }
    ]
  }
}
```
