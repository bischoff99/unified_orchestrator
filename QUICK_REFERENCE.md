# Quick Reference Card

## ✅ Environment
- **Python**: 3.11.14
- **Shell**: zsh (auto-activates venv)
- **venv Location**: `venv/`
- **Old venv**: `venv_old_py39/` (backup)

## 🚀 Minimal Crew (4 Agents)
```bash
python main.py "YOUR_TASK" --minimal
```
**Agents**: Architect, Builder, QA, Docs  
**Speed**: 40% faster  
**Cost**: 50% less tokens

## 🏗️ Full Crew (6 Agents)
```bash
python main.py "YOUR_TASK"
```
**Agents**: Architect, FullStack, DevOps, QA, Docs, Critic  
**Quality**: Comprehensive production-ready output

## 🎓 Training Pipeline
```bash
# Prepare dataset
python scripts/prepare_training_data.py

# Train model
python scripts/train_standalone.py

# Test inference
python scripts/test_inference.py

# View results
open http://localhost:5000  # MLflow UI
```

## 📊 Benchmarking
```bash
python main.py "YOUR_TASK" --minimal --benchmark
cat logs/metrics.json
```

## 🔧 LLM Backends
```bash
--backend ollama   # Local (default)
--backend mlx      # Apple Silicon native
--backend openai   # OpenAI API
```

## 📚 Documentation
- **Minimal Crew Guide**: `docs/MINIMAL_CREW_QUICKSTART.md`
- **Crew Comparison**: `docs/CREW_COMPARISON.md`
- **Training Status**: `TRAINING_STATUS.md`
- **Next Steps**: `NEXT_STEPS.md`
- **Main README**: `README.md`

## 🐛 Troubleshooting
```bash
# Check Python version
python --version  # Should be 3.11.14

# Manually activate venv
source venv/bin/activate

# Test minimal crew
python test_minimal_crew.py

# View logs
tail -f logs/*.log
```

## 🔄 Terminal Setup
Your zsh automatically activates the venv when you `cd` into this directory!

```bash
cd ~/Developer/projects/unified_orchestrator
# venv activates automatically ✨
```

## 📈 Quick Stats
| Metric | Minimal | Full |
|--------|---------|------|
| Agents | 4 | 6 |
| Time | ~8-12 min | ~15-20 min |
| Tokens | ~25k | ~50k |
| Cost | Lower | Higher |

## 🎯 Best Practices
1. **Start minimal** for prototyping
2. **Use full crew** for production
3. **Benchmark** to compare performance
4. **Train models** for custom needs

## 🚨 Important
- **Python 3.10+** required (you have 3.11.14 ✅)
- **Ollama** must be running for local inference
- **MLflow** runs on port 5000
- **Git**: All changes committed and pushed

---
**Last Updated**: After Python 3.11 upgrade  
**Status**: ✅ Fully operational

