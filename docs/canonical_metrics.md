# Canonical Metrics — Definitions & Formulas

All metrics are computed strictly from structured runtime events, NOT from post-hoc analysis of final outputs alone. Each metric includes:
- **Formula**: Exact calculation
- **Required Events**: Event types needed for computation
- **Aggregation Window**: Time period or session scope
- **Direction**: Higher is better (↑) or lower is better (↓)
- **Stratification**: Recommended groupings (agent, version, tenant, domain, tool, node)

---

## 1. Task Success Metrics

### 1.1 Task Success Rate
**Definition**: Percentage of runs that completed successfully and met all constraints.

**Formula**:
```
Task_Success_Rate = (COUNT(finalized WHERE success=true AND constraints_met=true) / COUNT(finalized)) × 100
```

**Required Events**: `finalized`

**Aggregation Window**: Per day, per agent_id, per tenant

**Direction**: ↑ Higher is better

**Thresholds**:
- Critical: < 90%
- Warning: < 95%
- Target: ≥ 98%

**Notes**:
- Filter by `domain` to get domain-specific success rates
- Stratify by `agent_id` version to track regression
- Exclude sessions with `error` events if measuring pure logic success

---

### 1.2 Escalation Rate
**Definition**: Percentage of runs that required escalation to humans or supervisor agents.

**Formula**:
```
Escalation_Rate = (COUNT(DISTINCT session_id WHERE event='escalation') / COUNT(DISTINCT session_id WHERE event='finalized')) × 100
```

**Required Events**: `escalation`, `finalized`

**Aggregation Window**: Per day, per agent_id

**Direction**: ↓ Lower is better (unless high escalation is policy)

**Thresholds**:
- Critical: > 30% (indicates agent unreliable)
- Warning: > 15%
- Target: < 10%

**Stratification**:
- By `escalation_reason` (uncertainty, safety_concern, etc.)
- By `domain` (healthcare should have higher safety-driven escalations)

---

### 1.3 Safety Violation Rate
**Definition**: Percentage of runs flagged for safety or policy violations.

**Formula**:
```
Safety_Violation_Rate = (COUNT(DISTINCT session_id WHERE event='policy_flag' AND severity IN ('violation', 'critical')) / COUNT(DISTINCT session_id WHERE event='finalized')) × 100
```

**Required Events**: `policy_flag`, `finalized`

**Aggregation Window**: Per day, per agent_id, per tenant

**Direction**: ↓ Lower is better

**Thresholds**:
- Critical: > 1% (in regulated domains)
- Warning: > 0.1%
- Target: 0%

**Notes**:
- Group by `policy_id` to identify most common violations
- In healthcare/banking, any critical violation should trigger immediate review

---

## 2. Constraint & Grounding Metrics

### 2.1 Constraint Adherence Rate
**Definition**: Percentage of runs that satisfied all declared constraints.

**Formula**:
```
Constraint_Adherence = (COUNT(finalized WHERE constraints_met=true) / COUNT(finalized)) × 100
```

**Required Events**: `finalized`, `session_start` (for constraints list)

**Aggregation Window**: Per day, per agent_id

**Direction**: ↑ Higher is better

**Thresholds**:
- Critical: < 95%
- Warning: < 98%
- Target: 100%

---

### 2.2 Grounded Claim Ratio
**Definition**: Percentage of observations backed by evidence references.

**Formula**:
```
Grounded_Claim_Ratio = (COUNT(observation WHERE grounded=true) / COUNT(observation)) × 100
```

**Required Events**: `observation`

**Aggregation Window**: Per session, per agent_id

**Direction**: ↑ Higher is better

**Thresholds**:
- Critical: < 70% (for fact-checking agents)
- Warning: < 85%
- Target: ≥ 90%

**Notes**:
- Only applicable to agents that should cite sources
- Check `evidence_refs` array length distribution

---

### 2.3 Evidence Missing Rate
**Definition**: Percentage of observations that should have evidence but lack `evidence_refs`.

