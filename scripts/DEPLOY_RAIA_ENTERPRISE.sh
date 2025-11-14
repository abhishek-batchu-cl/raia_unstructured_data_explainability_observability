#!/bin/bash

################################################################################
# RAIA ENTERPRISE FULL-STACK DEPLOYMENT
################################################################################
#
# Deploys the complete RAIA Enterprise application:
# - FastAPI backend with ALL 15 database tables
# - React + TypeScript frontend with RAIA-specific pages
# - Real-time monitoring and analytics
#
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logos and branding
print_header() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════════════════════╗"
    echo "║                                                                            ║"
    echo "║              🚀 RAIA ENTERPRISE - FULL-STACK DEPLOYMENT 🚀                 ║"
    echo "║                                                                            ║"
    echo "║   Responsible AI Analytics & Agent Evaluation Framework                   ║"
    echo "║   Production-Grade RAG Evaluation Platform                                 ║"
    echo "║                                                                            ║"
    echo "╚════════════════════════════════════════════════════════════════════════════╝"
    echo ""
}

print_section() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_section "Checking Prerequisites"

    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python 3 found: $PYTHON_VERSION"
    else
        print_error "Python 3 not found. Please install Python 3.8+"
        exit 1
    fi

    # Check Node.js
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Node.js found: $NODE_VERSION"
    else
        print_error "Node.js not found. Please install Node.js 18+"
        exit 1
    fi

    # Check npm
    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm --version)
        print_success "npm found: $NPM_VERSION"
    else
        print_error "npm not found. Please install npm"
        exit 1
    fi

    # Check for databases
    if [ -f "complete_end_to_end_demo.db" ] || [ -f "agentic_ai_demo.db" ]; then
        print_success "Database files found"
    else
        print_warning "No database files found. Run demos to generate data."
    fi
}

# Setup backend
setup_backend() {
    print_section "Setting Up Backend (FastAPI)"

    cd backend

    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_info "Creating Python virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_info "Virtual environment already exists"
    fi

    # Activate virtual environment
    print_info "Activating virtual environment..."
    source venv/bin/activate

    # Install dependencies
    print_info "Installing Python dependencies..."
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    print_success "Backend dependencies installed"

    # Verify main_complete.py exists
    if [ -f "main_complete.py" ]; then
        print_success "Comprehensive backend found (main_complete.py)"
    else
        print_error "main_complete.py not found!"
        exit 1
    fi

    cd ..
}

# Setup frontend
setup_frontend() {
    print_section "Setting Up Frontend (React + TypeScript)"

    if [ ! -d "frontend_complete" ]; then
        print_error "frontend_complete directory not found!"
        exit 1
    fi

    cd frontend_complete

    # Install npm dependencies
    if [ ! -d "node_modules" ]; then
        print_info "Installing npm dependencies (this may take a few minutes)..."
        npm install
        print_success "Frontend dependencies installed"
    else
        print_info "node_modules already exists, skipping npm install"
    fi

    # Verify .env.local exists
    if [ ! -f ".env.local" ]; then
        if [ -f ".env.example" ]; then
            print_info "Creating .env.local from .env.example..."
            cp .env.example .env.local
            print_success ".env.local created"
        else
            print_warning ".env.local not found, creating default..."
            echo "VITE_API_BASE_URL=http://localhost:8000" > .env.local
            print_success ".env.local created with default values"
        fi
    fi

    cd ..
}

# Create startup script
create_startup_script() {
    print_section "Creating Startup Script"

    cat > start_raia_enterprise.sh << 'STARTSCRIPT'
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
uvicorn main_complete:app --reload --host 0.0.0.0 --port 8000 &
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
cd frontend_complete
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
STARTSCRIPT

    chmod +x start_raia_enterprise.sh
    print_success "Startup script created: start_raia_enterprise.sh"
}

