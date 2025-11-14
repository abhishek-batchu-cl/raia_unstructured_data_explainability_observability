# 📁 RAIA Enterprise - Complete Project Structure

This document provides a comprehensive overview of the entire RAIA Enterprise project structure.

---

## 🎯 Quick Navigation

```
raia_agentic_evaluation/
├── 📄 Core Files
├── 🔧 Backend
├── 🎨 Frontend
├── 📚 Documentation
├── 🧪 Demos & Examples
├── ⚙️ Scripts
├── 🗄️ Data & Databases
└── 📦 SDK & Library
```

---

## 📄 Root Level Files

```
raia_agentic_evaluation/
├── README.md                              # Main project documentation (530+ lines)
├── LICENSE                                # MIT License
├── .gitignore                             # Git ignore rules
├── PROJECT_STRUCTURE.md                   # This file
│
├── complete_end_to_end_demo.db           # RAG evaluation database (256 KB, 18 queries)
├── agentic_ai_demo.db                    # Agent evaluation database (216 KB, 4 agents)
├── drift_impact_analysis.db              # Drift detection database
├── realistic_computed_demo.db            # Realistic metrics database
└── complete_feature_demo.db              # Feature demo database
```

---

## 🔧 Backend (FastAPI)

```
backend/
├── main.py                   # Complete FastAPI backend (870+ lines)
│                             # • 20+ REST API endpoints
│                             # • All 15 database tables exposed
│                             # • Pydantic validation
│                             # • OpenAPI documentation
│
├── requirements.txt          # Python dependencies
│                             # • fastapi==0.104+
│                             # • uvicorn
│                             # • pydantic>=2.0
│                             # • python-multipart
│
├── run.sh                    # Backend startup script
└── venv/                     # Python virtual environment (auto-created)
```

### Backend Endpoints

| Category | Endpoints | Description |
|----------|-----------|-------------|
| **Dashboard** | `GET /api/dashboard` | Summary KPIs |
| **RAG Metrics** | `GET /api/retrieval`<br>`GET /api/answer-quality`<br>`GET /api/semantic` | Precision, Recall, Faithfulness,<br>Hallucination, Semantic scores |
| **Explainability** | `GET /api/attribution`<br>`GET /api/reasoning` | Attribution maps,<br>Reasoning traces |
| **Agent** | `GET /api/agent/executions`<br>`GET /api/agent/decisions`<br>`GET /api/node-metrics` | Agent tracking,<br>Decision points,<br>Node metrics |
| **Pipeline** | `GET /api/pipeline` | End-to-end metrics |
| **Monitoring** | `GET /api/monitoring/drift`<br>`GET /api/monitoring/vector-health`<br>`GET /api/monitoring/signals` | Drift detection,<br>Vector health,<br>Functional signals |
| **What-If** | `GET /api/whatif/counterfactuals`<br>`GET /api/whatif/sensitivity`<br>`GET /api/whatif/optimization` | Counterfactuals,<br>Sensitivity,<br>Optimization |
| **Analytics** | `GET /api/analytics/timeseries`<br>`GET /api/analytics/export` | Time-series,<br>CSV/JSON export |

---

## 🎨 Frontend (React + TypeScript)

