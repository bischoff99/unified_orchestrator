"""HuggingFace Trainer Agent - LoRA fine-tuning with MCP profiling"""
import logging
import torch
from typing import Dict, Any, Optional
from pathlib import Path

from crewai import Agent
from config import get_llm_backend

logger = logging.getLogger(__name__)


class HFTrainerAgent:
    """Agent for HuggingFace model training with integrated MCP profiling."""

    def __init__(self):
        """Initialize HF Trainer agent."""
        self.llm = get_llm_backend()
        self.tools = []  # Training is compute-heavy, not a CrewAI tool

    def create(self) -> Agent:
        """Create CrewAI agent for ML training orchestration."""
        return Agent(
            role="ML Training Specialist",
            goal="Fine-tune models on M3 Max with LoRA, profile performance, optimize training",
            backstory="""You are an ML engineer specializing in efficient fine-tuning.
            You leverage LoRA for parameter-efficient training, use M3 Max MPS acceleration,
            and always profile training runs to identify bottlenecks.
            You track all experiments with MLflow and optimize for both speed and cost.""",
            llm=self.llm,
            tools=self.tools,
            verbose=True,
        )

    @staticmethod
    def train_with_profiling(
        model_name: str = "meta-llama/Llama-3.1-8B-Instruct",
        dataset_path: str = "data/train.jsonl",
        output_dir: str = "models/finetuned",
        hf_repo: Optional[str] = None,
        max_steps: int = 100,
        profile_steps: int = 10,
    ) -> Dict[str, Any]:
        """Train model with LoRA and integrated MCP profiling.

        Args:
            model_name: HuggingFace model ID
            dataset_path: Path to training data (JSONL/CSV)
            output_dir: Directory to save trained model
            hf_repo: Optional HF repo to upload (e.g., "username/model-name")
            max_steps: Maximum training steps
            profile_steps: Number of steps to profile

        Returns:
            Dict with model_path, hf_repo, profiling_report, loss
        """
        try:
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
            from src.mcp import ProfilingAnalyzer

            # Start MLflow experiment tracking
            mlflow.set_experiment("unified_orchestrator_training")
            
            with mlflow.start_run():
                # Log parameters
                params = {
                    "base_model": model_name,
                    "max_steps": max_steps,
                    "device": "mps",
                    "lora_r": 16,
                    "lora_alpha": 32,
                    "profile_steps": profile_steps,
                }
                mlflow.log_params(params)
                logger.info(f"Training parameters: {params}")

                # Load model for M3 Max MPS
                logger.info(f"Loading model: {model_name}")
                model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    device_map="mps",
                    torch_dtype=torch.float16,
                    use_cache=False,  # Required for gradient checkpointing
                )
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                
                # Set pad token if not present
                if tokenizer.pad_token is None:
                    tokenizer.pad_token = tokenizer.eos_token
                    model.config.pad_token_id = tokenizer.eos_token_id

                # LoRA configuration (Context7 pattern)
                lora_config = LoraConfig(
                    r=16,
                    lora_alpha=32,
                    target_modules=["q_proj", "v_proj"],
                    lora_dropout=0.05,
                    bias="none",
                    task_type=TaskType.CAUSAL_LM,
                )

                # Prepare and apply LoRA
                model = prepare_model_for_kbit_training(model)
                model = get_peft_model(model, lora_config)
                
                logger.info(f"LoRA applied to model")
                model.print_trainable_parameters()

                # Model architecture summary (MCP Tool)
                model_summary_str = str(summary(model, verbose=0))
                logger.info(f"Model architecture summary generated")
                mlflow.log_text(model_summary_str, "model_architecture.txt")

                # Load and tokenize dataset
                logger.info(f"Loading dataset from {dataset_path}")
                if dataset_path.endswith(".jsonl"):
                    dataset = load_dataset("json", data_files=dataset_path)
                elif dataset_path.endswith(".csv"):
                    dataset = load_dataset("csv", data_files=dataset_path)
                else:
                    raise ValueError(f"Unsupported format: {dataset_path}")

                def tokenize_function(examples):
                    """Tokenize text examples."""
                    return tokenizer(
                        examples.get("text", examples.get("content", "")),
                        truncation=True,
                        max_length=512,
                        padding="max_length",
                    )

                tokenized_dataset = dataset.map(
                    tokenize_function,
                    batched=True,
                    remove_columns=dataset["train"].column_names,
                )
                
                logger.info(f"Dataset tokenized: {len(tokenized_dataset['train'])} examples")

                # Training arguments (M3 Max optimized)
                training_args = TrainingArguments(
                    output_dir=output_dir,
                    max_steps=max_steps,
                    per_device_train_batch_size=4,
                    gradient_accumulation_steps=4,
                    learning_rate=2e-4,
                    fp16=True,  # Mixed precision for M3 Max
                    logging_steps=10,
                    save_steps=50,
                    report_to="mlflow",
                    # M3 Max specific optimizations
                    dataloader_num_workers=8,  # 16-core CPU
                    dataloader_pin_memory=True,
                    warmup_steps=10,
                    max_grad_norm=1.0,
                    optim="adamw_torch",  # Faster than adamw_hf on MPS
                )

                # Data collator
                data_collator = DataCollatorForLanguageModeling(
                    tokenizer=tokenizer,
                    mlm=False,  # Causal LM
                )

                # Create trainer
                trainer = Trainer(
                    model=model,
                    args=training_args,
                    train_dataset=tokenized_dataset["train"],
                    data_collator=data_collator,
                )

                # MCP PROFILING INTEGRATION
                logger.info(f"Starting training with profiling ({profile_steps} steps)...")
                
                with torch.profiler.profile(
                    activities=[
                        torch.profiler.ProfilerActivity.CPU,
                        torch.profiler.ProfilerActivity.MPS,  # M3 Max GPU
                    ],
                    schedule=torch.profiler.schedule(
                        wait=1,
                        warmup=1,
                        active=profile_steps,
                        repeat=1,
                    ),
                    on_trace_ready=torch.profiler.tensorboard_trace_handler("logs/profiling"),
                    record_shapes=True,
                    profile_memory=True,
                    with_stack=True,
                ) as prof:
                    # Train with profiling
                    train_output = trainer.train()
                    prof.step()  # Advance profiler

                logger.info("Training complete!")

                # Save profiling report
                prof_report = prof.key_averages().table(
                    sort_by="self_mps_time_total", row_limit=20
                )
                logger.info(f"Profiling report:\n{prof_report}")
                mlflow.log_text(prof_report, "profiling_report.txt")

                # Log training metrics
                metrics = {
                    "final_loss": train_output.training_loss,
                    "train_runtime_sec": train_output.metrics["train_runtime"],
                    "train_samples_per_sec": train_output.metrics["train_samples_per_second"],
                }
                mlflow.log_metrics(metrics)
                logger.info(f"Training metrics: {metrics}")

                # MCP Profiling Analysis
                logger.info("Analyzing profiling data with MCP ProfilingAnalyzer...")
                findings = ProfilingAnalyzer.analyze_trace("logs/profiling")
                mlflow.log_dict(findings, "mcp_profiling_analysis.json")
                
                logger.info(f"Found {len(findings['bottlenecks'])} bottlenecks")
                for rec in findings["recommendations"]:
                    logger.info(f"  [{rec['priority']}] {rec['action']}")

                # Save model
                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)
                model.save_pretrained(output_dir)
                tokenizer.save_pretrained(output_dir)
                logger.info(f"Model saved to {output_dir}")

                # Upload to HuggingFace Pro (if specified)
                if hf_repo:
                    logger.info(f"Uploading to HuggingFace: {hf_repo}")
                    from huggingface_hub import HfApi, create_repo
                    
                    api = HfApi()
                    try:
                        create_repo(hf_repo, private=True, exist_ok=True)
                    except Exception as e:
                        logger.warning(f"Repo creation: {e}")
                    
                    api.upload_folder(
                        folder_path=output_dir,
                        repo_id=hf_repo,
                        repo_type="model",
                    )
                    logger.info(f"✅ Model uploaded to HF Pro: {hf_repo}")
                    mlflow.log_param("hf_repo", hf_repo)

                mlflow.end_run()

                return {
                    "status": "success",
                    "model_path": output_dir,
                    "hf_repo": hf_repo,
                    "profiling_report": prof_report,
                    "loss": train_output.training_loss,
                    "metrics": metrics,
                    "mcp_findings": findings,
                }

        except Exception as e:
            logger.error(f"Training failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
            }

