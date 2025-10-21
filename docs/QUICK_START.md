# Quick Start: Multi-Agent Orchestration on M3 Max

## Your Toolset

| Tool | Role | Cost | Setup | Use It? |
|------|------|------|-------|--------|
| **Ollama** | Local LLM inference | FREE | 2 min | ✅ YES |
| **Crew AI** | Agent orchestration | FREE | 2 min | ✅ YES |
| **Claude MCP** | Reasoning + tools | FREE/API | 10 min | ⚠️ Later |
| **Hugging Face Pro** | Model serving | PAID | 5 min | ⚠️ Optional |
| **Gemini CLI** | Fast validation | FREE/API | 5 min | ⚠️ Optional |
| **Cursor Pro** | IDE (not orchestration) | PAID | N/A | ❌ NO |
| **Codex CLI** | Deprecated | N/A | N/A | ❌ NO |

---

## 30-Second Setup

```bash
# 1. Ensure Ollama is running
ollama serve &

# 2. Pull models
ollama pull mistral
ollama pull codellama
ollama pull llama2

# 3. Activate environment
conda activate crewai

# 4. Run pipeline
cd /Users/andrejsp/crew-workflows
python crew_pipeline_local.py
```

---

## Five Orchestration Options

### Option 1: Claude MCP Server
```bash
pip install claude-mcp
claude-mcp start --port 8000
```
**Use when:** Need Claude's reasoning + tool integration
**Cost:** FREE (local) or API calls (if Claude backend)

### Option 2: Crew AI + Ollama ⭐ RECOMMENDED
```bash
python crew_pipeline_local.py
```
**Use when:** Want offline, free, simple
**Cost:** FREE
**Quality:** Good (Mistral/CodeLlama)

### Option 3: Hybrid (Crew AI + Claude MCP + Ollama)
```bash
# Terminal 1
ollama serve &
claude-mcp start --port 8000

# Terminal 2
python hybrid_pipeline.py
```
**Use when:** Need both local + cloud models
**Cost:** Minimal (mostly local)

### Option 4: Hugging Face + Crew AI
```bash
export HF_API_KEY=hf_xxxxx
python crew_pipeline_huggingface.py
```
**Use when:** Need custom fine-tuned models
**Cost:** HF Pro subscription + inference fees

### Option 5: Full Production Stack
```
Claude MCP (reasoning)
├── Crew AI (orchestration)
├── Ollama (fallback)
├── HF Pro (heavy lifting)
└── Gemini CLI (validation)
```
**Use when:** Enterprise deployment
**Cost:** Multiple subscriptions

---

## Quick Decision Guide

### "I want to get started RIGHT NOW"
→ **Option 2: Crew AI + Ollama**
```bash
python crew_pipeline_local.py
```

### "I have Hugging Face Pro"
→ **Option 4: Crew AI + HF**
```bash
export HF_API_KEY=hf_xxxxx
python crew_pipeline_huggingface.py
```

### "I need maximum quality reasoning"
→ **Option 1: Claude MCP Server**
```bash
pip install claude-mcp
claude-mcp start --port 8000
```

### "I want everything"
→ **Option 5: Full Stack**
```bash
# Set environment variables
export CLAUDE_API_KEY=sk-xxx
export HF_API_KEY=hf_xxx
export GEMINI_API_KEY=gm_xxx

# Start services
ollama serve &
claude-mcp start --port 8000

# Run hybrid
python hybrid_pipeline.py
```

---

## File Reference

| File | Purpose | Command |
|------|---------|---------|
| `ORCHESTRATION_OPTIONS.md` | Compare all 3 options | Reference guide |
| `INTEGRATION_GUIDE.md` | HF/Cursor/Codex breakdown | Read this first |
| `crew_pipeline_local.py` | Option 2 (Ollama) | `python crew_pipeline_local.py` |
| `crew_pipeline_huggingface.py` | Option 4 (HF Pro) | `python crew_pipeline_huggingface.py` |
| `example_anthropic.py` | Claude API example | `python example_anthropic.py` |
| `example_ollama.py` | Local Ollama example | `python example_ollama.py` |
| `simple_example.py` | Hello World | `python simple_example.py` |

---

## Common Questions

**Q: Can I use Cursor Pro for orchestration?**
A: No. Cursor is an IDE for manual development. Use Crew AI for automation.

**Q: What about Codex CLI?**
A: Deprecated (2023). Use OpenAI API or GitHub Copilot CLI instead.

**Q: Which is best for my M3 Max?**
A: **Option 2 (Crew AI + Ollama)** - Free, fast, offline, 40-core GPU utilization.

**Q: Can I mix models from different providers?**
A: Yes! Option 3 and 5 show hybrid setups with Ollama + HF + Claude.

**Q: How do agents communicate?**
A: Via shared JSON task queues, file I/O, or direct method calls.

**Q: Do I need API keys?**
A: Not for Option 2 (Ollama). Options 1/4/5 need Claude/HF/Gemini keys.

---

## Performance Notes

### M3 Max 128GB + 40-core GPU

| Model | Local (Ollama) | Via HF Pro | Quality |
|-------|---|---|---|
| Mistral 7B | 50ms/token | - | Very Good |
| CodeLlama 13B | 100ms/token | - | Excellent |
| Claude 3.5 | - | 200ms/token | Superior |
| CodeT5-base | - | 150ms/token | Good |

**Recommendation:** Use Ollama for planning/validation (fast), HF Pro for complex code generation.

---

## Next Steps

1. **Run Example:**
   ```bash
   conda activate crewai
   python crew_pipeline_local.py
   ```

2. **Try Hugging Face:**
   ```bash
   export HF_API_KEY=hf_xxxxx
   python crew_pipeline_huggingface.py
   ```

3. **Scale to Claude MCP:**
   ```bash
   pip install claude-mcp
   python hybrid_pipeline.py
   ```

4. **Customize for Your Use Case:**
   - Edit agent roles in pipeline files
   - Add custom tools
   - Modify task descriptions
   - Adjust model selections

---

## Troubleshooting

**"No module named crewai"**
```bash
conda activate crewai
pip install crewai crewai-tools
```

**"Ollama connection refused"**
```bash
ollama serve &
# Wait 5 seconds for startup
```

**"HF_API_KEY not set"**
```bash
export HF_API_KEY=hf_your_token_here
```

**"Claude MCP won't start"**
```bash
pip install --upgrade claude-mcp
claude-mcp start --port 8000 --debug
```

---

## Support Files

- `ORCHESTRATION_OPTIONS.md` - Deep dive into architecture
- `INTEGRATION_GUIDE.md` - Tool classification & when to use each
- Examples: `crew_pipeline_*.py`, `example_*.py`
- Configuration: `config.py`, `.env`

**Happy orchestrating! 🚀**
