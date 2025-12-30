# Celery & Redis Setup Documentation

## Overview

This document describes the Celery task queue setup for automated news collection and vectorization in the SearchNewsRAG project.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     CELERY BEAT SCHEDULER                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Daily News Update Task (00:01 Asia/Baku)                │   │
│  │  - Scheduled with Celery Beat                            │   │
│  │  - Triggers daily_news_update() task                     │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     REDIS MESSAGE BROKER                        │
│  - Queue: celery (default)                                      │
│  - Backend: redis://redis:6379/0                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     CELERY WORKER POOL                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  daily_news_update() Task Execution:                     │   │
│  │  1. TelegramNewsFetcher → Collect messages from channels │   │
│  │  2. ArticleContentParser → Parse full articles (50 conc.)│   │
│  │  3. NewsVectorizer → Analyze & vectorize (20 conc.)      │   │
│  └──────────────────────────────────────────────────────────┘   │
│  Concurrency: 2 (local) / 4 (prod)                              │
│  Resources: 2-4 CPU, 2-4GB RAM                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     DATA PERSISTENCE                            │
│  - PostgreSQL: Articles, metadata, entities                     │
│  - ChromaDB: Vector embeddings for semantic search              │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Celery Application (`backend/src/tasks/celery_app.py`)

**Configuration**:
- Broker: Redis (`redis://redis:6379/0`)
- Timezone: `Asia/Baku` (UTC+4)
- Beat Schedule: Daily task at 00:01

**Key Features**:
- Task discovery from `tasks.news_tasks` module
- Automatic result backend configuration
- UTC time handling with local timezone conversion

### 2. News Tasks (`backend/src/tasks/news_tasks.py`)

#### NewsUpdateConfig
Dataclass for configuration management:
- `source_dirs`: List of news source directories
- `chunk_size`: 800 characters (optimized for embeddings)
- `chunk_overlap`: 150 characters (context preservation)
- `collection_name`: `news_analyzed_2025_800_150_large_v2`
- `analyzer_mode`: async (concurrent LLM calls)
- `max_concurrent`: 20 (vectorization concurrency)

#### TelegramNewsFetcher
Responsible for collecting news from Telegram channels:
- Uses `NewsCollectionService` from telegram_fetcher module
- Collects messages from yesterday (00:00 to 23:59 Baku time)
- Output: JSON files in source-specific directories

#### ArticleContentParser
Parses full article content from collected URLs:
- Uses `NewsParsingService` with concurrent processing (50 parallel)
- Extracts full text, images, metadata from source websites
- Updates JSON files with `detail` field

#### NewsVectorizer
Performs AI analysis and vectorization:
- **"Analyze ONCE, Chunk MANY" pattern**: Analyzes full article once, then chunks
- LLM Analysis: category, entities, sentiment, importance (1-10)
- Embedding: OpenAI text-embedding-3-large
- Storage: PostgreSQL (metadata) + ChromaDB (vectors)

#### DailyNewsUpdateOrchestrator
Orchestrates the 3-step pipeline:
1. Fetch → 2. Parse → 3. Vectorize

