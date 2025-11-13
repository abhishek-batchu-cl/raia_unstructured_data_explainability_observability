# Why RAIA Inspectors? 🤔

## The Problem with Existing Observability Tools

When you run a LangChain or LangGraph agent, existing tools tell you **WHAT happened**, but not **HOW WELL** it happened.

---

## 🔍 What Existing Tools Give You

### LangSmith
```
✅ "Your agent called the search tool"
✅ "The tool returned 5 results"
✅ "Total execution: 3.5 seconds"

❌ "Your agent called search 3 times with the same query" (inefficiency)
❌ "Your agent is stuck in a loop between node A and B" (behavioral issue)
❌ "Tool X takes 2s but only uses 10 tokens - optimize it" (performance insight)
```

### LangFuse
```
✅ "Here are your traces and spans"
✅ "Total cost: $0.50"
✅ "Quality score: 0.85"

❌ "You're executing 10 nodes when 3 would suffice" (path analysis)
❌ "The same tool is called redundantly" (waste detection)
❌ "Loop detected at step 5" (behavioral pattern)
```

### Arize Phoenix
```
✅ "Embeddings visualization"
✅ "Model drift detected"
✅ "Response time: 2.3s"

❌ "Agent behavior patterns" (not agent-focused)
❌ "Tool usage efficiency" (not agent-focused)
❌ "Graph traversal analysis" (not agent-focused)
```

---

## ✨ What RAIA Inspectors Gives You

### Behavioral Intelligence

```python
# Run your agent
for event in stream_with_inspection(graph, input):
    print(event)

# Get insights
signals = storage.get_signals_for_run(run_id)

>>> [
  Signal(type="loop_detected", severity="high",
         message="Node 'search' executed 5 times"),

  Signal(type="redundant_tool_use", severity="medium",
         message="Tool 'search_pubmed' called 3x with similar queries"),

  Signal(type="suboptimal_path", severity="medium",
         message="Execution took 12 nodes (expected: 4-6)")
]
```

### Performance Analysis

```python
# Per-node breakdown
metrics = storage.get_node_metrics_for_run(run_id)

>>> Node: search_pubmed    | 1,250ms | $0.0025 | ✓
    Node: gpt-4 (planning) | 850ms   | $0.0180 | ✓
    Node: calculator       | 50ms    | $0.0001 | ✓
    Node: search_pubmed    | 1,280ms | $0.0025 | ✓  ← REDUNDANT!
    Node: final_answer     | 920ms   | $0.0190 | ✓

    Total: 4,350ms | $0.0421
```

### Quality Scoring

```python
# Pluggable semantic evaluation
scores = inspector.evaluate_step(run_id, node_name="final_answer")

>>> [
  Score(dimension="hallucination_risk", score=0.12, explanation="Well-grounded"),
  Score(dimension="instruction_adherence", score=0.95, explanation="Followed all rules"),
  Score(dimension="clarity", score=0.88, explanation="Clear and concise")
]
```

---

## 🎯 Side-by-Side: The Same Agent Run

### LangSmith Shows:
```
Trace ID: abc123
├─ LLM Call (2.1s)
├─ Tool: search_pubmed (1.2s)
├─ LLM Call (1.8s)
├─ Tool: search_pubmed (1.3s)
├─ LLM Call (1.9s)
└─ Tool: search_pubmed (1.2s)

Total: 9.5s
Cost: $0.15
Status: ✓ Success
```

### RAIA Inspectors Shows:
```
Run ID: abc123

⚠️  BEHAVIORAL ISSUES DETECTED:

1. 🔴 LOOP DETECTED (High)
   Node 'search_pubmed' called 3 times
   → Investigate: Why is the agent searching repeatedly?

2. 🟡 REDUNDANT TOOL USE (Medium)
   Tool 'search_pubmed' called 3x with queries:
   - "diabetes treatment" (1.2s, $0.025)
   - "diabetes treatment options" (1.3s, $0.025)  ← 95% similar
   - "diabetes therapy" (1.2s, $0.025)            ← 90% similar
   → Optimization: Cache results or improve query planning

3. 🟡 SUBOPTIMAL PATH (Medium)
   Execution: 6 nodes (expected: 3-4)
   → Agent is making unnecessary LLM calls

💰 COST BREAKDOWN:
   LLM calls:   $0.12 (3 calls @ $0.04 avg)
   Tool calls:  $0.03 (3 calls @ $0.01 avg)
   Total:       $0.15
   Potential savings: $0.05 (33%) if redundancy eliminated

⏱️  LATENCY BREAKDOWN:
   LLM:   5.8s (61%)
   Tools: 3.7s (39%)
   Fastest path possible: ~4.5s (current: 9.5s)
```

---

## 🔥 Real-World Example: Production Debugging

### Scenario: Agent is slow and expensive

**With LangSmith:**
```
Engineer: "Hmm, the agent takes 15 seconds and costs $0.80 per run"
Engineer: *looks at trace*
Engineer: "I see lots of tool calls... but which ones are redundant?"
Engineer: *manually analyzes 50 traces*
Engineer: "I think maybe the search tool is being called too much?"
Engineer: *writes custom analysis script*
```

