"""Example: Train custom model with HFTrainerAgent

Demonstrates LoRA fine-tuning with integrated profiling on M3 Max.
"""
import logging
from src.agents.hf_trainer_agent import HFTrainerAgent

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Run training example."""
    
    print("="*60)
    print("HF Trainer Agent - LoRA Fine-tuning Example")
    print("="*60)
    
    # Create agent instance
    agent = HFTrainerAgent()
    
    # Training configuration
    config = {
        "model_name": "meta-llama/Llama-3.1-8B-Instruct",
        "dataset_path": "data/sample_train.jsonl",  # Create your training data
        "output_dir": "models/finetuned_llama",
        "hf_repo": None,  # Set to "your-username/model-name" to upload
        "max_steps": 50,  # Small number for testing
        "profile_steps": 10,
    }
    
    print(f"\nTraining Configuration:")
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    print(f"\n🚀 Starting training...")
    print(f"   Device: M3 Max (MPS)")
    print(f"   Method: LoRA (r=16, alpha=32)")
    print(f"   Profiling: Enabled")
    print(f"   Tracking: MLflow\n")
    
    # Run training with profiling
    result = agent.train_with_profiling(**config)
    
    # Display results
    print("\n" + "="*60)
    print("TRAINING COMPLETE")
    print("="*60)
    
    if result["status"] == "success":
        print(f"\n✅ Status: SUCCESS")
        print(f"\n📁 Model saved to: {result['model_path']}")
        print(f"📊 Final loss: {result['loss']:.4f}")
        print(f"⏱️  Runtime: {result['metrics']['train_runtime_sec']:.1f}s")
        print(f"🔥 Samples/sec: {result['metrics']['train_samples_per_sec']:.2f}")
        
        # MCP Analysis
        if "mcp_findings" in result:
            findings = result["mcp_findings"]
            print(f"\n🔍 MCP Profiling Analysis:")
            print(f"   Bottlenecks found: {findings['metrics']['num_bottlenecks']}")
            print(f"   Optimization potential: {findings['metrics']['optimization_potential']:.0f}%")
            
            if findings["recommendations"]:
                print(f"\n💡 Top Recommendations:")
                for i, rec in enumerate(findings["recommendations"][:3], 1):
                    print(f"   {i}. [{rec['priority']}] {rec['action']}")
                    print(f"      Expected speedup: {rec['expected_speedup']}")
        
        # HF Pro upload
        if result.get("hf_repo"):
            print(f"\n☁️  Uploaded to HF Pro: https://huggingface.co/{result['hf_repo']}")
        
        print(f"\n📈 View metrics: mlflow ui")
        print(f"📊 View profiling: tensorboard --logdir logs/profiling")
        
    else:
        print(f"\n❌ Status: FAILED")
        print(f"Error: {result.get('error', 'Unknown error')}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()

