# Next Steps - Prioritized Action Plan

## 🎯 Immediate Actions (Next 30 min)

### 1. Update .gitignore
**Why**: Exclude ML artifacts and experiment data from version control

```bash
# Add to .gitignore:
mlruns/
data/*.jsonl
*.ckpt
```

**Impact**: Keeps repo clean, prevents large file commits

---

### 2. Commit Training Pipeline
**Why**: Preserve working training infrastructure

```bash
git add scripts/prepare_training_data.py
git add scripts/train_standalone.py  
git add scripts/test_inference.py
git add TRAINING_STATUS.md
git commit -m "feat: Add LoRA training pipeline with MLflow tracking

- GPT-2 fine-tuning in 32s on M3 Max MPS
- Dataset downloader for HF datasets
- Inference validation script
- MLflow experiment tracking
- PyTorch profiler integration
"
git push
```

**Impact**: Training pipeline safely versioned

---

### 3. Update README
**Why**: Document training workflow for users

Add to README.md after line 339 (HuggingFace Pro Training section):

```markdown
### Quick Start: Train Your Own Model

1. **Prepare Dataset**
   ```bash
   python scripts/prepare_training_data.py
   # Downloads 1000 IMDB samples to data/sample_train.jsonl
   ```

2. **Start MLflow Tracking**
   ```bash
   mlflow ui --host 0.0.0.0 --port 5000 &
   # Access at http://localhost:5000
   ```

3. **Train with LoRA**
   ```bash
   python scripts/train_standalone.py
   # Trains GPT-2 in ~32s on M3 Max
   # Model saved to models/finetuned_gpt2/
   ```

4. **Test Inference**
   ```bash
   python scripts/test_inference.py
   # Validates trained model generation
   ```

**Results**: 6.5MB LoRA adapter, 6.17 samples/sec, Loss 3.81
```

**Impact**: Users can train models immediately

---

## 📊 Short-term (Next 1-2 hours)

### 4. Profile Analysis & Optimization
**Why**: Identify bottlenecks and improve training speed

```bash
# Review profiling data
python -c "
import torch.profiler as prof
# Parse logs/profiling traces
# Extract top CPU bottlenecks
# Generate optimization report
"

# Apply top 3 optimizations:
# - Increase batch size (2 -> 4)
# - Optimize data loading (num_workers)
# - Enable gradient checkpointing tuning
```

**Expected Improvement**: 20-40% speedup  
**Time Investment**: 1 hour

---

### 5. Create Training Documentation
**Why**: Comprehensive guide for advanced users

Create `docs/TRAINING.md`:
- Supported models (GPT-2, LLaMA, etc.)
- Dataset preparation (custom data)
- LoRA configuration tuning (r, alpha, target_modules)
- M3 Max optimization tips
- Troubleshooting guide
- Performance benchmarks

**Impact**: Self-service training capability

---

### 6. HuggingFace Pro Upload
**Why**: Host model for inference endpoints

```python
from huggingface_hub import HfApi

api = HfApi()
api.upload_folder(
    folder_path="models/finetuned_gpt2",
    repo_id="your-username/unified-orchestrator-gpt2",
    repo_type="model",
)

# Create inference endpoint via HF dashboard
# - Serverless or Dedicated
# - Cost monitoring enabled
# - Safety validation on outputs
```

**Cost**: ~£0.02/hour serverless  
**Impact**: Production-ready inference

---

## 🚀 Medium-term (Next 3-7 days)

### 7. Integrate with CrewAI Agents
**Why**: Agents can use custom-trained models

```python
# src/agents/custom_model_agent.py
class CustomModelAgent:
    def __init__(self):
        self.model = load_lora_model("models/finetuned_gpt2")
        self.llm = LLMWrapper(self.model)
    
    def create(self) -> Agent:
        return Agent(
            role="Custom Model Specialist",
            goal="Use fine-tuned model for specialized tasks",
            llm=self.llm,
            tools=[...],
        )
```

**Impact**: 7-agent orchestrator with custom models

---

