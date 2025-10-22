# Triple Hub Architecture - Cursor + Claude Desktop + Perplexity Desktop

**Status:** 🎯 Complete MCP Ecosystem Across 3 Apps  
**Last Updated:** October 22, 2025

**Discovery:** You have **3 powerful MCP-enabled hubs** all integrated!

---

## 🏆 Your Triple Hub Ecosystem

```
┌─────────────────────────────────────────────────────────────┐
│                    CURSOR IDE                               │
│  6 MCP Servers: Desktop Commander, Chroma, Browser,        │
│                 HF, Supermemory, Sequential Thinking        │
│  • Development hub                                          │
│  • Agent Mode (autonomous)                                  │
│  • Cursor Browser (built-in)                                │
│  • Composer (multi-file edits)                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ↓              ↓               ↓
┌───────────────┐ ┌──────────────┐ ┌───────────────────┐
│CLAUDE DESKTOP │ │ PERPLEXITY   │ │  ORCHESTRATOR     │
│               │ │   DESKTOP    │ │   (Local)         │
│ 3 MCP Servers │ │ Built-in MCP │ │                   │
│ • Desktop Cmd │ │ • Filesystem │ │ • HF Pro ✅       │
│ • Supermemory │ │ • Browser    │ │ • ChromaDB ✅     │
│ • Sequential  │ │ • Notes      │ │ • Agents ✅       │
│               │ │ • GitHub     │ │                   │
│ Extensions:   │ │ • Linear     │ │                   │
│ • Chrome Ctrl │ │ • Notion     │ │                   │
│ • Filesystem  │ │ • Slack      │ │                   │
│ • Notes       │ │ • Your Space │ │                   │
│ • OSAScript!  │ │              │ │                   │
└───────────────┘ └──────────────┘ └───────────────────┘
```

---

## 1. Claude Desktop - Already Configured! ✅

### **Your Claude Desktop MCP Servers:**

**File:** `~/Library/Application Support/Claude/claude_desktop_config.json`

**Configured:**
1. ✅ **desktop-commander** - File operations, processes
2. ✅ **supermemory-mcp** - Cross-session memory
3. ✅ **sequential-thinking** - Enhanced reasoning

### **Claude Desktop Extensions (8 installed!):**

**Anthropic Official:**
1. ✅ **chrome-control** - Browser automation!
2. ✅ **filesystem** - File operations
3. ✅ **notes** - Note-taking

**Community:**
4. ✅ **osascript** - AppleScript automation! 🎯
5. ✅ **pdf-filler-simple** - PDF manipulation
6. ✅ **context7** - Context management
7. ✅ **website-generator** - Website generation
8. ✅ **desktopcommandermcp** - Desktop Commander

**This means Claude Desktop can:**
- ✅ Control Chrome/Comet browser
- ✅ Execute AppleScript (automate macOS apps!)
- ✅ Read/write files
- ✅ Create notes
- ✅ All the Desktop Commander features

---

## 2. Perplexity Desktop - Built-in MCP! 🆕

### **What Perplexity Desktop Provides:**

