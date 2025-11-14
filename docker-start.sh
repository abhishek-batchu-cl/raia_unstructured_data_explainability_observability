#!/bin/bash

################################################################################
# RAIA Docker Quick Start Script
################################################################################
# This script helps you quickly start the entire RAIA stack with Docker

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'  # No Color

# Banner
echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                    RAIA Docker Quick Start                                 ║"
echo "║          Responsible AI Analytics & Agent Evaluation Platform              ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

################################################################################
# Pre-flight Checks
################################################################################

echo -e "${CYAN}═══ Pre-flight Checks ═══${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker is not installed${NC}"
    echo "Please install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi
echo -e "${GREEN}✓ Docker is installed${NC}"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}✗ Docker Compose is not installed${NC}"
    echo "Please install Docker Compose from: https://docs.docker.com/compose/install/"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose is installed${NC}"

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo -e "${RED}✗ Docker daemon is not running${NC}"
    echo "Please start Docker Desktop or Docker daemon"
    exit 1
fi
echo -e "${GREEN}✓ Docker daemon is running${NC}"

################################################################################
# Environment Setup
################################################################################

echo ""
echo -e "${CYAN}═══ Environment Setup ═══${NC}"

# Check if .env file exists, if not create from template
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠ .env file not found${NC}"
    if [ -f ".env.docker" ]; then
        echo "Creating .env from .env.docker template..."
        cp .env.docker .env
        echo -e "${GREEN}✓ .env file created${NC}"
        echo -e "${YELLOW}⚠ Please review and update .env file with your settings${NC}"
    else
        echo -e "${RED}✗ .env.docker template not found${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ .env file found${NC}"
fi

# Create required directories
echo "Creating required directories..."
mkdir -p backend/logs backend/data backend/backups
mkdir -p frontend/dist
mkdir -p grafana
echo -e "${GREEN}✓ Directories created${NC}"

################################################################################
# Docker Compose Operations
################################################################################

echo ""
echo -e "${CYAN}═══ Starting RAIA Stack ═══${NC}"

# Parse command line arguments
ACTION="${1:-up}"

case $ACTION in
    up|start)
        echo "Starting all services..."
        docker-compose up -d
        ;;
    down|stop)
        echo "Stopping all services..."
        docker-compose down
        exit 0
        ;;
    restart)
        echo "Restarting all services..."
        docker-compose restart
        ;;
    rebuild)
        echo "Rebuilding and starting all services..."
        docker-compose down
        docker-compose build --no-cache
        docker-compose up -d
        ;;
    logs)
        echo "Showing logs..."
        docker-compose logs -f
        exit 0
        ;;
    clean)
        echo -e "${YELLOW}⚠ This will remove all containers, volumes, and data${NC}"
        read -p "Are you sure? (yes/no): " -r
        if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
            docker-compose down -v
            echo -e "${GREEN}✓ Cleanup complete${NC}"
        else
            echo "Cleanup cancelled"
        fi
        exit 0
        ;;
    *)
        echo -e "${RED}Unknown action: $ACTION${NC}"
        echo "Usage: $0 {up|down|restart|rebuild|logs|clean}"
        exit 1
        ;;
esac

################################################################################
# Wait for Services
################################################################################

echo ""
echo -e "${CYAN}═══ Waiting for Services to Start ═══${NC}"

# Wait for PostgreSQL
echo -n "Waiting for PostgreSQL"
for i in {1..30}; do
    if docker-compose exec -T postgres pg_isready -U raia_user &> /dev/null; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    echo -n "."
    sleep 2
done

# Wait for Redis
echo -n "Waiting for Redis"
for i in {1..30}; do
    if docker-compose exec -T redis redis-cli ping &> /dev/null; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    echo -n "."
    sleep 2
done

# Wait for Backend
echo -n "Waiting for Backend"
for i in {1..60}; do
    if curl -f http://localhost:8000/health &> /dev/null; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    echo -n "."
    sleep 2
done

# Wait for Frontend
echo -n "Waiting for Frontend"
for i in {1..60}; do
    if curl -f http://localhost:5173 &> /dev/null; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    echo -n "."
    sleep 2
done

################################################################################
# Service Status
################################################################################

echo ""
echo -e "${CYAN}═══ Service Status ═══${NC}"
docker-compose ps

################################################################################
# Success Message
################################################################################

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    ✨ RAIA is Running! ✨                                   ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Access Points:${NC}"
echo -e "  ${CYAN}Frontend Dashboard:${NC}  http://localhost:5173"
echo -e "  ${CYAN}Backend API:${NC}         http://localhost:8000"
echo -e "  ${CYAN}API Documentation:${NC}   http://localhost:8000/docs"
echo -e "  ${CYAN}API Health:${NC}          http://localhost:8000/health"
echo -e "  ${CYAN}Prometheus:${NC}          http://localhost:9090"
echo -e "  ${CYAN}Grafana:${NC}             http://localhost:3000"
echo ""
echo -e "${BLUE}Default Credentials:${NC}"
echo -e "  ${CYAN}Admin User:${NC}"
echo -e "    Username: admin"
echo -e "    Password: admin123"
echo ""
echo -e "  ${CYAN}Grafana:${NC}"
echo -e "    Username: admin"
echo -e "    Password: admin"
echo ""
echo -e "${BLUE}Useful Commands:${NC}"
echo -e "  ${CYAN}View logs:${NC}           docker-compose logs -f"
echo -e "  ${CYAN}Stop services:${NC}       ./docker-start.sh down"
echo -e "  ${CYAN}Restart services:${NC}    ./docker-start.sh restart"
echo -e "  ${CYAN}Rebuild images:${NC}      ./docker-start.sh rebuild"
echo -e "  ${CYAN}Clean everything:${NC}    ./docker-start.sh clean"
echo ""
echo -e "${YELLOW}⚠ Important Security Notes:${NC}"
echo -e "  1. Change default passwords in .env file"
echo -e "  2. Never commit .env file to version control"
echo -e "  3. Use strong passwords in production"
echo -e "  4. Enable SSL/TLS for production deployments"
echo ""
echo -e "${GREEN}Happy analyzing! 🚀${NC}"
echo ""