**Error Handling**:
- Retries: Max 3 attempts with 5-minute delay
- Detailed logging for each step
- Graceful failure (doesn't block other tasks)

### 3. Docker Services

#### Redis
```yaml
image: redis:7-alpine
ports: 6379
resources: Minimal (in-memory, fast)
healthcheck: redis-cli ping
```

#### Celery Worker
```yaml
image: searchnewsrag-backend:latest
command: celery -A tasks.celery_app worker
concurrency: 2 (local) / 4 (prod)
resources:
  limits: 2-4 CPU, 2-4GB RAM
  reservations: 0.5-1 CPU, 512MB-1GB RAM
volumes:
  - datanew:/app/datanew (news JSON files)
  - session.session:/app/session.session:ro (Telegram auth)
```

#### Celery Beat
```yaml
image: searchnewsrag-backend:latest
command: celery -A tasks.celery_app beat
resources:
  limits: 0.5 CPU, 256MB RAM (minimal - just a scheduler)
  reservations: 0.1 CPU, 128MB RAM
volumes:
  - celerybeat-schedule:/app (persistent schedule)
```

#### Flower
```yaml
image: searchnewsrag-backend:latest
command: celery -A tasks.celery_app flower
ports: 5555
auth: Basic auth via ${FLOWER_USER}:${FLOWER_PASSWORD}
resources:
  limits: 0.5 CPU, 256MB RAM
```

## Environment Variables

### Required Variables

```bash
# Redis Configuration
REDIS_URL=redis://redis:6379/0
REDIS_PORT=6379

# Celery Configuration
CELERY_WORKER_CONCURRENCY=2  # Number of worker processes
FLOWER_PORT=5555
FLOWER_USER=admin
FLOWER_PASSWORD=change_me_in_production

# Resource Limits (Development)
CELERY_WORKER_CPU_LIMIT=2
CELERY_WORKER_MEMORY_LIMIT=2G
CELERY_WORKER_CPU_RESERVATION=0.5
CELERY_WORKER_MEMORY_RESERVATION=512M
CELERY_BEAT_CPU_LIMIT=0.5
CELERY_BEAT_MEMORY_LIMIT=256M
CELERY_BEAT_CPU_RESERVATION=0.1
CELERY_BEAT_MEMORY_RESERVATION=128M
FLOWER_CPU_LIMIT=0.5
FLOWER_MEMORY_LIMIT=256M
FLOWER_CPU_RESERVATION=0.1
FLOWER_MEMORY_RESERVATION=128M

# Production: Use higher limits for celery-worker
CELERY_WORKER_CONCURRENCY=4
CELERY_WORKER_CPU_LIMIT=4
CELERY_WORKER_MEMORY_LIMIT=4G
```

### OpenAI & Telegram (Already Existing)
```bash
OPENAI_API_KEY=sk-...
API_ID=12345678
API_HASH=abc123...
```

## Task Schedule

| Task | Schedule | Timezone | Description |
|------|----------|----------|-------------|
| `daily_news_update` | 00:01 | Asia/Baku | Collect, parse, vectorize yesterday's news |

## Monitoring

### Flower Dashboard
Access: `http://localhost:5555` (local) / `http://news.aitools.az:5555` (prod)

**Features**:
- Real-time task monitoring
- Worker status and performance
- Task history and success/failure rates
- Task arguments and results inspection

**Authentication**:
- Username: From `FLOWER_USER` env var
- Password: From `FLOWER_PASSWORD` env var

### Logs

**View logs**:
```bash
# All Celery services
docker-compose logs -f celery-worker celery-beat flower

# Worker only
docker-compose logs -f celery-worker

# Beat scheduler only
docker-compose logs -f celery-beat

# Last 100 lines
docker-compose logs --tail=100 celery-worker
```

**Log Format**:
```
[2025-01-24 00:01:00,123: INFO/MainProcess] Task tasks.news_tasks.daily_news_update[abc-123] received
[2025-01-24 00:01:05,456: INFO/ForkPoolWorker-1] Starting daily news update for 2025-01-23
[2025-01-24 00:05:30,789: INFO/ForkPoolWorker-1] Fetching complete: 45 messages collected
[2025-01-24 00:15:45,012: INFO/ForkPoolWorker-1] Parsing complete: 42 articles parsed
[2025-01-24 00:45:20,345: INFO/ForkPoolWorker-1] Vectorization complete: 42 articles processed
[2025-01-24 00:45:20,678: INFO/ForkPoolWorker-1] Task tasks.news_tasks.daily_news_update[abc-123] succeeded
```

## Deployment

### Local Development

```bash
# Start all services
docker-compose up -d

# Verify Celery worker registered task
docker-compose logs celery-worker | grep "daily_news_update"

# Expected output:
# [tasks]
#   . tasks.news_tasks.daily_news_update

# Check Beat schedule
docker-compose logs celery-beat | grep "daily-news-update"

# Trigger manual task execution (for testing)
docker-compose exec celery-worker celery -A tasks.celery_app call tasks.news_tasks.daily_news_update
```

### Production

```bash
# Deploy via GitHub Actions
git push origin main

# Or manual deployment
ssh user@vps
cd /opt/searchnewsrag
docker-compose -f docker-compose.prod.yml up -d --force-recreate celery-worker celery-beat flower

# Verify services
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs -f celery-worker
```

## Telegram Session Persistence

### Initial Setup

**First time only** - authenticate Telegram session:

```bash
# Local development
python -m telegram_fetcher --stop-date 2025-01-01

# Enter phone number and verification code when prompted
# This creates session.session file in project root

# Production - copy session file to VPS
scp session.session user@vps:/opt/searchnewsrag/session.session
```

### Volume Mounting

The `session.session` file is mounted as **read-only** to prevent accidental corruption:

```yaml
volumes:
  - ./session.session:/app/session.session:ro  # Local
  - session_data:/app/session.session:ro       # Production
```

**Important**: If session expires (rare), you'll need to:
1. Stop celery-worker
2. Re-authenticate locally
3. Copy new session.session file
4. Restart celery-worker

## Resource Management

### Why Minimal Resources for Celery Beat?

Celery Beat is **only a scheduler** - it doesn't execute tasks, just sends them to the queue. Therefore:
- CPU: 0.5 core (plenty for scheduling)
- Memory: 256MB (mostly idle)
- No need for ChromaDB/PostgreSQL connections

### Celery Worker Resource Allocation

**Development** (docker-compose.yml):
- CPU: 2 cores, 512MB reserved
- Memory: 2GB limit, 512MB reserved
- Concurrency: 2 workers

**Production** (docker-compose.prod.yml):
- CPU: 4 cores, 1 core reserved
- Memory: 4GB limit, 1GB reserved
- Concurrency: 4 workers

**Why these limits?**
- AI operations (OpenAI API calls) are I/O-bound, not CPU-bound
- ChromaDB operations can be memory-intensive with large collections
- Prevents runaway processes from killing VPS

## Troubleshooting

### Issue: Task not executing at scheduled time

**Solution**:
```bash
# Check Beat logs for schedule
docker-compose logs celery-beat | grep "Scheduler"

# Expected output:
# Scheduler: Sending due task daily-news-update (tasks.news_tasks.daily_news_update)

# Verify timezone
docker-compose exec celery-beat date
# Should show Asia/Baku time
```

### Issue: Worker OOM (Out of Memory)

**Solution**:
```bash
# Check memory usage
docker stats celery-worker

# Increase memory limit in .env
CELERY_WORKER_MEMORY_LIMIT=4G

# Reduce concurrency
CELERY_WORKER_CONCURRENCY=2

# Restart
docker-compose up -d celery-worker
```

### Issue: Telegram session expired

**Solution**:
```bash
# Stop worker
docker-compose stop celery-worker

# Re-authenticate locally
python -m telegram_fetcher --stop-date 2025-01-24

# Copy new session (if production)
scp session.session user@vps:/opt/searchnewsrag/session.session

# Restart worker
docker-compose up -d celery-worker
```

### Issue: Duplicate news entries

**Not an issue!** PostgreSQL has `UniqueConstraint(source_id, message_id)` in `Article` table. Duplicate entries are automatically rejected.

## Performance Metrics

### Expected Execution Times

| Operation | Articles | Time | Rate |
|-----------|----------|------|------|
| Fetch | 50 | ~5 min | 10/min |
| Parse (50 conc.) | 50 | ~10 min | 5/min |
| Vectorize (20 conc.) | 50 | ~30 min | 1.6/min |
| **Total** | 50 | ~45 min | - |

**Note**: Times vary based on:
- Article length
- Network latency
- OpenAI API response time
- Server resources

### Cost Estimation

**OpenAI API costs per 50 articles**:
- Analysis (GPT-4): ~$0.50 (1 call per article)
- Embeddings (text-embedding-3-large): ~$0.02 (10-15 chunks per article)
- **Total**: ~$0.52 per day (~$16/month)

**"Analyze ONCE, Chunk MANY" saves 90%+ on costs!**

## Security Best Practices

1. **No hardcoded credentials**: All passwords via environment variables
2. **Flower authentication**: Basic auth to prevent unauthorized access
3. **Read-only session**: Telegram session mounted as read-only
4. **Resource limits**: Prevents DoS from runaway processes
5. **Network isolation**: Celery services on private Docker network

## Future Enhancements

- [ ] Add task for real-time news monitoring (every 15 minutes)
- [ ] Implement task priority queue (breaking news = high priority)
- [ ] Add task for automated analytics reports (weekly)
- [ ] Implement task result webhooks for notifications
- [ ] Add Celery task metrics export to Prometheus

## References

- [Celery Documentation](https://docs.celeryproject.org/)
- [Redis Documentation](https://redis.io/docs/)
- [Flower Documentation](https://flower.readthedocs.io/)
- [Docker Compose Resource Limits](https://docs.docker.com/compose/compose-file/deploy/)
