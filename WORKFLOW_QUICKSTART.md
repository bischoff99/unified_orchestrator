# 🚀 Master Workflow Quick Start

**Ready to automate everything?** This guide gets you running in 5 minutes!

---

## ✅ Prerequisites Check

### Required Apps
- [ ] **Cursor IDE** - With all 6 MCP servers configured
- [ ] **Claude Desktop** - With 3 MCP servers + extensions
- [ ] **Perplexity Desktop** - With built-in MCP connectors

### Quick Verification
```bash
# Check if apps are installed
ls /Applications | grep -E "Cursor|Claude|Perplexity"
```

---

## 🎯 One Command to Rule Them All

### Basic Usage
```bash
# Navigate to project
cd ~/Developer/projects/unified_orchestrator

# Launch workflow for any feature
./scripts/launch_workflow.sh "implement JWT authentication with refresh tokens"
```

**That's it!** The workflow will:
1. 🔍 Research best practices (Perplexity)
2. 📋 Create technical spec (Claude + Perplexity)
3. 💻 Generate code (Cursor)
4. 🧪 Run tests (All three)
5. 🚀 Deploy (Claude coordinating)
6. 📚 Document everything (All three)

---

## 🎮 Execution Modes

### Mode 1: Automatic (Hands-Free)
```bash
./scripts/launch_workflow.sh "your feature"
# Choose option 1 when prompted
# Sit back and watch the magic! ✨
```

### Mode 2: Interactive (With Checkpoints)
```bash
./scripts/launch_workflow.sh "your feature"
# Choose option 2 when prompted
# Confirm before each phase
```

---

## 📊 Monitor Progress

### Live Monitoring (Optional)
```bash
# In a separate terminal
python scripts/workflow_monitor.py runs/workflow_*/state.json
```

### View Logs
```bash
# Follow the workflow log
tail -f runs/workflow_*/workflow.log
```

---

## 🔄 Phase Control

### Execute Single Phase
```bash
# Run just one phase
osascript scripts/coordinate_clients.scpt research "your feature"
```

### Available Phases
- `research` - Perplexity searches and creates Linear epic
- `planning` - Claude analyzes and creates spec
- `development` - Cursor generates code
- `testing` - All three run tests
- `deployment` - Claude coordinates deployment
- `documentation` - All create docs

---

## 🛠️ Manual Phase Execution

### Research Only
```applescript
osascript -e 'tell application "Perplexity" to activate'
# Then: "Research patterns for [feature]"
```

### Development Only
```applescript
osascript -e 'tell application "Cursor" to activate'
# Then: Cmd+L → Agent Mode → "Generate [feature]"
```

### Planning Only
```applescript
osascript -e 'tell application "Claude" to activate'
# Then: "Create spec for [feature] using desktop-commander"
```

---

## 📁 Output Structure

After workflow completes:
```
runs/
└── workflow_20251022_143022/
    ├── config.json           # Workflow configuration
    ├── workflow.log          # Complete execution log
    ├── checkpoint_*.json     # Phase checkpoints
    └── report.md            # Final report with all links
    
research/
├── patterns_*.md            # Research findings
└── best_practices_*.md      # Best practices

src/features/
└── your_feature/            # Generated code
    ├── __init__.py
    ├── models.py
    ├── services.py
    └── api.py

tests/
└── test_your_feature.py    # Generated tests
```

---

## 🔗 Quick Access Links

After workflow, find everything at:
- **Linear Tasks**: Check the epic created
- **GitHub PR**: Review generated code
- **Notion Docs**: Complete documentation
- **Perplexity Space**: Updated with learnings
- **ChromaDB**: Specifications stored
- **Supermemory**: Patterns saved

---

## 🆘 Troubleshooting

### App Not Starting?
```bash
# Manually open apps
open -a Cursor
open -a Claude
open -a Perplexity
```

### Phase Failed?
```bash
# Workflow will prompt to retry
# Choose 'y' to retry the phase
# Choose 'n' to abort
```

### Resume Interrupted Workflow?
```bash
# Workflow auto-detects and offers to resume
./scripts/launch_workflow.sh "same feature"
# Choose 'y' to resume from last checkpoint
```

### Permission Issues?
```bash
# Grant accessibility permissions
System Settings → Privacy & Security → Accessibility
# Add Terminal/iTerm and the three apps
```

---

## 🎯 Example Workflows

### 1. API Endpoint
```bash
./scripts/launch_workflow.sh "create REST API for user management with CRUD operations"
```

### 2. Frontend Component
```bash
./scripts/launch_workflow.sh "build React dashboard with real-time charts"
```

### 3. Integration
```bash
./scripts/launch_workflow.sh "integrate Stripe payment processing with webhooks"
```

### 4. Refactoring
```bash
./scripts/launch_workflow.sh "refactor authentication to use JWT with refresh tokens"
```

---

## 💡 Pro Tips

### Speed Run Mode
```bash
# Skip confirmation prompts
yes | ./scripts/launch_workflow.sh "feature" &
```

### Batch Multiple Features
```bash
# Create a batch script
for feature in "auth" "payments" "notifications"; do
    ./scripts/launch_workflow.sh "implement $feature module"
    sleep 60  # Wait between features
done
```

### Custom Phase Order
```bash
# Edit PHASES array in launch_workflow.sh
PHASES=("research" "development" "testing")  # Skip planning, deployment, docs
```

---

## 🎉 Success Metrics

**Typical Workflow Duration:**
- Simple feature: 10-15 minutes
- Medium feature: 20-30 minutes
- Complex feature: 30-45 minutes

**What You Get:**
- ✅ Researched best practices
- ✅ Technical specification
- ✅ Generated code
- ✅ Comprehensive tests
- ✅ GitHub PR ready
- ✅ Complete documentation
- ✅ Team notifications
- ✅ Knowledge base updated

---

## 🚦 Start Now!

```bash
# Your first automated feature - try something simple
./scripts/launch_workflow.sh "create a hello world API endpoint"

# Watch the magic happen! 🎩✨
```

---

## 📞 Support

**Issues?** Check:
1. `runs/workflow_*/workflow.log` - Detailed logs
2. `docs/MASTER_WORKFLOW_ORCHESTRATION.md` - Full documentation
3. `docs/TRIPLE_HUB_ARCHITECTURE.md` - Architecture details

**Still stuck?** The workflow is idempotent - just run it again!

---

**Remember:** This workflow turns hours of work into minutes of automation! 🚀
