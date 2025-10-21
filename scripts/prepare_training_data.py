"""Download and prepare HuggingFace training dataset."""
import sys
from pathlib import Path

def prepare_dataset(dataset_name: str = "imdb", max_samples: int = 1000):
    """Download and prepare HF dataset for training.
    
    Args:
        dataset_name: HuggingFace dataset ID (alpaca, imdb, oasst, code)
        max_samples: Maximum samples to use
    """
    try:
        from datasets import load_dataset
    except ImportError:
        print("❌ datasets library not installed")
        print("Run: pip install datasets")
        sys.exit(1)
    
    print(f"📥 Loading dataset: {dataset_name} ({max_samples} samples)")
    
    try:
        if dataset_name == "alpaca":
            dataset = load_dataset("tatsu-lab/alpaca", split=f"train[:{max_samples}]")
            dataset = dataset.map(
                lambda x: {"text": f"### Instruction: {x['instruction']}\n### Input: {x['input']}\n### Response: {x['output']}"},
                remove_columns=dataset.column_names
            )
        
        elif dataset_name == "imdb":
            dataset = load_dataset("imdb", split=f"train[:{max_samples}]")
            dataset = dataset.map(
                lambda x: {"text": x["text"]},
                remove_columns=['label']
            )
        
        elif dataset_name == "oasst":
            dataset = load_dataset("OpenAssistant/oasst1", split=f"train[:{max_samples}]")
            dataset = dataset.map(lambda x: {"text": x["text"]})
        
        elif dataset_name == "code":
            dataset = load_dataset("sahil2801/CodeAlpaca-20k", split=f"train[:{max_samples}]")
            dataset = dataset.map(
                lambda x: {"text": f"# Task: {x['instruction']}\n{x['output']}"},
                remove_columns=dataset.column_names
            )
        
        else:
            print(f"❌ Unknown dataset: {dataset_name}")
            print("Available: alpaca, imdb, oasst, code")
            sys.exit(1)
        
        # Save as JSONL
        output_path = Path("data/sample_train.jsonl")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        dataset.to_json(output_path)
        
        print(f"\n✅ Success!")
        print(f"   Saved {len(dataset)} examples to: {output_path}")
        print(f"   Sample text (first 200 chars):")
        print(f"   {dataset[0]['text'][:200]}...")
        print(f"\n🚀 Ready to train!")
        print(f"   Run: python examples/train_custom_model.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Default: IMDB dataset (quick testing, simple text)
    prepare_dataset(dataset_name="imdb", max_samples=1000)