### 8. Automated Training Pipeline
**Why**: Continuous model improvement

Create `.github/workflows/train.yml`:
- Scheduled re-training (weekly)
- Model evaluation on test set
- Auto-upload to HF Pro if improved
- Slack/Discord notifications

**Impact**: Self-improving models

---

### 9. Multi-Dataset Support
**Why**: Validate generalization

```bash
# Train on different datasets
python scripts/prepare_training_data.py --dataset alpaca --samples 5000
python scripts/train_standalone.py --dataset data/alpaca_train.jsonl

python scripts/prepare_training_data.py --dataset code --samples 2000
python scripts/train_standalone.py --dataset data/code_train.jsonl
```

**Impact**: Domain-specific model variants

---

### 10. Safety & Bias Validation
**Why**: Ensure ethical AI outputs

```python
from src.mcp import SafetyValidator

validator = SafetyValidator()

# Test trained model outputs
prompts = ["Generate code for...", "Explain..."]
for prompt in prompts:
    output = model.generate(prompt)
    result = validator.validate_output(output)
    
    if not result["passed"]:
        print(f"Safety violation: {result['issues']}")
```

**Impact**: Production-safe models

---

## 🔬 Optional/Advanced (Future)

### 11. LLaMA 3.1-8B Training
**Why**: State-of-the-art model quality

**Requirements**:
- HF Pro account with LLaMA access
- Accept Meta's license agreement
- ~60GB memory (M3 Max can handle it)

**Command**:
```bash
huggingface-cli login
python scripts/train_standalone.py \
    --model meta-llama/Llama-3.1-8B-Instruct \
    --max-steps 200 \
    --batch-size 1
```

**Time**: ~15-20 minutes  
**Quality**: Significantly better than GPT-2

---

### 12. Distributed Training (Multi-GPU)
**Why**: Faster training for large models

If you have access to multiple GPUs:
```python
# Use accelerate for distributed training
accelerate config
accelerate launch scripts/train_standalone.py
```

**Not applicable for M3 Max** (single GPU)

---

### 13. Custom Dataset: Train on Codebase
**Why**: Domain-specific model for this project

```bash
# Create dataset from unified_orchestrator codebase
python scripts/create_code_dataset.py \
    --input src/ \
    --output data/unified_orchestrator_code.jsonl

# Train
python scripts/train_standalone.py \
    --dataset data/unified_orchestrator_code.jsonl \
    --model codellama/CodeLlama-7b-hf
```

**Impact**: Model understands project patterns

---

## 🎯 Recommended Priority Order

**Today (30 min)**:
1. ✅ Update .gitignore
2. ✅ Commit training scripts
3. ✅ Update README

**This Week**:
4. Profile analysis + optimization (1-2 hours)
5. Create TRAINING.md documentation (1 hour)
6. HF Pro upload (30 min)

**Next Week**:
7. Integrate with CrewAI agents (2-3 hours)
8. Automated training pipeline (2 hours)
9. Multi-dataset validation (1 hour)

**Future**:
10. Safety validation integration
11. LLaMA 3.1 training (if needed)
12. Custom codebase dataset

---

## 📈 Success Metrics

- [x] Training pipeline functional
- [x] Model inference validated
- [ ] Documentation complete
- [ ] HF Pro integration working
- [ ] Cost monitoring < £3.33/day
- [ ] Agent integration tested
- [ ] 3+ dataset variants trained

---

## 🐛 Blockers & Risks

1. **Python 3.9 vs 3.10**: CrewAI incompatible with 3.9
   - **Mitigation**: Use standalone scripts or upgrade Python

2. **HF Pro Costs**: Could exceed £100/month budget
   - **Mitigation**: Cost monitoring, auto-fallback to Ollama

3. **Model Quality**: GPT-2 may not be good enough
   - **Mitigation**: Upgrade to LLaMA 3.1-8B

4. **MPS Limitations**: No fp16, limited profiling
   - **Mitigation**: Accept limitations, CPU profiling sufficient

---

**Next Action**: Run items 1-3 in the next 30 minutes to secure progress.

