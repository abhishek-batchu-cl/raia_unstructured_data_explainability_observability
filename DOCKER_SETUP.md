# RAIA Docker Setup Guide

**Complete Dockerized Full-Stack Application**

This guide explains how to run the entire RAIA platform using Docker. With Docker, you can run the complete stack (frontend, backend, databases, monitoring) with a single command.

---

## Quick Start

### Prerequisites

- **Docker** (20.10 or later)
- **Docker Compose** (2.0 or later)
- **Git**
- 8GB RAM minimum, 16GB recommended
- 20GB free disk space

### One-Command Setup

```bash
# Clone the repository
git clone <repository-url>
cd raia_agentic_evaluation

# Start everything
./docker-start.sh
```

That's it! The entire RAIA platform will be running in minutes.

---

## What Gets Deployed?

When you run `./docker-start.sh`, Docker will automatically:

1. **Build Docker images** for:
   - Backend (FastAPI with all dependencies)
   - Frontend (React with Nginx)

2. **Start services**:
   - **PostgreSQL** (Database) - Port 5432
   - **Redis** (Cache) - Port 6379
   - **Backend API** (FastAPI) - Port 8000
   - **Frontend** (React + Nginx) - Port 5173
   - **Prometheus** (Metrics) - Port 9090
   - **Grafana** (Dashboards) - Port 3000
   - **Node Exporter** (System Metrics) - Port 9100

3. **Configure everything**:
   - Database schemas
   - Redis caching
   - Authentication
   - Monitoring
   - WebSocket support
   - All integrations

4. **Verify health** of all services

---

## Access Points

After startup, access the following services:

| Service | URL | Credentials |
|---------|-----|-------------|
| **Frontend Dashboard** | http://localhost:5173 | admin / admin123 |
| **Backend API** | http://localhost:8000 | - |
| **API Documentation** | http://localhost:8000/docs | - |
| **API Health Check** | http://localhost:8000/health | - |
| **Metrics Endpoint** | http://localhost:8000/metrics | - |
| **Prometheus** | http://localhost:9090 | - |
| **Grafana** | http://localhost:3000 | admin / admin |
| **PostgreSQL** | localhost:5432 | raia_user / raia_secure_password_2025 |
| **Redis** | localhost:6379 | raia_redis_password |

---

## Docker Commands

### Basic Operations

```bash
# Start all services
./docker-start.sh

# Or using docker-compose directly
docker-compose up -d

# Stop all services
./docker-start.sh down
# Or
docker-compose down

# Restart services
./docker-start.sh restart
# Or
docker-compose restart

# View logs (all services)
./docker-start.sh logs
# Or
docker-compose logs -f

# View logs (specific service)
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Advanced Operations

```bash
# Rebuild images (after code changes)
./docker-start.sh rebuild
# Or
docker-compose build --no-cache
docker-compose up -d

# Clean everything (removes volumes!)
./docker-start.sh clean
# Or
docker-compose down -v

# Check service status
docker-compose ps

# Execute commands in containers
docker-compose exec backend bash
docker-compose exec frontend sh
docker-compose exec postgres psql -U raia_user -d raia

# View resource usage
docker stats

# Scale services
docker-compose up -d --scale backend=3
```

### Database Operations

```bash
# Access PostgreSQL
docker-compose exec postgres psql -U raia_user -d raia

# Backup database
docker-compose exec postgres pg_dump -U raia_user raia > backup.sql

# Restore database
cat backup.sql | docker-compose exec -T postgres psql -U raia_user -d raia

# Access Redis
docker-compose exec redis redis-cli -a raia_redis_password
```

---

## Configuration

### Environment Variables

Configuration is managed through the `.env` file. On first run, the script creates `.env` from `.env.docker` template.

**Edit `.env` to customize:**

```bash
# PostgreSQL
POSTGRES_DB=raia
POSTGRES_USER=raia_user
POSTGRES_PASSWORD=your_secure_password

# Redis
REDIS_PASSWORD=your_redis_password

# Backend
SECRET_KEY=your_secret_key_here
ENVIRONMENT=production

# Ports (change if needed)
BACKEND_PORT=8000
FRONTEND_PORT=5173
POSTGRES_PORT=5432
REDIS_PORT=6379
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
```

### Custom Ports

To run on different ports, edit `.env`:

```bash
BACKEND_PORT=9000
FRONTEND_PORT=3001
```

Then restart:

```bash
docker-compose down
docker-compose up -d
```

### Production Configuration

For production deployments:

1. **Change all default passwords** in `.env`
2. **Use strong passwords** (20+ characters, random)
3. **Enable SSL/TLS** (add nginx SSL config or use a reverse proxy)
4. **Configure firewall rules**
5. **Set up backup automation**
6. **Configure monitoring alerts**

```bash
# Example production .env
POSTGRES_PASSWORD=$(openssl rand -base64 32)
REDIS_PASSWORD=$(openssl rand -base64 32)
SECRET_KEY=$(openssl rand -base64 64)
ENVIRONMENT=production
LOG_LEVEL=warning
```

---

## Architecture

### Service Dependencies

```
Frontend (Port 5173)
    ↓