**Formula**:
```
Evidence_Missing_Rate = (COUNT(observation WHERE grounded=false AND success=true) / COUNT(observation WHERE success=true)) × 100
```

**Required Events**: `observation`

**Aggregation Window**: Per session, per agent_id

**Direction**: ↓ Lower is better

**Thresholds**:
- Critical: > 30%
- Warning: > 15%
- Target: < 5%

---

## 3. Tool Use Efficiency Metrics

### 3.1 Wrong Tool Selection Rate
**Definition**: Percentage of tool calls where the tool used differs from the planned/expected tool.

**Formula**:
```
Wrong_Tool_Rate = (COUNT(tool_call WHERE tool_name != expected_tool AND expected_tool IS NOT NULL) / COUNT(tool_call WHERE expected_tool IS NOT NULL)) × 100
```

**Required Events**: `tool_call` (with `expected_tool` field)

**Aggregation Window**: Per session, per agent_id

**Direction**: ↓ Lower is better

**Thresholds**:
- Critical: > 20%
- Warning: > 10%
- Target: < 5%

**Stratification**:
- By `tool_name` to identify commonly confused tools
- By `graph_node` to localize issues

---

### 3.2 Redundant Tool Call Rate
**Definition**: Percentage of tool calls that are duplicate invocations with identical arguments.

**Formula**:
```
Redundant_Call_Rate = (COUNT(tool_call AS tc1 WHERE EXISTS(tool_call AS tc2 WHERE tc2.session_id=tc1.session_id AND tc2.tool_name=tc1.tool_name AND tc2.tool_args=tc1.tool_args AND tc2.ts < tc1.ts)) / COUNT(tool_call)) × 100
```

**Required Events**: `tool_call`

**Aggregation Window**: Per session

**Direction**: ↓ Lower is better

**Thresholds**:
- Critical: > 25%
- Warning: > 15%
- Target: < 5%

**Notes**:
- High redundancy indicates poor memory or planning
- Exclude intentional retries (where `is_retry=true`)

---

## 4. Planning & Reasoning Metrics

### 4.1 Backtrack Rate
**Definition**: Percentage of runs requiring backtracking (correction events of type 'backtrack').

**Formula**:
```
Backtrack_Rate = (COUNT(DISTINCT session_id WHERE event='correction' AND correction_type='backtrack') / COUNT(DISTINCT session_id WHERE event='finalized')) × 100
```

**Required Events**: `correction`, `finalized`

**Aggregation Window**: Per day, per agent_id

**Direction**: ↓ Lower is better (unless reflection is encouraged)

**Thresholds**:
- Critical: > 40%
- Warning: > 25%
- Target: < 15%

---

### 4.2 Average Plan Depth
**Definition**: Mean number of steps in initial plans.

**Formula**:
```
Avg_Plan_Depth = AVG(plan_depth WHERE event='plan_created' AND revision_count=0)
```

**Required Events**: `plan_created`

**Aggregation Window**: Per agent_id, per domain

**Direction**: Context-dependent (simpler tasks should have lower depth)

**Notes**:
- Monitor trend over time; increasing depth may indicate task complexity creep
- Compare to `total_steps` in `finalized` to see plan vs. execution divergence

---

### 4.3 Plan Revision Rate
**Definition**: Percentage of plans that were revised at least once.

**Formula**:
```
Plan_Revision_Rate = (COUNT(DISTINCT session_id WHERE event='plan_created' AND revision_count > 0) / COUNT(DISTINCT session_id WHERE event='plan_created')) × 100
```

**Required Events**: `plan_created`

**Aggregation Window**: Per agent_id

**Direction**: ↓ Lower is better (indicates better initial planning)

**Thresholds**:
- Critical: > 50%
- Warning: > 30%
- Target: < 20%

---

## 5. Performance & Cost Metrics

### 5.1 End-to-End Latency (p50, p95)
**Definition**: Time from `session_start` to `finalized` event.

**Formula**:
```
E2E_Latency = finalized.ts - session_start.ts (in milliseconds)
p50 = PERCENTILE(E2E_Latency, 0.50)
p95 = PERCENTILE(E2E_Latency, 0.95)
```