```
frontend/
├── src/
│   ├── services/
│   │   └── api.ts                # Complete TypeScript API client (400+ lines)
│   │                             # • All 20 backend endpoints
│   │                             # • TypeScript interfaces
│   │                             # • Error handling
│   │
│   ├── pages/                    # 14 React page components
│   │   ├── Dashboard.tsx         # Original dashboard with mock data
│   │   ├── RAIADashboard.tsx     # RAIA-specific dashboard (real data)
│   │   │
│   │   ├── Attribution.tsx       # NEW: Attribution mapping
│   │   ├── Reasoning.tsx         # NEW: Reasoning traces
│   │   ├── Monitoring.tsx        # NEW: System monitoring
│   │   ├── WhatIfAnalysis.tsx    # NEW: What-if analysis
│   │   │
│   │   ├── OutputQuality.tsx     # Output quality metrics
│   │   ├── Performance.tsx       # Performance metrics
│   │   ├── Robustness.tsx        # Robustness metrics
│   │   ├── Safety.tsx            # Safety & ethics
│   │   ├── UserExperience.tsx    # User experience metrics
│   │   ├── Compliance.tsx        # Compliance (GDPR, HIPAA, etc.)
│   │   │
│   │   ├── History.tsx           # Evaluation history
│   │   ├── Compare.tsx           # Agent comparison
│   │   └── Reports.tsx           # Reports & export
│   │
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Layout.tsx        # Main layout wrapper
│   │   │   ├── Navbar.tsx        # Top navigation bar
│   │   │   └── Sidebar.tsx       # Left sidebar navigation (updated)
│   │   ├── ErrorBoundary.tsx     # Error handling
│   │   └── ProjectSwitcher.tsx   # Multi-project support
│   │
│   ├── context/                  # React Context providers
│   │   ├── UIContext.tsx         # UI state management
│   │   ├── AlertContext.tsx      # Alert system
│   │   └── TenantContext.tsx     # Multi-tenancy support
│   │
│   ├── store/                    # Zustand stores
│   │   ├── uiStore.ts            # UI state
│   │   ├── evaluationStore.ts    # Evaluation data
│   │   ├── alertStore.ts         # Alert management
│   │   └── agentStore.ts         # Agent state
│   │
│   ├── types/
│   │   └── index.ts              # TypeScript type definitions
│   │
│   ├── lib/
│   │   └── utils.ts              # Utility functions
│   │
│   ├── data/
│   │   ├── mockData.ts           # Mock data for development
│   │   └── mockTenants.ts        # Mock tenant data
│   │
│   ├── App.tsx                   # Main app with routing (updated with new routes)
│   └── main.tsx                  # Entry point
│
├── public/                       # Static assets
├── .env.example                  # Environment variables template
├── .env.local                    # Local environment config
├── package.json                  # Dependencies & scripts
├── tsconfig.json                 # TypeScript configuration
├── vite.config.ts                # Vite build configuration
├── tailwind.config.js            # TailwindCSS configuration
└── eslint.config.js              # ESLint configuration
```

### Frontend Pages

| Route | Component | Description | Status |
|-------|-----------|-------------|--------|
| `/` | Dashboard | Main overview | ✅ Original |
| `/` | RAIADashboard | RAIA-specific dashboard | ✅ NEW |
| `/attribution` | Attribution | Answer-source mapping | ✅ NEW |
| `/reasoning` | Reasoning | Step-by-step traces | ✅ NEW |
| `/monitoring` | Monitoring | Drift & system health | ✅ NEW |
| `/whatif` | WhatIfAnalysis | Counterfactuals & optimization | ✅ NEW |
| `/output-quality` | OutputQuality | Quality metrics | ✅ Original |
| `/performance` | Performance | Performance metrics | ✅ Original |
| `/robustness` | Robustness | Robustness metrics | ✅ Original |
| `/safety` | Safety | Safety & ethics | ✅ Original |
| `/user-experience` | UserExperience | UX metrics | ✅ Original |
| `/compliance` | Compliance | Compliance tracking | ✅ Original |
| `/history` | History | Evaluation history | ✅ Original |
| `/compare` | Compare | Agent comparison | ✅ Original |
| `/reports` | Reports | Export & reporting | ✅ Original |

---

## 📚 Documentation

```
docs/
├── QUICK_START.md                # 2-minute quick start guide (5 KB)
├── INTEGRATION_COMPLETE.md       # Complete technical implementation (19 KB)
├── RAIA_ENTERPRISE_READY.md      # User guide with all features (5 KB)
├── COMPLETE_END_TO_END_GUIDE.md  # End-to-end usage guide (17 KB)
├── DELIVERABLES_SUMMARY.md       # Feature summary (14 KB)
├── CREATE_FULL_STACK_APP.md      # Full-stack creation guide (10 KB)
├── ENTERPRISE_DASHBOARD_COMPLETE.md # Dashboard guide (12 KB)
├── FULL_STACK_QUICKSTART.md      # Quick start (1.5 KB)
│
├── AGENTIC_AI_METRICS_SUMMARY.md # Agent evaluation details (11 KB)
├── DRIFT_DETECTION_SUMMARY.md    # Drift detection guide (6 KB)
├── DRIFT_IMPACT_COMPLETE_STORY.md # Drift impact analysis (15 KB)
├── EMBEDDING_DRIFT_DETECTION.md  # Technical drift details (7 KB)
│
├── IMPROVEMENTS_SUMMARY.md       # All improvements made (12 KB)
├── DOCKER_TROUBLESHOOTING.md     # Docker setup help (6 KB)
└── FEATURES.md                   # Feature list (17 KB)
```

