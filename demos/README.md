# RAIA Demo Scripts

This directory contains organized demo scripts showcasing RAIA's capabilities.

## Available Demos

### 1. Complete Demo (`01_complete_demo.py`)
**Recommended for: First-time users and comprehensive testing**

- Complete end-to-end demonstration of all RAIA features
- Creates a fully populated database with realistic data
- Covers: RAG evaluation, agent metrics, drift detection, explainability, and what-if analysis
- Database: `complete_end_to_end_demo.db` (328 KB)
- Runtime: ~2-3 minutes

**Run:**
```bash
python demos/01_complete_demo.py
```

### 2. Quickstart (`02_quickstart.py`)
**Recommended for: Quick testing and getting started**

- Minimal demo covering basic RAIA functionality
- Creates a lightweight database with essential metrics
- Focuses on core RAG evaluation and agent metrics
- Database: `quickstart_demo.db` (~100 KB)
- Runtime: ~30 seconds

**Run:**
```bash
python demos/02_quickstart.py
```

### 3. Agentic AI Evaluation (`03_agentic_evaluation.py`)
**Recommended for: Agent-specific evaluation and testing**

- Focused demo on agentic AI evaluation capabilities
- Demonstrates agent decision tracking, node metrics, and execution traces
- Creates specialized agent evaluation database
- Database: `agentic_ai_demo.db` (216 KB)
- Runtime: ~1 minute

**Run:**
```bash
python demos/03_agentic_evaluation.py
```

## Archived Demos

Additional feature-specific demos are available in `/archive/old_demos/`:
- `demo_drift_impact_analysis.py` - Drift detection deep dive
- `demo_explainability.py` - Explainability features showcase
- `demo_whatif.py` - What-if analysis examples
- `demo_realistic_computed_metrics.py` - Realistic metric computation

These demos have been archived as their functionality is covered in the main demos above.

## Database Files

Demo databases are stored in `/data/demo_databases/` after running the demos.

## Next Steps

After running a demo:
1. Start the backend: `cd backend && ./run.sh`
2. Start the frontend: `cd frontend && npm run dev`
3. View results at: http://localhost:5173
4. Explore API docs at: http://localhost:8000/docs