Backend (Port 8000)
    ↓
├── PostgreSQL (Port 5432)
├── Redis (Port 6379)
└── Prometheus (Port 9090)
         ↓
    Grafana (Port 3000)
```

### Network

All services communicate through `raia-network` bridge network:
- Services can reference each other by name (e.g., `postgres`, `redis`, `backend`)
- External access through exposed ports
- Internal DNS resolution provided by Docker

### Volumes

Persistent data is stored in Docker volumes:

```bash
# List volumes
docker volume ls | grep raia

# Inspect volume
docker volume inspect raia-postgres-data

# Backup volume
docker run --rm -v raia-postgres-data:/data -v $(pwd):/backup alpine tar czf /backup/postgres-backup.tar.gz /data

# Restore volume
docker run --rm -v raia-postgres-data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres-backup.tar.gz -C /
```

---

## Development Workflow

### Code Changes

**Backend changes:**

```bash
# 1. Make code changes in ./backend/
# 2. Rebuild and restart
docker-compose build backend
docker-compose restart backend

# Or rebuild everything
./docker-start.sh rebuild
```

**Frontend changes:**

```bash
# 1. Make code changes in ./frontend/
# 2. Rebuild and restart
docker-compose build frontend
docker-compose restart frontend
```

### Hot Reloading (Development Mode)

For development with hot reloading, use a development compose file:

```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  backend:
    build: ./backend
    volumes:
      - ./backend:/app
    command: uvicorn main:app --reload --host 0.0.0.0 --port 8000

  frontend:
    build: ./frontend
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev
```

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Debugging

**View logs:**

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

**Access container shell:**

```bash
# Backend
docker-compose exec backend bash

# Frontend
docker-compose exec frontend sh

# Run Python commands
docker-compose exec backend python -c "import raia; print(raia.__version__)"
```

**Debug database:**

```bash
# PostgreSQL
docker-compose exec postgres psql -U raia_user -d raia

# Check tables
\dt

# Query data
SELECT * FROM users LIMIT 10;
```

---

## Troubleshooting

### Common Issues

**1. Port already in use**

```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or change port in .env
BACKEND_PORT=9000
```

**2. Services not starting**

```bash
# Check logs
docker-compose logs

# Check service status
docker-compose ps

# Restart services
docker-compose restart
```

**3. Database connection errors**

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Verify connection
docker-compose exec postgres pg_isready -U raia_user
```

**4. Out of disk space**

```bash
# Clean up unused Docker resources
docker system prune -a

# Remove old volumes (careful!)
docker volume prune
```

**5. Permission errors**

```bash
# Fix permissions
sudo chown -R $USER:$USER backend/logs backend/data backend/backups
chmod -R 755 backend/logs backend/data backend/backups
```

**6. Frontend not loading**

```bash
# Check frontend logs
docker-compose logs frontend

# Check nginx status
docker-compose exec frontend nginx -t

# Rebuild frontend
docker-compose build --no-cache frontend
docker-compose restart frontend
```

**7. WebSocket not connecting**

```bash
# Check backend WebSocket support
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" http://localhost:8000/ws

# Check nginx WebSocket proxy
docker-compose logs frontend | grep ws
```

### Health Checks

```bash
# Check all services
docker-compose ps

# Backend health
curl http://localhost:8000/health

# Database health
docker-compose exec postgres pg_isready

# Redis health
docker-compose exec redis redis-cli ping
```

---

## Performance Tuning

### Resource Limits

Add resource limits to `docker-compose.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

### Scaling

Scale services horizontally:

```bash
# Scale backend to 3 instances
docker-compose up -d --scale backend=3

# Add load balancer
# See docs/LOAD_BALANCING.md
```

### Caching

Redis caching is enabled by default. Configure in `.env`:

```bash
ENABLE_CACHING=true
REDIS_CACHE_TTL=3600
```

---

## Production Deployment

### Checklist

- [ ] Change all default passwords
- [ ] Configure SSL/TLS
- [ ] Set up firewall rules
- [ ] Configure backup automation
- [ ] Set up monitoring alerts
- [ ] Configure log rotation
- [ ] Set resource limits
- [ ] Configure reverse proxy
- [ ] Set up CI/CD pipeline
- [ ] Test disaster recovery

### Recommended Stack

For production, use:

1. **Docker Swarm** or **Kubernetes** for orchestration
2. **Nginx** or **Traefik** as reverse proxy with SSL
3. **AWS RDS** or **managed PostgreSQL** for database
4. **AWS ElastiCache** or **managed Redis** for caching
5. **AWS CloudWatch** or **Datadog** for monitoring
6. **AWS S3** for backups

### Docker Swarm Example

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml raia

# Scale services
docker service scale raia_backend=5

# Update service
docker service update --image raia-backend:v2 raia_backend
```

