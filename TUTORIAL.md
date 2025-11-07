# RAIA Tutorial: Building & Monitoring a LangGraph Agent

## 🎯 What You'll Build

A LangGraph agent that:
1. Automatically logs every step (planning, tool calls, observations)
2. Sends events to RAIA ingestion service
3. Computes reliability metrics (success rate, latency, etc.)
4. Displays results in a dashboard

**Total Time**: 15-20 minutes

---

## Step 1: Environment Setup (5 min)

### 1.1 Clone the Framework

```bash
cd ~/projects
git clone <your-repo-url> raia
cd raia
```

### 1.2 Install Python Dependencies

```bash
# Install RAIA SDK
cd sdk/python
pip install -e .

# Install LangGraph and LangChain
pip install langchain langgraph langchain-openai langchain-community

# Install tools
cd ../../tools
pip install -r requirements.txt
```

### 1.3 Set OpenAI API Key

```bash
export OPENAI_API_KEY="sk-your-api-key-here"
```

---

## Step 2: Start RAIA Ingestion Service (2 min)

### Option A: Docker (Recommended)

```bash
cd ~/projects/raia/services/ingestion

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  ingestion:
    build: .
    ports:
      - "8000:8000"
    environment:
      - RAIA_STORAGE_BACKEND=file
      - RAIA_FILE_PATH=/data/events.ndjson
      - RAIA_REQUIRE_API_KEY=false
      - RAIA_REQUIRE_SIGNATURE=false
      - RAIA_ENABLE_VALIDATION=true
    volumes:
      - ./data:/data
    command: ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# Start service
docker-compose up -d

# Check it's running
curl http://localhost:8000/healthz
# Expected: {"status":"healthy"}
```

### Option B: Run Locally (Alternative)

```bash
cd ~/projects/raia/services/ingestion

# Install dependencies
pip install -r requirements.txt

# Set environment
export RAIA_STORAGE_BACKEND=file
export RAIA_FILE_PATH=$HOME/raia_events.ndjson
export RAIA_REQUIRE_API_KEY=false
export RAIA_REQUIRE_SIGNATURE=false

# Start service
python main.py
# Service runs on http://localhost:8000
```

---

## Step 3: Create Your LangGraph Agent with RAIA (5 min)

Create a new file: `my_agent.py`

