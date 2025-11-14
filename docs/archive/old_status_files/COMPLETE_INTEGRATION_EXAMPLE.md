# Complete Integration Example: Agentic AI → RAIA Dashboard

**How metrics flow from your cloud-based agentic AI to the RAIA dashboard**

---

## 🎯 Overview

This guide shows the **complete end-to-end flow** of how your agentic AI solution (running anywhere in the cloud) connects to RAIA and displays metrics in the dashboard.

---

## 📊 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│ YOUR AGENTIC AI (AWS/GCP/Azure/On-Premise)                          │
│                                                                      │
│  Step 1: User Query                                                 │
│  ┌──────────────────────────────────────────────────┐              │
│  │ query = "What is the capital of France?"         │              │
│  └──────────────────────────────────────────────────┘              │
│         ↓                                                            │
│  Step 2: RAIA Client Logs Event                                     │
│  ┌──────────────────────────────────────────────────┐              │
│  │ raia.start_run(query)                            │              │
│  │ ↓ Sends HTTP POST                                │              │
│  │ {                                                 │              │
│  │   "event_type": "query_received",                │              │
│  │   "timestamp": "2025-01-14T12:00:00Z",           │              │
│  │   "run_id": "abc-123",                           │              │
│  │   "data": {"query": "..."}                       │              │
│  │ }                                                 │              │
│  └──────────────────────────────────────────────────┘              │
│                                                                      │
│  Step 3: Retrieval → Log to RAIA                                    │
│  ┌──────────────────────────────────────────────────┐              │
│  │ docs = retriever.retrieve(query)                 │              │
│  │ raia.log_retrieval(query, docs)                  │              │
│  └──────────────────────────────────────────────────┘              │
│                                                                      │
│  Step 4: LLM Call → Log to RAIA                                     │
│  ┌──────────────────────────────────────────────────┐              │
│  │ response = llm.generate(prompt)                  │              │
│  │ raia.log_llm_call(prompt, response, ...)         │              │
│  └──────────────────────────────────────────────────┘              │
│                                                                      │
│  Step 5: Final Response → Log to RAIA                               │
│  ┌──────────────────────────────────────────────────┐              │
│  │ raia.log_response(response, sources)             │              │
│  │ raia.end_run()                                   │              │
│  └──────────────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────────────┘
                            ↓
                   HTTPS POST Request
                            ↓
┌─────────────────────────────────────────────────────────────────────┐
│ RAIA PLATFORM (Docker Container or Cloud)                           │
│                                                                      │
│  Step 6: Backend Receives Events                                    │
│  ┌──────────────────────────────────────────────────┐              │
│  │ POST /api/events/ingest                          │              │
│  │ ✓ Validate event                                 │              │
│  │ ✓ Store in PostgreSQL                            │              │
│  │ ✓ Trigger metric computation                     │              │
│  └──────────────────────────────────────────────────┘              │
│         ↓                                                            │
│  Step 7: Metric Computation                                         │
│  ┌──────────────────────────────────────────────────┐              │
│  │ • Calculate precision, recall, F1                │              │
│  │ • Calculate faithfulness, hallucination          │              │
│  │ • Detect drift                                   │              │
│  │ • Update aggregations                            │              │
│  └──────────────────────────────────────────────────┘              │
│         ↓                                                            │
│  Step 8: WebSocket Broadcast                                        │
│  ┌──────────────────────────────────────────────────┐              │
│  │ ws.broadcast({                                   │              │
│  │   "type": "metrics_update",                      │              │
│  │   "data": { precision: 0.85, ... }               │              │
│  │ })                                                │              │
│  └──────────────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────────────┘
                            ↓
                   WebSocket Update
                            ↓
┌─────────────────────────────────────────────────────────────────────┐
│ FRONTEND DASHBOARD (Browser)                                        │
│                                                                      │
│  Step 9: Dashboard Updates in Real-Time                             │
│  ┌──────────────────────────────────────────────────┐              │
│  │  📊 Dashboard                                     │              │
│  │                                                   │              │
│  │  Total Runs: 150 ↗                               │              │
│  │  Avg Precision: 0.85 ↗                           │              │
│  │  Avg Faithfulness: 0.92 ↗                        │              │
│  │  Avg Hallucination: 0.08 ↘                       │              │
│  │                                                   │              │
│  │  [Chart showing metrics over time]               │              │
│  │  [Table showing recent runs]                     │              │
│  └──────────────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start Guide

### 1. Deploy RAIA Platform

