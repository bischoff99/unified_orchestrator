.PHONY: help install setup run bench test clean preflight monitor

help:
	@echo "Unified Orchestrator - Make Targets"
	@echo ""
	@echo "  make install    Install dependencies"
	@echo "  make setup      Setup environment (.env, Ollama)"
	@echo "  make preflight  Pre-flight system check (M3 Max validation)"
	@echo "  make run        Run orchestrator (Ollama backend)"
	@echo "  make run-mlx    Run orchestrator (MLX backend)"
	@echo "  make bench      Run benchmark"
	@echo "  make test       Run validation tests"
	@echo "  make monitor    Monitor M3 Max resources in real-time"
	@echo "  make clean      Clean generated files"

install:
	pip3 install -r requirements.txt

setup:
	@echo "Setting up environment..."
	@if [ ! -f .env ]; then cp .env.example .env && echo "✅ Created .env from template"; else echo "⚠️  .env already exists"; fi
	@mkdir -p .chroma logs memory src/generated
	@echo "✅ Created directories"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Edit .env with your settings"
	@echo "  2. Start Ollama: ollama serve"
	@echo "  3. Pull model: ollama pull llama3.1:8b-instruct-q5_K_M"
	@echo "  4. Run: make run"

run:
	python3 main.py "Build a FastAPI notes service with React frontend" --backend ollama

run-mlx:
	python3 main.py "Build a FastAPI notes service with React frontend" --backend mlx

bench:
	python3 main.py "Build a FastAPI notes service" --benchmark
	@echo ""
	@echo "Metrics saved to logs/metrics.json"
	@cat logs/metrics.json

bench-standalone:
	python3 benchmarks/parallel_benchmark.py

test:
	@echo "Running structure validation..."
	python3 validate_structure.py
	@echo ""
	@echo "Running import tests..."
	@python3 -c "from src.orchestrator.crew_config import ProductionCrew; from src.utils.metrics import MetricsCollector; from src.utils.vector_store import VectorMemory; print('✅ All imports successful')"

clean:
	@echo "Cleaning generated files..."
	rm -rf src/generated/* logs/* .chroma/*
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Clean complete"

# Development helpers
dev-ollama:
	ollama serve

pull-model:
	ollama pull llama3.1:8b-instruct-q5_K_M

mlx-setup:
	pip3 install mlx mlx-lm
	@echo "MLX installed. Download models to mlx_models/"

smoke-workflow:
	@echo "Running workflow smoke test (60s timeout)..."
	@chmod +x smoke_test_workflow.sh
	./smoke_test_workflow.sh

# M3 Max Optimization
preflight:
	@chmod +x preflight_check.py
	python3 preflight_check.py

monitor:
	@chmod +x monitor_resources.py
	@echo "🍎 Starting M3 Max resource monitor..."
	@echo "   Press Ctrl+C to stop"
	python3 monitor_resources.py
