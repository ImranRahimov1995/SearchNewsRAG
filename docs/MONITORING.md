# Monitoring & Observability

## Quick Start

```bash
docker-compose -f docker-compose.monitoring.yml up -d
```

**Grafana**: http://localhost:3000 (admin/monitoring_admin_2024)

## Architecture

- **Loki**: Log aggregation (port 3100)
- **Prometheus**: Metrics collection (port 9090)
- **Promtail**: Log collector from Docker containers
- **Grafana**: Visualization dashboards
- **Node Exporter**: System metrics (port 9100)
- **cAdvisor**: Container metrics (port 8080)

All logs use JSON format for structured parsing.

## Dashboards

### Docker Logs - Loki
**URL**: `/d/docker-logs-loki`

Real-time container logs with filtering by container name, log level, and text search.

**Panels**: Log stream, rate by level, distribution pie chart, error/warning counters.

### FastAPI Observability
**URL**: `/d/fastapi-observability`

Application performance metrics.

**Panels**: Total requests, RPS, 4xx/5xx errors, request rate by endpoint, response status, latency (p95/p99), memory usage.

### FastAPI Logs
**URL**: `/d/fastapi-logs`

Application-specific log viewer for SearchNewsRAG containers.

## Production Deployment

### 1. Update Environment Variables

```bash
# .env.production
GRAFANA_ADMIN_PASSWORD=<strong-password>
PROMETHEUS_RETENTION_TIME=30d
LOKI_RETENTION_PERIOD=30d
```

### 2. Deploy Stack

```bash
docker-compose -f docker-compose.monitoring.prod.yml up -d
```

### 3. Configure Nginx Reverse Proxy

```nginx
location /grafana/ {
    proxy_pass http://grafana:3000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

### 4. Setup Alerts

Configure alert rules in Grafana:
- Error rate > threshold
- High memory usage
- Service unavailable

## Log Format

All application logs use JSON:

```json
{
  "timestamp": "2025-12-22T17:19:31.134034Z",
  "level": "INFO",
  "logger": "uvicorn.access",
  "message": "127.0.0.1 - GET /health HTTP/1.1 200"
}
```

**Labels**: `job`, `container_name`, `app`, `env`, `level`, `logger`

## Queries

### LogQL (Loki)

```logql
{job="docker", container_name="searchnewsrag-backend"}
{job="docker", level="ERROR"}
sum by (level) (count_over_time({job="docker"}[5m]))
```

### PromQL (Prometheus)

```promql
http_requests_total{job="backend"}
rate(http_requests_total{job="backend"}[5m])
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

## Troubleshooting

**No data in dashboards**:
```bash
docker logs promtail
docker logs loki
curl http://localhost:3100/loki/api/v1/label
```

**Metrics missing**:
```bash
curl http://localhost:8000/metrics
curl http://localhost:9090/api/v1/targets
```

## Management

```bash
make monitoring-start
make monitoring-stop
make monitoring-logs
make monitoring-status
```