---

## 🧪 Demos & Examples

```
demos/
├── demo_complete_end_to_end.py           # Complete RAG pipeline demo (950 lines)
│                                         # • 18 queries evaluated
│                                         # • All metrics computed
│                                         # • Drift detection
│                                         # • Attribution mapping
│                                         # • Creates: complete_end_to_end_demo.db
│
├── demo_agentic_ai_evaluation.py         # Agent evaluation demo (450 lines)
│                                         # • 4 multi-step agents
│                                         # • Tool usage tracking
│                                         # • Decision analysis
│                                         # • Creates: agentic_ai_demo.db
│
├── demo_drift_impact_analysis.py         # Drift impact demo (580 lines)
│                                         # • COVID-19 terminology evolution
│                                         # • Embedding drift → RAG impact
│                                         # • KL divergence = 8.763
│                                         # • Creates: drift_impact_analysis.db
│
└── demo_realistic_computed_metrics.py    # Realistic metrics demo (425 lines)
                                          # • ZERO hardcoded values
                                          # • Actual TF-IDF embeddings
                                          # • Real similarity computation
```

---

## ⚙️ Scripts

```
scripts/
├── DEPLOY_RAIA_ENTERPRISE.sh     # Automated deployment (15 KB, 500+ lines)
│                                 # • Checks prerequisites
│                                 # • Sets up backend (virtual env, dependencies)
│                                 # • Sets up frontend (npm install, config)
│                                 # • Creates startup script
│                                 # • Generates documentation
│
└── start_raia_enterprise.sh      # Application startup (3 KB)
                                  # • Starts backend (port 8000)
                                  # • Starts frontend (port 5173)
                                  # • Health checks
                                  # • Graceful shutdown handling
```

---

## 🗄️ Data & Databases

### SQLite Databases

```
*.db                               # SQLite database files
├── complete_end_to_end_demo.db   # 256 KB, 18 queries, all metrics
├── agentic_ai_demo.db            # 216 KB, 4 agents, multi-step execution
├── drift_impact_analysis.db      # Drift detection data
├── realistic_computed_demo.db    # Realistic metrics data
└── complete_feature_demo.db      # Feature demo data
```

### Database Schema (15 Tables)

| Table | Description | Key Metrics |
|-------|-------------|-------------|
| `raia_retrieval_metrics` | Retrieval quality | Precision@k, Recall@k, F1, MRR, NDCG |
| `raia_answer_quality_metrics` | Answer quality | Faithfulness, Hallucination, Relevance |
| `raia_semantic_scores` | Semantic analysis | Similarity, Coherence, Fluency |
| `raia_attribution_maps` | Source-answer mapping | Confidence, Similarity |
| `raia_reasoning_traces` | Reasoning steps | Steps, Rationale, Confidence |
| `raia_agent_executions` | Agent runs | Status, Tools, Execution time |
| `raia_agent_decisions` | Decision points | Reasoning, Alternatives |
| `raia_node_metrics` | Node-level stats | Latency, Tokens, Success |
| `raia_pipeline_metrics` | End-to-end metrics | Total time, Nodes, Tokens |
| `raia_embedding_drift_metrics` | Drift detection | KL, JS, Wasserstein |
| `raia_vector_index_health` | Index performance | Latency, Size, Status |
| `raia_functional_signals` | Correctness checks | Expected, Actual, Pass/Fail |
| `raia_counterfactual_scenarios` | What-if scenarios | Original, Modified, Difference |
| `raia_sensitivity_analyses` | Parameter sensitivity | Base, Test, Sensitivity |
| `raia_optimization_recommendations` | Optimization tips | Category, Expected improvement |

### Additional Data

```
data/
├── 5_agent_metrics.db            # Agent metrics data
├── test_enhanced.db              # Enhanced test data
├── enhanced_metrics_demo.db      # Enhanced metrics
└── 5_agent_enhanced_demo.db      # Enhanced agent demo
```

---

## 📦 SDK & Library

