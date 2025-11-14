# RAIA Project - Key Files Reference Guide

**Complete file inventory for understanding the codebase architecture**

---

## Backend (FastAPI)

### Main API Server
- **`backend/main.py`** (870 lines) - All 20+ REST endpoints
  - Dashboard endpoints
  - RAG metrics endpoints
  - Agent evaluation endpoints
  - Monitoring endpoints
  - What-If analysis endpoints
  - Analytics endpoints

### Backend Configuration
- **`backend/requirements.txt`** - Python dependencies
  - FastAPI 0.104.1
  - Uvicorn 0.24.0
  - Pydantic 2.5.0
  - python-multipart

### Backend Startup
- **`backend/run.sh`** - Simple startup script
- **`backend/venv/`** - Python virtual environment (50 MB)

### Backend Database
- **`backend/complete_end_to_end_demo.db`** - Empty database file (created on startup)

---

## Frontend (React + TypeScript)

### Main Application
- **`frontend/src/App.tsx`** - Main app component with routing

### Pages (15 Total)
#### Core Pages
- **`frontend/src/pages/Dashboard.tsx`** - Main overview dashboard
- **`frontend/src/pages/RAIADashboard.tsx`** - RAIA-specific dashboard

#### RAIA Feature Pages
- **`frontend/src/pages/Attribution.tsx`** - Answer-source mapping visualization
- **`frontend/src/pages/Reasoning.tsx`** - Step-by-step execution traces
- **`frontend/src/pages/Monitoring.tsx`** - Drift detection & system health
- **`frontend/src/pages/WhatIfAnalysis.tsx`** - Counterfactuals & optimization

#### Metric Pages
- **`frontend/src/pages/OutputQuality.tsx`** - Answer quality metrics
- **`frontend/src/pages/Performance.tsx`** - Latency & throughput
- **`frontend/src/pages/Robustness.tsx`** - Error handling & reliability
- **`frontend/src/pages/Safety.tsx`** - Safety & ethics metrics
- **`frontend/src/pages/UserExperience.tsx`** - User satisfaction
- **`frontend/src/pages/Compliance.tsx`** - Compliance tracking

#### Analysis Pages
- **`frontend/src/pages/History.tsx`** - Evaluation history
- **`frontend/src/pages/Compare.tsx`** - A/B comparison
- **`frontend/src/pages/Reports.tsx`** - Report generation

### API Client
- **`frontend/src/services/api.ts`** (400+ lines)
  - Centralized API service
  - All 20+ endpoint definitions
  - Response type definitions
  - Error handling
  - React Query integration

### Frontend Components
- **`frontend/src/components/`** - Reusable UI components

### Frontend Configuration
- **`frontend/.env.local`** - Environment variables
  ```
  VITE_API_BASE_URL=http://localhost:8000
  VITE_DEV_MODE=true
  ```

### Frontend Dependencies
- **`frontend/package.json`** - npm dependencies (20+ packages)
- **`frontend/node_modules/`** - Installed dependencies (351 MB)

### Frontend Configuration Files
- **`frontend/tsconfig.json`** - TypeScript configuration
- **`frontend/tsconfig.app.json`** - App TypeScript config
- **`frontend/tsconfig.node.json`** - Node TypeScript config
- **`frontend/vite.config.ts`** - Vite build configuration

---

## Python SDK (raia/)

### Main Package
- **`raia/__init__.py`** (178 lines)
  - Main exports
  - Module initialization
  - Version definition

### Configuration
- **`raia/config.py`** - Configuration management

### Data Models
- **`raia/models.py`** - Core data models (agent runs, node metrics)
- **`raia/models_rag.py`** - RAG evaluation models
- **`raia/models_explainability.py`** - Attribution & reasoning models
- **`raia/models_whatif.py`** - What-if analysis models
- **`raia/models_comparison.py`** - Comparison & reporting models

