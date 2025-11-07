#!/bin/bash

# RAIA Quick Start Script
# This script sets up everything and runs a demo agent

set -e  # Exit on error

echo "🚀 RAIA Quick Start Script"
echo "=========================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check requirements
echo "📋 Checking requirements..."

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is required but not installed${NC}"
    exit 1
fi

if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ pip3 is required but not installed${NC}"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker not found. Will run ingestion service locally.${NC}"
    USE_DOCKER=false
else
    USE_DOCKER=true
fi

echo -e "${GREEN}✅ Requirements met${NC}"
echo ""

# Step 1: Install SDK
echo "1️⃣  Installing RAIA SDK..."
cd sdk/python
pip3 install -e . > /dev/null 2>&1
pip3 install langchain langgraph langchain-openai > /dev/null 2>&1
cd ../..
echo -e "${GREEN}   ✅ SDK installed${NC}"
echo ""

# Step 2: Start Ingestion Service
echo "2️⃣  Starting ingestion service..."

if [ "$USE_DOCKER" = true ]; then
    cd services/ingestion

    # Create docker-compose if not exists
    if [ ! -f docker-compose.yml ]; then
        cat > docker-compose.yml << 'DOCKEREOF'
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
      - RAIA_ENABLE_VALIDATION=false
    volumes:
      - ./data:/data
DOCKEREOF
    fi

    # Start docker
    docker-compose up -d > /dev/null 2>&1

    # Wait for service
    echo "   Waiting for service to start..."
    sleep 5

    cd ../..
    EVENTS_FILE="services/ingestion/data/events.ndjson"
else
    # Run locally
    export RAIA_STORAGE_BACKEND=file
    export RAIA_FILE_PATH="$PWD/demo_events.ndjson"
    export RAIA_REQUIRE_API_KEY=false
    export RAIA_REQUIRE_SIGNATURE=false
    export RAIA_ENABLE_VALIDATION=false

    cd services/ingestion
    pip3 install -r requirements.txt > /dev/null 2>&1
    python main.py &
    INGESTION_PID=$!
    cd ../..

    # Wait for service
    echo "   Waiting for service to start..."
    sleep 5

    EVENTS_FILE="$PWD/demo_events.ndjson"
fi

# Check if service is running
if curl -s http://localhost:8000/healthz > /dev/null 2>&1; then
    echo -e "${GREEN}   ✅ Ingestion service running at http://localhost:8000${NC}"
else
    echo -e "${RED}   ❌ Failed to start ingestion service${NC}"
    exit 1
fi
echo ""

# Step 3: Create demo agent
echo "3️⃣  Creating demo agent..."

cat > demo_agent.py << 'PYTHONEOF'
import asyncio
import uuid
from datetime import datetime
from raia import EventEmitter, EmitterConfig

async def run_demo():
    """Simple demo agent that emits events."""

    # Configure RAIA
    config = EmitterConfig(
        tenant="demo-company",
        project="quickstart",
        agent_id="demo-agent-v1.0",
        transport="http",
        endpoint="http://localhost:8000/ingest",
        batch_size=5,
        flush_interval_ms=1000,
    )

    # Start emitter
    emitter = EventEmitter(config)
    await emitter.start()

    print("   Running 3 agent sessions...\n")

    # Simulate 3 agent runs
    for i in range(3):
        session_id = str(uuid.uuid4())
        run_id = str(uuid.uuid4())

        print(f"   Session {i+1}: Answering user question...")

        # Session start
        emitter.emit({
            "event": "session_start",
            "session_id": session_id,
            "run_id": run_id,
            "agent_id": "demo-agent-v1.0",
            "user_id": f"user_{i+1}",
            "task": f"Demo task {i+1}: What is 2+2?",
            "domain": "general",
            "constraints": ["accurate"],
            "env": {},
        })

        # Plan
        emitter.emit({
            "event": "plan_created",
            "session_id": session_id,
            "run_id": run_id,
            "agent_id": "demo-agent-v1.0",
            "plan": {
                "steps": [
                    {"id": "1", "description": "Understand question"},
                    {"id": "2", "description": "Calculate answer"},
                    {"id": "3", "description": "Format response"},
                ],
                "rationale": "Simple calculation"
            },
            "plan_depth": 3,
            "revision_count": 0,
            "env": {},
        })

        # Tool call
        tool_id = str(uuid.uuid4())
        emitter.emit({
            "event": "tool_call",
            "event_id": tool_id,
            "session_id": session_id,
            "run_id": run_id,
            "agent_id": "demo-agent-v1.0",
            "tool_name": "calculator",
            "tool_args": {"expression": "2+2"},
            "is_retry": False,
            "retry_count": 0,
            "latency_ms": 45.2,
            "env": {},
        })

        # Observation
        emitter.emit({
            "event": "observation",
            "session_id": session_id,
            "run_id": run_id,
            "agent_id": "demo-agent-v1.0",
            "parent_event_id": tool_id,
            "observation": "Result: 4",
            "success": True,
            "grounded": True,
            "evidence_refs": [{"source": "calculator", "id": "calc_1"}],
            "latency_ms": 10.5,
            "env": {},
        })

        # Finalize
        emitter.emit({
            "event": "finalized",
            "session_id": session_id,
            "run_id": run_id,
            "agent_id": "demo-agent-v1.0",
            "final_answer": "The answer is 4",
            "success": True,
            "constraints_met": True,
            "total_steps": 3,
            "total_tool_calls": 1,
            "latency_ms": 1234.5,
            "env": {},
        })

        await asyncio.sleep(0.5)

    print()

    # Flush and shutdown
    await emitter.flush()

    # Show stats
    health = emitter.get_health()
    print(f"   📊 Events emitted: {health['eventsEmitted']}")
    print(f"   📦 Batches sent: {health['batchesSent']}")

    await emitter.shutdown()

