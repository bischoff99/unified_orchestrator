# Comet Browser + Perplexity Labs Integration

**Status:** 🎯 Advanced Automation Workflows  
**Last Updated:** 2025-10-22

## Overview

This guide shows how to leverage:
1. **Comet Browser Assistant** - Automate GitHub, Linear, Notion, Slack
2. **Perplexity Labs** (Max subscription) - Advanced AI features

---

## 1. Comet Browser Automation

### **What Comet Can Do:**

Comet Browser Assistant provides **no-code automation** with connectors to:
- **GitHub** - Create repos, issues, PRs, manage projects
- **Linear** - Create/update tickets, manage workflows
- **Notion** - Create pages, update databases, organize knowledge
- **Slack** - Send messages, create channels, manage notifications

### **Integration Methods:**

#### **A. Browser Automation (Visual)**

Comet can automate browser tasks visually - you can record workflows:

**Example Workflow: "Deploy Generated Code"**
```
1. Open Comet Browser Assistant
2. Record new workflow: "Deploy Orchestrator Run"
3. Steps:
   - Navigate to GitHub → New Repository
   - Fill name: "generated-{project}"
   - Set description from orchestrator manifest
   - Initialize with README
   - Open repository
   - Upload files from runs/{job_id}/outputs/
   - Create Linear ticket with repo link
   - Create Notion page with summary
   - Post to Slack #engineering
4. Save workflow
5. Trigger with: Run ID from orchestrator
```

#### **B. CLI Integration (Programmatic)**

If Comet provides CLI tools:

```python
# scripts/comet_deploy.py
"""Deploy orchestrator run using Comet Browser automation"""

import subprocess
from pathlib import Path

def deploy_with_comet(run_id: str):
    """
    Deploy generated code using Comet Browser workflows.
    
    Assumes Comet workflow named 'deploy-orchestrator' exists.
    """
    run_dir = Path(f"runs/{run_id}")
    
    # Trigger Comet workflow
    cmd = [
        "comet-cli",  # If Comet provides CLI
        "run-workflow",
        "--name", "deploy-orchestrator",
        "--variables", f"run_id={run_id},project={project_name}"
    ]
    
    result = subprocess.run(cmd, capture_output=True)
    return result.returncode == 0
```

#### **C. Webhook Integration**

```python
# scripts/comet_webhook.py
"""Trigger Comet workflows via webhooks"""

import requests
import os

def trigger_comet_workflow(workflow_id: str, data: dict):
    """
    Trigger Comet workflow via webhook.
    
    Args:
        workflow_id: Comet workflow identifier
        data: Workflow input data
    """
    webhook_url = os.getenv("COMET_WEBHOOK_URL")
    
    payload = {
        "workflow_id": workflow_id,
        "inputs": data
    }
    
    response = requests.post(webhook_url, json=payload)
    return response.status_code == 200

# Example: Trigger after orchestrator run
trigger_comet_workflow(
    workflow_id="deploy-orchestrator",
    data={
        "run_id": "job_a44e32b65ff9",
        "project": "tiny_notes_api",
        "repo_name": "generated-tiny-notes-api"
    }
)
```

---

## 2. Perplexity Labs Integration

### **What Perplexity Labs Offers (Max Subscription):**

**Web Interface Features:**
- **Collections** - Organize research by topic
- **Spaces** - Collaborative research workspaces
- **Advanced Search** - Domain filtering, recency filters
- **File Upload** - Search within your documents
- **API Access** - pplx-api endpoints (if enabled)

### **Browser-Based Workflows**

#### **A. Research Collections for Orchestrator**

Create Perplexity Collections for each framework:

**Collections to Create:**
1. **FastAPI Patterns** - Latest FastAPI best practices
2. **ChromaDB Optimization** - Vector search techniques
3. **CrewAI Examples** - Multi-agent patterns
4. **Python Architecture** - Design patterns
5. **Generated Code Reviews** - Past project insights

**Workflow:**
```
1. Open Perplexity Labs (https://labs.perplexity.ai)
2. Create Collection: "Orchestrator Knowledge Base"
3. Add threads:
   - "FastAPI authentication best practices 2025"
   - "ChromaDB performance optimization"
   - "CrewAI multi-agent coordination patterns"
4. Before each orchestrator run:
   - Open relevant collection
   - Review latest insights
   - Copy comprehensive answers
   - Ingest to ChromaDB
```

#### **B. File Upload for Context**

