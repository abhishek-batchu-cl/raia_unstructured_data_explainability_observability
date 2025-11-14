# Docker Installation & Troubleshooting Guide

## Quick Start (No Docker Required!)

**If you're having Docker issues, you can run RAIA without Docker:**

```bash
# Install dependencies
pip3 install -e .

# Run the realistic demo (with actually computed metrics)
python3 demo_realistic_computed_metrics.py

# Or run the complete demo
python3 demo_complete_all_features.py
```

---

## Common Docker Issues & Solutions

### Issue 1: "Docker is not running"

**Symptoms:**
```
❌ Docker is not running. Please start Docker Desktop and try again.
```

**Solutions:**

**macOS:**
```bash
# Open Docker Desktop
open -a Docker

# Wait 30 seconds for Docker to start
sleep 30

# Verify Docker is running
docker ps
```

**Linux:**
```bash
# Start Docker service
sudo systemctl start docker

# Enable Docker to start on boot
sudo systemctl enable docker

# Verify
docker ps
```

**Windows:**
```powershell
# Start Docker Desktop from Start Menu
# Or via PowerShell:
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"

# Wait for Docker to start, then verify:
docker ps
```

---

### Issue 2: Permission Denied

**Symptoms:**
```
permission denied while trying to connect to the Docker daemon socket
```

**Solution (Linux):**
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and log back in, OR run:
newgrp docker

# Verify
docker ps
```

**Solution (macOS/Windows):**
- Restart Docker Desktop
- Ensure Docker Desktop has proper permissions in System Preferences/Settings

---

### Issue 3: Port Already in Use

**Symptoms:**
```
Error: Bind for 0.0.0.0:8000 failed: port is already allocated
```

**Solution:**
```bash
# Find what's using the port
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process OR change the port in docker-compose.yml:
ports:
  - "8001:8000"  # Use 8001 instead
```

---

### Issue 4: Build Failures

**Symptoms:**
```
ERROR [internal] load metadata for docker.io/library/python:3.11-slim
```

**Solution:**
```bash
# Pull base image manually
docker pull python:3.11-slim

# Clear Docker cache and rebuild
docker system prune -a
docker-compose build --no-cache
```

---

### Issue 5: Dependencies Not Installing

**Symptoms:**
```
ModuleNotFoundError: No module named 'raia'
```

**Solution:**

**Option 1: Use local installation (recommended)**
```bash
# Install RAIA locally without Docker
pip3 install -e .

# Run demos
python3 demo_realistic_computed_metrics.py
```

**Option 2: Fix Docker installation**
```dockerfile
# Ensure Dockerfile has:
COPY . /app
WORKDIR /app
RUN pip install --no-cache-dir -e .
```

---

## Simplified Dockerfile

If you're having issues, use this minimal Dockerfile:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Install RAIA
RUN pip install --no-cache-dir -e .

# Default command
CMD ["python3", "demo_realistic_computed_metrics.py"]
```

---

## Testing Docker Setup

```bash
# Test 1: Docker is running
docker ps

# Test 2: Can build image
docker build -t raia-test .

# Test 3: Can run container
docker run --rm raia-test python3 -c "import raia; print('✅ RAIA installed')"

# Test 4: Run demo
docker run --rm raia-test python3 demo_realistic_computed_metrics.py
```

---

## Alternative: VS Code DevContainer

If Docker Desktop is problematic, use VS Code DevContainers:

**.devcontainer/devcontainer.json:**
```json
{
  "name": "RAIA Development",
  "image": "python:3.11",
  "postCreateCommand": "pip install -e .",
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance"
      ]
    }
  }
}
```

Then in VS Code:
1. Install "Dev Containers" extension
2. Command Palette → "Dev Containers: Reopen in Container"
3. Run demos inside container

---

## For Your Team: Quick Setup Script

Create `setup_team.sh`:

```bash
#!/bin/bash

echo "🚀 RAIA Team Setup Script"
echo "========================="
echo ""

# Check Python
echo "Checking Python installation..."
python3 --version || { echo "❌ Python 3.9+ required"; exit 1; }

# Install dependencies
echo "Installing dependencies..."
pip3 install -e . || { echo "❌ Installation failed"; exit 1; }

# Test installation
echo "Testing installation..."
python3 -c "import raia; print('✅ RAIA installed successfully')" || { echo "❌ Import failed"; exit 1; }

# Run demo
echo "Running demo..."
python3 demo_realistic_computed_metrics.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Run demos: python3 demo_realistic_computed_metrics.py"
echo "  2. Explore database: sqlite3 realistic_computed_demo.db"
echo "  3. Read docs: cat FEATURES.md"
```

Make it executable:
```bash
chmod +x setup_team.sh
./setup_team.sh
```

---

## Recommended Approach for Teams

### Skip Docker Initially

```bash
# 1. Clone repo
git clone <repo-url>
cd raia_agentic_evaluation

# 2. Install locally
pip3 install -e .

# 3. Run demos
python3 demo_realistic_computed_metrics.py

# 4. Explore
sqlite3 realistic_computed_demo.db
```

### Only Use Docker for Production

Docker is great for production but can be problematic for development:

**Development:** Local installation
**CI/CD:** Docker
**Production:** Docker/Kubernetes

---

## Still Having Issues?

### Debug Checklist

- [ ] Python 3.9+ installed (`python3 --version`)
- [ ] pip installed (`pip3 --version`)
- [ ] Dependencies installed (`pip3 list | grep numpy`)
- [ ] RAIA importable (`python3 -c "import raia"`)
- [ ] Demo runs (`python3 demo_realistic_computed_metrics.py`)

### Get Help

1. Check error messages carefully
2. Try local installation first (skip Docker)
3. Verify all dependencies: `pip3 install -r requirements.txt`
4. Run with verbose errors: `python3 -v demo_realistic_computed_metrics.py`

---

## Summary

**For Quick Start:**
```bash
pip3 install -e .
python3 demo_realistic_computed_metrics.py
```

**For Docker Issues:**
1. Try local installation first
2. Ensure Docker is running (`docker ps`)
3. Use minimal Dockerfile above
4. Clear cache and rebuild (`docker system prune -a`)

**For Team:**
- Share `setup_team.sh` script
- Use local installation for development
- Save Docker for production deployment
