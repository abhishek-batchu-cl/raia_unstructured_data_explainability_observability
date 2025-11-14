# RAIA Cloud Integration Guide

**How to Connect Your Agentic AI Solution to RAIA**

This guide explains how to integrate your agentic AI solution (running anywhere) with the RAIA platform to collect metrics and display them in the dashboard.

---

## 🏗️ Integration Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  YOUR AGENTIC AI SOLUTION (Cloud/On-Premise)                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  LangChain/LangGraph/Custom Agent                        │   │
│  │  ┌────────────────────────────────────────────┐          │   │
│  │  │  1. User Query                             │          │   │
│  │  │  2. Retrieval (RAG)                        │          │   │
│  │  │  3. LLM Call                               │          │   │
│  │  │  4. Tool Usage                             │          │   │
│  │  │  5. Response Generation                    │          │   │
│  │  └────────────────────────────────────────────┘          │   │
│  │                      ↓                                    │   │
│  │  ┌────────────────────────────────────────────┐          │   │
│  │  │  RAIA Instrumentation Library              │          │   │
│  │  │  • emit_query_event()                      │          │   │
│  │  │  • emit_retrieval_event()                  │          │   │
│  │  │  • emit_llm_event()                        │          │   │
│  │  │  • emit_tool_event()                       │          │   │
│  │  │  • emit_response_event()                   │          │   │
│  │  └────────────────────────────────────────────┘          │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                  Events (JSON over HTTP/HTTPS)
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  RAIA PLATFORM (Docker Container or Cloud)                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Backend API (Port 8000)                                 │   │
│  │  POST /api/events/ingest         ← Receive events        │   │
│  │  POST /api/events/batch          ← Batch events          │   │
│  │  GET  /api/runs                  ← Query runs            │   │
│  │  GET  /api/metrics               ← Get metrics           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                          ↓                                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  PostgreSQL Database                                     │   │
│  │  • Events table (raw events)                             │   │
│  │  • Runs table (aggregated)                               │   │
│  │  • Metrics table (computed metrics)                      │   │
│  └──────────────────────────────────────────────────────────┘   │
│                          ↓                                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Metric Computation Engine                               │   │
│  │  • Calculate precision, recall, F1                       │   │
│  │  • Calculate faithfulness, hallucination                 │   │
│  │  • Detect drift                                          │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                     Real-time Updates via WebSocket
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  FRONTEND DASHBOARD (Port 5173)                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  React Dashboard                                         │   │
│  │  • Real-time metric updates                              │   │
│  │  • Charts and visualizations                             │   │
│  │  • Attribution explorer                                  │   │
│  │  • Reasoning trace viewer                                │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📝 Step-by-Step Integration

### Step 1: Install RAIA Client Library in Your Agentic AI Solution

```bash
# In your agentic AI solution
pip install raia-client  # Or use the library from this repo
```

### Step 2: Configure RAIA Endpoint

```python
# config.py in your agentic AI solution
import os

RAIA_CONFIG = {
    "api_url": os.getenv("RAIA_API_URL", "https://your-raia-instance.com"),
    "api_key": os.getenv("RAIA_API_KEY", "your-api-key"),
    "tenant": "your-company",
    "project": "your-project",
    "agent_id": "your-agent-name"
}
```

### Step 3: Instrument Your Agentic AI Solution