**With RAIA Inspectors:**
```
Engineer: "Let me check the behavioral signals"

>>> signals = storage.get_signals_for_run(run_id)
>>> print(signals)

[
  Signal(type="redundant_tool_use",
         message="Tool 'search_api' called 8 times in 10s window",
         metadata={"calls": ["call_1", "call_2", ...]}),

  Signal(type="loop_detected",
         message="Cycle detected: plan → search → plan → search",
         metadata={"cycle_length": 2, "repetitions": 4})
]

Engineer: "Ah! The planner is stuck in a loop. Let me check the prompt..."
Engineer: *fixes prompt to break loop*
Engineer: *re-runs agent*

New metrics:
- Latency: 4.5s (was 15s) ✓
- Cost: $0.20 (was $0.80) ✓
- No loops detected ✓
```

---

## 📊 What You Can Do with RAIA Inspectors

### 1. Performance Optimization
```python
# Find your slowest nodes
metrics = storage.get_node_metrics_for_run(run_id)
sorted_by_latency = sorted(metrics, key=lambda m: m.latency_ms, reverse=True)

for m in sorted_by_latency[:5]:
    print(f"{m.node_name}: {m.latency_ms}ms")

# Optimize the top offenders
```

### 2. Cost Reduction
```python
# Find expensive nodes
expensive = [m for m in metrics if m.cost_usd > 0.01]

total_cost = sum(m.cost_usd for m in metrics)
potential_savings = sum(m.cost_usd for m in expensive if m.retry_count > 0)

print(f"Total: ${total_cost:.4f}")
print(f"Wasted on retries: ${potential_savings:.4f}")
```

### 3. Behavioral Debugging
```python
# Detect patterns across multiple runs
all_runs = [get_signals_for_run(rid) for rid in run_ids]
loop_count = sum(1 for signals in all_runs
                 if any(s.signal_type == "loop_detected" for s in signals))

print(f"Loops detected in {loop_count}/{len(all_runs)} runs")
# → Indicates systematic issue, not one-off
```

### 4. Quality Assurance
```python
# Track quality over time
scores = storage.get_semantic_scores_for_run(run_id)
hallucination_scores = [s.score for s in scores
                        if s.dimension == "hallucination_risk"]

avg_risk = sum(hallucination_scores) / len(hallucination_scores)
if avg_risk > 0.3:
    print("⚠️  High hallucination risk detected")
```

---

## 🎓 Key Differentiators

### RAIA Inspectors is THE ONLY tool that:

1. **Detects Agent-Specific Patterns**
   - Loop detection (simple & cyclic)
   - Redundant tool usage
   - Suboptimal graph traversal
   - State inconsistencies

2. **Provides Local, Queryable Storage**
   - SQLite (no cloud required)
   - SQL queries for custom analysis
   - Full data ownership
   - No vendor lock-in

3. **Works with Existing RAIA Event Framework**
   - Complementary, not competitive
   - Both can run simultaneously
   - Events for compliance, metrics for performance

4. **Pluggable Semantic Evaluation**
   - Bring your own evaluator
   - Not tied to specific LLM providers
   - Protocol-based interface

5. **Zero External Dependencies**
   - Only requires Pydantic
   - LangChain/LangGraph are optional
   - No backend service needed

---

## 🤝 When to Use Each Tool

### Use LangSmith for:
- 🎯 Development & debugging
- 🎯 Quick trace visualization
- 🎯 Team collaboration
- 🎯 When UI > data ownership

### Use LangFuse for:
- 🎯 Production observability with UI
- 🎯 Prompt management
- 🎯 LLM-as-judge evaluation
- 🎯 When you need self-hosting

### Use RAIA Event Framework for:
- 🎯 Compliance audit trails
- 🎯 Deterministic replay
- 🎯 Event sourcing
- 🎯 PII/PHI redaction

### Use RAIA Inspectors for:
- 🎯 Performance optimization
- 🎯 Behavioral debugging (loops, redundancy)
- 🎯 Cost reduction
- 🎯 Quality scoring
- 🎯 Local, SQL-queryable metrics

### Use Multiple Tools:
- ✅ **LangSmith (dev) + RAIA Inspectors (prod)**
- ✅ **RAIA Events (compliance) + RAIA Inspectors (performance)**
- ✅ **LangFuse (observability) + RAIA Inspectors (behavioral analysis)**

---

## 🚀 Getting Started in 2 Minutes

```bash
# Install
cd raia_inspectors
pip install -e .

# Use with LangChain
from raia_inspectors import RAIAExecutionInspector

inspector = RAIAExecutionInspector(agent_name="my_agent")
result = chain.invoke(input, config={"callbacks": [inspector]})

# Check results
run = inspector.storage.get_run(inspector.run_id)
print(f"Latency: {run.total_latency_ms}ms")
print(f"Cost: ${run.total_cost_usd}")

signals = inspector.storage.get_signals_for_run(inspector.run_id)
for s in signals:
    print(f"⚠️  {s.signal_type}: {s.message}")

# Use with LangGraph
from raia_inspectors.integration import stream_with_inspection

for event in stream_with_inspection(graph, input):
    print(event)

# Metrics automatically saved!
```

---

## 💡 The Bottom Line

**Existing tools answer:** "What did my agent do?"

**RAIA Inspectors answers:**
- "**Why** is my agent slow?"
- "**Where** is it wasting money?"
- "**How** can I make it more efficient?"
- "**What** behavioral patterns are problematic?"

**It's the difference between a trace and an insight.** 🎯

---

## 📚 Learn More

- **Full README**: `raia_inspectors/README.md`
- **Examples**: `raia_inspectors/examples/`
- **Tests**: `raia_inspectors/tests/`
- **Framework Comparison**: `/FRAMEWORK_COMPARISON.md`

---

**Built for engineers who want to optimize, not just observe.** 🔧
