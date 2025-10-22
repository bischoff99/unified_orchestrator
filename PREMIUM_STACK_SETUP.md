# Premium Stack Quick Setup Guide

**🎯 Get your $1,224/year automation stack running in 10 minutes!**

---

## ✅ What You Have

Your premium automation ecosystem:
1. **Cursor IDE Pro** - Already active with Rules ✅
2. **HuggingFace Pro** - Already integrated ✅
3. **Claude.ai Max** - Browser-based
4. **Perplexity Max** - Browser-based  
5. **Comet Browser** - Needs connector setup
6. **Raycast Pro** - Needs commands
7. **Warp Pro** - Needs workflows

---

## 🚀 Quick Setup (10 minutes)

### **Step 1: Install Dependencies** (1 min)

```bash
cd ~/Developer/projects/unified_orchestrator
pip install pyperclip
```

### **Step 2: Install Raycast Commands** (2 min)

```bash
bash scripts/setup_raycast.sh
```

**Test:** Open Raycast (Cmd+Space) → Type "orchestrator" → See 5 commands

### **Step 3: Install Warp Workflows** (1 min)

```bash
mkdir -p ~/.warp/workflows
cp config/warp_workflows.yaml ~/.warp/workflows/unified-orchestrator.yaml
```

**Test:** Open Warp → Cmd+G → Search "orchestrator" → See 7 workflows

### **Step 4: Test Clipboard Ingestion** (2 min)

```bash
# Copy some text
echo "FastAPI authentication best practices" | pbcopy

# Preview (doesn't save)
python scripts/ingest_from_clipboard.py --preview

# Save to ChromaDB
python scripts/ingest_from_clipboard.py --collection research
```

### **Step 5: Configure Comet (Optional)** (5 min)

Open Comet Browser Assistant and connect:
- GitHub (for repo creation)
- Linear (for task tracking)
- Notion (for documentation)
- Slack (for notifications)

---

## 🎯 Usage Examples

### **A. Quick Code Generation (Raycast)**

1. Open Raycast (Cmd+Space)
2. Type: "Run Orchestrator"
3. Enter: "examples/tiny_spec.yaml"
4. ✅ Code generated and opened in Cursor!

### **B. Research & Generate (Warp)**

1. Open Warp
2. Cmd+G → Search "Research & Generate"
3. Enter research topic: "FastAPI WebSocket patterns"
4. ✅ Opens Perplexity → Copy answer → Generates code

### **C. Full Automation Pipeline (All Tools)**

```bash
# In Warp, run:
cd ~/Developer/projects/unified_orchestrator
source venv/bin/activate

# 1. Research in Perplexity
open "https://www.perplexity.ai/?q=FastAPI+authentication"
# Copy answer (Cmd+A, Cmd+C)

# 2. Ingest research
python scripts/ingest_from_clipboard.py --collection research

# 3. Generate code
orchestrator run examples/tiny_spec.yaml

# 4. Open in Cursor
cursor runs/$(ls -t runs/ | head -1)/outputs

# 5. Review in Claude
cat runs/$(ls -t runs/ | head -1)/outputs/**/*.py | pbcopy
open "https://claude.ai/new"
# Paste for review

# 6. Automate deployment
python scripts/comet_integrations.py full-automation $(ls -t runs/ | head -1)
```

---

## 📚 Available Commands

### **Raycast Commands**

| Command | Description | Example |
|---------|-------------|---------|
| Run Orchestrator | Generate code | Type spec file path |
| Show Latest Run | View most recent run | No input needed |
| Open in Cursor | Open generated code | No input needed |
| Query Memory | Search vector memory | "FastAPI patterns" |
| Ingest Clipboard | Save to ChromaDB | Copy text first |

### **Warp Workflows**

| Workflow | Description | Variables |
|----------|-------------|-----------|
| Quick Generate | Fast code generation | None |
| Research & Generate | Perplexity → code | TOPIC, SPEC |
| Full Pipeline | Complete automation | TOPIC, SPEC |
| Query Memory | Search ChromaDB | QUERY |
| Show Collections | List all collections | None |
| Deploy to GitHub | Create repo + push | None |

---

## 🎓 Workflows

### **Daily Development**
```
Morning:
1. Raycast: "Query Memory" → Review yesterday's patterns
2. Perplexity: Research new topics
3. Raycast: "Ingest Clipboard" → Save research
4. Raycast: "Run Orchestrator" → Generate code
5. Cursor: Edit and refine
```

