"""Benchmark Script for Performance Testing"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrator.crew_config import ProductionCrew
from src.utils.metrics import MetricsCollector

def benchmark(task: str = "Build a FastAPI notes service with React frontend"):
    """
    Run benchmark test on the production crew.
    
    Args:
        task: Task description to benchmark
    """
    print(f"Starting benchmark for task: {task}")
    print("="*60)
    
    metrics = MetricsCollector()
    
    try:
        with metrics.measure("full_workflow"):
            crew = ProductionCrew(task)
            result = crew.run()
        
        # Save metrics
        metrics.save()
        print("\n" + "="*60)
        print("BENCHMARK COMPLETE")
        print("="*60)
        print(f"\nResults saved to: logs/metrics.json")
        print(f"\nSummary: {metrics.summary()}")
        
        return result
        
    except Exception as e:
        print(f"\nError during benchmark: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Benchmark the production orchestrator")
    parser.add_argument(
        "--task",
        default="Build a FastAPI notes service with React frontend",
        help="Task description to benchmark"
    )
    
    args = parser.parse_args()
    benchmark(args.task)

