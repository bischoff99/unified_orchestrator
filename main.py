#!/usr/bin/env python3
"""Production Multi-Agent Orchestrator - Main Entry Point"""
import asyncio
import argparse
import os
from src.orchestrator.crew_config import ProductionCrew
from src.utils.logging_setup import setup_logging

log = setup_logging()

async def main():
    parser = argparse.ArgumentParser(
        description="Production Multi-Agent Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py "Build a FastAPI notes service"
  python main.py "Build a FastAPI notes service" --backend ollama
  python main.py "Build a FastAPI notes service" --backend mlx
  python main.py "Create a React dashboard" --benchmark

Backends:
  ollama  - Local Ollama models (default)
  mlx     - Apple Silicon MLX backend
  openai  - OpenAI API
        """
    )
    
    parser.add_argument(
        "task",
        help="Task description for the multi-agent crew"
    )
    
    parser.add_argument(
        "--backend",
        choices=["ollama", "mlx", "openai"],
        default="ollama",
        help="LLM backend to use (default: ollama)"
    )
    
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Collect performance metrics"
    )
    
    args = parser.parse_args()
    
    # Set backend environment variable
    os.environ["MODEL_BACKEND"] = args.backend
    
    log.info(f"Task: {args.task}")
    log.info(f"Backend: {args.backend}")
    
    # Run with metrics if benchmarking
    if args.benchmark:
        try:
            from src.utils.metrics import MetricsCollector
            metrics = MetricsCollector()
            
            with metrics.measure("orchestration"):
                crew = ProductionCrew(args.task)
                result = await asyncio.to_thread(crew.run)
            
            metrics.save()
            log.info(f"Metrics saved to logs/metrics.json")
            log.info(f"Summary: {metrics.summary()}")
        except ImportError:
            log.warning("Metrics module not available, running without benchmarking")
            crew = ProductionCrew(args.task)
            result = await asyncio.to_thread(crew.run)
    else:
        crew = ProductionCrew(args.task)
        result = await asyncio.to_thread(crew.run)
    
    log.info("Orchestration complete")
    print("\n" + "="*60)
    print("RESULT")
    print("="*60)
    print(result)
    
    return result

if __name__ == "__main__":
    asyncio.run(main())