```python
"""
LangGraph Agent with RAIA Instrumentation
This agent answers questions using tools and logs everything to RAIA.
"""

import asyncio
import os
from typing import TypedDict, Annotated
from datetime import datetime
import uuid

# LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool

# RAIA imports
from raia import EventEmitter, EmitterConfig

# Configure RAIA
config = EmitterConfig(
    tenant="my-company",
    project="demo-agent",
    agent_id="research-assistant-v1.0",
    transport="http",
    endpoint="http://localhost:8000/ingest",
    batch_size=10,
    flush_interval_ms=2000,
    llm="openai/gpt-4",
    seed=42,
)

# Global emitter (in production, pass this through your app)
emitter = None


# Define Tools
@tool
def search_wikipedia(query: str) -> str:
    """Search Wikipedia for information."""
    # Simulate search (in production, use actual API)
    return f"Wikipedia results for '{query}': [Sample article content about {query}]"


@tool
def calculate(expression: str) -> str:
    """Perform mathematical calculations."""
    try:
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"


# Define Agent State
class AgentState(TypedDict):
    messages: list
    session_id: str
    run_id: str
    next_action: str


# Helper function to emit events
def emit_event(event_type: str, state: AgentState, **kwargs):
    """Helper to emit RAIA events."""
    if emitter:
        event = {
            "event": event_type,
            "session_id": state["session_id"],
            "run_id": state["run_id"],
            "agent_id": config.agent_id,
            "ts": datetime.utcnow().isoformat() + "Z",
            "env": {},  # Auto-enriched by emitter
            **kwargs
        }
        emitter.emit(event)


# Agent Nodes
def start_session(state: AgentState) -> AgentState:
    """Initialize session and emit session_start event."""
    task = state["messages"][0].content if state["messages"] else "Unknown task"

    emit_event(
        "session_start",
        state,
        user_id="demo_user",
        task=task,
        domain="general",
        constraints=["accurate", "concise"]
    )

    state["next_action"] = "plan"
    return state


def plan(state: AgentState) -> AgentState:
    """Create a plan and emit plan_created event."""
    task = state["messages"][0].content

    # Simple planning logic
    plan_steps = [
        {"id": "1", "description": "Analyze the question", "tool": None},
        {"id": "2", "description": "Search for information", "tool": "search_wikipedia"},
        {"id": "3", "description": "Formulate answer", "tool": None},
    ]

    emit_event(
        "plan_created",
        state,
        plan={"steps": plan_steps, "rationale": "Standard information retrieval workflow"},
        plan_depth=len(plan_steps),
        revision_count=0
    )

    state["next_action"] = "execute"
    return state


def execute(state: AgentState) -> AgentState:
    """Execute the agent with tools and emit tool events."""
    messages = state["messages"]

    # Create LLM with tools
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    tools = [search_wikipedia, calculate]
    llm_with_tools = llm.bind_tools(tools)

    # Call LLM
    start_time = datetime.utcnow()
    response = llm_with_tools.invoke(messages)
    latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

    # Check if tool calls are needed
    if hasattr(response, 'tool_calls') and response.tool_calls:
        for tool_call in response.tool_calls:
            tool_event_id = str(uuid.uuid4())

            # Emit tool_call event
            emit_event(
                "tool_call",
                state,
                event_id=tool_event_id,
                tool_name=tool_call['name'],
                tool_args=tool_call['args'],
                is_retry=False,
                retry_count=0,
                latency_ms=latency_ms
            )

            # Execute tool
            if tool_call['name'] == 'search_wikipedia':
                result = search_wikipedia.invoke(tool_call['args'])
            elif tool_call['name'] == 'calculate':
                result = calculate.invoke(tool_call['args'])
            else:
                result = "Tool not found"

            # Emit observation event
            emit_event(
                "observation",
                state,
                parent_event_id=tool_event_id,
                observation=result,
                success=True,
                grounded=True,
                evidence_refs=[{"source": tool_call['name'], "id": "result_1"}],
                latency_ms=50  # Tool execution time
            )

            # Add tool result to messages
            messages.append(AIMessage(content=f"Tool {tool_call['name']} returned: {result}"))

    # Get final response
    final_llm = ChatOpenAI(model="gpt-4", temperature=0)
    final_response = final_llm.invoke(messages)

    state["messages"].append(final_response)
    state["next_action"] = "finalize"
    return state


def finalize(state: AgentState) -> AgentState:
    """Finalize session and emit finalized event."""
    final_message = state["messages"][-1].content if state["messages"] else "No response"

    emit_event(
        "finalized",
        state,
        final_answer=final_message,
        success=True,
        constraints_met=True,
        total_steps=3,
        total_tool_calls=1
    )

    return state


# Build the Graph
def create_agent_graph():
    """Create the LangGraph agent."""
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("start", start_session)
    workflow.add_node("plan", plan)
    workflow.add_node("execute", execute)
    workflow.add_node("finalize", finalize)

    # Add edges
    workflow.set_entry_point("start")
    workflow.add_edge("start", "plan")
    workflow.add_edge("plan", "execute")
    workflow.add_edge("execute", "finalize")
    workflow.add_edge("finalize", END)

    return workflow.compile()


# Main execution
async def main():
    """Run the agent and demonstrate RAIA integration."""
    global emitter

    print("🚀 Starting RAIA-Instrumented LangGraph Agent\n")

    # 1. Initialize RAIA Emitter
    print("1️⃣  Initializing RAIA emitter...")
    emitter = EventEmitter(config)
    await emitter.start()
    print("   ✅ Emitter started\n")

    # 2. Create Agent
    print("2️⃣  Creating LangGraph agent...")
    agent = create_agent_graph()
    print("   ✅ Agent created\n")

    # 3. Run Agent on Sample Tasks
    tasks = [
        "What is the capital of France?",
        "Calculate 15 * 23 + 7",
        "Tell me about artificial intelligence",
    ]

    print("3️⃣  Running agent on sample tasks...\n")

    for i, task in enumerate(tasks, 1):
        print(f"   Task {i}: {task}")

        # Create initial state
        initial_state = {
            "messages": [HumanMessage(content=task)],
            "session_id": str(uuid.uuid4()),
            "run_id": str(uuid.uuid4()),
            "next_action": "start"
        }

        # Run agent
        final_state = agent.invoke(initial_state)

        # Get response
        response = final_state["messages"][-1].content
        print(f"   ✅ Response: {response[:100]}...\n")

    # 4. Flush Events
    print("4️⃣  Flushing events to ingestion service...")
    await emitter.flush()
    print("   ✅ Events sent\n")

    # 5. Show Statistics
    health = emitter.get_health()
    print("5️⃣  RAIA Statistics:")
    print(f"   📊 Events emitted: {health['eventsEmitted']}")
    print(f"   ❌ Events dropped: {health['eventsDropped']}")
    print(f"   📦 Batches sent: {health['batchesSent']}")
    print(f"   🔄 Queue size: {health['queueSize']}\n")

    # 6. Shutdown
    print("6️⃣  Shutting down emitter...")
    await emitter.shutdown()
    print("   ✅ Shutdown complete\n")

    print("✨ Demo complete! Check next steps below.")


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Step 4: Run Your Agent (1 min)

```bash
cd ~/projects/raia
python my_agent.py
```

**Expected Output:**
```
🚀 Starting RAIA-Instrumented LangGraph Agent

