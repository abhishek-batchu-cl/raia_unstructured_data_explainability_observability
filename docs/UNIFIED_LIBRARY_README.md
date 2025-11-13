# RAIA - Unified Library Guide

## What Changed?

All RAIA functionality has been consolidated into a **single unified library**: `raia`

### Before (Two Separate Systems)
```python
# Old: Event logging
from sdk.python.raia import EventEmitter, EmitterConfig

# Old: Behavioral analysis
from raia_inspectors import RAIAExecutionInspector, RAIABehaviorInspector
```

### After (One Unified Library)
```python
# New: Everything from one package
from raia import (
    # Event Logging
    EventEmitter,
    EmitterConfig,
    Redactor,
    EventSigner,
    # Behavioral Analysis
    RAIAExecutionInspector,
    RAIABehaviorInspector,
    RAIASemanticInspector,
    # Storage
    SQLiteRAIAStorage,
    # Integrations
    LangChainCallbackHandler,
    stream_with_inspection,
)
```

---

## Package Structure

```
raia/
├── __init__.py                 # Main exports
├── config.py                   # Configuration
├── models.py                   # Data models
├── events/                     # Event logging system
│   ├── emitter.py             # Event emitter with batching
│   ├── redactor.py            # PII/PHI redaction
│   └── signer.py              # HMAC signing
├── inspectors/                 # Behavioral analysis
│   ├── execution.py           # Performance metrics
│   ├── behavior.py            # Pattern detection
│   └── semantic.py            # Quality evaluation
├── storage/                    # Storage backends
│   ├── base.py                # Storage interface
│   └── sqlite.py              # SQLite implementation
└── integrations/               # Framework integrations
    ├── langchain.py           # LangChain integration
    └── langgraph.py           # LangGraph integration
```

---

## Installation

### Option 1: From Source
```bash
git clone <repository>
cd raia_agentic_evaluation
pip install -e .
```

### Option 2: With Optional Dependencies
```bash
# For LangChain support
pip install -e ".[langchain]"

# For LangGraph support
pip install -e ".[langgraph]"

# For Kafka transport
pip install -e ".[kafka]"

# Everything
pip install -e ".[all]"
```

### Option 3: Docker (Recommended for Cross-Platform)
```bash
# Mac/Linux
./run.sh build
./run.sh test

# Windows
run.bat build
run.bat test
```

---

## Quick Start

### Event Logging (Production Telemetry)
```python
import asyncio
from raia import EventEmitter, EmitterConfig, TransportType

async def main():
    # Configure event emitter
    config = EmitterConfig(
        tenant="my-org",
        project="my-project",
        agent_id="my-agent",
        transport=TransportType.FILE,
        file_path="./logs/events.jsonl",
    )

    emitter = EventEmitter(config)
    await emitter.start()

    # Emit events
    emitter.emit({
        "event": "session_start",
        "session_id": "sess-123",
        "user_id": "user-456",
        "task": "Analyze data",
    })

    # Graceful shutdown
    await emitter.shutdown()

asyncio.run(main())
```

### Behavioral Analysis (Performance Metrics)
```python
from raia import RAIAExecutionInspector, SQLiteRAIAStorage

# Create inspector with storage
storage = SQLiteRAIAStorage("metrics.db")
inspector = RAIAExecutionInspector(
    storage=storage,
    agent_name="my-agent"
)

# Use as LangChain callback
result = chain.invoke(
    {"input": "What is AI?"},
    config={"callbacks": [inspector]}
)

# Query metrics
run = storage.get_run(inspector.run_id)
print(f"Latency: {run.total_latency_ms}ms")
print(f"Tokens: {run.total_tokens_prompt + run.total_tokens_completion}")
print(f"Cost: ${run.total_cost_usd}")
```

### Using Both Systems Together
```python
import asyncio
from raia import (
    EventEmitter,
    EmitterConfig,
    RAIAExecutionInspector,
    SQLiteRAIAStorage,
    create_unified_callback,
)

async def main():
    # Setup event logging
    emitter_config = EmitterConfig.from_env()
    emitter = EventEmitter(emitter_config)
    await emitter.start()

    # Setup behavioral analysis
    storage = SQLiteRAIAStorage("metrics.db")

    # Create unified callback
    callbacks = create_unified_callback(
        emitter=emitter,
        storage=storage,
        agent_name="my-agent",
        use_events=True,
        use_inspectors=True,
    )

    # Use in your chain
    result = chain.invoke(
        {"input": "Question"},
        config={"callbacks": callbacks}
    )

    await emitter.shutdown()

asyncio.run(main())
```

---

## Components

### 1. Event Logging (`raia.events`)
**Purpose**: Production telemetry, audit trails, compliance

**Features**:
- Async batching and circuit breaker
- Multiple transports (file, HTTP, Kafka, OTLP)
- PII/PHI redaction
- HMAC signing for integrity
- Graceful shutdown with flush