Perplexity Max allows uploading files for context:

```
1. Export orchestrator run manifest
2. Upload to Perplexity
3. Ask: "Review this generated code and suggest improvements"
4. Get AI analysis with web-sourced best practices
5. Save to ChromaDB for agent access
```

#### **C. Automated Research Pipeline**

```python
# scripts/perplexity_research_pipeline.py
"""Automated research using Perplexity Max via browser automation"""

import webbrowser
import time
import pyperclip

class PerplexityResearchPipeline:
    """
    Automate research using Perplexity Labs features.
    
    Workflow:
    1. Open Perplexity with query
    2. Wait for comprehensive answer
    3. Copy answer (manual)
    4. Ingest to ChromaDB (automatic)
    5. Agents can now access research
    """
    
    def research_and_ingest(self, topic: str, collection: str = "research"):
        """
        Research topic in Perplexity and save to ChromaDB.
        
        Args:
            topic: Research topic/query
            collection: ChromaDB collection name
        """
        print(f"🔍 Researching: {topic}")
        
        # 1. Open Perplexity Labs
        query = topic.replace(" ", "+")
        url = f"https://labs.perplexity.ai/?q={query}"
        webbrowser.open(url)
        
        print("\n📚 Perplexity Labs opened")
        print("Steps:")
        print("1. Wait for comprehensive answer with sources")
        print("2. Review citations and related threads")
        print("3. Copy complete answer (Cmd+A, Cmd+C)")
        print("4. Press Enter to save to ChromaDB...")
        
        input()  # Wait for user
        
        # 2. Ingest from clipboard
        import subprocess
        result = subprocess.run(
            [
                "python",
                "scripts/ingest_from_clipboard.py",
                "--collection", collection,
                "--metadata", f"source=perplexity_labs,topic={topic}"
            ],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Research saved to ChromaDB")
            print(f"📊 Collection: {collection}")
        else:
            print(f"❌ Error: {result.stderr}")
        
        return result.returncode == 0
    
    def batch_research(self, topics: list[str]):
        """Research multiple topics sequentially"""
        for i, topic in enumerate(topics, 1):
            print(f"\n{'='*60}")
            print(f"Research {i}/{len(topics)}: {topic}")
            print('='*60)
            self.research_and_ingest(topic)
        
        print(f"\n✅ Batch research complete! {len(topics)} topics ingested")


# Example usage
if __name__ == "__main__":
    pipeline = PerplexityResearchPipeline()
    
    # Research topics before code generation
    topics = [
        "FastAPI WebSocket authentication patterns 2025",
        "ChromaDB HNSW index optimization techniques",
        "Python async best practices for API servers",
    ]
    
    pipeline.batch_research(topics)
```

---

## 3. Comet + Perplexity Integrated Workflow

### **Complete Automation Pipeline:**