---

## Backup and Restore

### Automated Backups

Create a backup script:

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)

# Backup database
docker-compose exec -T postgres pg_dump -U raia_user raia | gzip > "backups/db_${DATE}.sql.gz"

# Backup volumes
docker run --rm -v raia-postgres-data:/data -v $(pwd)/backups:/backup alpine tar czf "/backup/volumes_${DATE}.tar.gz" /data

# Upload to S3 (optional)
aws s3 cp "backups/db_${DATE}.sql.gz" s3://your-bucket/backups/
```

Run with cron:

```bash
# Run daily at 2 AM
0 2 * * * /path/to/backup.sh
```

### Restore

```bash
# Restore database
gunzip < backups/db_20250114.sql.gz | docker-compose exec -T postgres psql -U raia_user -d raia

# Restore volumes
docker run --rm -v raia-postgres-data:/data -v $(pwd)/backups:/backup alpine tar xzf /backup/volumes_20250114.tar.gz -C /
```

---

## Monitoring

### Prometheus Metrics

Access metrics at:
- Application metrics: http://localhost:8000/metrics
- Prometheus UI: http://localhost:9090
- System metrics: http://localhost:9100/metrics

### Grafana Dashboards

1. Open http://localhost:3000
2. Login with admin/admin
3. Pre-configured dashboard loads automatically
4. Create custom dashboards as needed

### Alerts

Configure alerts in `prometheus.yml`:

```yaml
alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - 'alerts.yml'
```

---

## Security

### Best Practices

1. **Never commit .env files** - Add to .gitignore
2. **Use secrets management** - AWS Secrets Manager, Vault
3. **Regular updates** - Keep images updated
4. **Network isolation** - Use internal networks
5. **Least privilege** - Run as non-root user
6. **Scan images** - Use Trivy or Snyk
7. **Enable SSL/TLS** - Use Let's Encrypt
8. **Audit logs** - Enable audit logging
9. **Rate limiting** - Configure API rate limits
10. **Firewall rules** - Restrict access

### Security Scanning

```bash
# Scan images for vulnerabilities
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image raia-backend:latest

# Scan compose file
docker run --rm -v $(pwd):/project aquasec/trivy config /project/docker-compose.yml
```

---

## CI/CD Integration

### GitHub Actions

```yaml
name: Docker Build and Deploy

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build images
        run: docker-compose build

      - name: Run tests
        run: docker-compose run backend pytest

      - name: Push images
        run: |
          docker tag raia-backend:latest myrepo/raia-backend:latest
          docker push myrepo/raia-backend:latest

      - name: Deploy
        run: |
          ssh production "cd /app && docker-compose pull && docker-compose up -d"
```

---

## FAQ

**Q: Can I run this on Windows/Mac/Linux?**
A: Yes, Docker works on all platforms.

**Q: How much resources does this need?**
A: Minimum 8GB RAM, 20GB disk. Recommended 16GB RAM.

**Q: Can I use my own PostgreSQL/Redis?**
A: Yes, edit `.env` to point to external services and comment out those services in docker-compose.yml.

**Q: How do I update to the latest version?**
A: `git pull && ./docker-start.sh rebuild`

**Q: Can I run this in production?**
A: Yes, but follow the production checklist and security best practices.

**Q: How do I scale horizontally?**
A: Use `docker-compose up -d --scale backend=3` or deploy to Kubernetes/Swarm.

**Q: Where are logs stored?**
A: In `backend/logs/` and viewable with `docker-compose logs`.

**Q: How do I customize the frontend?**
A: Edit files in `frontend/src/`, then run `./docker-start.sh rebuild`.

---

## Support

For issues or questions:

1. Check the troubleshooting section
2. View logs: `docker-compose logs`
3. Check GitHub issues
4. Contact support team

---

## Summary

**To get started:**

```bash
git clone <repo>
cd raia_agentic_evaluation
./docker-start.sh
```

**To stop:**

```bash
./docker-start.sh down
```

**That's it!** Docker handles everything else.

---

**Last Updated**: January 14, 2025
**Version**: 1.0.0
**Tested On**: Docker 24.0+, Docker Compose 2.20+
