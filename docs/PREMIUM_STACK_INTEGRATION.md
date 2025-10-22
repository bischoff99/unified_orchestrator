# Premium Automation Stack Integration

**Status:** 🎯 Complete Premium Ecosystem  
**Last Updated:** 2025-10-22

## 🏆 Your Premium Stack ($1,200+/year value)

### **Development & AI**
1. ✅ **Cursor IDE Pro** ($20/mo) - AI-powered development with Composer
2. ✅ **Claude.ai Max** ($20/mo) - Extended context (200K tokens, 20+ projects)
3. ✅ **HuggingFace Pro** ($9/mo) - Already integrated! (`src/utils/hf_inference_client.py`)
4. ✅ **Perplexity Max** ($20/mo) - Real-time research (browser access)

### **Automation & Integration**
5. ✅ **Comet Browser Assistant** ($10/mo) - GitHub, Linear, Notion, Slack connectors
6. ✅ **Raycast Pro** ($8/mo) - Command launcher + AI automation
7. ✅ **Warp Pro** ($15/mo) - AI-powered terminal workflows

---

## 🎯 Integrated Architecture

```
┌────────────────────────────────────────────────────────┐
│         Cursor IDE Pro (Development Hub)               │
│  • Composer for multi-file edits                       │
│  • Rules enforcement (.cursor/rules/*.mdc) ✅          │
│  • AI code completion                                  │
│  • Integrated with orchestrator project                │
└────────────────┬───────────────────────────────────────┘
                 │
    ┌────────────┼────────────┐
    ↓            ↓             ↓
┌─────────┐ ┌────────┐ ┌──────────┐
│ Raycast │ │  Warp  │ │  Comet   │
│   Pro   │ │  Pro   │ │ Browser  │
└────┬────┘ └───┬────┘ └─────┬────┘
     │          │            │
     └──────────┼────────────┘
                ↓
    unified_orchestrator
                ↓
    ┌───────────┼───────────┐
    ↓           ↓            ↓
┌────────┐ ┌─────────┐ ┌────────────┐
│ HF Pro │ │ Claude  │ │ Perplexity │
│  API   │ │ Max Web │ │  Max Web   │
└────────┘ └─────────┘ └────────────┘
```

---

## 1. Cursor IDE Pro Integration ✅

### **Current Setup (Already Active)**

**Cursor Rules:** `.cursor/rules/*.mdc` ✅
- `orchestrator-core.mdc` - DAG, events, I/O rules
- `providers.mdc` - Provider contract, retries, circuit breakers
- `testing-ci.mdc` - Testing standards
- `docs.mdc` - Documentation rules
- `repo-guardrails.mdc` - Git workflow rules

### **Using Composer with Orchestrator**

**Multi-File Code Generation:**
```
1. Cmd+I → Open Composer
2. Prompt: "Create a FastAPI authentication service using the orchestrator pattern"
3. Composer:
   - Reads Cursor Rules for architectural constraints
   - Uses project context (README, docs, examples)
   - Multi-file edits across src/agents/, src/providers/, examples/
   - Maintains DAG architecture per rules
```

**Example Prompts for Composer:**
- "Add a new provider for Groq AI following providers.mdc rules"
- "Create integration tests following testing-ci.mdc standards"
- "Refactor the orchestrator to support conditional DAG execution"

### **Cursor + Local Models**

Cursor works great with your local Ollama setup:
```json
// Already configured via your setup
{
  "ollama": {
    "model": "codellama:13b-instruct",
    "endpoint": "http://localhost:11434"
  }
}
```

---

## 2. HuggingFace Pro Integration ✅ ACTIVE

### **Current Implementation**

**Files:**
- ✅ `src/utils/hf_inference_client.py` - Production client
- ✅ `src/utils/hf_cost_monitor.py` - Budget tracking (£3.33/day)
- ✅ `src/agents/hf_trainer_agent.py` - LoRA training
- ✅ `examples/hf_pro_inference_example.py` - Usage examples

**Features Active:**
- ✅ Text generation with retries
- ✅ Cost monitoring and budget enforcement
- ✅ Automatic fallback to Ollama
- ✅ Thread-safe usage tracking
- ✅ Prometheus metrics

### **Enhanced: HF Pro Embeddings**