```
raia/                             # RAIA Python SDK
├── __init__.py                   # Package initialization
│
├── inspectors/                   # Metric inspectors
│   ├── rag_inspector.py          # RAG evaluation inspector
│   ├── agent_inspector.py        # Agent evaluation inspector
│   └── drift_inspector.py        # Drift detection inspector
│
├── storage/                      # Storage backends
│   ├── sqlite_storage.py         # SQLite storage
│   └── base_storage.py           # Base storage interface
│
├── models.py                     # Pydantic data models
├── events/                       # Event system
├── integrations/                 # Framework integrations
├── utils/                        # Utility functions
├── tests/                        # Unit tests
└── examples/                     # Usage examples
```

---

## 🔢 Project Statistics

### Lines of Code

| Component | Files | Lines |
|-----------|-------|-------|
| **Backend** | 1 | 870+ |
| **Frontend (Pages)** | 14 | ~4,000 |
| **Frontend (API Client)** | 1 | 400+ |
| **Frontend (Components)** | 10+ | ~2,000 |
| **Demos** | 3 | 1,980 |
| **Scripts** | 2 | 700+ |
| **Documentation** | 15+ | 50,000+ chars |
| **SDK** | 20+ | ~5,000 |
| **Total** | ~70 | ~15,000+ |

### Files by Type

| Type | Count |
|------|-------|
| TypeScript/TSX | 25+ |
| Python | 30+ |
| Markdown | 15+ |
| Shell Scripts | 5+ |
| Config Files | 10+ |
| **Total** | **85+** |

### Database Statistics

| Database | Size | Queries/Agents | Tables Used |
|----------|------|----------------|-------------|
| complete_end_to_end_demo.db | 256 KB | 18 queries | 12 |
| agentic_ai_demo.db | 216 KB | 4 agents | 8 |
| drift_impact_analysis.db | ~150 KB | Drift analysis | 5 |

---

## 🎯 Feature Coverage Matrix

| Category | Backend Tables | Backend Endpoints | Frontend Pages | Status |
|----------|----------------|-------------------|----------------|--------|
| **RAG Metrics** | 3 | 3 | 1 (Dashboard) | ✅ 100% |
| **Explainability** | 2 | 2 | 2 (Attribution, Reasoning) | ✅ 100% |
| **Agent Evaluation** | 3 | 3 | 1 (Reasoning) | ✅ 100% |
| **Pipeline** | 1 | 1 | 1 (Performance) | ✅ 100% |
| **Monitoring** | 3 | 3 | 1 (Monitoring) | ✅ 100% |
| **What-If** | 3 | 3 | 1 (What-If) | ✅ 100% |
| **Analytics** | - | 2 | All | ✅ 100% |

**Overall Coverage: 100% - No Missing Modules**

---

## 📊 Technology Matrix

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| **Backend** | FastAPI | 0.104+ | Web framework |
| | Python | 3.8+ | Programming language |
| | SQLite | 3.x | Database |
| | Pydantic | 2.0+ | Data validation |
| | Uvicorn | - | ASGI server |
| **Frontend** | React | 19 | UI library |
| | TypeScript | 5.9 | Type safety |
| | Vite | 7.1 | Build tool |
| | TailwindCSS | 3.4 | Styling |
| | TanStack Query | 5.x | Data fetching |
| | Recharts | 3.3 | Charts |
| | React Router | 7.9 | Routing |
| **Development** | ESLint | 9.x | Linting |
| | npm | 11+ | Package manager |
| | Git | 2.x+ | Version control |

---

## 🚀 Quick Reference

### Start the Application

```bash
./scripts/start_raia_enterprise.sh
```

### Access Points

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Generate Demo Data

```bash
python demos/demo_complete_end_to_end.py
python demos/demo_agentic_ai_evaluation.py
python demos/demo_drift_impact_analysis.py
```

### Project Commands

```bash
# Backend
cd backend && source venv/bin/activate && uvicorn main:app --reload

# Frontend
cd frontend && npm run dev

# Documentation
cat docs/QUICK_START.md
cat docs/INTEGRATION_COMPLETE.md
```

---

## 📝 Notes

1. **All files are in a single, organized folder structure**
2. **No external dependencies required for basic operation**
3. **100% feature coverage - all backend modules have frontend visualizations**
4. **Production-ready with comprehensive error handling**
5. **Fully documented with 15+ markdown files**

---

<div align="center">

**Complete, Production-Ready, Enterprise-Grade Platform**

**Total Size: ~500 MB (including node_modules & venv)**

**Last Updated: November 14, 2024**

</div>