### Event Logging System (`raia/events/`)
- **`raia/events/__init__.py`** - Event module initialization
- **`raia/events/emitter.py`** - Event batching & dispatch
- **`raia/events/redactor.py`** - PII/PHI redaction
- **`raia/events/signer.py`** - HMAC signing

### Inspectors (`raia/inspectors/`)
- **`raia/inspectors/__init__.py`** - Inspector module init
- **`raia/inspectors/base.py`** - Abstract base inspector
- **`raia/inspectors/execution.py`** - Execution metrics inspector
- **`raia/inspectors/behavior.py`** - Behavioral pattern inspector
- **`raia/inspectors/rag.py`** - RAG-specific inspector
- **`raia/inspectors/semantic.py`** - Semantic evaluation inspector

### Storage Layer (`raia/storage/`)
- **`raia/storage/__init__.py`** - Storage module init
- **`raia/storage/base.py`** - Abstract storage interface
- **`raia/storage/sqlite.py`** - SQLite implementation

### Framework Integrations (`raia/integrations/`)
- **`raia/integrations/__init__.py`** - Integration module init
- **`raia/integrations/langchain.py`** - LangChain integration
- **`raia/integrations/langgraph.py`** - LangGraph integration

### Utilities (`raia/utils/`)
- **`raia/utils/__init__.py`** - Utils module init
- **`raia/utils/comparison.py`** - Run comparison logic
- **`raia/utils/drift_detection.py`** - Embedding drift analysis

### Tests (`raia/tests/`)
- **`raia/tests/test_execution_inspector.py`**
- **`raia/tests/test_behavior_inspector.py`**
- **`raia/tests/test_semantic_inspector.py`**
- **`raia/tests/test_storage_sqlite.py`**

### Examples (`raia/examples/`)
- **`raia/examples/example_langchain_usage.py`**
- **`raia/examples/example_langgraph_usage.py`**
- **`raia/examples/demo_5_agent_system.py`**

---

## Demo Scripts

### Primary Demos (RECOMMENDED)
- **`demo_complete_end_to_end.py`** (903 lines)
  - Main comprehensive demo
  - Customer support scenario
  - All metrics demonstrated
  - Populates `complete_end_to_end_demo.db`

- **`demo_agentic_ai_evaluation.py`** (526 lines)
  - Multi-step agent execution
  - Tool usage demonstration
  - Populates `agentic_ai_demo.db`

- **`demo_drift_impact_analysis.py`** (545 lines)
  - Embedding drift detection
  - Medical documentation scenario
  - Shows cause-effect relationships
  - Populates `drift_impact_analysis.db`

### Secondary Demos
- **`demo_explainability.py`** (535 lines) - Attribution & reasoning
- **`demo_whatif.py`** (386 lines) - Counterfactual analysis
- **`demo_realistic_computed_metrics.py`** (442 lines) - Realistic data
- **`demo_quickstart.py`** (280 lines) - Minimal quick start

### Redundant/Deprecated Demos (REMOVE)
- **`demo_complete.py`** (318 lines) - Simplified duplicate
- **`demo_complete_FULL.py`** (104 lines) - Stub
- **`demo_complete_all_features.py`** (1017 lines) - Duplicate of end_to_end

### Other Scripts
- **`populate_all_tables.py`** (570 lines) - Data population utility

---

## Deployment Scripts

### Main Deployment
- **`scripts/DEPLOY_RAIA_ENTERPRISE.sh`** (15 KB, 450+ lines)
  - Primary deployment script
  - Creates venv
  - Installs all dependencies
  - Configures environment
  - **RECOMMENDED: Use this one**

### Application Startup
- **`scripts/start_raia_enterprise.sh`** (3 KB)
  - Starts backend and frontend
  - **RECOMMENDED: Use this one**