### **Project Kickoff**
```
1. Research in Perplexity (architecture patterns)
2. Ingest to ChromaDB
3. Warp: "Research & Generate" workflow
4. Review in Claude.ai Max (extended context)
5. Warp: "Deploy to GitHub" workflow
6. Comet: Auto-creates Linear ticket + Notion doc + Slack notification
```

### **Code Review**
```
1. Generate code with orchestrator
2. Copy all files to clipboard
3. Open Claude.ai Max project
4. Paste and ask: "Review for security, performance, best practices"
5. Claude provides comprehensive review with 200K context
```

---

## 💡 Pro Tips

### **Perplexity Research**
- Use specific queries: "FastAPI authentication best practices 2025"
- Copy entire answer with citations (Cmd+A, Cmd+C)
- Ingest immediately: `python scripts/ingest_from_clipboard.py --collection research`
- Research is now searchable by agents!

### **Claude.ai Max Projects**
Create projects for organized knowledge:
- `unified_orchestrator_docs` - All project documentation
- `generated_code_review` - Recent orchestrator outputs
- `framework_research` - FastAPI, ChromaDB, CrewAI examples

### **Raycast Productivity**
- Create aliases: "orch run" → Run Orchestrator
- Use keyboard shortcuts for frequent commands
- Chain commands with workflows

### **Warp AI**
- Natural language: "run orchestrator" → Warp suggests workflow
- Save custom commands for your use cases
- Share workflows with team

---

## 🔧 Troubleshooting

### **Raycast commands not showing**
```bash
# Check installation
ls ~/.config/raycast/scripts/orchestrator-*.sh

# Re-run installer
bash scripts/setup_raycast.sh

# Refresh Raycast
Cmd+R in Raycast
```

### **Warp workflows not appearing**
```bash
# Check installation
ls ~/.warp/workflows/unified-orchestrator.yaml

# Re-copy
cp config/warp_workflows.yaml ~/.warp/workflows/

# Restart Warp
```

### **Clipboard ingestion fails**
```bash
# Install pyperclip
pip install pyperclip

# Test
python -c "import pyperclip; print(pyperclip.paste())"
```

### **Comet automation fails**
- Ensure Comet Browser Assistant is running
- Check connector setup (GitHub, Linear, Notion, Slack)
- Test manually first, then automate

---

## 📊 ROI Tracker

Track your time savings:

| Week | Projects | Hours Saved | Value ($100/hr) |
|------|----------|-------------|-----------------|
| 1 | 2 | 14 hrs | $1,400 |
| 2 | 3 | 21 hrs | $2,100 |
| 3 | 2 | 14 hrs | $1,400 |
| 4 | 3 | 21 hrs | $2,100 |
| **Month** | **10** | **70 hrs** | **$7,000** |

**Stack Cost:** $102/month  
**Monthly Value:** $7,000+  
**ROI:** 68x 🚀

---

## 📚 Documentation

**Complete Guides:**
- `docs/PREMIUM_STACK_INTEGRATION.md` - Full integration guide (554 lines)
- `docs/CHROMA_INTEGRATIONS.md` - ChromaDB + frameworks (554 lines)
- `docs/CHROMA_MCP_INTEGRATION.md` - MCP server setup (417 lines)

**Implementation:**
- `scripts/comet_integrations.py` - Comet automation
- `scripts/ingest_from_clipboard.py` - Clipboard → ChromaDB
- `scripts/setup_raycast.sh` - Raycast installer
- `config/warp_workflows.yaml` - Warp workflows

---

## 🎯 Next Steps

**Today:**
1. ✅ Install Raycast commands
2. ✅ Install Warp workflows
3. ✅ Test clipboard ingestion
4. ✅ Generate your first project

**This Week:**
1. Configure Comet connectors
2. Create Claude.ai Max projects
3. Build your first end-to-end workflow
4. Share workflows with team

**This Month:**
1. Customize commands for your use cases
2. Add team-specific automations
3. Track ROI and time savings
4. Optimize workflows

---

**🚀 Your $1,224/year premium automation stack is ready to deliver 27x ROI!**

**Questions?** Check `docs/PREMIUM_STACK_INTEGRATION.md` for detailed documentation.