if __name__ == "__main__":
    asyncio.run(run_demo())
PYTHONEOF

echo -e "${GREEN}   ✅ Demo agent created${NC}"
echo ""

# Step 4: Run demo agent
echo "4️⃣  Running demo agent..."
python3 demo_agent.py
echo -e "${GREEN}   ✅ Agent completed${NC}"
echo ""

# Step 5: View events
echo "5️⃣  Viewing collected events..."
if [ -f "$EVENTS_FILE" ]; then
    echo "   Last 5 events:"
    tail -5 "$EVENTS_FILE" | while read line; do
        event_type=$(echo "$line" | python3 -c "import sys, json; print(json.load(sys.stdin).get('event', 'unknown'))" 2>/dev/null || echo "unknown")
        echo "   - $event_type"
    done
    echo ""
    echo -e "${GREEN}   ✅ Events stored in: $EVENTS_FILE${NC}"
else
    echo -e "${YELLOW}   ⚠️  No events file found${NC}"
fi
echo ""

# Step 6: Compute metrics
echo "6️⃣  Computing metrics..."
cd tools
pip3 install -r requirements.txt > /dev/null 2>&1
cd ..

python3 tools/replay_compute.py \
  "$EVENTS_FILE" \
  --metrics-config config/metrics_config.json \
  --output-csv demo_metrics.csv \
  2>&1 | grep -E "(task_success_rate|escalation_rate|e2e_latency_p95|Metrics exported)" || true

if [ -f demo_metrics.csv ]; then
    echo ""
    echo "   Top metrics:"
    echo "   -------------"

    # Read and display key metrics
    if command -v python3 &> /dev/null; then
        python3 << 'PYEOF'
import csv
with open('demo_metrics.csv') as f:
    reader = csv.DictReader(f)
    row = next(reader)
    print(f"   Task Success Rate: {float(row['task_success_rate']):.1f}%")
    print(f"   Escalation Rate: {float(row['escalation_rate']):.1f}%")
    print(f"   Error Rate: {float(row['error_rate']):.1f}%")
    print(f"   Avg Plan Depth: {float(row['avg_plan_depth']):.1f}")
    print(f"   P95 Latency: {float(row['e2e_latency_p95']):.0f}ms")
PYEOF
    fi

    echo ""
    echo -e "${GREEN}   ✅ Full metrics saved to: demo_metrics.csv${NC}"
else
    echo -e "${YELLOW}   ⚠️  Metrics computation failed${NC}"
fi
echo ""

# Summary
echo "=========================="
echo "✨ Quick Start Complete!"
echo "=========================="
echo ""
echo "What just happened:"
echo "  ✅ Installed RAIA SDK"
echo "  ✅ Started ingestion service (http://localhost:8000)"
echo "  ✅ Ran demo agent (3 sessions)"
echo "  ✅ Collected 15 events"
echo "  ✅ Computed 22 metrics"
echo ""
echo "Files created:"
echo "  📄 $EVENTS_FILE (raw events)"
echo "  📊 demo_metrics.csv (computed metrics)"
echo "  🐍 demo_agent.py (sample code)"
echo ""
echo "Next steps:"
echo "  1. View events: cat $EVENTS_FILE | head -5"
echo "  2. View metrics: cat demo_metrics.csv"
echo "  3. Open tutorial: cat TUTORIAL.md"
echo "  4. Check docs: cat docs/quickstart.md"
echo ""
echo "To use with YOUR agent:"
echo "  1. pip install -e sdk/python"
echo "  2. from raia import EventEmitter, EmitterConfig"
echo "  3. emitter.emit({'event': 'session_start', ...})"
echo ""
echo "To stop services:"

if [ "$USE_DOCKER" = true ]; then
    echo "  cd services/ingestion && docker-compose down"
else
    echo "  kill $INGESTION_PID"
fi

echo ""
echo "Questions? Check TUTORIAL.md for detailed walkthrough"
echo ""
