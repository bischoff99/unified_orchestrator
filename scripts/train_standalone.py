"""Standalone LoRA training script - No CrewAI dependencies.

Runs LoRA fine-tuning with profiling, MLflow tracking, and GPU coordination.
Bypasses CrewAI imports for Python 3.9 compatibility.
"""

import logging
import torch
from pathlib import Path
import mlflow
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
)
from peft import LoraConfig, get_peft_model, TaskType, prepare_model_for_kbit_training
from datasets import load_dataset
from torchinfo import summary

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train_with_profiling(
    model_name: str = "gpt2",  # Using GPT-2 for testing (ungated, 124M params)
    dataset_path: str = "data/sample_train.jsonl",
    output_dir: str = "models/finetuned_gpt2",
    max_steps: int = 50,
    profile_steps: int = 10,
):
    """Train model with LoRA and profiling."""
    
    print("="*60)
    print("LoRA Training with Profiling")
    print("="*60)
    print(f"Model: {model_name}")
    print(f"Dataset: {dataset_path}")
    print(f"Steps: {max_steps}")
    print(f"Device: M3 Max MPS")
    print("="*60)
    
    try:
        # Start MLflow
        mlflow.set_experiment("unified_orchestrator_training")
        
        with mlflow.start_run():
            params = {
                "base_model": model_name,
                "max_steps": max_steps,
                "device": "mps",
                "lora_r": 16,
                "lora_alpha": 32,
            }
            mlflow.log_params(params)
            
            # Load model
            logger.info(f"Loading model: {model_name}")
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                device_map="mps",
                torch_dtype=torch.float16,
                use_cache=False,
            )
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
                model.config.pad_token_id = tokenizer.eos_token_id
            
            # LoRA configuration (GPT-2 uses c_attn for attention)
            lora_config = LoraConfig(
                r=16,
                lora_alpha=32,
                target_modules=["c_attn", "c_proj"],  # GPT-2 attention layers
                lora_dropout=0.05,
                bias="none",
                task_type=TaskType.CAUSAL_LM,
            )
            
            model = prepare_model_for_kbit_training(model)
            model = get_peft_model(model, lora_config)
            
            logger.info("LoRA applied to model")
            model.print_trainable_parameters()
            
            # Model summary
            model_summary = str(summary(model, verbose=0))
            mlflow.log_text(model_summary, "model_architecture.txt")
            
            # Load dataset
            logger.info(f"Loading dataset: {dataset_path}")
            dataset = load_dataset("json", data_files=dataset_path)
            
            def tokenize_function(examples):
                return tokenizer(
                    examples["text"],
                    truncation=True,
                    max_length=512,
                    padding="max_length",
                )
            
            tokenized = dataset.map(tokenize_function, batched=True, remove_columns=dataset["train"].column_names)
            logger.info(f"Dataset tokenized: {len(tokenized['train'])} examples")
            
            # Training args (MPS-compatible)
            training_args = TrainingArguments(
                output_dir=output_dir,
                max_steps=max_steps,
                per_device_train_batch_size=2,  # Smaller for GPT-2
                gradient_accumulation_steps=2,
                learning_rate=2e-4,
                # fp16=False,  # MPS doesn't support fp16 in transformers
                logging_steps=10,
                save_steps=50,
                report_to="mlflow",
                dataloader_num_workers=4,  # Reduced for stability
                warmup_steps=5,
                max_grad_norm=1.0,
                optim="adamw_torch",
            )
            
            data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
            
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=tokenized["train"],
                data_collator=data_collator,
            )
            
            # Train with profiling
            logger.info("Starting training with profiling...")
            
            with torch.profiler.profile(
                activities=[
                    torch.profiler.ProfilerActivity.CPU,  # MPS profiling not available in this PyTorch version
                ],
                schedule=torch.profiler.schedule(wait=1, warmup=1, active=profile_steps, repeat=1),
                on_trace_ready=torch.profiler.tensorboard_trace_handler("logs/profiling"),
                record_shapes=True,
                profile_memory=True,
                with_stack=True,
            ) as prof:
                train_output = trainer.train()
                prof.step()
            
            logger.info("Training complete!")
            
            # Save profiling report
            prof_report = prof.key_averages().table(sort_by="self_mps_time_total", row_limit=20)
            print("\nProfiling Report:")
            print(prof_report)
            mlflow.log_text(prof_report, "profiling_report.txt")
            
            # Log metrics
            metrics = {
                "final_loss": train_output.training_loss,
                "train_runtime_sec": train_output.metrics["train_runtime"],
                "train_samples_per_sec": train_output.metrics["train_samples_per_second"],
            }
            mlflow.log_metrics(metrics)
            
            # Save model
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            model.save_pretrained(output_dir)
            tokenizer.save_pretrained(output_dir)
            
            mlflow.end_run()
            
            print("\n" + "="*60)
            print("TRAINING COMPLETE!")
            print("="*60)
            print(f"Model saved: {output_dir}")
            print(f"Final loss: {train_output.training_loss:.4f}")
            print(f"Runtime: {train_output.metrics['train_runtime']:.1f}s")
            print(f"Samples/sec: {train_output.metrics['train_samples_per_second']:.2f}")
            print("\nView results:")
            print("  MLflow: http://localhost:5000")
            print("  TensorBoard: tensorboard --logdir logs/profiling")
            print("="*60)
            
            return {"status": "success", "model_path": output_dir, "loss": train_output.training_loss}
            
    except Exception as e:
        logger.error(f"Training failed: {e}", exc_info=True)
        return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    result = train_with_profiling()
    if result["status"] != "success":
        exit(1)