1️⃣  Initializing RAIA emitter...
   ✅ Emitter started

2️⃣  Creating LangGraph agent...
   ✅ Agent created

3️⃣  Running agent on sample tasks...

   Task 1: What is the capital of France?
   ✅ Response: The capital of France is Paris...

   Task 2: Calculate 15 * 23 + 7
   ✅ Response: Result: 352...

   Task 3: Tell me about artificial intelligence
   ✅ Response: Artificial intelligence (AI) is...

4️⃣  Flushing events to ingestion service...
   ✅ Events sent

5️⃣  RAIA Statistics:
   📊 Events emitted: 15
   ❌ Events dropped: 0
   📦 Batches sent: 1
   🔄 Queue size: 0

6️⃣  Shutting down emitter...
   ✅ Shutdown complete

✨ Demo complete! Check next steps below.
```

---

## Step 5: View Collected Events (2 min)

### 5.1 View Raw Events

```bash
# If using Docker
tail -20 ~/projects/raia/services/ingestion/data/events.ndjson

# If running locally
tail -20 ~/raia_events.ndjson
```

**You'll see events like:**
```json
{"event":"session_start","session_id":"abc-123","task":"What is the capital of France?","domain":"general",...}
{"event":"plan_created","session_id":"abc-123","plan":{"steps":[...]},"plan_depth":3,...}
{"event":"tool_call","session_id":"abc-123","tool_name":"search_wikipedia","tool_args":{"query":"France capital"},...}
{"event":"observation","session_id":"abc-123","observation":"Wikipedia results...","success":true,...}
{"event":"finalized","session_id":"abc-123","final_answer":"The capital of France is Paris","success":true,...}
```

### 5.2 Count Events by Type

```bash
# Using jq (install with: brew install jq)
cat ~/raia_events.ndjson | jq -r '.event' | sort | uniq -c

# Output:
#   3 session_start
#   3 plan_created
#   3 tool_call
#   3 observation
#   3 finalized
```

---

## Step 6: Compute & Display Metrics (3 min)

### 6.1 Run Metrics Computation

```bash
cd ~/projects/raia

python tools/replay_compute.py \
  ~/raia_events.ndjson \
  --metrics-config config/metrics_config.json \
  --output-csv metrics_results.csv \
  --schema schemas/event_schema.json
```

**Output:**
```
INFO:__main__:Loading events from ~/raia_events.ndjson
INFO:__main__:Loaded 15 valid events
INFO:__main__:Computing metrics for 15 events across 3 sessions

=== Computed Metrics ===
INFO:__main__:task_success_rate: 100.00
INFO:__main__:escalation_rate: 0.00
INFO:__main__:safety_violation_rate: 0.00
INFO:__main__:constraint_adherence_rate: 100.00
INFO:__main__:grounded_claim_ratio: 100.00
INFO:__main__:evidence_missing_rate: 0.00
INFO:__main__:wrong_tool_rate: 0.00
INFO:__main__:redundant_call_rate: 0.00
INFO:__main__:backtrack_rate: 0.00
INFO:__main__:avg_plan_depth: 3.00
INFO:__main__:plan_revision_rate: 0.00
INFO:__main__:e2e_latency_p50: 2345.67
INFO:__main__:e2e_latency_p95: 2567.89
INFO:__main__:token_efficiency: 456.00
INFO:__main__:cost_per_success: 0.02
INFO:__main__:retry_rate: 0.00
INFO:__main__:error_rate: 0.00
INFO:__main__:observability_coverage: 100.00

Metrics exported to metrics_results.csv
```

### 6.2 View Metrics in Spreadsheet

```bash
# Open in your default spreadsheet app
open metrics_results.csv

# Or view in terminal
column -t -s, metrics_results.csv
```

### 6.3 Create a Simple Dashboard

```python
# save as: view_metrics.py
import pandas as pd
import matplotlib.pyplot as plt

# Read metrics
df = pd.read_csv('metrics_results.csv')

# Key metrics to visualize
metrics_to_plot = [
    'task_success_rate',
    'escalation_rate',
    'avg_plan_depth',
    'e2e_latency_p95',
    'cost_per_success'
]

# Create dashboard
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
fig.suptitle('RAIA Agent Metrics Dashboard', fontsize=16)