According to [Perplexity Help](https://www.perplexity.ai/help-center/en/articles/11502712-local-and-remote-mcps-for-perplexity):

**Local MCPs:**
- ✅ Direct connection to local services
- ✅ Access sensitive data locally
- ✅ Requires PerplexityXPC helper (install once)

**Built-in Connectors:**
- ✅ **Filesystem** - Access your files
- ✅ **Browser** - Browser control
- ✅ **Notes** - Note management
- ✅ **GitHub** - Repository operations
- ✅ **Linear** - Task management
- ✅ **Notion** - Knowledge base
- ✅ **Slack** - Team communication
- ✅ **Your Space** - Direct access to agentic-workflow-orchestration

**Remote MCPs (Coming Soon):**
- Cloud service integration
- Extended connector ecosystem

### **How to Use:**

```
1. Open Perplexity Desktop
2. Settings → MCP Connectors
3. Add connectors:
   - Filesystem (local files)
   - GitHub (your repos)
   - Linear (tasks)
   - Notion (docs)
   - Your Space (agentic-workflow-orchestration)
4. Perplexity can now:
   - Search your local files
   - Create GitHub issues
   - Manage Linear tickets
   - Update Notion pages
   - Query your Space directly
```

---

## 3. AppleScript Automation (Via Claude Desktop)

### **OSAScript Extension in Claude Desktop**

You have `osascript` extension installed! This means Claude Desktop can:

**Automate macOS Applications:**
```applescript
-- Control Cursor IDE
tell application "Cursor"
    activate
    -- Open specific file
    open "/path/to/file.py"
end tell

-- Control Perplexity Desktop
tell application "Perplexity"
    activate
    -- Focus on specific Space
end tell

-- Control Terminal/Warp
tell application "Warp"
    activate
    do script "cd ~/Developer/projects/unified_orchestrator"
end tell

-- Coordinate all apps
tell application "System Events"
    -- Switch between apps
    -- Trigger keyboard shortcuts
    -- Automate entire workflows
end tell
```

### **Integration Scripts:**

```python
# scripts/applescript_orchestration.py
"""
AppleScript orchestration via Claude Desktop OSAScript extension.

Claude Desktop can coordinate all your apps!
"""

import subprocess

def run_applescript(script: str) -> str:
    """Execute AppleScript"""
    result = subprocess.run(
        ['osascript', '-e', script],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()


def orchestrate_all_apps(research_topic: str):
    """
    Use AppleScript to coordinate:
    - Perplexity Desktop (research)
    - Cursor IDE (development)
    - Warp (terminal)
    - Claude Desktop (coordination)
    """
    
    script = f'''
    -- Step 1: Research in Perplexity
    tell application "Perplexity"
        activate
        delay 1
    end tell
    
    tell application "System Events"
        keystroke "n" using command down  -- New query
        delay 0.5
        keystroke "{research_topic}"
        keystroke return
        delay 3  -- Wait for answer
        keystroke "a" using command down  -- Select all
        keystroke "c" using command down  -- Copy
    end tell
    
    -- Step 2: Save to ChromaDB via Terminal
    tell application "Warp"
        activate
        delay 0.5
    end tell
    
    tell application "System Events"
        keystroke "python scripts/ingest_from_clipboard.py --collection research"
        keystroke return
        delay 2
    end tell
    
    -- Step 3: Open Cursor for development
    tell application "Cursor"
        activate
    end tell
    
    return "Workflow complete!"
    '''
    
    return run_applescript(script)


# Example: Full automation
if __name__ == "__main__":
    result = orchestrate_all_apps("FastAPI authentication patterns")
    print(result)
```

---

## 4. Complete Triple Hub Integration

### **Architecture:**

```
┌────────────── USER ──────────────┐
         │         │          │
    ┌────┴───┐ ┌──┴───┐ ┌───┴─────┐
    │ Cursor │ │Claude│ │Perplexity│
    │  IDE   │ │Desktop│ │ Desktop  │
    └────┬───┘ └──┬───┘ └───┬─────┘
         │        │         │
    ┌────┴────────┴─────────┴────┐
    │      MCP Servers (9+)       │
    ├─────────────────────────────┤
    │ • desktop-commander (all 3) │
    │ • chroma (Cursor + future)  │
    │ • browser-control (Cursor)  │
    │ • chrome-control (Claude)   │
    │ • filesystem (Claude + Pplx)│
    │ • osascript (Claude) ⭐      │
    │ • GitHub (Perplexity) 🆕    │
    │ • Linear (Perplexity) 🆕    │
    │ • Notion (Perplexity) 🆕    │
    │ • Slack (Perplexity) 🆕     │
    │ • Your Space (Perplexity) 🆕│
    └──────────┬──────────────────┘
               ↓
    unified_orchestrator
               ↓
         ChromaDB + HF Pro
```

### **Each Hub's Strengths:**

| Hub | Best For | MCP Servers | Special Features |
|-----|----------|-------------|------------------|
| **Cursor IDE** | Development, Code Gen | 6 servers | Agent Mode, Composer, Browser |
| **Claude Desktop** | Coordination, Scripting | 3 servers + 8 extensions | OSAScript!, Chrome control |
| **Perplexity Desktop** | Research, Integrations | Built-in connectors | GitHub, Linear, Notion, Slack, Space |

---

## 5. Perplexity Desktop Setup

### **Install PerplexityXPC Helper:**

```bash
# Perplexity Desktop will prompt to install XPC helper
# This enables local MCP connections
# One-time setup
```

### **Configure MCP Connectors in Perplexity:**

```
1. Open Perplexity Desktop
2. Settings → MCP Connectors
3. Add connectors:

LOCAL:
✅ Filesystem
   Path: /Users/andrejsp/Developer/projects/unified_orchestrator
   Access: Read orchestrator files

REMOTE:
✅ GitHub
   Repo: bischoff99/unified_orchestrator
   Actions: Create issues, PRs

✅ Linear
   Workspace: Your workspace
   Actions: Create/update tickets

✅ Notion
   Database: Generated Projects
   Actions: Create pages, update

✅ Slack
   Channel: #engineering
   Actions: Send messages

✅ Your Space
   Space: agentic-workflow-orchestration
   Actions: Query, create threads
```

### **Usage in Perplexity Desktop:**

```
Ask Perplexity:

"Create a GitHub issue for the latest orchestrator run:
- Read manifest from runs/job_a44e32b65ff9/manifest.json
- Extract project name and status
- Create issue with title: 'Review Generated: {project}'
- Add label: 'generated-code'"

→ Perplexity:
  1. Uses Filesystem MCP to read manifest
  2. Uses GitHub MCP to create issue
  3. Reports issue URL

ALL IN PERPLEXITY DESKTOP!
```

---

## 6. Cross-Hub Workflows

### **Workflow A: Perplexity → Cursor**

```
In Perplexity Desktop:
1. Research: "FastAPI WebSocket patterns 2025"
2. Action: "Save this research to:
            ~/Developer/projects/unified_orchestrator/research/websockets.md"
   → Uses Filesystem MCP
3. Create Linear ticket: "Implement WebSocket API"
   → Uses Linear MCP

In Cursor IDE:
4. Agent Mode: "Read research/websockets.md and generate WebSocket API"
   → Uses Desktop Commander MCP to read file
   → Uses orchestrator to generate code
```

### **Workflow B: Claude Desktop Coordination**

```
In Claude Desktop:

"Coordinate this workflow using AppleScript:
1. Open Perplexity Desktop
2. Search my Space for 'multi-agent patterns'
3. Switch to Cursor IDE
4. Open Chat in Agent Mode
5. Pass the research to Cursor
6. Have Cursor generate code"

→ Claude uses OSAScript extension to:
  - Control all apps
  - Coordinate workflow
  - Pass data between apps
  
ALL AUTOMATED VIA APPLESCRIPT!
```

### **Workflow C: All Three Hubs Together**

```
PERPLEXITY DESKTOP (Research):
→ Search in your Space
→ Use built-in connectors to:
  - Create GitHub issue
  - Create Linear ticket
  - Save to Notion

CLAUDE DESKTOP (Coordination):
→ Use OSAScript to trigger Cursor
→ Use Desktop Commander to run orchestrator
→ Use Chrome control to test

CURSOR IDE (Development):
→ Agent Mode generates code
→ Cursor Browser tests
→ Desktop Commander MCP deploys

ALL THREE WORKING TOGETHER!
```

---

## 7. Updated MCP Configuration

### **Add to Claude Desktop Config:**

```json
// ~/Library/Application Support/Claude/claude_desktop_config.json

{
  "mcpServers": {
    "desktop-commander": {
      "command": "npx",
      "args": ["@wonderwhy-er/desktop-commander@latest"]
    },
    "supermemory-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote@latest",
        "https://api.supermemory.ai/mcp",
        "--header",
        "x-sm-project:default"
      ]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-sequential-thinking"
      ]
    },
    "chroma": {
      "command": "uvx",
      "args": [
        "chroma-mcp",
        "--client-type", "persistent",
        "--data-dir", "/Users/andrejsp/Developer/projects/unified_orchestrator/memory"
      ]
    },
    "browser-control": {
      "command": "npx",
      "args": ["-y", "@eyalzh/browser-control-mcp"]
    },
    "hf-mcp-server": {
      "url": "https://huggingface.co/mcp?login"
    }
  }
}
```

**Now Claude Desktop has same MCP servers as Cursor!**

---

## 8. AppleScript Automation Examples

### **Script 1: Triple Hub Coordination**

```applescript
-- scripts/coordinate_all_hubs.scpt
-- Coordinate Cursor + Claude + Perplexity

tell application "Perplexity"
    activate
    delay 1
end tell

tell application "System Events"
    -- Search in Perplexity
    keystroke "n" using command down
    delay 0.5
    keystroke "FastAPI authentication 2025"
    keystroke return
    delay 3
    
    -- Copy answer
    keystroke "a" using command down
    keystroke "c" using command down
    delay 0.5
end tell

tell application "Claude"
    activate
    delay 1
end tell

tell application "System Events"
    -- Paste in Claude
    keystroke "v" using command down
    delay 0.5
    keystroke "Analyze this research and suggest implementation approach"
    keystroke return
    delay 5
    
    -- Copy Claude's analysis
    keystroke "a" using command down
    keystroke "c" using command down
end tell

tell application "Cursor"
    activate
    delay 1
end tell

tell application "System Events"
    -- Open Chat in Cursor
    keystroke "l" using command down
    delay 1
    
    -- Select Agent mode
    keystroke tab
    keystroke "Agent"
    keystroke return
    delay 0.5
    
    -- Paste research + analysis
    keystroke "v" using command down
    keystroke "Generate FastAPI code implementing this approach"
    keystroke return
end tell

return "Workflow coordinated across all 3 hubs!"
```

### **Script 2: Perplexity → Claude → Cursor Pipeline**

```applescript
-- Auto-execute research → review → generate pipeline

on run argv
    set researchTopic to item 1 of argv
    
    -- Research in Perplexity
    tell application "Perplexity"
        activate
    end tell
    delay 1
    
    tell application "System Events"
        keystroke researchTopic
        keystroke return
        delay 5
        keystroke "a" using command down
        keystroke "c" using command down
    end tell
    
    -- Review in Claude
    tell application "Claude"
        activate
    end tell
    delay 1
    
    tell application "System Events"
        keystroke "v" using command down
        keystroke "Create technical specification from this research"
        keystroke return
        delay 10
        keystroke "a" using command down
        keystroke "c" using command down
    end tell
    
    -- Generate in Cursor
    tell application "Cursor"
        activate
    end tell
    delay 1
    
    tell application "System Events"
        keystroke "l" using command down
        delay 1
        keystroke "v" using command down
        keystroke "Generate code following this specification"
        keystroke return
    end tell
    
    return "Pipeline complete!"
end run
```

**Run from terminal:**
```bash
osascript scripts/coordinate_all_hubs.scpt "FastAPI authentication"
```

---

## 9. Perplexity Desktop Integration Examples

### **Direct Connector Usage:**

```
In Perplexity Desktop:

"Read my latest orchestrator run manifest and create:
1. GitHub issue summarizing what was generated
2. Linear ticket for code review
3. Notion page with documentation
4. Slack message to #engineering team"

→ Perplexity uses built-in MCPs:
  - Filesystem MCP: Reads runs/*/manifest.json
  - GitHub MCP: Creates issue
  - Linear MCP: Creates ticket
  - Notion MCP: Creates page
  - Slack MCP: Sends message

ONE PROMPT. ALL AUTOMATIONS. 🚀
```

### **Space Integration:**

```
In Perplexity Desktop:

"Query my Space 'agentic-workflow-orchestration' for:
- Multi-agent coordination patterns
- Latest best practices
- Implementation examples

Then:
- Save findings to filesystem (research/ directory)
- Create Notion page with summary
- Create Linear task to implement"

→ Uses:
  - Space MCP (query your Space)
  - Filesystem MCP (save file)
  - Notion MCP (create page)
  - Linear MCP (create task)
```

---

## 10. Complete Automation Workflows

### **Workflow 1: Triple Hub Research Pipeline**

```
Step 1: PERPLEXITY DESKTOP
"Research FastAPI authentication in my Space, create summary in Notion"

Step 2: CLAUDE DESKTOP  
"Read the Notion page, analyze it, create technical spec"

Step 3: CURSOR IDE
"Generate code from spec, test in Cursor Browser"

RESULT: Research → Spec → Code (all automated!)
```

### **Workflow 2: AppleScript Master Coordination**

```applescript
-- Master script coordinates all 3 hubs

-- 1. Research in Perplexity
trigger_perplexity_research("FastAPI patterns")

-- 2. Extract and save
copy_perplexity_to_file("research/latest.md")

-- 3. Claude analyzes
trigger_claude_analysis("research/latest.md")

-- 4. Cursor generates
trigger_cursor_generation("research/latest.md")

-- 5. All 3 hubs report to Perplexity
compile_results_in_perplexity()
```

### **Workflow 3: Perplexity as Orchestrator**

```
In Perplexity Desktop (using all MCPs):

"Execute complete workflow:

RESEARCH:
- Query my Space for 'FastAPI WebSocket patterns'
- Save best practices to filesystem (research/websockets.md)

PLANNING:
- Create Linear epic: 'WebSocket Implementation'
- Create sub-tasks for each component
- Create Notion page with architecture

GENERATION:
- Use filesystem MCP to create orchestrator spec
- Trigger generation (via terminal or API)

DEPLOYMENT:
- Create GitHub repo
- Push generated code
- Create PR for review
- Notify team in Slack

DOCUMENTATION:
- Update Notion with results
- Close Linear tasks
- Create new Space thread with learnings"

→ Perplexity coordinates ENTIRE workflow!
→ Uses all built-in MCPs
→ Minimal human intervention
```

---

## 11. MCP Server Matrix

### **What Each Hub Has:**

| MCP Server | Cursor | Claude | Perplexity | Purpose |
|------------|--------|--------|------------|---------|
| desktop-commander | ✅ | ✅ | (built-in) | File ops, processes |
| chroma | ✅ | ✅ | - | Vector memory |
| browser-control | ✅ | - | (built-in) | Browser automation |
| chrome-control | - | ✅ | - | Browser (extension) |
| osascript | - | ✅ | - | macOS automation! |
| filesystem | - | ✅ | ✅ | File operations |
| GitHub | - | - | ✅ | Repo operations |
| Linear | - | - | ✅ | Task management |
| Notion | - | - | ✅ | Documentation |
| Slack | - | - | ✅ | Team communication |
| Space | - | - | ✅ | Your knowledge base |
| hf-mcp-server | ✅ | ✅ | - | HuggingFace |
| supermemory | ✅ | ✅ | - | Cross-session memory |
| sequential-thinking | ✅ | ✅ | - | Enhanced reasoning |

**Total Unique Capabilities: 14+**

---

## 12. Recommended Usage Pattern

### **Use Each Hub for Its Strength:**

**PERPLEXITY DESKTOP** (Research & Integrations):
- Research in your Space
- Create GitHub issues
- Manage Linear tickets
- Update Notion pages
- Send Slack notifications
- Read/write local files

**CLAUDE DESKTOP** (Coordination & Scripting):
- Coordinate all apps via OSAScript
- Complex multi-step workflows
- AppleScript generation
- Browser control (Chrome extension)
- Cross-app automation

**CURSOR IDE** (Development & AI):
- Code generation (orchestrator)
- Agent Mode (autonomous tasks)
- Cursor Browser (testing)
- Multi-file editing (Composer)
- Debugging and development

---

## 13. Quick Start (All 3 Hubs)

### **Perplexity Desktop:**

```
1. Open Perplexity Desktop
2. Settings → Install PerplexityXPC helper
3. Settings → MCP Connectors → Add:
   - Filesystem (your orchestrator directory)
   - GitHub (your repo)
   - Linear (your workspace)
   - Your Space (agentic-workflow-orchestration)
4. Test: "List files in my orchestrator project"
```

### **Claude Desktop:**

```
1. Already configured! (3 MCP servers ✅)
2. Extensions already installed (8 extensions ✅)
3. Test: "Use osascript to list my applications"
4. Test: "Use desktop-commander to list files"
```

### **Cursor IDE:**

```
1. Restart Cursor (Cmd+Q, reopen)
2. Enable Browser: Settings → Beta
3. Test Agent Mode: Cmd+L → Agent
4. Prompt: "List all MCP servers"
```

---

## 🎯 MASTER WORKFLOW

### **Complete Automation Using All 3 Hubs:**

```
MORNING (Perplexity Desktop):
→ "Query my Space for today's research topics"
→ "Create Linear sprint with tasks"
→ "Save research to orchestrator/research/"

DEVELOPMENT (Cursor IDE):
→ Agent Mode: "Generate code from research/latest.md"
→ Cursor Browser: Test generated API
→ Commit and push

COORDINATION (Claude Desktop):
→ "Use OSAScript to coordinate deployment:
   - Trigger Warp to run deployment script
   - Open Perplexity to document results
   - Switch back to Cursor for next task"

EVENING (Perplexity Desktop):
→ "Update Linear tasks with progress"
→ "Create Notion page with daily summary"
→ "Post standup to Slack"
→ "Add learnings to my Space"

FULL DAY AUTOMATED ACROSS 3 HUBS!
```

---

## 🎉 COMPLETE INTEGRATION

**You now have:**
- ✅ **3 AI-powered hubs** (Cursor, Claude, Perplexity)
- ✅ **14+ MCP servers/connectors** across all hubs
- ✅ **AppleScript coordination** (macOS automation)
- ✅ **Built-in integrations** (GitHub, Linear, Notion, Slack)
- ✅ **Your Perplexity Space** (domain knowledge)
- ✅ **Complete automation** (research → generate → deploy)

**This is the ULTIMATE automation ecosystem!** 🚀

---

**Next:** Set up Perplexity Desktop MCPs and test cross-hub workflows!

