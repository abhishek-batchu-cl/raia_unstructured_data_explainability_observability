# RAIA Docker Guide 🐳

Complete guide for running RAIA in Docker on Mac, Windows, or Linux.

---

## 🎯 Quick Start (2 Minutes)

### Mac / Linux
```bash
# Build the image
./run.sh build

# Run tests
./run.sh test

# Run examples
./run.sh examples
```

### Windows
```powershell
# Build the image
run.bat build

# Run tests
run.bat test

# Run examples
run.bat examples
```

---

## 📋 Prerequisites

### 1. Install Docker Desktop

**Mac:**
- Download from: https://www.docker.com/products/docker-desktop/
- Install and start Docker Desktop
- Verify: `docker --version`

**Windows:**
- Download from: https://www.docker.com/products/docker-desktop/
- Install and start Docker Desktop
- Enable WSL 2 if prompted
- Verify: `docker --version`

**Linux:**
- Install Docker Engine: https://docs.docker.com/engine/install/
- Install Docker Compose: https://docs.docker.com/compose/install/
- Verify: `docker --version` and `docker-compose --version`

### 2. Verify Docker is Running
```bash
docker info
```

If you see an error, start Docker Desktop and try again.

---

## 🚀 Available Commands

### Build the Image
Creates the Docker image with all dependencies installed.

**Mac/Linux:**
```bash
./run.sh build
```

**Windows:**
```powershell
run.bat build
```

**What it does:**
- Installs Python 3.11
- Installs all dependencies (pydantic, pytest, etc.)
- Sets up RAIA Inspectors package
- Prepares the environment

**Time:** ~2-3 minutes (first time), ~30 seconds (subsequent builds)

---

### Run Tests
Executes all 39 tests to verify everything works.

**Mac/Linux:**
```bash
./run.sh test
```

**Windows:**
```powershell
run.bat test
```

**Expected output:**
```
=========== test session starts ===========
collected 39 items

test_storage_sqlite.py ........ [ 20%]
test_execution_inspector.py ........ [ 40%]
test_behavior_inspector.py ......... [ 65%]
test_semantic_inspector.py ........ [100%]

=========== 39 passed in 2.5s ===========
```

---

### Run Examples
Executes the example scripts to demonstrate functionality.

**Mac/Linux:**
```bash
./run.sh examples
```

**Windows:**
```powershell
run.bat examples
```

**What it runs:**
1. LangChain example (if langchain installed)
2. LangGraph example (if langgraph installed)

**Note:** Examples may show "Note: Requires langchain/langgraph" if optional dependencies aren't installed. This is normal - the core functionality still works.

---

### Interactive Shell
Opens a bash shell inside the container for manual testing.

**Mac/Linux:**
```bash
./run.sh shell
```

**Windows:**
```powershell
run.bat shell
```

**Inside the shell, you can:**
```bash
# Import and test modules
python3 -c "import raia_inspectors; print(raia_inspectors.__version__)"

# Run Python interactively
python3

# Run specific tests
pytest /app/raia_inspectors_pkg/tests/test_storage_sqlite.py -v

# Exit the shell
exit
```

---

### Clean Up
Removes Docker containers, volumes, and cleans up resources.

**Mac/Linux:**
```bash
./run.sh clean
```

**Windows:**
```powershell
run.bat clean
```

**Use this when:**
- You want to start fresh
- Docker is using too much disk space
- You're done testing

---

## 🔧 Advanced Usage

### Using Docker Compose Directly

**Run specific service:**
```bash
docker-compose up raia-inspectors      # Run tests
docker-compose up raia-examples        # Run examples
docker-compose run raia-inspectors-shell bash  # Interactive shell
```

**View logs:**
```bash
docker-compose logs raia-inspectors
```

**Stop all services:**
```bash
docker-compose down
```

**Rebuild from scratch:**
```bash
docker-compose build --no-cache
```

---

### Custom Python Scripts

**Run a custom script:**

**Mac/Linux:**
```bash
docker-compose run --rm raia-inspectors-shell python /app/your_script.py
```

**Windows:**
```powershell
docker-compose run --rm raia-inspectors-shell python /app/your_script.py
```

**Mount your own scripts:**

Edit `docker-compose.yml` and add:
```yaml
volumes:
  - ./my_scripts:/app/my_scripts
```

Then run:
```bash
docker-compose run --rm raia-inspectors-shell python /app/my_scripts/test.py
```

---

### Using with Your Own Agents

**1. Create a custom Dockerfile:**

Create `Dockerfile.custom`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy RAIA
COPY . /app/

# Install RAIA + your dependencies
RUN pip install -e /app/raia_inspectors_pkg && \
    pip install langchain langgraph langchain-openai