### Alternative/Redundant Scripts
- **`scripts/DEPLOY_FULL_STACK.sh`** - Alternative deployment (duplicate)
- **`scripts/quickstart.sh`** - Quick start variant
- **`scripts/setup_frontend.sh`** - Frontend-only setup
- **`scripts/setup_team.sh`** - Team setup variant
- **`backend/run.sh`** - Backend-only startup
- **`scripts/run.sh`** - Generic run script

---

## Documentation

### Core Documentation (READ THESE)
- **`README.md`** - Main project documentation
  - Quick start
  - Feature overview
  - Architecture diagram
  - Installation instructions
  - API reference
  - Technology stack

- **`docs/QUICK_START.md`** - 5-minute quick start guide
- **`docs/INTEGRATION_COMPLETE.md`** - Technical implementation details

### Feature-Specific Documentation
- **`docs/AGENTIC_AI_METRICS_SUMMARY.md`** - Agent evaluation guide
- **`docs/DRIFT_DETECTION_SUMMARY.md`** - Drift detection guide
- **`docs/COMPLETE_END_TO_END_GUIDE.md`** - End-to-end tutorial

### Additional Documentation (BLOAT - CONSOLIDATE)
- **`docs/RAIA_ENTERPRISE_READY.md`** - User guide
- **`docs/DELIVERABLES_SUMMARY.md`** - Deliverables summary
- **`docs/DRIFT_IMPACT_COMPLETE_STORY.md`** - Drift impact story
- **`docs/EMBEDDING_DRIFT_DETECTION.md`** - Embedding drift deep dive
- **`docs/DOCKER_SETUP.md`** - Docker setup guide
- **`docs/DOCKER_TROUBLESHOOTING.md`** - Docker troubleshooting
- **`docs/ENTERPRISE_DASHBOARD_COMPLETE.md`** - Dashboard guide
- **`docs/FEATURES.md`** - Feature list
- **`docs/FULL_STACK_QUICKSTART.md`** - Full stack quick start
- **`docs/IMPROVEMENTS_SUMMARY.md`** - Improvements list
- **`docs/DELIVERY_SUMMARY.md`** - Delivery summary
- **`docs/CREATE_FULL_STACK_APP.md`** - Full stack creation
- **`docs/UNIFIED_LIBRARY_README.md`** - Unified library readme
- **`docs/RAG_IMPLEMENTATION_SUMMARY.md`** - RAG implementation

### Root-Level Summary Files (ARCHIVE)
- **`PROJECT_STRUCTURE.md`** - Project structure (duplicate)
- **`FOLDER_STRUCTURE.txt`** - Folder structure text (duplicate)
- **`COMPLETION_SUMMARY.md`** - Completion notes
- **`FINAL_SUMMARY.md`** - Final summary
- **`CLEANUP_SUMMARY.txt`** - Cleanup history

---

## Configuration & Build Files

### Python Configuration
- **`pyproject.toml`** - Python project metadata
  - Package name: raia
  - Version: 1.0.0
  - Dependencies defined
  - Build system configured

- **`setup.py`** - Legacy setup script

### Docker Configuration
- **`Dockerfile`** - Docker image definition
  - Python 3.11 slim base
  - Installs dependencies
  - Sets up RAIA package

- **`docker-compose.yml`** - Docker Compose configuration
  - Test runner service
  - Shell service
  - Examples runner service

- **`.dockerignore`** - Docker ignore rules

### Git Configuration
- **`.gitignore`** - Git ignore rules
- **`.git/`** - Git repository

### Frontend Build Configuration
- **`frontend/vite.config.ts`** - Vite build config
- **`frontend/tsconfig.json`** - TypeScript config
- **`frontend/eslint.config.js`** - ESLint config
- **`frontend/postcss.config.js`** - PostCSS config
- **`frontend/tailwind.config.js`** - TailwindCSS config

### Claude Code Configuration
- **`.claude/`** - Claude Code settings

---

## Database Files

### Root Level (Demo Data - Main)
- **`complete_end_to_end_demo.db`** (328 KB)
  - Primary demo database
  - All 15 tables populated
  - Complete example data

