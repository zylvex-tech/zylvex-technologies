# Monitoring Stack — Zylvex Technologies

Prometheus + Grafana + Alertmanager monitoring stack for all Zylvex platform services.

## Quick Start

1. **Start the full application stack first** (if not already running):

   ```bash
   docker compose -f docker-compose.full-stack.yml up -d
   ```

2. **Start the monitoring stack:**

   ```bash
   cd infrastructure/monitoring
   docker compose -f docker-compose.monitoring.yml up -d
   ```

   > The monitoring stack uses the same `zylvex-network` as the full stack, so the
   > full stack must be running (or the network must exist) before starting monitoring.

3. **Access the dashboards:**

   | Service      | URL                        |
   |-------------|----------------------------|
   | Prometheus  | http://localhost:9090       |
   | Grafana     | http://localhost:3000       |
   | Alertmanager| http://localhost:9093       |

## Default Grafana Login

- **Username:** `admin`
- **Password:** `zylvex-grafana`

> Change the password on first login in production.

## Pre-Provisioned Dashboards

Dashboards are auto-imported on Grafana startup via provisioning:

| Dashboard               | Description                                              |
|------------------------|----------------------------------------------------------|
| **Zylvex Platform Overview** | Total requests/sec, error rates, p50/p95/p99 latency, WebSocket connections, anchors & mind maps created/hr, active users |
| **Auth Service**        | Login success/failure rate, registration rate, token verification latency, cache hit rate |

### Importing Additional Dashboards

1. Open Grafana at http://localhost:3000
2. Go to **Dashboards → Import**
3. Upload a JSON file or paste JSON model
4. Select **Prometheus** as the data source

## How to Add a New Alert Rule

1. Create a new `.yml` file in `prometheus/alerts/` (or add rules to an existing file):

   ```yaml
   groups:
     - name: my_alerts
       rules:
         - alert: MyNewAlert
           expr: my_metric > threshold
           for: 5m
           labels:
             severity: warning
           annotations:
             summary: "Description of the alert"
             description: "Detailed info with {{ $value }}"
   ```

2. Restart Prometheus to pick up the new rules:

   ```bash
   docker compose -f docker-compose.monitoring.yml restart prometheus
   ```

   Or, if `--web.enable-lifecycle` is set (default), reload config without restart:

   ```bash
   curl -X POST http://localhost:9090/-/reload
   ```

3. Verify in Prometheus UI → **Status → Rules**.

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│  Prometheus  │────▶│   Grafana   │     │ Alertmanager │
│   :9090      │     │   :3000     │     │    :9093     │
└──────┬───────┘     └─────────────┘     └──────────────┘
       │ scrapes /metrics every 15s              ▲
       │                                         │ alerts
       ▼                                         │
┌──────────────────────────────────────────────────────┐
│  auth:8001  spatial:8000  mm:8002  social:8003       │
│  notifications:8005  realtime:8004  web-app:80       │
└──────────────────────────────────────────────────────┘
```

## Scraped Services

All services expose `/metrics` via `prometheus-fastapi-instrumentator`:

| Service              | Target                              |
|---------------------|-------------------------------------|
| Auth Service        | `auth-service:8001/metrics`         |
| Spatial Canvas      | `spatial-canvas-backend:8000/metrics` |
| Mind Mapper         | `mind-mapper-backend:8002/metrics`  |
| Social Service      | `social-service:8003/metrics`       |
| Notifications       | `notifications-service:8005/metrics`|
| Realtime Gateway    | `realtime-service:8004/metrics`     |
| Web App (nginx)     | `web-app:80/stub_metrics`           |