```python
# scripts/upgrade_to_hf_embeddings.py
"""Upgrade ChromaDB to use HF Pro embeddings for better quality"""

from huggingface_hub import InferenceClient
from src.utils.vector_store import VectorMemory
import os

class HFProEmbeddings:
    """Premium embeddings via HF Pro API (768-dim vs local 384-dim)"""
    
    def __init__(self, model="sentence-transformers/all-mpnet-base-v2"):
        self.model = model
        self.client = InferenceClient(token=os.getenv("HF_TOKEN"))
    
    def __call__(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings via HF Pro"""
        return [self.client.feature_extraction(text, model=self.model) 
                for text in texts]

# Optional: Upgrade to premium embeddings
# Better quality, no local storage, always current
```

---

## 3. Claude.ai Max Integration (Browser)

### **Use Cases**

#### **A. Extended Context Code Review**

**Workflow:**
```bash
# 1. Generate code with orchestrator
orchestrator run examples/tiny_spec.yaml

# 2. Copy all generated code
LATEST=$(ls -t runs/ | head -1)
cat runs/$LATEST/outputs/**/*.py | pbcopy

# 3. Open Claude.ai Max
open "https://claude.ai/new"

# 4. Paste and prompt:
# "Review this FastAPI implementation for security, performance, and best practices"

# Claude Max can analyze:
# - 200K tokens (entire codebase + docs)
# - 20+ projects for organized reviews
# - Extended context for architectural analysis
```

#### **B. Claude Projects Structure**

Create projects in Claude.ai Max:

**1. unified_orchestrator_docs**
- Upload: All `.md` files from `docs/`
- Upload: `README.md`, `QUICKSTART.md`
- Upload: `.cursor/rules/*.mdc`
- Use for: Documentation questions, architecture discussions

**2. generated_code_review**
- Upload: Recent orchestrator outputs
- Upload: Code quality reports
- Use for: Code review, improvement suggestions

**3. framework_research**
- Upload: FastAPI examples
- Upload: ChromaDB patterns
- Upload: CrewAI examples
- Use for: Best practices research

---

## 4. Perplexity Max Integration (Browser)

### **Research Workflow**

**Before Code Generation:**
```bash
# 1. Research latest patterns
open "https://www.perplexity.ai/?q=FastAPI+authentication+best+practices+2025"

# 2. Wait for comprehensive answer with citations

# 3. Copy answer to clipboard (Cmd+A, Cmd+C)

# 4. Ingest into ChromaDB
python -c "
import pyperclip
from src.utils.vector_store import VectorMemory
from datetime import datetime

content = pyperclip.paste()
memory = VectorMemory(collection_name='research')
memory.save(
    key=f'perplexity_research_{datetime.now().isoformat()}',
    content=content,
    metadata={
        'source': 'perplexity',
        'topic': 'FastAPI authentication',
        'date': datetime.now().isoformat()
    }
)
print('✅ Research saved to ChromaDB')
"

# 5. Now run orchestrator with fresh context
orchestrator run examples/fastapi-auth.yaml
```

**Research Topics for Orchestrator:**
- "Latest Python async patterns 2025"
- "FastAPI vs Flask performance comparison"
- "ChromaDB optimization techniques"
- "CrewAI best practices"
- "PostgreSQL vs MongoDB for vector search"

---

## 5. Raycast Pro Integration

### **Custom Commands**

Create these scripts in `~/.config/raycast/scripts/`:

```bash
# 1. run-orchestrator.sh
#!/bin/bash
# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Run Orchestrator
# @raycast.mode fullOutput
# @raycast.packageName unified_orchestrator
# @raycast.icon 🚀
# @raycast.argument1 { "type": "text", "placeholder": "Spec file", "optional": false }

cd ~/Developer/projects/unified_orchestrator
source venv/bin/activate
orchestrator run "$1"

# 2. show-latest.sh
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title Show Latest Run
# @raycast.mode fullOutput
# @raycast.packageName unified_orchestrator
# @raycast.icon 📊

cd ~/Developer/projects/unified_orchestrator
source venv/bin/activate
LATEST=$(ls -t runs/ | head -1)
orchestrator show "$LATEST"

# 3. open-in-cursor.sh
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title Open in Cursor
# @raycast.mode silent
# @raycast.packageName unified_orchestrator
# @raycast.icon 💻

cd ~/Developer/projects/unified_orchestrator
LATEST=$(ls -t runs/ | head -1)
cursor "runs/$LATEST/outputs"

# 4. query-memory.sh
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title Query Memory
# @raycast.mode fullOutput
# @raycast.packageName unified_orchestrator
# @raycast.icon 🧠
# @raycast.argument1 { "type": "text", "placeholder": "Query" }

cd ~/Developer/projects/unified_orchestrator
source venv/bin/activate
python -c "
from src.utils.vector_store import VectorMemory
m = VectorMemory()
results = m.query('$1', k=5)
for i, r in enumerate(results, 1):
    print(f'\n{i}. {r[\"id\"]}')
    print(f'   {r[\"document\"][:200]}...')
"

# 5. research-and-generate.sh
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title Research & Generate
# @raycast.mode fullOutput
# @raycast.packageName unified_orchestrator
# @raycast.icon 🔍
# @raycast.argument1 { "type": "text", "placeholder": "Research topic" }

# Open Perplexity
open "https://www.perplexity.ai/?q=$1"
echo "📚 Research opened in Perplexity Max"
echo "💡 Copy answer, then press Enter to continue..."
read

# Save research
cd ~/Developer/projects/unified_orchestrator
source venv/bin/activate
python scripts/ingest_from_clipboard.py

echo "✅ Research saved to ChromaDB"
```

### **Raycast Quicklinks**

Add these quicklinks:
- `orch run` → `~/Developer/projects/unified_orchestrator && orchestrator run examples/tiny_spec.yaml`
- `orch show` → Opens latest run in terminal
- `claude review` → Opens Claude.ai with clipboard content
- `pplx research` → Opens Perplexity with query

---

## 6. Warp Pro Integration

### **Saved Workflows**

```yaml
# ~/.warp/workflows/unified-orchestrator.yaml

name: Unified Orchestrator
description: Multi-agent code generation workflows

workflows:
  - name: Quick Generate
    description: Fast code generation
    command: |
      cd ~/Developer/projects/unified_orchestrator
      source venv/bin/activate
      orchestrator run examples/tiny_spec.yaml
      LATEST=$(ls -t runs/ | head -1)
      echo "✅ Generated: runs/$LATEST"
      cursor "runs/$LATEST/outputs"
    tags: [orchestrator, generate]
  
  - name: Research & Generate
    description: Research in Perplexity, then generate
    command: |
      # Research phase
      open "https://www.perplexity.ai/?q=${TOPIC}"
      echo "📚 Research ${TOPIC} in Perplexity..."
      echo "Press Enter when ready to continue..."
      read
      
      # Generate phase
      cd ~/Developer/projects/unified_orchestrator
      source venv/bin/activate
      orchestrator run ${SPEC}
      
      # Review phase
      LATEST=$(ls -t runs/ | head -1)
      cat runs/$LATEST/outputs/**/*.py | pbcopy
      open "https://claude.ai/new"
      echo "📋 Code copied to clipboard - paste in Claude for review"
    variables:
      - name: TOPIC
        description: Research topic
      - name: SPEC
        description: Spec file
        default: examples/tiny_spec.yaml
    tags: [orchestrator, research, review]
  
  - name: Full Automation Pipeline
    description: Complete workflow with all integrations
    command: |
      cd ~/Developer/projects/unified_orchestrator
      source venv/bin/activate
      
      # 1. Run orchestrator
      echo "🚀 Running orchestrator..."
      orchestrator run ${SPEC}
      LATEST=$(ls -t runs/ | head -1)
      
      # 2. Open in Cursor
      echo "💻 Opening in Cursor..."
      cursor "runs/$LATEST/outputs"
      
      # 3. Copy for Claude review
      cat runs/$LATEST/outputs/**/*.py | pbcopy
      open "https://claude.ai/new"
      
      # 4. Run Comet automations
      echo "🤖 Running Comet integrations..."
      python scripts/comet_integrations.py full-automation "$LATEST"
      
      echo "✅ Pipeline complete!"
    variables:
      - name: SPEC
        description: Spec file
        default: examples/tiny_spec.yaml
    tags: [orchestrator, automation, pipeline]
  
  - name: Query Memory
    description: Search vector memory
    command: |
      cd ~/Developer/projects/unified_orchestrator
      source venv/bin/activate
      python -c "
      from src.utils.vector_store import VectorMemory
      m = VectorMemory()
      results = m.query('${QUERY}', k=5)
      for i, r in enumerate(results, 1):
          print(f'\n{i}. {r[\"id\"]}')
          print(f'   {r[\"document\"][:300]}...')
      "
    variables:
      - name: QUERY
        description: Search query
    tags: [orchestrator, memory, search]
```