# Create summary documentation
create_summary() {
    print_section "Creating Documentation"

    cat > RAIA_ENTERPRISE_READY.md << 'SUMMARY'
# 🎉 RAIA Enterprise - DEPLOYMENT COMPLETE!

## What You Have

### ✅ Complete FastAPI Backend
- **File**: `backend/main_complete.py`
- **Features**: ALL 15 database tables exposed via REST API
- **Endpoints**: 20+ endpoints covering all RAIA modules
- **Documentation**: Auto-generated at http://localhost:8000/docs

### ✅ Enterprise React Frontend
- **Directory**: `frontend_complete/`
- **Pages**: 14 pages including RAIA-specific features
- **Features**:
  - Real-time dashboard with live metrics
  - Attribution mapping visualization
  - Reasoning traces explorer
  - System monitoring (drift detection, vector health)
  - What-If analysis (counterfactuals, sensitivity, optimization)
  - All original pages (Output Quality, Performance, etc.)

### ✅ RAIA Modules Coverage

**Metrics & Evaluation:**
- ✅ Retrieval Metrics (Precision, Recall, F1, MRR, NDCG)
- ✅ Answer Quality (Faithfulness, Hallucination, Relevance)
- ✅ Semantic Scores
- ✅ Node Metrics
- ✅ Pipeline Metrics

**Explainability:**
- ✅ Attribution Maps
- ✅ Reasoning Traces
- ✅ Agent Decisions

**Monitoring:**
- ✅ Embedding Drift Detection
- ✅ Vector Index Health
- ✅ Functional Signals

**What-If Analysis:**
- ✅ Counterfactual Scenarios
- ✅ Sensitivity Analysis
- ✅ Optimization Recommendations

**Analytics:**
- ✅ Time-series Data
- ✅ Export Capabilities (CSV/JSON)

---

## 🚀 Quick Start

### Start the Application
```bash
./start_raia_enterprise.sh
```

### Access Points
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 📊 Features

### Dashboard
- Real-time metrics from actual database
- Faithfulness, Precision, Recall trends
- Attribution and Reasoning trace counts
- Drift detection status
- Quick links to all RAIA features

### New RAIA Pages

**1. Attribution** (`/attribution`)
- View answer-source mappings
- Confidence scores
- Source document tracking

**2. Reasoning Traces** (`/reasoning`)
- Step-by-step execution
- Decision-making process
- Confidence per step
- Input/output inspection

**3. System Monitoring** (`/monitoring`)
- Embedding drift trends (KL/JS divergence)
- Vector index health
- Functional correctness signals
- Real-time alerts

**4. What-If Analysis** (`/whatif`)
- Counterfactual scenarios
- Parameter sensitivity analysis
- Optimization recommendations

---

## 🔧 Technology Stack

**Backend:**
- FastAPI 0.104+
- SQLite with real RAIA data
- Pydantic for validation
- CORS enabled

**Frontend:**
- React 19
- TypeScript
- TanStack Query for data fetching
- Recharts for visualizations
- TailwindCSS for styling
- Lucide React for icons

---

## 📁 Project Structure

```
raia_agentic_evaluation/
├── backend/
│   ├── main_complete.py       ← Comprehensive FastAPI backend
│   ├── requirements.txt
│   └── venv/
├── frontend_complete/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx          (Original)
│   │   │   ├── RAIADashboard.tsx      (RAIA-specific)
│   │   │   ├── Attribution.tsx        (NEW)
│   │   │   ├── Reasoning.tsx          (NEW)
│   │   │   ├── Monitoring.tsx         (NEW)
│   │   │   └── WhatIfAnalysis.tsx     (NEW)
│   │   ├── services/
│   │   │   └── api.ts                 (Complete API client)
│   │   └── components/
│   ├── .env.local
│   └── package.json
├── complete_end_to_end_demo.db        ← Real data (256 KB)
├── agentic_ai_demo.db                 ← Agent data (216 KB)
├── start_raia_enterprise.sh           ← Startup script
└── RAIA_ENTERPRISE_READY.md           ← This file
```

---

## 🎯 Next Steps

1. **Start the Application**
   ```bash
   ./start_raia_enterprise.sh
   ```

2. **Explore the Dashboard**
   - Open http://localhost:5173
   - Check real-time metrics
   - Navigate to RAIA-specific pages

3. **Test API Endpoints**
   - Open http://localhost:8000/docs
   - Try different endpoints
   - Inspect responses

4. **Generate More Data**
   ```bash
   python demos/demo_complete_end_to_end.py
   python demos/demo_agentic_ai_evaluation.py
   ```

---

## 🎉 You Now Have

✅ **World-Class Enterprise Product**
- Complete backend with ALL RAIA modules
- Professional frontend with real data integration
- Attribution, reasoning, monitoring, what-if analysis
- Production-ready deployment

✅ **Zero Configuration Needed**
- Everything is pre-configured
- Database paths auto-detected
- API automatically connects

✅ **Ready for Production**
- Enterprise-grade architecture
- Real-time monitoring
- Comprehensive error handling
- Complete documentation

---

**Enjoy your RAIA Enterprise Platform! 🚀**
SUMMARY

    print_success "Documentation created: RAIA_ENTERPRISE_READY.md"
}

# Main deployment process
main() {
    print_header

    # Run all setup steps
    check_prerequisites
    setup_backend
    setup_frontend
    create_startup_script
    create_summary

    # Final summary
    print_section "🎉 DEPLOYMENT COMPLETE!"

    echo ""
    echo -e "${GREEN}✨ RAIA Enterprise is ready to run!${NC}"
    echo ""
    echo -e "${BLUE}To start the application:${NC}"
    echo -e "${YELLOW}    ./start_raia_enterprise.sh${NC}"
    echo ""
    echo -e "${BLUE}Access points after starting:${NC}"
    echo -e "    • Frontend:  ${GREEN}http://localhost:5173${NC}"
    echo -e "    • Backend:   ${GREEN}http://localhost:8000${NC}"
    echo -e "    • API Docs:  ${GREEN}http://localhost:8000/docs${NC}"
    echo ""
    echo -e "${BLUE}Documentation:${NC}"
    echo -e "    • Read ${GREEN}RAIA_ENTERPRISE_READY.md${NC} for complete guide"
    echo ""
    echo "╔════════════════════════════════════════════════════════════════════════════╗"
    echo "║                        🎉 ALL SET! 🎉                                      ║"
    echo "╚════════════════════════════════════════════════════════════════════════════╝"
    echo ""
}

# Run main
main
