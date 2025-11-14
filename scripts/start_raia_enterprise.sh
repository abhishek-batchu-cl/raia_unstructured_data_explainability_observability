#!/bin/bash

################################################################################
# RAIA ENTERPRISE - STARTUP SCRIPT
################################################################################

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║          🚀 STARTING RAIA ENTERPRISE APPLICATION 🚀                        ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Start backend
echo -e "${BLUE}═══ Starting Backend API (Port 8000) ═══${NC}"
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"
cd ..

# Wait for backend to be ready
echo -e "${YELLOW}⏳ Waiting for backend to be ready...${NC}"
sleep 5

# Test backend
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✓ Backend is healthy!${NC}"
else
    echo -e "${RED}✗ Backend health check failed${NC}"
fi

# Start frontend
echo ""
echo -e "${BLUE}═══ Starting Frontend Dashboard (Port 5173) ═══${NC}"
cd frontend
npm run dev &
FRONTEND_PID=$!
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
cd ..

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                    ✨ RAIA ENTERPRISE IS READY! ✨                         ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}📊 Frontend Dashboard:${NC}    http://localhost:5173"
echo -e "${GREEN}🔧 Backend API:${NC}           http://localhost:8000"
echo -e "${GREEN}📖 API Documentation:${NC}     http://localhost:8000/docs"
echo ""
echo -e "${BLUE}Features Available:${NC}"
echo "  • RAG Metrics (Retrieval, Answer Quality, Semantic)"
echo "  • Attribution Mapping"
echo "  • Reasoning Traces"
echo "  • Agent Evaluation"
echo "  • Drift Detection & Monitoring"
echo "  • What-If Analysis"
echo "  • Pipeline Metrics"
echo "  • Real-time Analytics"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Trap Ctrl+C to kill both processes
trap "echo ''; echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT

# Wait for processes
wait