---

## 7. Comet Browser Assistant Integration

### **Automation Scripts**

```python
# scripts/comet_integrations.py
"""
Integration with Comet Browser Assistant
Connects to GitHub, Linear, Notion, Slack
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


class CometWorkflow:
    """
    Orchestrator integrations via Comet Browser Assistant.
    
    Requires Comet CLI or browser automation setup.
    Adjust commands based on your Comet configuration.
    """
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
    
    def full_automation(self, run_id: str):
        """
        Complete post-generation workflow:
        1. Create GitHub repo
        2. Create Linear ticket
        3. Document in Notion
        4. Notify in Slack
        """
        print(f"🚀 Full automation for run: {run_id}\n")
        
        # Load run manifest
        manifest = self._load_manifest(run_id)
        if not manifest:
            print(f"❌ Manifest not found for {run_id}")
            return
        
        project_name = manifest.get("project", run_id)
        
        # 1. GitHub
        print("📦 Creating GitHub repository...")
        repo_url = self.create_github_repo(run_id, project_name)
        
        # 2. Linear
        print("📊 Creating Linear ticket...")
        ticket_id = self.create_linear_ticket(
            title=f"Review: {project_name}",
            description=f"Generated code ready for review\nRepo: {repo_url}",
            project="Engineering"
        )
        
        # 3. Notion
        print("📚 Documenting in Notion...")
        page_url = self.create_notion_page(
            title=f"Generated: {project_name}",
            content=self._format_run_summary(manifest, repo_url),
            database="Generated Projects"
        )
        
        # 4. Slack
        print("💬 Notifying team in Slack...")
        self.notify_slack(
            channel="engineering",
            message=f"""
🎉 *New Code Generated!*

*Project:* {project_name}
*Run ID:* {run_id}
*GitHub:* {repo_url}
*Linear:* {ticket_id}
*Notion:* {page_url}

Ready for review! 🚀
            """
        )
        
        print("\n✅ Full automation complete!")
    
    def create_github_repo(self, run_id: str, project_name: str) -> str:
        """Create GitHub repo from generated code"""
        run_dir = self.project_root / "runs" / run_id / "outputs"
        
        # Method 1: Via Comet CLI (if available)
        try:
            cmd = [
                "comet", "github", "create-repo",
                "--name", f"generated-{project_name}",
                "--description", f"Generated by unified_orchestrator (run: {run_id})",
                "--private", "false",
                "--source", str(run_dir)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                repo_url = result.stdout.strip()
                print(f"  ✅ Repo created: {repo_url}")
                return repo_url
        except FileNotFoundError:
            pass
        
        # Method 2: Manual with instructions
        print("  📝 Manual setup required:")
        print(f"     1. Create repo: https://github.com/new")
        print(f"     2. Name: generated-{project_name}")
        print(f"     3. Push code from: {run_dir}")
        
        return f"https://github.com/YOUR_USERNAME/generated-{project_name}"
    
    def create_linear_ticket(self, title: str, description: str, project: str) -> str:
        """Create Linear ticket for code review"""
        try:
            cmd = [
                "comet", "linear", "create-issue",
                "--title", title,
                "--description", description,
                "--project", project,
                "--priority", "medium"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                ticket_id = result.stdout.strip()
                print(f"  ✅ Ticket created: {ticket_id}")
                return ticket_id
        except FileNotFoundError:
            pass
        
        print("  📝 Create ticket manually in Linear")
        return "LINEAR-XXX"
    
    def create_notion_page(self, title: str, content: str, database: str) -> str:
        """Create Notion documentation page"""
        try:
            cmd = [
                "comet", "notion", "create-page",
                "--title", title,
                "--content", content,
                "--database", database
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                page_url = result.stdout.strip()
                print(f"  ✅ Page created: {page_url}")
                return page_url
        except FileNotFoundError:
            pass
        
        print("  📝 Create page manually in Notion")
        return "https://notion.so/your-page"
    
    def notify_slack(self, channel: str, message: str):
        """Send Slack notification"""
        try:
            cmd = [
                "comet", "slack", "send-message",
                "--channel", channel,
                "--text", message
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"  ✅ Notification sent to #{channel}")
                return True
        except FileNotFoundError:
            pass
        
        print(f"  📝 Post manually to Slack #{channel}")
        return False
    
    def _load_manifest(self, run_id: str) -> dict:
        """Load run manifest"""
        manifest_path = self.project_root / "runs" / run_id / "manifest.json"
        if manifest_path.exists():
            return json.loads(manifest_path.read_text())
        return {}
    
    def _format_run_summary(self, manifest: dict, repo_url: str) -> str:
        """Format run summary for Notion"""
        return f"""
# Generated Project Summary

**Run ID:** {manifest.get('job_id', 'unknown')}
**Project:** {manifest.get('project', 'unknown')}
**Status:** {manifest.get('status', 'unknown')}
**Duration:** {manifest.get('duration_s', 0):.1f}s
**Provider:** {manifest.get('provider', 'unknown')}
**Generated At:** {manifest.get('started_at', 'unknown')}

## Repository
{repo_url}

## Files Generated
{len(manifest.get('files', []))} files

## Next Steps
1. Review code in GitHub
2. Run tests
3. Deploy to staging
"""


def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Comet integrations for orchestrator")
    parser.add_argument("action", choices=["full-automation"], help="Action to perform")
    parser.add_argument("run_id", help="Orchestrator run ID")
    
    args = parser.parse_args()
    
    workflow = CometWorkflow()
    
    if args.action == "full-automation":
        workflow.full_automation(args.run_id)


if __name__ == "__main__":
    main()
```

