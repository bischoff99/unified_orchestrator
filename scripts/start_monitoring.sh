#!/bin/bash
# Start monitoring stack (Prometheus + Grafana + MLflow)

echo "🚀 Starting Unified Orchestrator Monitoring Stack"
echo "=================================================="

# Start monitoring services
echo "📊 Starting Prometheus, Grafana, MLflow, Node Exporter..."
docker-compose --profile monitoring up -d

# Wait for services to be ready
echo "⏳ Waiting for services to initialize..."
sleep 10

# Check service status
echo ""
echo "📋 Service Status:"
docker-compose ps --filter "status=running" | grep -E "prometheus|grafana|mlflow|node-exporter"

echo ""
echo "✅ Monitoring stack started successfully!"
echo ""
echo "🌐 Access URLs:"
echo "   Grafana:    http://localhost:3000 (admin/admin)"
echo "   Prometheus: http://localhost:9090"
echo "   MLflow:     http://localhost:5000"
echo "   Node Stats: http://localhost:9100/metrics"
echo ""
echo "📊 Default dashboard: HuggingFace Pro + MCP Monitoring"
echo "   Navigate to: Dashboards → HuggingFace Pro + MCP Monitoring"
echo ""
echo "To stop: docker-compose --profile monitoring down"