**Required Events**: `session_start`, `finalized`

**Aggregation Window**: Per hour, per agent_id

**Direction**: ↓ Lower is better

**Thresholds** (interactive agents):
- Critical: p95 > 30,000ms (30s)
- Warning: p95 > 15,000ms
- Target: p95 < 10,000ms

---

### 5.2 Step Latency (p50, p95)
**Definition**: Latency distribution across all steps (tool calls, observations, plans).

**Formula**:
```
Step_Latency = latency_ms (for events with latency_ms field)
p50 = PERCENTILE(Step_Latency, 0.50)
p95 = PERCENTILE(Step_Latency, 0.95)
```

**Required Events**: Any event with `latency_ms`

**Aggregation Window**: Per agent_id, per event type

**Direction**: ↓ Lower is better

**Stratification**:
- By `event` type to identify slow operations
- By `tool_name` for tool-specific latency

---

### 5.3 Token Efficiency
**Definition**: Average tokens per successful task completion.

**Formula**:
```
Token_Efficiency = SUM(token_usage.total_tokens) / COUNT(finalized WHERE success=true)
```

**Required Events**: Any event with `token_usage`, `finalized`

**Aggregation Window**: Per agent_id, per day

**Direction**: ↓ Lower is better (cost optimization)

**Notes**:
- Monitor trend to detect prompt bloat or inefficient reasoning
- Stratify by `llm` to compare model efficiency

---

### 5.4 Cost per Success
**Definition**: Average cost (USD) per successfully completed task.

**Formula**:
```
Cost_Per_Success = SUM(cost) / COUNT(finalized WHERE success=true)
```

**Required Events**: Any event with `cost`, `finalized`

**Aggregation Window**: Per agent_id, per month

**Direction**: ↓ Lower is better

**Thresholds**: Domain-specific (set budget targets)

---

## 6. Reliability Metrics

### 6.1 Retry Rate
**Definition**: Percentage of tool calls that are retries.

**Formula**:
```
Retry_Rate = (COUNT(tool_call WHERE is_retry=true) / COUNT(tool_call)) × 100
```

**Required Events**: `tool_call`

**Aggregation Window**: Per agent_id, per tool

**Direction**: ↓ Lower is better

**Thresholds**:
- Critical: > 30%
- Warning: > 15%
- Target: < 10%

---

### 6.2 Error Rate
**Definition**: Percentage of runs encountering unrecoverable errors.

**Formula**:
```
Error_Rate = (COUNT(DISTINCT session_id WHERE event='error' AND recoverable=false) / COUNT(DISTINCT session_id WHERE event='session_start')) × 100
```

**Required Events**: `error`, `session_start`

**Aggregation Window**: Per hour, per agent_id

**Direction**: ↓ Lower is better

**Thresholds**:
- Critical: > 5%
- Warning: > 2%
- Target: < 1%

**Stratification**:
- By `error_type` to identify systemic issues (e.g., timeout, llm_error)

---

## 7. Reproducibility Metrics

### 7.1 Seed Stability
**Definition**: Variance in outcomes for identical inputs with same seed.

**Formula**:
```
For each unique (agent_id, inputs, env.seed):
  Group sessions by these keys
  Calculate outcome variance:
    Seed_Stability = 1 - (COUNT(DISTINCT final_answer) / COUNT(session_id))
```

**Required Events**: `session_start`, `finalized`

**Aggregation Window**: Batch analysis across runs

**Direction**: ↑ Higher is better (1.0 = perfectly deterministic)

**Thresholds**:
- Critical: < 0.7 (high variance)
- Warning: < 0.85
- Target: ≥ 0.95

**Notes**:
- Requires controlled replay experiments
- Exclude sessions with non-deterministic tool outputs (e.g., real-time APIs)

---

## 8. Observability Coverage Metric

### 8.1 Observability Coverage
**Definition**: Percentage of agent steps that emit structured events.

