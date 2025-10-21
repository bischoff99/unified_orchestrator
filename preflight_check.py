#!/usr/bin/env python3
"""Pre-flight Check - Validate system before running workflows"""
import os
import sys
import subprocess
from pathlib import Path

def check(name, condition, fix_hint=""):
    """Check a condition and print status"""
    status = "✅" if condition else "❌"
    print(f"{status} {name}")
    if not condition and fix_hint:
        print(f"   Fix: {fix_hint}")
    return condition

def main():
    print("="*60)
    print("  PRE-FLIGHT CHECK - M3 Max Orchestrator")
    print("="*60)
    
    all_pass = True
    
    # 1. Python Environment
    print("\n🐍 Python Environment:")
    venv_active = sys.prefix != sys.base_prefix
    all_pass &= check("Virtual environment active", venv_active, "Run: source venv/bin/activate")
    
    python_version = sys.version_info
    version_ok = (python_version.major == 3 and 10 <= python_version.minor <= 13)
    all_pass &= check(f"Python {python_version.major}.{python_version.minor} (requires 3.10-3.13)", 
                      version_ok)
    
    # 2. Dependencies
    print("\n📦 Dependencies:")
    try:
        import crewai
        check("crewai installed", True)
    except ImportError:
        all_pass &= check("crewai installed", False, "Run: pip install -r requirements.txt")
    
    try:
        import chromadb
        check("chromadb installed", True)
    except ImportError:
        all_pass &= check("chromadb installed", False, "Run: pip install chromadb")
    
    try:
        import psutil
        cpu_count = psutil.cpu_count(logical=False)
        check(f"psutil ({cpu_count} CPU cores detected)", True)
    except ImportError:
        all_pass &= check("psutil installed", False, "Run: pip install psutil")
    
    # 3. Configuration
    print("\n⚙️  Configuration:")
    env_exists = Path(".env").exists()
    all_pass &= check(".env file exists", env_exists, "Run: cp .env.example .env")
    
    if env_exists:
        from dotenv import load_dotenv
        load_dotenv()
        
        backend = os.getenv("MODEL_BACKEND", "")
        check(f"MODEL_BACKEND={backend}", backend in ["ollama", "mlx", "openai", "anthropic"])
        
        model_name = os.getenv("MODEL_NAME", "")
        check(f"MODEL_NAME={model_name}", len(model_name) > 0)
        
        batch_size = os.getenv("OLLAMA_NUM_BATCH", "512")
        check(f"OLLAMA_NUM_BATCH={batch_size} (M3 Max optimized)", int(batch_size) >= 1024)
        
        concurrent = os.getenv("MAX_CONCURRENT_TASKS", "3")
        check(f"MAX_CONCURRENT_TASKS={concurrent} (parallelism)", int(concurrent) >= 6)
    
    # 4. Ollama Service
    print("\n🦙 Ollama Service:")
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
        ollama_running = result.returncode == 0
        all_pass &= check("Ollama service running", ollama_running, "Run: ollama serve")
        
        if ollama_running:
            model_name = os.getenv("MODEL_NAME", "llama3.1:8b-instruct-q5_K_M")
            models = result.stdout
            model_available = model_name.split(":")[0] in models or model_name in models
            all_pass &= check(f"Model '{model_name}' available", model_available, 
                            f"Run: ollama pull {model_name}")
            
            model_count = len([l for l in models.split("\n") if l.strip() and not l.startswith("NAME")])
            check(f"{model_count} models loaded", True)
    except FileNotFoundError:
        all_pass &= check("Ollama installed", False, "Install from: ollama.ai/download")
    except subprocess.TimeoutExpired:
        all_pass &= check("Ollama responsive", False, "Restart: killall ollama && ollama serve")
    
    # 5. Directory Structure
    print("\n📁 Directory Structure:")
    dirs = ["src/agents", "src/orchestrator", "src/utils", "logs", "memory"]
    for d in dirs:
        all_pass &= check(f"{d}/", Path(d).exists(), f"Run: mkdir -p {d}")
    
    # 6. System Resources
    print("\n💻 System Resources:")
    try:
        mem = psutil.virtual_memory()
        total_gb = mem.total / (1024**3)
        check(f"RAM: {total_gb:.0f}GB total", total_gb >= 16)
        check(f"RAM Available: {mem.available / (1024**3):.1f}GB", mem.percent < 90)
        
        cpu = psutil.cpu_count(logical=False)
        check(f"CPU Cores: {cpu} physical", cpu >= 8)
        
        if total_gb >= 64:
            print(f"   🚀 {total_gb:.0f}GB RAM = Ready for large models (70B+)")
    except:
        pass
    
    # 7. Optimization Check
    print("\n🍎 M3 Max Optimizations:")
    ollama_config = Path.home() / ".ollama" / "config.json"
    check("Ollama config.json exists", ollama_config.exists(), 
          "See: M3_MAX_OPTIMIZATION_GUIDE.md")
    
    if ollama_config.exists():
        import json
        with open(ollama_config) as f:
            config = json.load(f)
        
        check(f"num_batch={config.get('num_batch', 0)} (high throughput)", 
              config.get("num_batch", 0) >= 1024)
        check(f"num_gpu={config.get('num_gpu', 0)} (GPU acceleration)", 
              config.get("num_gpu", 0) >= 20)
    
    # Final Verdict
    print("\n" + "="*60)
    if all_pass:
        print("✅ PRE-FLIGHT CHECK PASSED - Ready to launch!")
        print("="*60)
        print("\n🚀 Next steps:")
        print("   python main.py \"Your task here\" --backend ollama")
        return 0
    else:
        print("❌ PRE-FLIGHT CHECK FAILED - Fix issues above")
        print("="*60)
        return 1

if __name__ == "__main__":
    sys.exit(main())