```python
# agent.py in your agentic AI solution
from datetime import datetime
import uuid
import requests
from typing import List, Dict, Any

class RAIAInstrumentation:
    """RAIA instrumentation for agentic AI solutions"""

    def __init__(self, api_url: str, api_key: str, tenant: str, project: str, agent_id: str):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.tenant = tenant
        self.project = project
        self.agent_id = agent_id
        self.session_id = str(uuid.uuid4())
        self.run_id = None

    def start_run(self, query: str) -> str:
        """Start a new run"""
        self.run_id = str(uuid.uuid4())

        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": "query_received",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "tenant": self.tenant,
            "project": self.project,
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "run_id": self.run_id,
            "data": {
                "query": query,
                "query_length": len(query)
            }
        }

        self._send_event(event)
        return self.run_id

    def log_retrieval(self, query: str, retrieved_docs: List[Dict], top_k: int = 5):
        """Log retrieval event"""
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": "retrieval_completed",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "tenant": self.tenant,
            "project": self.project,
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "run_id": self.run_id,
            "data": {
                "query": query,
                "num_retrieved": len(retrieved_docs),
                "top_k": top_k,
                "retrieved_docs": [
                    {
                        "doc_id": doc.get("id", f"doc_{i}"),
                        "content": doc.get("content", ""),
                        "score": doc.get("score", 0.0),
                        "metadata": doc.get("metadata", {})
                    }
                    for i, doc in enumerate(retrieved_docs[:top_k])
                ]
            }
        }

        self._send_event(event)

    def log_llm_call(self, prompt: str, response: str, model: str, tokens_used: int):
        """Log LLM call event"""
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": "llm_call_completed",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "tenant": self.tenant,
            "project": self.project,
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "run_id": self.run_id,
            "data": {
                "prompt": prompt,
                "response": response,
                "model": model,
                "tokens_used": tokens_used,
                "prompt_length": len(prompt),
                "response_length": len(response)
            }
        }

        self._send_event(event)

    def log_tool_usage(self, tool_name: str, tool_input: Dict, tool_output: Any):
        """Log tool usage event"""
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": "tool_executed",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "tenant": self.tenant,
            "project": self.project,
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "run_id": self.run_id,
            "data": {
                "tool_name": tool_name,
                "tool_input": tool_input,
                "tool_output": str(tool_output),
                "success": True
            }
        }

        self._send_event(event)

    def log_response(self, final_response: str, sources_used: List[str]):
        """Log final response event"""
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": "response_generated",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "tenant": self.tenant,
            "project": self.project,
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "run_id": self.run_id,
            "data": {
                "response": final_response,
                "response_length": len(final_response),
                "sources_used": sources_used,
                "num_sources": len(sources_used)
            }
        }

        self._send_event(event)

    def log_evaluation(self, ground_truth: str = None, relevance_score: float = None,
                       faithfulness_score: float = None):
        """Log evaluation metrics (if you have ground truth)"""
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": "evaluation_completed",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "tenant": self.tenant,
            "project": self.project,
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "run_id": self.run_id,
            "data": {
                "ground_truth": ground_truth,
                "relevance_score": relevance_score,
                "faithfulness_score": faithfulness_score
            }
        }

        self._send_event(event)

    def _send_event(self, event: Dict):
        """Send event to RAIA platform"""
        try:
            response = requests.post(
                f"{self.api_url}/api/events/ingest",
                json=event,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                timeout=5
            )
            response.raise_for_status()
            print(f"✓ Event sent: {event['event_type']}")
        except Exception as e:
            print(f"✗ Failed to send event: {e}")
            # In production, you might want to queue failed events for retry


# Example usage in your agentic AI solution
class MyAgenticAI:
    def __init__(self):
        from config import RAIA_CONFIG

        # Initialize RAIA instrumentation
        self.raia = RAIAInstrumentation(
            api_url=RAIA_CONFIG["api_url"],
            api_key=RAIA_CONFIG["api_key"],
            tenant=RAIA_CONFIG["tenant"],
            project=RAIA_CONFIG["project"],
            agent_id=RAIA_CONFIG["agent_id"]
        )

        # Your agent components
        self.retriever = self._init_retriever()
        self.llm = self._init_llm()

    def process_query(self, query: str) -> str:
        """Process a user query with RAIA instrumentation"""

        # 1. Start run
        run_id = self.raia.start_run(query)
        print(f"Started run: {run_id}")

        # 2. Retrieval
        retrieved_docs = self.retriever.retrieve(query, top_k=5)
        self.raia.log_retrieval(query, retrieved_docs, top_k=5)

        # 3. Build prompt
        context = "\n\n".join([doc["content"] for doc in retrieved_docs])
        prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"

        # 4. LLM call
        response = self.llm.generate(prompt)
        self.raia.log_llm_call(
            prompt=prompt,
            response=response,
            model="gpt-4",
            tokens_used=len(prompt.split()) + len(response.split())
        )

        # 5. Tool usage (if any)
        if self._needs_tool(response):
            tool_result = self._use_tool("calculator", {"expression": "2+2"})
            self.raia.log_tool_usage("calculator", {"expression": "2+2"}, tool_result)

        # 6. Log final response
        sources = [doc["id"] for doc in retrieved_docs]
        self.raia.log_response(response, sources)

        # 7. Optional: Log evaluation if you have ground truth
        # self.raia.log_evaluation(
        #     ground_truth="expected answer",
        #     relevance_score=0.95,
        #     faithfulness_score=0.92
        # )

        return response

    def _init_retriever(self):
        # Your retriever initialization
        pass

    def _init_llm(self):
        # Your LLM initialization
        pass

    def _needs_tool(self, response):
        # Check if tool is needed
        return False

    def _use_tool(self, tool_name, tool_input):
        # Use tool
        return {"result": 4}


# Run your agent
if __name__ == "__main__":
    agent = MyAgenticAI()

    # Process queries
    response = agent.process_query("What is the capital of France?")
    print(f"Response: {response}")
```

---

## 🔌 Backend API Endpoints (RAIA Side)

The RAIA backend needs these endpoints to receive events:

### 1. Single Event Ingestion

```python
# backend/main.py

@app.post("/api/events/ingest")
async def ingest_event(event: Dict[str, Any], api_key: str = Depends(verify_api_key)):
    """
    Ingest a single event from agentic AI solution

    Event format:
    {
        "event_id": "uuid",
        "event_type": "query_received | retrieval_completed | llm_call_completed | ...",
        "timestamp": "2025-01-14T12:00:00Z",
        "tenant": "company",
        "project": "project",
        "agent_id": "agent-name",
        "session_id": "session-uuid",
        "run_id": "run-uuid",
        "data": { ... event-specific data ... }
    }
    """
    try:
        # Validate event
        if not event.get("event_id") or not event.get("event_type"):
            raise HTTPException(status_code=400, detail="Missing required fields")

        # Store event in database
        db.execute(
            """
            INSERT INTO events (event_id, event_type, timestamp, tenant, project,
                                agent_id, session_id, run_id, data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event["event_id"],
                event["event_type"],
                event["timestamp"],
                event.get("tenant"),
                event.get("project"),
                event.get("agent_id"),
                event.get("session_id"),
                event.get("run_id"),
                json.dumps(event.get("data", {}))
            )
        )

        # Process event and update metrics (async)
        await process_event_async(event)

        # Emit real-time update via WebSocket
        await websocket_manager.broadcast({
            "type": "new_event",
            "event": event
        })

        return {"status": "success", "event_id": event["event_id"]}

    except Exception as e:
        logger.error(f"Error ingesting event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/events/batch")
async def ingest_batch(events: List[Dict[str, Any]], api_key: str = Depends(verify_api_key)):
    """Ingest multiple events at once (better performance)"""
    results = []

    for event in events:
        try:
            # Store event
            db.execute(
                """INSERT INTO events (...) VALUES (...)""",
                (...)
            )
            results.append({"event_id": event["event_id"], "status": "success"})
        except Exception as e:
            results.append({"event_id": event.get("event_id"), "status": "error", "error": str(e)})

    # Process all events
    await process_events_batch(events)

    return {"results": results}
```

### 2. Query Endpoints (For Frontend)

```python
@app.get("/api/runs")
async def get_runs(
    limit: int = 100,
    offset: int = 0,
    tenant: str = None,
    project: str = None,
    agent_id: str = None
):
    """Get list of runs with computed metrics"""
    query = """
        SELECT
            r.run_id,
            r.query,
            r.response,
            r.timestamp,
            m.precision,
            m.recall,
            m.f1_score,
            m.faithfulness,
            m.hallucination_score,
            r.agent_id,
            r.project
        FROM runs r
        LEFT JOIN metrics m ON r.run_id = m.run_id
        WHERE 1=1
    """

    params = []
    if tenant:
        query += " AND r.tenant = ?"
        params.append(tenant)
    if project:
        query += " AND r.project = ?"
        params.append(project)
    if agent_id:
        query += " AND r.agent_id = ?"
        params.append(agent_id)

    query += " ORDER BY r.timestamp DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    runs = db.execute_query(query, tuple(params))

    return {"runs": runs, "total": len(runs)}


@app.get("/api/metrics/dashboard")
async def get_dashboard_metrics(
    tenant: str = None,
    project: str = None,
    time_range: str = "24h"
):
    """Get aggregated metrics for dashboard"""

    # Convert time_range to SQL
    time_filter = get_time_filter(time_range)  # "24h" -> "timestamp > NOW() - INTERVAL '24 hours'"

    query = f"""
        SELECT
            COUNT(DISTINCT run_id) as total_runs,
            AVG(precision) as avg_precision,
            AVG(recall) as avg_recall,
            AVG(f1_score) as avg_f1,
            AVG(faithfulness) as avg_faithfulness,
            AVG(hallucination_score) as avg_hallucination,
            COUNT(DISTINCT session_id) as total_sessions,
            COUNT(DISTINCT agent_id) as total_agents
        FROM runs r
        LEFT JOIN metrics m ON r.run_id = m.run_id
        WHERE {time_filter}
    """

    params = []
    if tenant:
        query += " AND r.tenant = ?"
        params.append(tenant)
    if project:
        query += " AND r.project = ?"
        params.append(project)

    metrics = db.execute_query(query, tuple(params))[0]

    return metrics
```

---

## 🎨 Frontend Integration

### Update Dashboard to Show Real-Time Metrics

