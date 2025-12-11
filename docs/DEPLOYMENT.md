# Deployment Guide

## Overview

SearchNewsRAG uses an automated CI/CD pipeline with GitHub Actions for production deployment. The pipeline builds Docker images, pushes them to Docker Hub, and deploys a multi-service stack to the VPS.

## Architecture

```
Internet → Cloudflare (SSL) → VPS:80 → System Nginx → localhost:8080
    ↓
Docker Stack:
    ├── Nginx (Reverse Proxy + Rate Limiting)
    ├── Frontend (React/Vite)
    ├── Backend (FastAPI/Python)
    └── ChromaDB (Vector Database)
```

**Key Points**:
- Domain: `news.aitools.az`
- SSL handled by Cloudflare
- System Nginx proxies to Docker Nginx on port 8080
- All services communicate via internal Docker network
- ChromaDB data persisted at `/opt/searchnewsrag/data/chroma`

## Deployment Pipeline

**Trigger**: PR merge to `main` branch or manual trigger via GitHub Actions

**Pipeline Stages**:

1. **Build**: Docker images built for backend, frontend, and nginx
   - Multi-stage builds with BuildKit caching
   - Tagged with `latest` and commit SHA

2. **Push**: Images pushed to Docker Hub
   - `imranrahimov1995/searchnewsrag-backend:latest`
   - `imranrahimov1995/searchnewsrag-frontend:latest`
   - `imranrahimov1995/searchnewsrag-nginx:latest`

3. **Deploy**: Services deployed to VPS via SSH
   ```bash
   cd /opt/searchnewsrag
   docker pull <all-images>
   docker compose up -d --force-recreate
   docker image prune -f
   ```

4. **Verify**: Health checks ensure all services running

## Configuration

### GitHub Secrets (Environment: `test`)

| Secret | Purpose |
|--------|---------|
| `DOCKERHUB_USERNAME` / `DOCKERHUB_TOKEN` | Docker Hub authentication |
| `VPS_HOST` / `VPS_USER` / `VPS_SSH_KEY` | VPS SSH access |
| `OPENAI_API_KEY` | OpenAI API access |
| `TELEGRAM_API_ID` / `TELEGRAM_API_HASH` | Telegram Bot API |

Secrets are injected into containers via environment variables at runtime.
- Injected via GitHub Actions secure environment
- Passed through SSH to Docker Compose

## Services

**Stack Configuration** (`docker-compose.prod.yml`):

- **ChromaDB**: Vector database with persistent storage at `/opt/searchnewsrag/data/chroma`
- **Backend**: FastAPI service, depends on ChromaDB, health check at `/health`
- **Frontend**: React/Vite build, depends on backend
- **Nginx**: Reverse proxy, exposes ports 8080:80 and 8443:443

**Rate Limiting**:
- Chat API: 5 req/min per IP
- General API: 30 req/min per IP

**CORS**: `["http://news.aitools.az", "https://news.aitools.az"]`

**Service Dependencies**: ChromaDB → Backend → Frontend → Nginx

## Monitoring & Troubleshooting

**Monitoring infrastructure with Prometheus/Grafana dashboards coming soon.**

### Quick Diagnostics

**Check service status**:
```bash
docker compose ps
```

**View logs**:
```bash
docker compose logs -f backend
docker compose logs --tail=50
```

**Health checks**:
```bash
curl http://localhost:8000/health  # Backend
curl https://news.aitools.az/api/health  # Public endpoint
```

**Common fixes**:
```bash
# Restart single service
docker compose restart backend

# Restart all services
docker compose restart

# Full redeploy
docker compose down
docker compose up -d --force-recreate
```

## Rollback



**Method 1: Revert commit and redeploy**:
```bash
git revert <commit-sha>
git push origin main
# CI/CD will automatically deploy reverted version
```

## Maintenance

**Backup ChromaDB**:
```bash
cd /opt/searchnewsrag
tar -czf chroma_backup_$(date +%Y%m%d).tar.gz data/chroma/
```

**Restore ChromaDB**:
```bash
docker compose down chromadb
tar -xzf chroma_backup_YYYYMMDD.tar.gz -C ./
docker compose up -d chromadb
```

**Secret Rotation** (recommended every 90 days):
1. Generate new API keys
2. Update GitHub Secrets
3. Trigger manual deployment

## Quick Reference

**Local Development**:
```bash
docker-compose up -d
```

**Useful Commands**:
```bash
docker compose ps                              # Service status
docker compose logs -f backend                 # Follow logs
docker compose restart backend                 # Restart service
docker compose up -d --no-deps backend         # Update single service
docker system prune -a --volumes               # Clean up
```

**URLs**:
- Production: https://news.aitools.az
- Health Check: https://news.aitools.az/api/health
- GitHub Actions: https://github.com/ImranRahimov1995/SearchNewsRAG/actions