**Use when**:
- You need audit trails for compliance
- You want deterministic replay capabilities
- You're deploying to production
- You need to stream events to external systems

### 2. Behavioral Analysis (`raia.inspectors`)
**Purpose**: Performance optimization, pattern detection

**Features**:
- Execution metrics (latency, tokens, cost)
- Loop detection (simple & cyclic)
- Redundancy detection
- Suboptimal path analysis
- Semantic evaluation framework

**Use when**:
- You're debugging agent behavior
- You want to optimize performance
- You need to detect anti-patterns
- You're analyzing agent quality

### 3. Storage (`raia.storage`)
**Purpose**: Persistent metrics and analysis results

**Features**:
- SQLite backend with proper indexing
- Time-series queries
- Aggregation helpers
- Efficient bulk inserts

**Use when**:
- You need to query historical metrics
- You want to compare runs over time
- You're building dashboards
- You need offline analysis

### 4. Integrations (`raia.integrations`)
**Purpose**: Seamless framework integration

**Features**:
- LangChain callback handlers
- LangGraph streaming with inspection
- Tool instrumentation decorators
- Unified callback creation

**Use when**:
- You're using LangChain/LangGraph
- You want automatic instrumentation
- You need minimal code changes

---

## Migration from Old Structure

### Importing
```python
# OLD
from raia_inspectors import RAIAExecutionInspector
from raia_inspectors.storage.sqlite_storage import SQLiteRAIAStorage
from sdk.python.raia import EventEmitter

# NEW
from raia import RAIAExecutionInspector, SQLiteRAIAStorage, EventEmitter
```

### Storage Class Names
```python
# OLD
from raia_inspectors.storage.sqlite_storage import SQLiteRAIAStorage
from raia_inspectors.storage.base import BaseRAIAStorage

# NEW (same class names, different imports)
from raia.storage import SQLiteRAIAStorage, BaseRAIAStorage
```

### Integration Helpers
```python
# OLD
from raia_inspectors.integration.langchain_callbacks import create_inspector_callback
from raia_inspectors.integration.langgraph_integration import stream_with_inspection

# NEW
from raia.integrations import LangChainExecutionInspector, stream_with_inspection

# Or use unified callback
from raia.integrations import create_unified_callback
```

---

## Examples

See `raia/examples/`:
- **example_langchain_usage.py** - LangChain with both event logging and inspection
- **example_langgraph_usage.py** - LangGraph with behavioral analysis

Run examples:
```bash
# Locally (if Python 3.10+)
python raia/examples/example_langchain_usage.py

# Docker (any platform)
./run.sh examples  # Mac/Linux
run.bat examples   # Windows
```

---

## Testing

### Run All Tests
```bash
# Locally
pytest raia/tests/ -v

# Docker
./run.sh test  # Mac/Linux
run.bat test   # Windows
```

### Expected Output
```
=========== test session starts ===========
collected 39 items

raia/tests/test_storage_sqlite.py ........... [28%]
raia/tests/test_execution_inspector.py ....... [46%]
raia/tests/test_behavior_inspector.py ......... [69%]
raia/tests/test_semantic_inspector.py ........ [100%]

=========== 39 passed in 3.2s ===========
```

---

## Docker Usage

### Quick Start
```bash
# Build image
./run.sh build

# Run tests
./run.sh test

# Run examples
./run.sh examples

# Interactive shell
./run.sh shell
```

### What Docker Includes
- Python 3.11
- All raia dependencies
- LangChain/LangGraph for examples
- pytest for testing
- SQLite for storage

### Data Persistence
Docker mounts local directories:
- `./data/` → `/app/data/` (databases)
- `./logs/` → `/app/logs/` (event logs)

Files created in Docker are available on your host machine!

---

## Documentation

- **READ_THIS_FIRST.md** - Main documentation entry point
- **FRAMEWORK_COMPARISON.md** - Comparison with LangSmith, LangFuse, etc.
- **WHY_RAIA_INSPECTORS.md** - Visual examples of differences
- **DOCKER_GUIDE.md** - Complete Docker documentation
- **DOCKER_README.md** - Quick Docker reference

---

## Key Benefits of Unified Library

### Before (Two Separate Systems)
- ❌ Two different import paths
- ❌ Confusion about which to use when
- ❌ Duplicate code for LangChain integration
- ❌ Separate documentation
- ❌ Two installation processes

### After (One Unified Library)
- ✅ Single import path: `from raia import ...`
- ✅ Clear component organization (events, inspectors, storage, integrations)
- ✅ Unified LangChain/LangGraph integration
- ✅ One comprehensive documentation
- ✅ One installation: `pip install -e .`
- ✅ Easy to use both systems together
- ✅ Consistent API across components

---

## Support

For issues, questions, or contributions:
- See examples in `raia/examples/`
- Check tests in `raia/tests/` for usage patterns
- Read comprehensive docs in repo root

---

**The unified RAIA library - Complete observability for agentic systems! 🚀**