**Formula**:
```
Observability_Coverage = (COUNT(events WHERE event != 'session_start') / (finalized.total_steps)) × 100
```

**Required Events**: All events, `finalized`

**Aggregation Window**: Per agent_id

**Direction**: ↑ Higher is better

**Thresholds**:
- Critical: < 80%
- Warning: < 90%
- Target: 100%

**Notes**:
- Low coverage suggests incomplete instrumentation
- Every tool call, observation, and plan should generate events

---

## Aggregation Semantics

### Time Windows
- **Hourly**: For operational monitoring (latency, error rate)
- **Daily**: For quality metrics (success rate, escalation rate)
- **Weekly/Monthly**: For cost trends and efficiency optimization

### Grouping Dimensions
```sql
GROUP BY
  agent_id,              -- Agent type and version
  env.tenant,            -- Multi-tenant isolation
  env.project,           -- Project within tenant
  domain,                -- Application domain (healthcare, banking, etc.)
  tool_name,             -- Tool-level analysis
  graph_node,            -- LangGraph node-level debugging
  env.deployment         -- Dev/staging/prod comparison
```

### Filtering Best Practices
- **Exclude test traffic**: `WHERE env.project != 'test'`
- **Production only**: `WHERE env.deployment = 'prod'`
- **Specific model**: `WHERE env.llm = 'openai/gpt-4'`
- **Regulated domains**: `WHERE domain IN ('healthcare', 'banking')`

---

## Composite Scores

### Agent Reliability Score (ARS)
Weighted composite of key reliability metrics:

```
ARS = (
  0.35 × Task_Success_Rate +
  0.20 × (100 - Escalation_Rate) +
  0.20 × (100 - Safety_Violation_Rate) +
  0.15 × (100 - Error_Rate) +
  0.10 × Constraint_Adherence
) / 100

Range: 0.0 to 1.0
Target: ≥ 0.90
```

### Agent Efficiency Score (AES)
Composite for cost and speed:

```
AES = (
  0.40 × Normalized_Latency_Score +  // Invert and normalize p95 latency
  0.30 × Normalized_Token_Efficiency +
  0.20 × (100 - Wrong_Tool_Rate) +
  0.10 × (100 - Redundant_Call_Rate)
) / 100

Range: 0.0 to 1.0
Target: ≥ 0.85
```

---

## Metric Versioning

All metrics are versioned with the schema. When metric definitions change:
1. Increment `metrics_config_version`
2. Maintain backward compatibility for 2 major versions
3. Document calculation differences in changelog
4. Provide migration scripts for historical re-computation

---

## Notes on Stratification

**By Tool**: Identify problematic tools driving down success or efficiency
```sql
SELECT tool_name,
       AVG(latency_ms) as avg_latency,
       COUNT(*) as call_count
FROM tool_call
GROUP BY tool_name
ORDER BY avg_latency DESC;
```

**By Domain**: Compare agent performance across regulated vs. unregulated contexts
```sql
SELECT domain,
       Task_Success_Rate,
       Safety_Violation_Rate
FROM metrics
GROUP BY domain;
```

**By Node** (LangGraph): Pinpoint graph nodes causing backtracks or errors
```sql
SELECT graph_node,
       COUNT(*) FILTER (WHERE event='correction') as correction_count
FROM events
GROUP BY graph_node
ORDER BY correction_count DESC;
```

---

## CI/CD Quality Gates

Fail deployment if any of these regression checks fail:

```yaml
quality_gates:
  - metric: Task_Success_Rate
    threshold: ">= 95"
    window: "last_7_days"

  - metric: Safety_Violation_Rate
    threshold: "< 0.1"
    window: "last_7_days"

  - metric: p95_E2E_Latency
    threshold: "< 15000"  # ms
    window: "last_24_hours"

  - metric: Cost_Per_Success
    threshold: "< 0.50"  # USD
    increase_tolerance: "10%"  # Allow 10% cost increase

  - metric: Error_Rate
    threshold: "< 2"
    window: "last_24_hours"
```

Compute metrics from staging deployment logs and compare to production baseline before promoting.
