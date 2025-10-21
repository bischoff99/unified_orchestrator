#!/bin/bash
# Smoke tests for unified orchestrator

set -e

echo "================================"
echo "SMOKE TESTS"
echo "================================"
echo ""

echo "1️⃣  Checking vector store module..."
python3 - <<'PY'
try:
    from src.utils.vector_store import VectorMemory
    print("✅ Vector store module OK")
except Exception as e:
    print(f"❌ Vector store failed: {e}")
    exit(1)
PY

echo ""
echo "2️⃣  Checking import paths..."
python3 - <<'PY'
import importlib
modules = [
    "src.agents.qa_agent",
    "src.agents.devops_agent",
    "src.agents.docs_agent",
    "src.orchestrator.crew_config",
    "src.utils.mlx_backend",
    "src.utils.metrics"
]
try:
    for m in modules:
        importlib.import_module(m)
    print("✅ All imports OK")
except Exception as e:
    print(f"❌ Import failed: {e}")
    exit(1)
PY

echo ""
echo "3️⃣  Checking structure..."
python3 validate_structure.py

echo ""
echo "================================"
echo "✅ ALL SMOKE TESTS PASSED"
echo "================================"

