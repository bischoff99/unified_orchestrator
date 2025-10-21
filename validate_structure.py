#!/usr/bin/env python3
"""Validate Project Structure Without Dependencies"""
import os
import ast
from pathlib import Path

def check_file_exists(filepath):
    """Check if file exists"""
    if Path(filepath).exists():
        print(f"✅ {filepath}")
        return True
    else:
        print(f"❌ {filepath} - MISSING")
        return False

def check_python_syntax(filepath):
    """Check if Python file has valid syntax"""
    try:
        with open(filepath, 'r') as f:
            ast.parse(f.read())
        return True
    except SyntaxError as e:
        print(f"   ⚠️  Syntax error: {e}")
        return False

print("="*60)
print("VALIDATING PROJECT STRUCTURE")
print("="*60)

# Track results
all_pass = True

print("\n📁 Core Structure:")
core_files = [
    "main.py",
    "config.py",
    "requirements.txt",
    "QUICKSTART.md",
    ".env.example"
]
for f in core_files:
    exists = check_file_exists(f)
    if exists and f.endswith('.py'):
        if not check_python_syntax(f):
            all_pass = False
    elif not exists:
        all_pass = False

print("\n📦 src/ Directory:")
src_files = [
    "src/__init__.py",
    "src/orchestrator/__init__.py",
    "src/orchestrator/crew_config.py",
    "src/agents/__init__.py",
    "src/agents/architect_agent.py",
    "src/agents/fullstack_agent.py",
    "src/agents/qa_agent.py",
    "src/agents/devops_agent.py",
    "src/agents/docs_agent.py",
    "src/agents/critic_agent.py",
    "src/utils/__init__.py",
    "src/utils/mlx_backend.py",
    "src/utils/vector_store.py",
    "src/utils/metrics.py",
    "src/tools/__init__.py"
]
for f in src_files:
    exists = check_file_exists(f)
    if exists and f.endswith('.py'):
        if not check_python_syntax(f):
            all_pass = False
    elif not exists:
        all_pass = False

print("\n🧪 Benchmarks:")
bench_files = [
    "benchmarks/parallel_benchmark.py"
]
for f in bench_files:
    exists = check_file_exists(f)
    if exists and f.endswith('.py'):
        if not check_python_syntax(f):
            all_pass = False
    elif not exists:
        all_pass = False

print("\n📚 Examples:")
example_files = [
    "examples/simple_example.py",
    "examples/research_crew.py",
    "examples/example_ollama.py",
    "examples/example_anthropic.py"
]
for f in example_files:
    exists = check_file_exists(f)
    if exists and f.endswith('.py'):
        if not check_python_syntax(f):
            all_pass = False
    elif not exists:
        all_pass = False

print("\n🔧 Additional Components:")
other_files = [
    "mcp-generator/generate.py",
    "ui/web_interface.py"
]
for f in other_files:
    exists = check_file_exists(f)
    if exists and f.endswith('.py'):
        if not check_python_syntax(f):
            all_pass = False
    elif not exists:
        all_pass = False

# Check removed files
print("\n🗑️  Verifying Cleanup (should NOT exist):")
removed = [
    "orchestrators/",
    "agents/",
    "utils/",
    "CONSOLIDATION_SUMMARY.md"
]
for item in removed:
    if not Path(item).exists():
        print(f"✅ {item} - correctly removed")
    else:
        print(f"❌ {item} - should be removed")
        all_pass = False

print("\n" + "="*60)
if all_pass:
    print("✅ VALIDATION PASSED - Structure is correct!")
    print("="*60)
    print("\nNext step: Install dependencies")
    print("  pip install -r requirements.txt")
    exit(0)
else:
    print("❌ VALIDATION FAILED - See errors above")
    print("="*60)
    exit(1)

