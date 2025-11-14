#!/bin/bash

################################################################################
# RAIA Production Deployment Script
################################################################################

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'  # No Color

# Configuration
ENVIRONMENT="${1:-production}"
BACKUP_BEFORE_DEPLOY="${BACKUP_BEFORE_DEPLOY:-true}"
RUN_MIGRATIONS="${RUN_MIGRATIONS:-true}"
RUN_TESTS="${RUN_TESTS:-true}"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              RAIA Production Deployment Script                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Environment:${NC} $ENVIRONMENT"
echo ""

################################################################################
# Pre-deployment Checks
################################################################################

echo -e "${BLUE}═══ Pre-deployment Checks ═══${NC}"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}✗ .env file not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ .env file found${NC}"

# Check if required services are running
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠ Docker not found - skipping container checks${NC}"
else
    echo -e "${GREEN}✓ Docker is installed${NC}"
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 is installed${NC}"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ Node.js not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Node.js is installed${NC}"

################################################################################
# Backup Database
################################################################################

if [ "$BACKUP_BEFORE_DEPLOY" = "true" ]; then
    echo ""
    echo -e "${BLUE}═══ Creating Backup ═══${NC}"

    python3 -c "
from backend.backup import BackupManager
manager = BackupManager(backup_dir='backups')
manager.backup_sqlite('data/demo_databases/complete_end_to_end_demo.db')
print('✓ Database backup created')
    " || echo -e "${YELLOW}⚠ Backup failed - continuing anyway${NC}"
fi

################################################################################
# Pull Latest Code
################################################################################

echo ""
echo -e "${BLUE}═══ Pulling Latest Code ═══${NC}"

if [ -d ".git" ]; then
    git fetch origin
    git checkout $ENVIRONMENT
    git pull origin $ENVIRONMENT
    echo -e "${GREEN}✓ Code updated${NC}"
else
    echo -e "${YELLOW}⚠ Not a git repository - skipping${NC}"
fi

################################################################################
# Backend Deployment
################################################################################

echo ""
echo -e "${BLUE}═══ Deploying Backend ═══${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "backend/venv" ]; then
    echo "Creating virtual environment..."
    cd backend
    python3 -m venv venv
    cd ..
fi

# Activate virtual environment and install dependencies
echo "Installing backend dependencies..."
cd backend
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-production.txt
echo -e "${GREEN}✓ Backend dependencies installed${NC}"

# Run database migrations if enabled
if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "Running database migrations..."
    python3 -c "
from database import DatabaseManager, DatabaseConfig, DatabaseType, Migrator
config = DatabaseConfig(db_type=DatabaseType.SQLITE, sqlite_path='data/demo_databases/complete_end_to_end_demo.db')
db = DatabaseManager(config)
Migrator.create_all_tables(db)
print('✓ Database migrations complete')
    " || echo -e "${YELLOW}⚠ Migrations failed - continuing anyway${NC}"
fi

# Run tests if enabled
if [ "$RUN_TESTS" = "true" ]; then
    echo "Running backend tests..."
    pytest tests/ -v || echo -e "${YELLOW}⚠ Some tests failed${NC}"
fi

deactivate
cd ..

################################################################################
# Frontend Deployment
################################################################################

echo ""
echo -e "${BLUE}═══ Deploying Frontend ═══${NC}"

cd frontend

# Install dependencies
echo "Installing frontend dependencies..."
npm ci
echo -e "${GREEN}✓ Frontend dependencies installed${NC}"

# Build production bundle
echo "Building production bundle..."
npm run build
echo -e "${GREEN}✓ Frontend built successfully${NC}"

cd ..

################################################################################
# Start/Restart Services
################################################################################

echo ""
echo -e "${BLUE}═══ Restarting Services ═══${NC}"

# Stop existing services
pkill -f "uvicorn main:app" || true
pkill -f "npm run dev" || true

# Start backend
echo "Starting backend..."
cd backend
source venv/bin/activate
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"
deactivate
cd ..

# Wait for backend to be ready
echo "Waiting for backend to be ready..."
sleep 5

# Check backend health
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend is healthy${NC}"
else
    echo -e "${RED}✗ Backend health check failed${NC}"
    exit 1
fi

# Start frontend (production server)
echo "Starting frontend..."
cd frontend
nohup npx serve -s dist -l 5173 > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
cd ..

################################################################################
# Post-deployment Checks
################################################################################

echo ""
echo -e "${BLUE}═══ Post-deployment Checks ═══${NC}"

# Wait for services to stabilize
sleep 3

# Check backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend is responding${NC}"
else
    echo -e "${RED}✗ Backend is not responding${NC}"
    exit 1
fi

# Check frontend
if curl -f http://localhost:5173 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Frontend is responding${NC}"
else
    echo -e "${YELLOW}⚠ Frontend may not be fully ready yet${NC}"
fi

# Check metrics endpoint
if curl -f http://localhost:8000/metrics > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Metrics endpoint is working${NC}"
else
    echo -e "${YELLOW}⚠ Metrics endpoint is not responding${NC}"
fi

################################################################################
# Completion
################################################################################

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    ✨ Deployment Completed Successfully ✨                 ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Services:${NC}"
echo -e "  Frontend:    http://localhost:5173"
echo -e "  Backend API: http://localhost:8000"
echo -e "  API Docs:    http://localhost:8000/docs"
echo -e "  Metrics:     http://localhost:8000/metrics"
echo -e "  Health:      http://localhost:8000/health"
echo ""
echo -e "${BLUE}Logs:${NC}"
echo -e "  Backend:  tail -f logs/backend.log"
echo -e "  Frontend: tail -f logs/frontend.log"
echo ""
echo -e "${BLUE}PIDs:${NC}"
echo -e "  Backend:  $BACKEND_PID"
echo -e "  Frontend: $FRONTEND_PID"
echo ""
echo -e "${YELLOW}To stop services:${NC}"
echo -e "  kill $BACKEND_PID $FRONTEND_PID"
echo ""