for i, metric in enumerate(metrics_to_plot):
    ax = axes[i // 3, i % 3]
    value = df[metric].iloc[0]

    ax.bar([metric], [value], color='steelblue')
    ax.set_title(metric.replace('_', ' ').title())
    ax.set_ylim(0, max(value * 1.2, 1))

    # Add value label
    ax.text(0, value, f'{value:.2f}', ha='center', va='bottom')

plt.tight_layout()
plt.savefig('metrics_dashboard.png', dpi=150)
print("📊 Dashboard saved to: metrics_dashboard.png")
plt.show()
```

Run it:
```bash
pip install pandas matplotlib
python view_metrics.py
```

---

## Step 7: Monitor in Real-Time (Optional)

### 7.1 Set Up Prometheus + Grafana

```bash
cd ~/projects/raia/observability

# Create docker-compose for monitoring stack
cat > docker-compose-monitoring.yml << 'EOF'
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    depends_on:
      - prometheus
EOF

# Create Prometheus config
cat > prometheus.yml << 'EOF'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'raia-ingestion'
    static_configs:
      - targets: ['host.docker.internal:8000']
EOF

# Start monitoring stack
docker-compose -f docker-compose-monitoring.yml up -d
```

### 7.2 Access Dashboards

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

Query examples in Prometheus:
```promql
# Total events received
sum(raia_events_received_total)

# Events per second
rate(raia_events_stored_total[1m])

# Queue depth
raia_queue_size
```

---

## What Just Happened? 🎓

### Automatic Data Collection

When your agent ran, RAIA automatically captured:

1. **Session Start**: Task, domain, constraints
2. **Plan Created**: Steps, rationale, depth
3. **Tool Calls**: Tool name, arguments, timing
4. **Observations**: Tool results, success/failure, evidence
5. **Finalization**: Success status, total steps

### Event Flow Diagram

```
Your LangGraph Agent
       ↓
  emit() calls
       ↓
RAIA SDK (batching, signing, redaction)
       ↓
HTTP POST to Ingestion Service
       ↓
Storage (NDJSON file / Postgres / Kafka)
       ↓
Replay & Compute Tool
       ↓
Metrics CSV / Dashboard
```

### Key Metrics Computed

- **Reliability**: Success rate, error rate, escalation rate
- **Performance**: P50/P95 latency, step timing
- **Quality**: Grounded claims, constraint adherence, wrong tool rate
- **Efficiency**: Token usage, cost per success
- **Behavior**: Plan depth, backtrack rate, revision rate

---

## Next Steps 🚀

### 1. Production Deployment

```bash
# Enable security
export RAIA_REQUIRE_API_KEY=true
export RAIA_API_KEYS="your-secure-key-here"
export RAIA_REQUIRE_SIGNATURE=true
export RAIA_HMAC_SECRET="your-hmac-secret"

# Use Postgres instead of files
export RAIA_STORAGE_BACKEND=postgres
export RAIA_POSTGRES_URL="postgresql://user:pass@host:5432/raia"
```

### 2. Add PII Redaction

```python
from raia import Redactor

# Redact healthcare data
redactor = Redactor.for_domain('healthcare')
emitter = EventEmitter(config, redactor=redactor)
```

### 3. Set Up Alerts

```bash
# Deploy Prometheus alerts
kubectl apply -f observability/prometheus_alerts.yaml

# Configure PagerDuty/Slack for critical alerts
```

### 4. Create Custom Dashboards

Use the queries in `observability/grafana_dashboard_queries.md` to build Grafana dashboards.

### 5. CI/CD Integration

```yaml
# .github/workflows/quality-gate.yml
- name: Run agent tests
  run: python my_agent.py

- name: Check metrics
  run: |
    python tools/replay_compute.py events.ndjson \
      --metrics-config config/metrics_config.json \
      --fail-on-threshold

    # Fails if success_rate < 95% or error_rate > 2%
```

---

## Troubleshooting 🔧

### Issue: Events not appearing

```bash
# Check ingestion service logs
docker logs raia-ingestion

# Test ingestion manually
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"event":"test","event_id":"123","ts":"2025-01-15T10:00:00Z","session_id":"s1","run_id":"r1","agent_id":"test","env":{"sdk_version":"1.0.0","schema_version":"1.0.0","tenant":"test","project":"test"}}'
```

### Issue: Schema validation errors

```bash
# Validate events manually
pip install jsonschema
jsonschema -i ~/raia_events.ndjson schemas/event_schema.json
```

### Issue: Metrics show 0 events

```bash
# Check file path
ls -lh ~/raia_events.ndjson

# Ensure events were flushed
# Add await emitter.flush() before shutdown
```

---

## Summary ✨

You now have:
- ✅ RAIA ingestion service running
- ✅ LangGraph agent with automatic instrumentation
- ✅ 15+ events captured per session
- ✅ 22 metrics computed from events
- ✅ Dashboard showing agent performance

**Every time your agent runs, RAIA automatically:**
1. Captures all decisions and tool calls
2. Validates and stores events
3. Enables metric computation
4. Powers reliability monitoring

**No manual logging needed** — just emit events and let RAIA handle the rest!
