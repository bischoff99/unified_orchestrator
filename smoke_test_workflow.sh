#!/bin/bash
set -e

echo "🧪 Running workflow smoke test..."

if timeout 60 python main.py "Write a Python function to calculate factorial" --backend ollama > /tmp/orchestrator_test.log 2>&1; then
  output_size=$(wc -c < /tmp/orchestrator_test.log)
  echo "✅ Workflow completed successfully. Output size: ${output_size} bytes."
else
  echo "❌ Workflow failed. Showing last 20 lines of log:"
  tail -n 20 /tmp/orchestrator_test.log || true
  exit 1
fi
