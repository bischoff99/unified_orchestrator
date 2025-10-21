# Monitoring Infrastructure

Production monitoring stack for unified_orchestrator with Prometheus, Grafana, and MLflow.

## Quick Start

### Start Monitoring Stack

```bash
# Start all monitoring services
./scripts/start_monitoring.sh

# Or manually with docker-compose
docker-compose --profile monitoring up -d
```

### Access Services

- **Grafana:** http://localhost:3000 (admin/admin)
- **Prometheus:** http://localhost:9090
- **MLflow:** http://localhost:5000
- **Node Exporter:** http://localhost:9100/metrics

### Setup Nightly Profiling

```bash
# Install cron job (runs daily at 2 AM)
./scripts/setup_cron.sh

# Verify installation
crontab -l | grep nightly_profile

# View logs
tail -f logs/nightly_profiling.log
```

## Dashboards

### HuggingFace Pro + MCP Dashboard

**Location:** `monitoring/dashboards/hf_pro_dashboard.json`

**Panels:**
1. Inference Latency (p50, p95, p99)
2. Daily Cost tracking
3. Total Tokens Generated
4. Safety Filter Failures
5. GPU Memory Usage
6. Budget Status (% used)
7. Token Generation Rate
8. Safety Pass Rate

**Alerts:**
- High latency (>100ms)
- Budget warning (>80%)
- Safety failures (>1%)

## Alerts

**Configuration:** `monitoring/alerts.yml`

### Alert Types

**Performance:**
- HighInferenceLatency: Latency >100ms for 5min
- LowThroughput: <10 tokens/sec for 10min

**Cost:**
- BudgetWarning: Daily cost >£2.66 (80% of budget)
- BudgetExceeded: Daily cost >=£3.33

**Safety:**
- HighSafetyFailureRate: >1% failures
- CriticalSafetyFailures: >5% failures

**Training:**
- TrainingStalled: No progress for 15min
- HighTrainingLoss: Loss >2.0
- HighGPUMemory: >80%
- CriticalGPUMemory: >95%

**System:**
- HighCPUUsage: >90% for 5min
- HighMemoryUsage: >90% for 3min
- DiskSpaceLow: <10GB free

## Metrics Exposed

From `src/mcp/continuous_monitor.py`:

```python
LATENCY = Histogram('hf_inference_latency_ms')
TOKENS_GENERATED = Counter('tokens_generated_total')
GPU_MEMORY = Gauge('gpu_memory_percent')
SAFETY_FAILURES = Counter('safety_failures_total')
COST_DAILY = Gauge('cost_daily_pounds')
```

## Usage

### Enable Metrics in Code

```python
from src.mcp import ContinuousMonitor, start_monitoring_server

# Start metrics server
start_monitoring_server(port=9090)

# Record metrics
monitor = ContinuousMonitor()
monitor.record_inference(latency_ms=75.0, tokens=100, passed_safety=True)
monitor.record_gpu_memory(percent=45.0)
monitor.record_cost(daily_cost=1.50, budget=3.33)
```

### View Metrics

```bash
# Prometheus metrics endpoint
curl http://localhost:9090/metrics

# Query specific metric
curl 'http://localhost:9090/api/v1/query?query=hf_inference_latency_ms'
```

## Troubleshooting

### Services won't start

```bash
# Check Docker is running
docker ps

# Check logs
docker-compose --profile monitoring logs prometheus
docker-compose --profile monitoring logs grafana
```

### Grafana dashboard not showing

1. Verify Prometheus is scraping: http://localhost:9090/targets
2. Check Prometheus data source in Grafana
3. Verify metrics are being generated (run inference)

### Alerts not firing

1. Check alert rules: http://localhost:9090/alerts
2. Verify Alertmanager is configured
3. Check alert rule syntax in `alerts.yml`

## Maintenance

### Stop Monitoring

```bash
docker-compose --profile monitoring down
```

### Clean Up Data

```bash
# Remove all monitoring data (metrics, dashboards state)
docker-compose --profile monitoring down -v
```

### Update Dashboards

1. Edit `monitoring/dashboards/hf_pro_dashboard.json`
2. Restart Grafana: `docker-compose restart grafana`
3. Refresh dashboard in browser

### Update Alert Rules

1. Edit `monitoring/alerts.yml`
2. Reload Prometheus: `curl -X POST http://localhost:9090/-/reload`

## Architecture

```
Application (Python)
    ↓ (exposes metrics on :9090)
Prometheus (scrapes metrics)
    ↓ (stores time-series data)
Grafana (visualizes)
    ↓ (dashboards + alerts)
User (monitors)
```

## Integration with MCP Tools

The monitoring stack integrates with all MCP components:

- **DataValidator:** Logs validation success/failure rates
- **SafetyValidator:** Tracks toxicity detection metrics
- **ProfilingAnalyzer:** Provides bottleneck analysis
- **ContinuousMonitor:** Exposes all metrics to Prometheus
- **HFCostMonitor:** Tracks budget usage
- **HFProClient:** Records latency and token usage

