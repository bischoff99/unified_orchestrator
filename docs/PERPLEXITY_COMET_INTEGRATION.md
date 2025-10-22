# Perplexity Max + Comet Browser Integration

**Status:** 🎯 Advanced Features for Max Subscribers  
**Last Updated:** 2025-10-22

**Source:** [Perplexity Max Features](https://www.perplexity.ai/mk/hub/blog/introducing-perplexity-max)

---

## 🎉 What Your Perplexity Max Subscription Includes:

### **1. Comet Browser** (Early Access ✨)
Perplexity's **AI-powered web browser** - a thought partner integrated into browsing

**Features:**
- AI assistance directly in browser
- Context-aware web interaction
- Smart information retrieval
- Integrated with Perplexity AI

### **2. Perplexity Labs** (Unlimited Access 🚀)
Transform ideas into actionable outputs:
- **Reports** - Research summaries
- **Spreadsheets** - Data analysis
- **Dashboards** - Visualization
- **Web Applications** - No-code app building

**Key Feature:** Natural language → working outputs (no coding required!)

### **3. Advanced AI Models**
- OpenAI o3-pro
- Anthropic Claude Opus 4
- Perplexity's latest models

---

## 🏗️ Integration with Unified Orchestrator

### **Architecture:**

```
Perplexity Max Ecosystem
    ↓
┌─────────────────┬────────────────┬──────────────┐
│  Comet Browser  │ Perplexity Labs│   Research   │
│  (AI browsing)  │ (Apps/Reports) │  (Standard)  │
└────────┬────────┴────────┬───────┴──────┬───────┘
         │                 │               │
         └─────────────────┼───────────────┘
                           ↓
              Clipboard Ingestion
                           ↓
                      ChromaDB
                           ↓
              unified_orchestrator
                (Agents with context)
```

---

## 1. Comet Browser Integration

### **Use Cases:**

#### **A. AI-Assisted Code Research**

```
While developing in Cursor:
1. Need FastAPI pattern
2. Open Comet Browser
3. Search: "FastAPI authentication 2025"
4. Comet AI suggests best resources
5. Copy comprehensive overview
6. Paste into orchestrator context
```

#### **B. GitHub Integration in Comet**

```
After orchestrator generates code:
1. Open generated code in Comet Browser
2. Navigate to GitHub
3. Comet AI helps:
   - Create optimal repo description
   - Suggest good README structure
   - Generate .gitignore
   - Create issue templates
```

#### **C. Research with Web Context**

```
In Comet Browser:
1. Browse FastAPI documentation
2. Ask Comet AI: "Summarize authentication best practices from this page"
3. Get AI summary in sidebar
4. Copy to orchestrator knowledge base
```

---

## 2. Perplexity Labs - App/Report Generation

### **Feature: Transform Ideas → Apps**

According to [MLQ.ai](https://mlq.ai/news/perplexity-labs-launches-ai-powered-workspace-to-transform-ideas-into-apps-and-reports/), Labs can:
- Create working applications from natural language
- Generate reports and dashboards
- Build spreadsheets with analysis
- **All without coding!**

### **Integration Workflows:**

#### **A. Generate Dashboard for Orchestrator Metrics**

```
In Perplexity Labs:

Prompt: "Create a dashboard for my unified_orchestrator metrics:
- Total runs per day
- Average duration per agent
- Success rate by provider
- Cost tracking (HuggingFace Pro usage)
- Memory usage over time

Data source: Parse JSON from runs/*/manifest.json"

→ Perplexity Labs generates working dashboard
→ Export or embed in Notion
```

#### **B. Create Analysis Reports**

```
In Perplexity Labs:

Prompt: "Analyze all orchestrator runs and create report:
- Most common project types
- Performance trends
- Quality scores over time
- Recommendations for improvement

Data: runs/*/manifest.json and logs/metrics.json"

→ Perplexity Labs generates comprehensive report
→ Save as PDF or export to Notion
```

#### **C. Build Monitoring Web App**

```
In Perplexity Labs:

Prompt: "Create a web app to monitor orchestrator runs:
- Real-time status dashboard
- Event timeline viewer
- Cost tracker
- Agent performance charts

Connect to: runs/*/events.jsonl"

→ Perplexity Labs builds no-code monitoring app
→ Deploy and access via browser
```

---

## 3. Complete Workflow Examples

### **Workflow 1: Research-Driven Code Generation**

```bash
# === STEP 1: Research in Comet Browser ===
# Open Comet (Perplexity's AI browser)
open -a "Comet"  # or navigate to labs.perplexity.ai

# Browse to: docs.fastapi.tiangolo.com
# Ask Comet AI: "What are the latest security patterns?"
# Copy AI summary

# === STEP 2: Ingest to ChromaDB ===
python scripts/ingest_from_clipboard.py \
  --collection research \
  --metadata "source=comet_browser,topic=FastAPI_security"

# === STEP 3: Generate with Context ===
python -m src.cli run examples/secure-api.yaml
# Agents query ChromaDB → get latest patterns → generate better code

# === STEP 4: Analyze in Perplexity Labs ===
# Upload generated main.py to Labs
# Ask: "Create analysis report comparing this to industry standards"
# Get comprehensive report with recommendations
```

### **Workflow 2: Automated Reporting**

```python
# scripts/generate_weekly_report.py
"""Use Perplexity Labs to generate weekly orchestrator reports"""

def generate_weekly_report():
    """
    1. Collect orchestrator metrics from last week
    2. Upload to Perplexity Labs
    3. Generate comprehensive report
    4. Save to Notion via browser automation
    """
    
    # Gather metrics
    metrics = collect_week_metrics()  # From runs/*/manifest.json
    
    # Create prompt for Perplexity Labs
    prompt = f"""
    Analyze these orchestrator metrics and create weekly report:
    
    Metrics:
    {json.dumps(metrics, indent=2)}
    
    Include:
    - Performance trends
    - Quality improvements
    - Cost analysis
    - Recommendations
    
    Format as executive summary with charts.
    """
    
    # Copy to clipboard
    pyperclip.copy(prompt)
    
    # Open Perplexity Labs
    webbrowser.open("https://labs.perplexity.ai")
    
    print("📊 Prompt copied to clipboard")
    print("📝 Paste in Perplexity Labs to generate report")
    print("⏳ Waiting for report generation...")
    input("Press Enter when report is ready...")
    
    # Report is now generated
    print("✅ Save report to Notion or export as PDF")
```

### **Workflow 3: No-Code App from Orchestrator Data**

```
In Perplexity Labs:

Prompt: "Build a web dashboard app:
- Show all orchestrator runs in table
- Filter by status, provider, date
- Click row to see details
- Display generated files
- Show event timeline

Data structure:
{
  "job_id": "job_abc",
  "project": "notes_api",
  "status": "succeeded",
  "duration_s": 66.9,
  "files": [...]
}

Use data from: /Users/andrejsp/Developer/projects/unified_orchestrator/runs/"

→ Perplexity Labs generates working dashboard
→ No coding required!
→ Deploy and share with team
```

---

## 4. Desktop Commander Orchestration

**Since you asked about orchestrating with Desktop Commander:**

```python
# scripts/desktop_commander_workflow.py
"""Orchestrate using Desktop Commander for file operations"""

from mcp_desktop-commander import (
    start_process,
    read_process_output,
    read_file,
    list_directory
)

def orchestrate_with_dc(spec_file: str):
    """Run orchestrator using Desktop Commander"""
    
    # 1. Run orchestrator
    pid = start_process(
        command=f"cd ~/Developer/projects/unified_orchestrator && "
                f"source venv/bin/activate && "
                f"python -m src.cli run {spec_file}",
        timeout_ms=120000
    )
    
    # 2. Wait for completion
    output = read_process_output(pid)
    
    # 3. Extract run ID
    run_id = extract_run_id(output)
    
    # 4. Read generated files
    files = list_directory(f"runs/{run_id}/outputs")
    
    # 5. Process each file
    for file in files:
        content = read_file(file)
        # Analyze, review, or deploy
    
    return run_id
```

---

## 🎯 **Quick Start Guide**

### **Today - Research & Generate:**

```bash
# 1. Research in Comet Browser or Perplexity Labs
open "https://labs.perplexity.ai"
# Query: "Best practices for FastAPI async endpoints"
# Copy answer

# 2. Ingest research
python scripts/ingest_from_clipboard.py --collection research

# 3. Generate code (agents use research context)
python -m src.cli run examples/tiny_spec.yaml

# 4. View results
python -m src.cli show $(ls -t runs/ | head -1)
```

### **This Week - Build Dashboard:**

```
In Perplexity Labs:
1. Create dashboard for orchestrator metrics
2. Connect to runs/*/manifest.json
3. Generate charts and insights
4. Export or integrate with Notion
```

### **Ongoing - Automated Reports:**

```bash
# Weekly cron job:
0 9 * * 1 cd ~/Developer/projects/unified_orchestrator && \
  python scripts/generate_weekly_report.py
# → Generates report in Perplexity Labs
# → Posts to Slack via automation
```

---

**Your Perplexity Max + Comet Browser give you:**
- ✅ AI-powered browsing (Comet)
- ✅ No-code app/report generation (Labs)
- ✅ Advanced AI models (o3-pro, Claude Opus 4)
- ✅ All integrated with your orchestrator!

Want me to create more automation scripts for these features? 🚀