# Copy your agent code
COPY your_agent/ /app/your_agent/

CMD ["python", "/app/your_agent/main.py"]
```

**2. Build and run:**
```bash
docker build -f Dockerfile.custom -t my-raia-agent .
docker run -e OPENAI_API_KEY=$OPENAI_API_KEY my-raia-agent
```

---

## 🐛 Troubleshooting

### Docker not running
```
❌ Docker is not running
```

**Solution:** Start Docker Desktop and wait for it to fully start.

---

### Build fails
```
ERROR: failed to solve: ...
```

**Solution:**
```bash
# Clean everything and rebuild
./run.sh clean
./run.sh build
```

---

### Port already in use
```
ERROR: port 8000 already in use
```

**Solution:** Stop other services using that port or edit `docker-compose.yml` to use a different port.

---

### Permission denied (Linux)
```
permission denied while trying to connect to Docker daemon
```

**Solution:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and log back in, then test
docker info
```

---

### Out of disk space
```
no space left on device
```

**Solution:**
```bash
# Clean up Docker
./run.sh clean

# Or manually
docker system prune -a --volumes
```

---

## 📊 What's Included

The Docker image includes:

### Core Components
- ✅ Python 3.11
- ✅ RAIA Inspectors library
- ✅ All dependencies (pydantic, pytest, etc.)
- ✅ SQLite for local storage

### Directory Structure
```
/app/
├── raia_inspectors_pkg/     # Installed package
│   ├── raia_inspectors/     # Core library
│   ├── tests/               # Test suite
│   └── examples/            # Example scripts
├── data/                    # Data directory (mounted)
├── logs/                    # Logs directory (mounted)
└── output/                  # Output directory
```

### Mounted Volumes
- `./data` → `/app/data` (for databases)
- `./logs` → `/app/logs` (for log files)
- `./raia_inspectors/examples` → `/app/examples` (for examples)

---

## 🎓 Common Workflows

### Workflow 1: Quick Test
```bash
# Build once
./run.sh build

# Run tests anytime
./run.sh test
```

### Workflow 2: Development
```bash
# Build once
./run.sh build

# Interactive shell for testing
./run.sh shell

# Inside shell:
python3
>>> import raia_inspectors
>>> from raia_inspectors import RAIAExecutionInspector
>>> # Test your code
```

### Workflow 3: Integration with Agent
```bash
# Build custom image with your agent
docker build -f Dockerfile.custom -t my-agent .

# Run your agent
docker run -e OPENAI_API_KEY=$OPENAI_API_KEY my-agent
```

---

## 🌐 Platform-Specific Notes

### Mac (Intel)
- ✅ Works out of the box
- Uses native Docker

### Mac (Apple Silicon / M1/M2/M3)
- ✅ Works out of the box
- Uses Rosetta 2 emulation (slightly slower build)
- To use ARM-native: change Dockerfile first line to:
  ```dockerfile
  FROM --platform=linux/arm64 python:3.11-slim
  ```

### Windows
- ✅ Works with WSL 2
- Make sure Docker Desktop is set to use WSL 2 backend
- Use PowerShell or CMD, not Git Bash
- Line endings: Docker handles them automatically

### Linux
- ✅ Native performance
- Requires Docker Engine + Docker Compose
- May need to add user to `docker` group

---

## 📈 Performance

### Build Time
- **First build:** 2-3 minutes
- **Subsequent builds:** 30 seconds (cached)
- **With --no-cache:** 3-4 minutes

### Run Time
- **Tests:** ~3-5 seconds
- **Examples:** ~10-15 seconds
- **Interactive shell:** Instant

### Resource Usage
- **Memory:** ~200-300 MB
- **Disk:** ~500 MB (image)
- **CPU:** Minimal (only during builds/tests)

---

## 🔒 Security Notes

- Docker images run in isolated containers
- No network access by default (unless you add ports)
- Volumes are mounted read-only where possible
- No root access required in containers

---

## ✨ Next Steps

After Docker is working:

1. **Read the docs:**
   - [READ_THIS_FIRST.md](READ_THIS_FIRST.md)
   - [raia_inspectors/README.md](raia_inspectors/README.md)

2. **Try examples:**
   - `./run.sh examples`
   - Check `./data/` for generated databases

3. **Integrate with your agent:**
   - Copy your agent code
   - Update Dockerfile.custom
   - Build and run

---

## 🆘 Getting Help

- **Documentation:** All `.md` files in this repo
- **Examples:** `raia_inspectors/examples/`
- **Tests:** `raia_inspectors/tests/` - shows how everything works
- **Issues:** GitHub issues

---

**Docker setup is production-ready! 🚀**

Works on Mac, Windows, and Linux with zero code changes.
