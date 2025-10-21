"""Optimization benchmarking - Iterative profiling and speedup measurement.

Demonstrates the complete MCP optimization workflow:
1. Baseline training with profiling
2. Analyze bottlenecks
3. Apply optimizations
4. Re-train and measure speedup
5. Iterate until optimal

Target: 40-60% speedup via MCP-driven optimizations.
"""

import logging
import json
from pathlib import Path
from datetime import datetime

from src.agents.hf_trainer_agent import HFTrainerAgent
from src.mcp import ProfilingAnalyzer, iterative_optimization

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_baseline_benchmark(config: dict) -> dict:
    """Run baseline training without optimizations.
    
    Args:
        config: Training configuration
        
    Returns:
        Baseline results with timing
    """
    logger.info("="*60)
    logger.info("BASELINE: Training without optimizations")
    logger.info("="*60)
    
    # Run training with profiling
    result = HFTrainerAgent.train_with_profiling(**config)
    
    if result["status"] == "success":
        baseline = {
            "runtime_sec": result["metrics"]["train_runtime_sec"],
            "samples_per_sec": result["metrics"]["train_samples_per_sec"],
            "loss": result["loss"],
            "config": config,
        }
        logger.info(f"Baseline runtime: {baseline['runtime_sec']:.1f}s")
        logger.info(f"Baseline throughput: {baseline['samples_per_sec']:.2f} samples/sec")
        return baseline
    else:
        logger.error(f"Baseline training failed: {result.get('error')}")
        return {}


def run_optimized_benchmark(base_config: dict, iterations: int = 3) -> dict:
    """Run optimized training with iterative improvements.
    
    Args:
        base_config: Base training configuration
        iterations: Number of optimization iterations
        
    Returns:
        Optimized results with speedup metrics
    """
    logger.info("="*60)
    logger.info(f"OPTIMIZED: Iterative optimization ({iterations} iterations)")
    logger.info("="*60)
    
    # Run iterative optimization
    results = iterative_optimization(base_config, max_iterations=iterations)
    
    # Get final optimized result
    final_config = results[-1]["config"]
    
    # Train with final optimized config
    logger.info("Training with final optimized configuration...")
    optimized_result = HFTrainerAgent.train_with_profiling(**final_config)
    
    if optimized_result["status"] == "success":
        optimized = {
            "runtime_sec": optimized_result["metrics"]["train_runtime_sec"],
            "samples_per_sec": optimized_result["metrics"]["train_samples_per_sec"],
            "loss": optimized_result["loss"],
            "config": final_config,
            "iterations": len(results),
        }
        logger.info(f"Optimized runtime: {optimized['runtime_sec']:.1f}s")
        logger.info(f"Optimized throughput: {optimized['samples_per_sec']:.2f} samples/sec")
        return optimized
    else:
        logger.error(f"Optimized training failed: {optimized_result.get('error')}")
        return {}


def calculate_speedup(baseline: dict, optimized: dict) -> dict:
    """Calculate speedup metrics.
    
    Args:
        baseline: Baseline results
        optimized: Optimized results
        
    Returns:
        Speedup metrics dictionary
    """
    runtime_speedup = ((baseline["runtime_sec"] - optimized["runtime_sec"]) 
                       / baseline["runtime_sec"] * 100)
    
    throughput_improvement = ((optimized["samples_per_sec"] - baseline["samples_per_sec"]) 
                               / baseline["samples_per_sec"] * 100)
    
    return {
        "runtime_speedup_pct": runtime_speedup,
        "throughput_improvement_pct": throughput_improvement,
        "baseline_runtime_sec": baseline["runtime_sec"],
        "optimized_runtime_sec": optimized["runtime_sec"],
        "time_saved_sec": baseline["runtime_sec"] - optimized["runtime_sec"],
        "baseline_throughput": baseline["samples_per_sec"],
        "optimized_throughput": optimized["samples_per_sec"],
        "target_met": runtime_speedup >= 40,  # 40-60% target
    }


def main():
    """Run complete optimization benchmark."""
    
    print("="*60)
    print("MCP OPTIMIZATION BENCHMARK")
    print("Target: 40-60% speedup via profiling-driven optimizations")
    print("="*60)
    print()
    
    # Base configuration (intentionally unoptimized)
    base_config = {
        "model_name": "meta-llama/Llama-3.1-8B-Instruct",
        "dataset_path": "data/training_data.jsonl",  # User must provide
        "output_dir": "models/benchmark_baseline",
        "max_steps": 100,
        "profile_steps": 20,
    }
    
    # Check if dataset exists
    if not Path(base_config["dataset_path"]).exists():
        print("⚠️  Training dataset not found!")
        print(f"   Expected: {base_config['dataset_path']}")
        print()
        print("📝 To run benchmark:")
        print("   1. Prepare training data in JSONL format")
        print("   2. Update dataset_path in this script")
        print("   3. Run: python benchmarks/optimization_benchmark.py")
        print()
        print("Example data format (JSONL):")
        print('   {"text": "Your training text here"}')
        print()
        return
    
    # Step 1: Baseline
    print("📊 Step 1/3: Running baseline training...")
    baseline = run_baseline_benchmark(base_config)
    
    if not baseline:
        print("❌ Baseline training failed. Aborting benchmark.")
        return
    
    # Step 2: Optimized
    print("\n📊 Step 2/3: Running optimized training...")
    optimized_config = base_config.copy()
    optimized_config["output_dir"] = "models/benchmark_optimized"
    optimized = run_optimized_benchmark(optimized_config, iterations=3)
    
    if not optimized:
        print("❌ Optimized training failed. Aborting benchmark.")
        return
    
    # Step 3: Calculate and report speedup
    print("\n📊 Step 3/3: Calculating speedup...")
    speedup_metrics = calculate_speedup(baseline, optimized)
    
    # Print report
    print("\n" + "="*60)
    print("BENCHMARK RESULTS")
    print("="*60)
    print()
    print(f"Baseline Runtime:    {speedup_metrics['baseline_runtime_sec']:.1f}s")
    print(f"Optimized Runtime:   {speedup_metrics['optimized_runtime_sec']:.1f}s")
    print(f"Time Saved:          {speedup_metrics['time_saved_sec']:.1f}s")
    print()
    print(f"🚀 Runtime Speedup:       {speedup_metrics['runtime_speedup_pct']:.1f}%")
    print(f"🔥 Throughput Improvement: {speedup_metrics['throughput_improvement_pct']:.1f}%")
    print()
    
    if speedup_metrics["target_met"]:
        print(f"✅ TARGET MET: Speedup >= 40% target")
    else:
        print(f"⚠️  Target not met: {speedup_metrics['runtime_speedup_pct']:.1f}% < 40%")
    
    # Save detailed report
    report_dir = Path("logs/benchmarks")
    report_dir.mkdir(exist_ok=True, parents=True)
    
    report_file = report_dir / f"optimization_benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    full_report = {
        "timestamp": datetime.now().isoformat(),
        "baseline": baseline,
        "optimized": optimized,
        "speedup_metrics": speedup_metrics,
        "target": "40-60% speedup",
        "target_met": speedup_metrics["target_met"],
    }
    
    with open(report_file, 'w') as f:
        json.dump(full_report, f, indent=2)
    
    print(f"\n📄 Full report saved: {report_file}")
    print("="*60)


if __name__ == "__main__":
    main()