```bash
# Clone and start RAIA
git clone <repository-url>
cd raia_agentic_evaluation
./docker-start.sh

# RAIA is now running at:
# - Frontend: http://localhost:5173
# - Backend:  http://localhost:8000
```

### 2. Add RAIA Client to Your Agentic AI

```bash
# In your agentic AI project
pip install requests  # Only dependency needed
```

Copy the RAIA client library:
- Copy `backend/raia_client.py` to your project

### 3. Instrument Your Agentic AI

```python
# your_agent.py
from raia_client import RAIAClient, RAIAConfig

# Configure RAIA
config = RAIAConfig(
    api_url="http://your-raia-instance.com:8000",  # Your RAIA URL
    api_key="your-api-key",
    tenant="your-company",
    project="your-project",
    agent_id="your-agent"
)

# Initialize client
raia = RAIAClient(config)

# In your agent's process_query method:
def process_query(query: str):
    # Start run
    raia.start_run(query)

    # Log retrieval
    docs = retriever.retrieve(query)
    raia.log_retrieval(query, docs)

    # Log LLM call
    response = llm.generate(prompt)
    raia.log_llm_call(prompt, response, "gpt-4", tokens=100)

    # Log final response
    raia.log_response(response, sources=["doc1", "doc2"])

    # End run
    raia.end_run()

    return response
```

### 4. Run Your Agentic AI

```python
# Your agentic AI runs anywhere:
# - AWS Lambda
# - GCP Cloud Run
# - Azure Functions
# - Docker containers
# - Kubernetes
# - On-premise

# It sends events to RAIA automatically!
agent = YourAgent()
response = agent.process_query("What is AI?")

# Events are sent to RAIA in real-time ✓
```

### 5. View Metrics in Dashboard

```bash
# Open browser
http://localhost:5173

# Login
Username: admin
Password: admin123

# See metrics in real-time! 📊
```

---

## 📝 Complete Working Example

See `examples/agentic_ai_with_raia.py` for a complete working example:

```bash
# Run the example
cd raia_agentic_evaluation
python examples/agentic_ai_with_raia.py
```

**This example shows:**
1. ✅ How to configure RAIA client
2. ✅ How to instrument your agent
3. ✅ How to log all events (query, retrieval, LLM, tools, response)
4. ✅ How events flow to RAIA
5. ✅ How metrics appear in dashboard

---

## 🔌 API Endpoints

### Event Ingestion (Your Agent → RAIA)

**Single Event:**
```http
POST /api/events/ingest
Authorization: Bearer your-api-key
Content-Type: application/json

{
  "event_id": "uuid",
  "event_type": "query_received",
  "timestamp": "2025-01-14T12:00:00Z",
  "tenant": "acme-corp",
  "project": "support-bot",
  "agent_id": "agent-v1",
  "session_id": "session-123",
  "run_id": "run-456",
  "data": {
    "query": "What is the capital of France?"
  }
}
```

**Batch Events:**
```http
POST /api/events/batch
Authorization: Bearer your-api-key
Content-Type: application/json

{
  "events": [
    { ... event 1 ... },
    { ... event 2 ... },
    { ... event 3 ... }
  ]
}
```

### Query Metrics (Dashboard → RAIA)

**Dashboard Metrics:**
```http
GET /api/metrics/dashboard?time_range=24h&project=support-bot

Response:
{
  "total_runs": 150,
  "avg_precision": 0.85,
  "avg_recall": 0.82,
  "avg_f1": 0.83,
  "avg_faithfulness": 0.92,
  "avg_hallucination": 0.08
}
```

**Recent Runs:**
```http
GET /api/runs?limit=20&project=support-bot

Response:
{
  "runs": [
    {
      "run_id": "run-456",
      "query": "What is the capital of France?",
      "response": "The capital of France is Paris.",
      "precision": 0.95,
      "faithfulness": 0.93,
      "timestamp": "2025-01-14T12:00:00Z"
    },
    ...
  ]
}
```

---

## 🌍 Deployment Scenarios

### Scenario 1: Agentic AI in AWS Lambda, RAIA in Docker

```
┌──────────────────────────┐
│ AWS Lambda Function      │
│ Your Agentic AI          │
│ • Processes user queries │
│ • Logs to RAIA           │
└──────────────────────────┘
         ↓ HTTPS
┌──────────────────────────┐
│ Your Server (EC2)        │
│ RAIA Platform (Docker)   │
│ • Receives events        │
│ • Computes metrics       │
│ • Shows dashboard        │
└──────────────────────────┘
```