```python
# scripts/premium_stack_workflow.py
"""
Complete workflow using all premium tools:
Perplexity → ChromaDB → Orchestrator → Cursor → Claude → Comet
"""

import subprocess
import webbrowser
import time
from pathlib import Path

class PremiumStackWorkflow:
    """End-to-end workflow using entire premium stack"""
    
    def full_pipeline(self, research_topic: str, spec_file: str):
        """
        Complete pipeline:
        1. Research in Perplexity Labs
        2. Ingest to ChromaDB
        3. Generate code with orchestrator
        4. Open in Cursor
        5. Copy for Claude review
        6. Deploy via Comet
        """
        print("🚀 PREMIUM STACK FULL PIPELINE")
        print("="*70)
        
        # Step 1: Perplexity Research
        print("\n📚 STEP 1: Research in Perplexity Labs")
        print("-"*70)
        query = research_topic.replace(" ", "+")
        webbrowser.open(f"https://labs.perplexity.ai/?q={query}")
        
        print(f"Research topic: {research_topic}")
        print("Instructions:")
        print("1. Wait for comprehensive answer")
        print("2. Review sources and citations")
        print("3. Copy answer (Cmd+A, Cmd+C)")
        print("\nPress Enter when ready...")
        input()
        
        # Step 2: Ingest to ChromaDB
        print("\n💾 STEP 2: Ingest Research to ChromaDB")
        print("-"*70)
        subprocess.run([
            "python", "scripts/ingest_from_clipboard.py",
            "--collection", "research",
            "--metadata", f"source=perplexity_labs,topic={research_topic}"
        ])
        
        # Step 3: Generate Code
        print("\n🚀 STEP 3: Generate Code with Orchestrator")
        print("-"*70)
        result = subprocess.run(
            ["python", "-m", "src.cli", "run", spec_file],
            capture_output=True,
            text=True
        )
        
        # Extract run ID from output
        run_id = None
        for line in result.stdout.split("\n"):
            if "Run ID:" in line:
                run_id = line.split(":")[-1].strip()
                break
        
        if not run_id:
            print("❌ Could not extract run ID")
            return False
        
        print(f"✅ Generated: {run_id}")
        
        # Step 4: Open in Cursor
        print("\n💻 STEP 4: Open in Cursor IDE Pro")
        print("-"*70)
        output_dir = f"runs/{run_id}/outputs"
        subprocess.run(["cursor", output_dir])
        print(f"✅ Opened: {output_dir}")
        
        # Step 5: Prepare for Claude Review
        print("\n🤖 STEP 5: Prepare for Claude.ai Max Review")
        print("-"*70)
        
        # Copy all Python files to clipboard
        py_files = list(Path(output_dir).rglob("*.py"))
        if py_files:
            combined = ""
            for f in py_files:
                combined += f"# {f.name}\n{f.read_text()}\n\n"
            
            subprocess.run(["pbcopy"], input=combined.encode())
            webbrowser.open("https://claude.ai/new")
            
            print(f"✅ Copied {len(py_files)} files to clipboard")
            print("✅ Claude.ai opened - paste for review")
            print("\nSuggested Claude prompt:")
            print('  "Review this generated code for security, performance,')
            print('   and best practices. Suggest improvements."')
        
        # Step 6: Deploy via Comet
        print("\n🔗 STEP 6: Deploy via Comet Browser")
        print("-"*70)
        print("Press Enter to trigger Comet automation...")
        input()
        
        subprocess.run([
            "python", "scripts/comet_integrations.py",
            "full-automation", run_id
        ])
        
        # Summary
        print("\n"+"="*70)
        print("✅ PREMIUM STACK PIPELINE COMPLETE!")
        print("="*70)
        print(f"\n📊 Summary:")
        print(f"  Research: {research_topic}")
        print(f"  Generated: {run_id}")
        print(f"  Location: {output_dir}")
        print(f"\n🎯 Next steps:")
        print(f"  1. Review in Cursor")
        print(f"  2. Review Claude's suggestions")
        print(f"  3. Check Comet automation results:")
        print(f"     - GitHub repository")
        print(f"     - Linear ticket")
        print(f"     - Notion documentation")
        print(f"     - Slack notification")
        
        return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Premium stack full workflow")
    parser.add_argument("research_topic", help="Topic to research in Perplexity")
    parser.add_argument("spec_file", help="Orchestrator spec file")
    
    args = parser.parse_args()
    
    workflow = PremiumStackWorkflow()
    workflow.full_pipeline(args.research_topic, args.spec_file)
```

---

## 4. Perplexity Labs Features

### **What You Get with Perplexity Max:**