```typescript
// frontend/src/pages/Dashboard.tsx

import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Line, Bar } from 'recharts';

export function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  const [ws, setWs] = useState<WebSocket | null>(null);

  // Fetch initial metrics
  const { data: dashboardData } = useQuery({
    queryKey: ['dashboard-metrics'],
    queryFn: async () => {
      const response = await fetch('http://localhost:8000/api/metrics/dashboard?time_range=24h');
      return response.json();
    },
    refetchInterval: 5000 // Poll every 5 seconds
  });

  // WebSocket for real-time updates
  useEffect(() => {
    const websocket = new WebSocket('ws://localhost:8000/ws');

    websocket.onmessage = (event) => {
      const message = JSON.parse(event.data);

      if (message.type === 'new_event') {
        // New event received, update metrics
        console.log('New event:', message.event);
        // Trigger refetch or update local state
      }

      if (message.type === 'metrics_update') {
        setMetrics(message.data);
      }
    };

    setWs(websocket);

    return () => websocket.close();
  }, []);

  return (
    <div className="dashboard">
      <h1>RAIA Dashboard - Real-Time Metrics</h1>

      {/* Metric Cards */}
      <div className="metrics-grid">
        <MetricCard
          title="Total Runs"
          value={dashboardData?.total_runs || 0}
          icon="🚀"
        />
        <MetricCard
          title="Avg Precision"
          value={(dashboardData?.avg_precision || 0).toFixed(3)}
          icon="🎯"
        />
        <MetricCard
          title="Avg Faithfulness"
          value={(dashboardData?.avg_faithfulness || 0).toFixed(3)}
          icon="✅"
        />
        <MetricCard
          title="Avg Hallucination"
          value={(dashboardData?.avg_hallucination || 0).toFixed(3)}
          icon="⚠️"
        />
      </div>

      {/* Charts */}
      <div className="charts">
        <TrendsChart />
        <DistributionChart />
      </div>

      {/* Recent Runs */}
      <RecentRuns />
    </div>
  );
}
```

---

## 🚀 Deployment Scenarios

### Scenario 1: Agentic AI in AWS, RAIA in Docker

```
┌──────────────────────────────────┐
│  AWS EC2/ECS/Lambda              │
│  Your Agentic AI Solution        │
│  └─> Sends events to RAIA        │
└──────────────────────────────────┘
           ↓ HTTPS
┌──────────────────────────────────┐
│  Your Server (Cloud/On-Premise)  │
│  RAIA Platform (Docker)          │
│  └─> Receives & processes events │
└──────────────────────────────────┘
```

**Setup:**
```bash
# On your server
./docker-start.sh

# In your AWS agentic AI code
RAIA_API_URL=https://your-raia-server.com:8000
RAIA_API_KEY=your-secure-api-key
```

### Scenario 2: Both in Cloud

```
┌──────────────────────────────────┐
│  AWS/GCP/Azure                   │
│  ┌────────────────────────────┐  │
│  │ Agentic AI Service         │  │
│  │ (ECS/Cloud Run/App Service)│  │
│  └────────────────────────────┘  │
│           ↓ Internal Network     │
│  ┌────────────────────────────┐  │
│  │ RAIA Platform              │  │
│  │ (ECS/Cloud Run/App Service)│  │
│  └────────────────────────────┘  │
└──────────────────────────────────┘
```

### Scenario 3: Multi-Agent Systems

```
┌──────────────────────────────────────────────┐
│  Multiple Agentic AI Solutions               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│  │ Agent 1  │ │ Agent 2  │ │ Agent 3  │     │
│  │ (AWS)    │ │ (GCP)    │ │ (Azure)  │     │
│  └──────────┘ └──────────┘ └──────────┘     │
└──────────────────────────────────────────────┘
       ↓              ↓              ↓
       └──────────────┴──────────────┘
                      ↓
       ┌──────────────────────────────┐
       │  Central RAIA Platform       │
       │  • Aggregates all metrics    │
       │  • Multi-tenant support      │
       │  • Single dashboard          │
       └──────────────────────────────┘
```

---

## 📊 Complete End-to-End Example

See `docs/INTEGRATION_EXAMPLE.md` for a complete working example with:
1. Sample agentic AI application
2. RAIA instrumentation
3. Event ingestion
4. Metric computation
5. Dashboard display

---

## 🔐 Security Best Practices

1. **API Keys**: Use secure API keys for authentication
2. **HTTPS**: Always use HTTPS in production
3. **Rate Limiting**: Implement rate limiting on ingestion endpoints
4. **Data Encryption**: Encrypt sensitive data in events
5. **Network Security**: Use VPC/private networks when possible

---

## 🎯 Next Steps

1. Install RAIA client library in your agentic AI solution
2. Add instrumentation to key points in your workflow
3. Configure RAIA endpoint and API key
4. Deploy RAIA platform (Docker)
5. Start sending events
6. View metrics in dashboard

**Need help?** See `docs/INTEGRATION_EXAMPLE.md` for complete code examples!
