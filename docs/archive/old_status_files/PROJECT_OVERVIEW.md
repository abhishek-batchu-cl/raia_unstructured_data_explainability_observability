# RAIA - Responsible AI Analytics & Agent Evaluation

Complete full-stack platform for evaluating RAG systems and agentic AI applications.

## Quick Start

### 1. Run a Demo (Choose One)

```bash
# Complete end-to-end demo (recommended first)
python demos/01_complete_demo.py

# Quick minimal demo
python demos/02_quickstart.py

# Agent-specific evaluation
python demos/03_agentic_evaluation.py
```

### 2. Start the Application

```bash
# Option A: Use the startup script (recommended)
./scripts/start_raia_enterprise.sh

# Option B: Manual start
# Terminal 1 - Backend
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### 3. Access the Application

- **Frontend Dashboard**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **API Schema**: http://localhost:8000/openapi.json

## Project Structure

```
raia_agentic_evaluation/
├── README.md                     # Main documentation
├── PROJECT_OVERVIEW.md           # This file
│
├── backend/                      # FastAPI Backend (850 lines)
│   ├── main.py                   # All 20+ REST endpoints
│   ├── requirements.txt          # Python dependencies
│   ├── run.sh                    # Backend startup script
│   └── venv/                     # Python virtual environment
│
├── frontend/                     # React 19 + TypeScript Frontend
│   ├── src/
│   │   ├── pages/                # 15 page components
│   │   ├── services/api.ts       # API client (459 lines)
│   │   ├── components/           # Reusable UI components
│   │   ├── hooks/                # Custom React hooks
│   │   └── App.tsx               # Main app with routing
│   ├── package.json              # Dependencies
│   ├── .env.local                # Configuration
│   └── node_modules/             # Installed dependencies
│
├── raia/                         # Python SDK (4500+ lines)
│   ├── __init__.py               # Main exports
│   ├── events/                   # Event logging system
│   ├── inspectors/               # Behavioral analysis
│   ├── integrations/             # LangChain/LangGraph
│   ├── storage/                  # Persistence layer
│   ├── utils/                    # Utilities
│   └── tests/                    # Unit tests
│
├── demos/                        # Organized Demo Scripts
│   ├── README.md                 # Demo documentation
│   ├── 01_complete_demo.py       # Complete end-to-end demo
│   ├── 02_quickstart.py          # Quick start demo
│   └── 03_agentic_evaluation.py  # Agent evaluation demo
│
├── docs/                         # Core Documentation (6 files)
│   ├── QUICK_START.md            # Getting started guide
│   ├── INTEGRATION_COMPLETE.md   # Technical reference
│   ├── FEATURES.md               # Feature documentation
│   ├── DOCKER_SETUP.md           # Docker deployment
│   ├── DOCKER_TROUBLESHOOTING.md # Docker help
│   └── EMBEDDING_DRIFT_DETECTION.md # Drift detection guide
│
├── data/                         # Data Storage
│   └── demo_databases/           # Demo database files
│       ├── complete_end_to_end_demo.db (328 KB)
│       ├── agentic_ai_demo.db (216 KB)
│       └── [other demo databases]
│
├── scripts/                      # Deployment Scripts (2 files)
│   ├── start_raia_enterprise.sh  # Startup script
│   └── DEPLOY_RAIA_ENTERPRISE.sh # Deployment script
│
├── archive/                      # Archived Files
│   ├── old_demos/                # Old demo versions
│   ├── old_docs/                 # Old documentation
│   └── old_scripts/              # Old deployment scripts
│
├── tools/                        # Utility tools
├── examples/                     # Example scripts
│
├── docker-compose.yml            # Docker Compose config
├── Dockerfile                    # Docker image definition
├── pyproject.toml                # Python package metadata
└── setup.py                      # Python package setup
```

## Technology Stack

### Backend
- **Framework**: FastAPI 0.104.1
- **Server**: Uvicorn 0.24.0
- **Database**: SQLite (15 tables)
- **Validation**: Pydantic
- **Python**: 3.10+

### Frontend
- **Framework**: React 19.1.1
- **Language**: TypeScript 5.9.3
- **Build Tool**: Vite 7.1.7
- **Styling**: TailwindCSS 3.4.18
- **State Management**: Zustand 5.0.8
- **Data Fetching**: React Query 5.90.5
- **Routing**: React Router 7.9.4
- **Charts**: Recharts 3.3.0, D3 7.9.0

### SDK
- **Core**: Pydantic, aiohttp
- **Optional**: LangChain, LangGraph, Kafka

## API Endpoints (20+)

### Dashboard
- `GET /api/dashboard` - Summary metrics with KPIs
- `GET /api/runs/{run_id}` - Individual run details

### RAG Metrics
- `GET /api/retrieval` - Precision, Recall, F1, MRR, NDCG
- `GET /api/answer-quality` - Faithfulness, Hallucination, Relevance
- `GET /api/semantic` - Similarity, Coherence, Fluency

### Agent Metrics
- `GET /api/agent/executions` - Agent execution history
- `GET /api/agent/decisions` - Decision points
- `GET /api/node-metrics` - Per-node execution stats
- `GET /api/pipeline` - End-to-end pipeline metrics

### Monitoring
- `GET /api/monitoring/drift` - Embedding drift detection
- `GET /api/monitoring/vector-health` - Index performance
- `GET /api/monitoring/signals` - Functional signals

### What-If Analysis
- `GET /api/whatif/counterfactuals` - Scenario modeling
- `GET /api/whatif/sensitivity` - Parameter sensitivity
- `GET /api/whatif/optimization` - AI recommendations

### Analytics
- `GET /api/analytics/timeseries` - Historical trends
- `GET /api/analytics/export` - CSV/JSON export

## Database Schema (15 Tables)

### Core Execution
1. `raia_runs` - Run metadata & performance
2. `raia_node_metrics` - Per-node execution stats
3. `raia_functional_signals` - Tool & LLM calls
4. `raia_semantic_scores` - Semantic quality metrics

### RAG Evaluation
5. `raia_retrieval_metrics` - Precision, Recall, F1, MRR, NDCG
6. `raia_answer_quality_metrics` - Faithfulness, Hallucination
7. `raia_vector_index_health` - Index performance metrics
8. `raia_pipeline_metrics` - End-to-end RAG metrics

### Monitoring
9. `raia_embedding_drift_metrics` - KL/JS divergence, Wasserstein

### Explainability
10. `raia_attribution_maps` - Answer-source mapping
11. `raia_reasoning_traces` - Step-by-step reasoning
12. `raia_agent_decisions` - Decision points

### What-If Analysis
13. `raia_counterfactual_scenarios` - Scenario modeling
14. `raia_sensitivity_analyses` - Parameter sensitivity
15. `raia_optimization_recommendations` - AI recommendations

## Frontend Pages (15)

1. **Dashboard** - Overview with KPIs
2. **RAIADashboard** - Comprehensive analytics
3. **Attribution** - Answer-source mapping
4. **Reasoning** - Reasoning traces
5. **Monitoring** - Drift & health monitoring
6. **Performance** - Performance metrics
7. **OutputQuality** - Output quality analysis
8. **Safety** - Safety evaluation
9. **Compliance** - Compliance checks
10. **Robustness** - Robustness testing
11. **UserExperience** - UX metrics
12. **WhatIfAnalysis** - What-if scenarios
13. **Compare** - Run comparison
14. **History** - Historical analysis
15. **Reports** - Report generation

## Key Features

### RAG Evaluation
- Retrieval metrics (Precision, Recall, F1, MRR, NDCG)
- Answer quality (Faithfulness, Hallucination detection)
- Attribution mapping (answer-to-source)
- Semantic evaluation (Similarity, Coherence, Fluency)

### Agent Evaluation
- Execution tracking
- Decision point analysis
- Node-level metrics
- Tool usage monitoring

### Monitoring
- Embedding drift detection (KL/JS divergence, Wasserstein distance)
- Vector index health monitoring
- Functional signal tracking
- Real-time alerting

### Explainability
- Step-by-step reasoning traces
- Attribution maps
- Decision logging
- Confidence scoring

### What-If Analysis
- Counterfactual scenarios
- Parameter sensitivity analysis
- AI-powered optimization recommendations

### Analytics
- Time-series analysis
- Trend visualization
- Export to CSV/JSON/Excel
- Custom filtering and aggregation

## Development

### Backend Development
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Running Demos
```bash
# From project root
python demos/01_complete_demo.py
python demos/02_quickstart.py
python demos/03_agentic_evaluation.py
```

## Deployment

### Docker
```bash
# Build and run with Docker Compose
docker-compose up --build