**In Perplexity Labs (https://labs.perplexity.ai):**

1. **Collections** - Organize research threads by topic
2. **Spaces** - Collaborative research workspaces
3. **File Upload** - Upload docs for context-aware search
4. **Advanced Filters:**
   - Domain filtering (search specific sites)
   - Recency filtering (hour, day, week, month)
   - Academic mode (peer-reviewed papers)
5. **Export Features** - Save research with citations
6. **Thread Linking** - Connect related research

### **Perplexity Labs Automation:**

#### **A. Pre-Generation Research**

```bash
# Before generating FastAPI code:

# 1. Open Perplexity Labs
open "https://labs.perplexity.ai"

# 2. Create Collection: "FastAPI 2025 Patterns"

# 3. Research in collection:
Query: "FastAPI authentication with JWT best practices 2025"
- Enable domain filter: fastapi.tiangolo.com, github.com
- Enable recency: month
- Upload existing FastAPI docs for context

# 4. Copy comprehensive answer with citations

# 5. Ingest to ChromaDB
python scripts/ingest_from_clipboard.py \
  --collection perplexity_labs \
  --metadata "source=perplexity_labs,collection=FastAPI_2025,domain=fastapi.tiangolo.com"

# 6. Now orchestrator agents can query this knowledge!
```

#### **B. Code Review with File Upload**

```bash
# After generation:

# 1. Export generated code
cp runs/job_a44e32b65ff9/outputs/tiny_notes_api/main.py /tmp/generated.py

# 2. Open Perplexity Labs
open "https://labs.perplexity.ai"

# 3. Upload generated.py

# 4. Ask:
"Review this FastAPI code. Compare with latest best practices.
Identify security issues, performance bottlenecks, and suggest improvements."

# 5. Perplexity analyzes your code + searches latest docs

# 6. Copy suggestions and save
python scripts/ingest_from_clipboard.py \
  --collection code_reviews \
  --metadata "source=perplexity_labs,run_id=job_a44e32b65ff9"
```

#### **C. Competitive Analysis**

```bash
# Research alternatives and comparisons

Topics in Perplexity Labs:
1. "FastAPI vs Flask performance comparison 2025"
2. "Best Python async web frameworks"
3. "ChromaDB vs Pinecone vs Weaviate"
4. "CrewAI vs LangGraph vs AutoGen comparison"

# Save all to ChromaDB for architectural decisions
```

---

## 5. Comet Browser Workflows

### **Workflow 1: GitHub Repository Creation**

**In Comet Browser:**
```
1. Create workflow: "Create GitHub Repo from Orchestrator"
2. Steps:
   - Navigate: github.com/new
   - Fill form:
     * Repository name: [variable: repo_name]
     * Description: "Generated by unified_orchestrator"
     * Visibility: Public
   - Initialize: with README
   - Click: Create repository
   - Copy: repository URL
   - Return: URL to orchestrator
3. Save workflow
```

**Trigger from orchestrator:**
```python
# After generation, trigger Comet workflow
comet_trigger("create-github-repo", {
    "repo_name": f"generated-{project_name}",
    "run_id": run_id
})
```

### **Workflow 2: Linear Ticket Creation**

**In Comet Browser:**
```
1. Create workflow: "Create Linear Review Ticket"
2. Steps:
   - Navigate: linear.app
   - Click: New Issue
   - Fill:
     * Title: [variable: title]
     * Description: [variable: description]
     * Project: Engineering
     * Priority: Medium
     * Labels: generated-code, review
   - Create issue
   - Copy: Issue URL
3. Save workflow
```

### **Workflow 3: Notion Documentation**

**In Comet Browser:**
```
1. Create workflow: "Document in Notion"
2. Steps:
   - Navigate: notion.so/Generated-Projects
   - New page
   - Fill template:
     * Title: [variable: project_name]
     * Run ID: [variable: run_id]
     * Status: [variable: status]
     * Links: GitHub, Linear
   - Save page
3. Save workflow
```

### **Workflow 4: Slack Notification**

**In Comet Browser:**
```
1. Create workflow: "Notify Team"
2. Steps:
   - Navigate: slack.com/app
   - Channel: #engineering
   - Compose message:
     "🎉 New code generated!
      Project: [project_name]
      GitHub: [repo_url]
      Linear: [ticket_url]
      Notion: [doc_url]"
   - Send
3. Save workflow
```

---

## 6. Integration Architecture

```
┌─────────────────────────────────────────────┐
│         Perplexity Labs (Research)          │
│  • Collections for organized knowledge      │
│  • File upload for code review              │
│  • Domain/recency filtering                 │
│  • Export with citations                    │
└──────────────────┬──────────────────────────┘
                   ↓ (Copy answer)
┌─────────────────────────────────────────────┐
│      Clipboard → ChromaDB Ingestion         │
│  • Semantic indexing                        │
│  • Metadata tagging                         │
│  • Vector search                            │
└──────────────────┬──────────────────────────┘
                   ↓ (Agents query)
┌─────────────────────────────────────────────┐
│         Unified Orchestrator                │
│  • Context-aware generation                 │
│  • Multi-agent execution                    │
│  • Code + docs generation                   │
└──────────────────┬──────────────────────────┘
                   ↓ (Generated code)
┌─────────────────────────────────────────────┐
│          Comet Browser Assistant            │
│  • GitHub: Create repo + push code          │
│  • Linear: Create review ticket             │
│  • Notion: Document generation              │
│  • Slack: Notify team                       │
└─────────────────────────────────────────────┘
```

---

## 7. Practical Workflows

### **Workflow A: FastAPI Project with Latest Patterns**

```bash
# 1. Research in Perplexity Labs
python scripts/perplexity_research_pipeline.py \
  "FastAPI authentication and authorization patterns 2025"

# 2. Generate code (agents query ChromaDB for context)
python -m src.cli run examples/fastapi-auth.yaml

# 3. Review with Perplexity Labs
# Upload generated main.py
# Ask: "Review this code against latest FastAPI docs"

# 4. Deploy via Comet
python scripts/comet_integrations.py full-automation $(ls -t runs/ | head -1)
```

### **Workflow B: Continuous Learning**

```bash
# Daily research ingestion (cron job)

# 1. Morning: Research latest updates
Topics:
- "FastAPI updates and changes this week"
- "Python 3.12 new features"
- "ChromaDB performance improvements"

# 2. Ingest all to ChromaDB collection: "daily_updates"

# 3. Agents now have access to latest knowledge

# 4. Generate code with fresh context
```

### **Workflow C: Competitive Analysis**

```bash
# 1. Research in Perplexity Labs Collection: "Competitor Analysis"
- "CrewAI alternatives and comparisons"
- "Vector database benchmarks 2025"
- "Multi-agent orchestration frameworks"

# 2. Save to ChromaDB collection: "competitive_intel"

# 3. Query before architectural decisions:
python scripts/orchestrator-query-memory.sh "best vector database for embeddings"
```

---

## 8. Browser Automation Scripts

### **Using AppleScript for Browser Control**

```bash
# scripts/automate_perplexity.sh
#!/bin/bash
# Automate Perplexity Labs via AppleScript

QUERY="$1"

# Open Perplexity Labs
open "https://labs.perplexity.ai/?q=${QUERY}"

# Wait for page load
sleep 3

# AppleScript to interact (if needed)
osascript << EOF
tell application "Safari"
    activate
    -- Wait for answer to load
    delay 5
    -- Select all content
    tell application "System Events"
        keystroke "a" using command down
        delay 0.5
        keystroke "c" using command down
    end tell
end tell
EOF

echo "✅ Research copied to clipboard"
echo "Saving to ChromaDB..."

# Ingest
python scripts/ingest_from_clipboard.py \
  --collection perplexity_labs \
  --metadata "query=${QUERY}"

echo "✅ Research saved and searchable!"
```

---

## 9. Comet Integration Examples

### **Setup Comet Workflows:**

**In Comet Browser Assistant:**

1. **Open Comet** → Create new automation

2. **Workflow: "Deploy Orchestrator Run"**
   ```
   Trigger: Manual (or webhook)
   
   Actions:
   1. Read file: runs/{run_id}/manifest.json
   2. Extract: project name, status, duration
   3. GitHub → Create repository
      - Name: generated-{project}
      - Upload: runs/{run_id}/outputs/*
   4. Linear → Create issue
      - Title: "Review: {project}"
      - Description: Include GitHub URL
   5. Notion → Create page in "Generated Projects"
      - Template: Project summary
   6. Slack → Post to #engineering
      - Message: "New code ready for review"
   ```

3. **Save workflow** with ID: `deploy-orchestrator`

4. **Trigger from CLI:**
   ```bash
   # Method 1: Comet CLI (if available)
   comet run-workflow deploy-orchestrator --var run_id=job_a44e32b65ff9
   
   # Method 2: Our Python script
   python scripts/comet_integrations.py full-automation job_a44e32b65ff9
   ```

---

## 🎯 **Immediate Actions You Can Take:**

### **1. Perplexity Labs Research (Now)**

```bash
# Open Perplexity Labs
open "https://labs.perplexity.ai"

# Create Collection: "Orchestrator Knowledge Base"

# Research and save:
1. Query: "FastAPI latest security best practices 2025"
2. Copy answer (Cmd+A, Cmd+C)
3. Run: python scripts/ingest_from_clipboard.py --collection research
```

### **2. Set Up Comet Workflows (10 min)**

```
1. Open Comet Browser Assistant
2. Create 4 workflows:
   - GitHub repo creation
   - Linear ticket creation
   - Notion documentation
   - Slack notification
3. Test each individually
4. Combine into "full-automation" workflow
```

### **3. Test Full Pipeline (Now)**

```bash
# Complete end-to-end with Desktop Commander:
python scripts/premium_stack_workflow.py \
  "FastAPI WebSocket best practices" \
  examples/tiny_spec.yaml
```

---

**Want me to create the full automation scripts for Comet + Perplexity Labs integration?** 🚀

The key is:
- **Perplexity Labs** = Research + file upload features (browser-based)
- **Comet Browser** = Automate repetitive browser tasks (visual workflows)
- **Both** = No API needed, leverage your Max subscriptions fully!

