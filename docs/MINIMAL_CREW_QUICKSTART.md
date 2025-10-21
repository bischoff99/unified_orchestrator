# Minimal Crew Quick Start

## ✅ What is Minimal Crew?

Streamlined **4-agent** configuration for faster iteration and lower costs:
- **Architect** - System design
- **Builder** - Code + Deployment (FullStack + DevOps merged)
- **QA** - Testing and validation
- **Docs** - Documentation + Light review

**vs. Full Crew (6 agents)**: 40% faster, 50% fewer tokens, ~50% lower cost

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+** (CrewAI requirement)
- Ollama installed (or other LLM backend)

**Check Python version:**
```bash
python --version  # Should be 3.10 or higher
```

**If Python 3.9:** CrewAI will fail with Union type error. Upgrade to Python 3.10+.

---

### Usage

```bash
# Basic usage
python main.py "Build a FastAPI notes service" --minimal

# With benchmarking
python main.py "Create a REST API" --minimal --benchmark

# With different backend
python main.py "Build a web app" --minimal --backend mlx
```

---

## 📊 Comparison

| Feature | Full Crew | Minimal Crew |
|---------|-----------|--------------|
| Agents | 6 | 4 |
| Time | ~15-20 min | ~8-12 min |
| Tokens | ~50,000 | ~25,000 |
| Cost | Higher | 50% less |
| Best for | Production | Prototyping |

---

## 🎯 When to Use Minimal Crew

**✅ Good for:**
- Rapid prototyping
- Learning and experimentation
- Simple to medium projects
- Budget constraints
- Fast feedback loops

**❌ Use Full Crew instead for:**
- Production applications
- Complex deployment (Kubernetes, multi-service)
- Critical security requirements
- Maximum quality and thoroughness

---

## 🔧 How It Works

### Workflow
```
Architect → Builder → QA → Docs+Review
```

### Agent Responsibilities

**1. Architect** (unchanged from full crew)
- System design
- Tech stack selection
- Component architecture

**2. Builder** (FullStack + DevOps merged)
- Backend implementation
- Frontend code
- Dockerfile, docker-compose.yml
- requirements.txt
- Basic CI/CD

**3. QA Engineer** (unchanged from full crew)
- Testing with test_code()
- Code validation
- Security checks

**4. Docs + Reviewer** (Docs + Critic merged)
- README and API docs
- Setup guides
- Light quality review
- Deployment recommendations

---

## 📝 Example Run

```bash
$ python main.py "Build a simple REST API for todos" --minimal

🚀 Starting Minimal Crew Orchestration...
📊 Agents: 4 (Architect, Builder, QA, Docs)
📋 Tasks: 4
⚙️  Process: Sequential with context dependencies
🧠 Memory: Enabled with ChromaDB
💡 Optimized for faster iteration

[Agent execution...]

✅ Minimal Crew orchestration complete!
```

**Output:**
- `src/generated/` - All code files
- `Dockerfile` - Container configuration
- `docker-compose.yml` - Local dev environment
- `requirements.txt` - Python dependencies
- `README.md` - Project documentation

---

## 🐛 Troubleshooting

### Python Version Error
```
TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'
```

**Solution:** Upgrade to Python 3.10+
```bash
# macOS with Homebrew
brew install python@3.11

# Create new venv with Python 3.10+
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### CrewAI Import Error
**Solution:** Ensure CrewAI is installed
```bash
pip install crewai crewai-tools
```

### Ollama Not Running
**Solution:** Start Ollama
```bash
ollama serve
```

---

## 🎓 Advanced Usage

### Switching Between Modes

**Start with Minimal for prototyping:**
```bash
python main.py "Build a blog API" --minimal
```

**Refine with Full Crew when ready:**
```bash
python main.py "Enhance blog API with advanced features"
# (no --minimal flag = uses full 6-agent crew)
```

### Benchmark Comparison
```bash
# Test both modes
python main.py "Build a REST API" --benchmark  # Full crew
python main.py "Build a REST API" --minimal --benchmark  # Minimal crew

# Compare results in logs/metrics.json
```

---

## 📚 See Also

- [CREW_COMPARISON.md](./CREW_COMPARISON.md) - Detailed comparison
- [README.md](../README.md) - Full documentation
- [TRAINING_STATUS.md](../TRAINING_STATUS.md) - Training pipeline

---

## ✅ Summary

**Minimal Crew = Fast + Affordable**
- 4 agents (vs 6)
- 40% faster execution
- 50% lower token costs
- Perfect for prototyping

**Command:**
```bash
python main.py "YOUR_TASK_HERE" --minimal
```

**Ready to use!** 🚀