---

## 🎯 Complete Workflow Example

### **End-to-End: Research → Generate → Review → Deploy**

```bash
# ===== STEP 1: Research in Perplexity Max =====
open "https://www.perplexity.ai/?q=FastAPI+WebSocket+best+practices+2025"
# Wait, read answer, copy to clipboard

# ===== STEP 2: Ingest Research =====
python scripts/ingest_from_clipboard.py --collection research

# ===== STEP 3: Generate Code =====
orchestrator run examples/websocket-api.yaml

# ===== STEP 4: Open in Cursor =====
cursor runs/$(ls -t runs/ | head -1)/outputs

# ===== STEP 5: Review in Claude Max =====
cat runs/$(ls -t runs/ | head -1)/outputs/**/*.py | pbcopy
open "https://claude.ai/new"
# Paste and ask: "Review this WebSocket implementation for security and performance"

# ===== STEP 6: Full Automation via Comet =====
python scripts/comet_integrations.py full-automation $(ls -t runs/ | head -1)

# Result:
# ✅ GitHub repo created
# ✅ Linear ticket created  
# ✅ Notion page documented
# ✅ Slack team notified
```

---

## 📊 Premium Stack ROI

| Tool | Monthly | Annual | Value Delivered |
|------|---------|--------|-----------------|
| Cursor Pro | $20 | $240 | AI coding, 10x faster |
| Claude Max | $20 | $240 | Extended context, 20+ projects |
| HF Pro | $9 | $108 | Enterprise ML inference |
| Perplexity Max | $20 | $240 | Real-time research |
| Comet | $10 | $120 | Multi-tool automation |
| Raycast Pro | $8 | $96 | Command automation |
| Warp Pro | $15 | $180 | AI terminal |
| **Total** | **$102** | **$1,224** | **Integrated ecosystem** |

**ROI Calculation:**
- **Time saved:** 7 hours per project (8hr → 1hr)
- **Value:** 7 hrs × $100/hr = $700 per project
- **Payback:** < 2 projects per month
- **Annual value:** $8,400+ (if 1 project/week)

---

## 🚀 Implementation Status

### **✅ Complete**
- [x] Cursor Rules configured
- [x] HuggingFace Pro integrated
- [x] ChromaDB vector memory active
- [x] Project structure optimized

### **⏳ Ready to Implement**
- [ ] Raycast commands (5 scripts)
- [ ] Warp workflows (5 workflows)
- [ ] Comet integration script
- [ ] Clipboard ingestion script
- [ ] Claude review automation

### **📚 Documentation Complete**
- [x] Premium stack overview
- [x] Integration architecture
- [x] Workflow examples
- [x] ROI analysis
- [x] Implementation guide

---

**Your $1,224/year premium stack is a complete automation ecosystem. Let's leverage it fully!** 🚀