- **`agentic_ai_demo.db`** (216 KB)
  - Agent evaluation demo
  - 4-agent system example

- **`drift_impact_analysis.db`** (200 KB)
  - Drift detection example
  - Medical documentation scenario

- **`realistic_computed_demo.db`** (204 KB)
  - Realistic metric computation
  - Production-like data

- **`complete_feature_demo.db`** (200 KB)
  - All features demonstration

### Data Subdirectory (Test Data)
- **`data/5_agent_enhanced_demo.db`** (40 KB)
- **`data/5_agent_metrics.db`** (65 KB)
- **`data/enhanced_metrics_demo.db`** (40 KB)
- **`data/test_enhanced.db`** (40 KB)
- **`data/5_agent_events.jsonl`** (3.4 KB)

---

## File Organization by Purpose

### For Getting Started
1. Read: `README.md`
2. Read: `docs/QUICK_START.md`
3. Run: `./scripts/DEPLOY_RAIA_ENTERPRISE.sh`
4. Run: `./scripts/start_raia_enterprise.sh`
5. Visit: http://localhost:5173

### For Understanding Architecture
1. Read: `docs/INTEGRATION_COMPLETE.md`
2. View: `backend/main.py` (API endpoints)
3. View: `frontend/src/services/api.ts` (API client)
4. View: `raia/__init__.py` (SDK exports)

### For Running Demos
1. Choose: `demo_complete_end_to_end.py` (recommended)
2. Or: `demo_agentic_ai_evaluation.py` (agents)
3. Or: `demo_drift_impact_analysis.py` (drift detection)

### For Understanding Database
1. All 15 tables defined in: `backend/main.py`
2. All data models in: `raia/models*.py`
3. SQLite implementation: `raia/storage/sqlite.py`
4. Example database: `complete_end_to_end_demo.db`

### For Frontend Development
1. Pages: `frontend/src/pages/*.tsx`
2. Components: `frontend/src/components/`
3. API Client: `frontend/src/services/api.ts`
4. Styling: `frontend/src/*.css` (TailwindCSS)
5. Config: `frontend/.env.local`

### For Backend Development
1. Main API: `backend/main.py`
2. Dependencies: `backend/requirements.txt`
3. Config: `backend/.env` (if exists)
4. Startup: `backend/run.sh`

### For SDK Development
1. Core: `raia/__init__.py` (exports)
2. Models: `raia/models*.py`
3. Inspectors: `raia/inspectors/*.py`
4. Storage: `raia/storage/*.py`
5. Tests: `raia/tests/*.py`
6. Integrations: `raia/integrations/*.py`

---

## Absolute File Paths

All files located in: `/Users/abhishekbatchu/Documents/raia_agentic_evaluation/`

Backend: `/Users/abhishekbatchu/Documents/raia_agentic_evaluation/backend/`
Frontend: `/Users/abhishekbatchu/Documents/raia_agentic_evaluation/frontend/`
SDK: `/Users/abhishekbatchu/Documents/raia_agentic_evaluation/raia/`
Scripts: `/Users/abhishekbatchu/Documents/raia_agentic_evaluation/scripts/`
Docs: `/Users/abhishekbatchu/Documents/raia_agentic_evaluation/docs/`
Data: `/Users/abhishekbatchu/Documents/raia_agentic_evaluation/data/`

---

## File Count Summary

- Backend Files: ~10 files (main code + config)
- Frontend Files: ~50+ files (pages, components, config)
- SDK Files: ~30 files (modules, inspectors, tests)
- Documentation: 22 files (bloated)
- Demo Scripts: 9 files (redundant)
- Database Files: 9 files (fragmented)
- Configuration: ~10 files

**Total: 140+ files (excluding node_modules and venv)**

---

For the complete analysis, see: **CODEBASE_ANALYSIS.md**
For quick reference, see: **ANALYSIS_SUMMARY.txt**