**Configuration:**
```python
# In AWS Lambda function
config = RAIAConfig(
    api_url="https://your-ec2-instance.com:8000",
    api_key=os.environ["RAIA_API_KEY"],  # From Lambda env vars
    tenant="acme-corp",
    project="lambda-agent",
    agent_id="lambda-agent-v1"
)
```

### Scenario 2: Multi-Region Agents, Centralized RAIA

```
┌─────────────────────────────────────────────┐
│ Multiple Agentic AI Instances               │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│ │ US-East  │ │ EU-West  │ │ AP-South │     │
│ │ (AWS)    │ │ (GCP)    │ │ (Azure)  │     │
│ └──────────┘ └──────────┘ └──────────┘     │
└─────────────────────────────────────────────┘
        ↓             ↓             ↓
        └─────────────┴─────────────┘
                      ↓
        ┌─────────────────────────┐
        │ Central RAIA Platform   │
        │ • Multi-tenant          │
        │ • Aggregated metrics    │
        │ • Single dashboard      │
        └─────────────────────────┘
```

### Scenario 3: Kubernetes Deployment

```
┌─────────────────────────────────────┐
│ Kubernetes Cluster                  │
│ ┌─────────────────────────────────┐ │
│ │ Agent Pods (multiple)           │ │
│ │ • Auto-scaling                  │ │
│ │ • Load balanced                 │ │
│ └─────────────────────────────────┘ │
│         ↓ Internal Service          │
│ ┌─────────────────────────────────┐ │
│ │ RAIA Service (in cluster)       │ │
│ │ • PostgreSQL StatefulSet        │ │
│ │ • Redis Deployment              │ │
│ │ • Backend Deployment            │ │
│ │ • Frontend Deployment           │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

---

## 📊 What Metrics Are Collected?

### Automatically Computed Metrics:

**Retrieval Metrics:**
- Precision@k, Recall@k, F1@k
- Mean Reciprocal Rank (MRR)
- NDCG (Normalized Discounted Cumulative Gain)

**Answer Quality:**
- Faithfulness (source grounding)
- Hallucination detection
- Relevance scoring
- Correctness

**Performance:**
- Response time
- LLM latency
- Retrieval latency
- Token usage

**Operational:**
- Success/failure rate
- Error types
- Tool usage frequency
- Session analytics

---

## 🎨 Dashboard Features

### Real-Time Updates:
- ✅ Metrics update as events arrive (WebSocket)
- ✅ No page refresh needed
- ✅ Live charts and graphs

### Visualizations:
- ✅ Metric trends over time
- ✅ Distribution histograms
- ✅ Heatmaps
- ✅ Attribution graphs
- ✅ Reasoning traces

### Filtering:
- ✅ By time range (1h, 24h, 7d, 30d)
- ✅ By tenant/project/agent
- ✅ By metric type
- ✅ By success/failure

### Drill-Down:
- ✅ Click on any run to see full details
- ✅ View source attribution
- ✅ See reasoning trace
- ✅ Inspect LLM prompts/responses

---

## 🔐 Security Best Practices

1. **Use HTTPS in production** - Always encrypt in transit
2. **Strong API keys** - Generate secure random keys
3. **Rate limiting** - Protect ingestion endpoints
4. **Network isolation** - Use VPC/private networks
5. **Data encryption** - Encrypt sensitive data in events
6. **Access control** - Use RBAC for dashboard access
7. **Audit logging** - Track who accesses what
8. **Regular updates** - Keep RAIA platform updated

---

## 🎯 Summary

**How it works:**

1. **Your agentic AI** runs anywhere (AWS, GCP, Azure, on-premise)
2. **RAIA client** sends events via HTTP POST
3. **RAIA backend** receives events, computes metrics
4. **RAIA frontend** displays metrics in real-time
5. **You** see everything in the dashboard!

**Integration steps:**

1. Deploy RAIA (one command: `./docker-start.sh`)
2. Copy RAIA client to your project
3. Add 5-10 lines of instrumentation code
4. Run your agent
5. View metrics in dashboard

**That's it!** Your agentic AI is now monitored with RAIA! 🎉

---

## 📚 Additional Resources

- **Architecture Guide**: `docs/CLOUD_INTEGRATION_GUIDE.md`
- **Working Example**: `examples/agentic_ai_with_raia.py`
- **Client Library**: `backend/raia_client.py`
- **API Endpoints**: `backend/event_ingestion.py`
- **Docker Setup**: `DOCKER_SETUP.md`

---

**Questions?** Check the documentation or run the example!

```bash
python examples/agentic_ai_with_raia.py
```