# Or use deployment script
./scripts/DEPLOY_RAIA_ENTERPRISE.sh
```

### Manual Deployment
1. Set up Python virtual environment
2. Install backend dependencies
3. Install frontend dependencies
4. Configure environment variables
5. Run startup script

## Configuration

### Backend Configuration
Edit `backend/main.py` or set environment variables:
- Database path
- CORS origins
- API settings

### Frontend Configuration
Edit `frontend/.env.local`:
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_DEV_MODE=true
```

## Architecture

### Request Flow
1. **Frontend** (React) → User interaction
2. **API Service** (api.ts) → HTTP request
3. **Backend** (FastAPI) → Process request
4. **Database** (SQLite) → Query data
5. **Backend** → JSON response
6. **React Query** → Cache response
7. **Frontend** → Re-render UI

### CORS Configuration
- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- CORS enabled for all methods and headers (dev mode)

## Production Readiness

### ✅ Production-Ready Components
- FastAPI backend with comprehensive endpoints
- React 19 frontend with modern architecture
- Complete database schema (15 tables)
- Docker deployment support
- Comprehensive error handling
- Input validation with Pydantic

### ⚠️ Recommended Additions for Production
1. **Security**
   - Add authentication (OAuth2/JWT)
   - Implement rate limiting
   - Add API key management

2. **Database**
   - Migrate to PostgreSQL for production
   - Add connection pooling
   - Implement backup strategy

3. **Monitoring**
   - Add Prometheus metrics
   - Set up Grafana dashboards
   - Implement logging (ELK stack)

4. **Performance**
   - Add Redis caching layer
   - Implement CDN for frontend
   - Optimize database queries

5. **Testing**
   - Add integration tests
   - Add E2E tests
   - Performance testing

6. **CI/CD**
   - Set up GitHub Actions
   - Automated testing
   - Automated deployment

## Contributing

This project follows a clean, organized structure:
- **Production code**: `backend/`, `frontend/`, `raia/`
- **Demo scripts**: `demos/`
- **Documentation**: `docs/`
- **Archived files**: `archive/`

## License

[Add license information here]

## Support

For issues and questions:
- Check documentation in `docs/`
- Review demo scripts in `demos/`
- Consult API documentation at http://localhost:8000/docs

---

**Version**: 1.0.0
**Last Updated**: November 2025
**Status**: Production-Ready (with recommended additions for enterprise scale)
