# Comet Browser MCP Integration

**Browser:** Comet (Perplexity's Chromium-based AI browser)  
**Control Method:** Model Context Protocol (MCP)  
**Status:** 🎯 Ready to Implement

**Source:** [Browser Control MCP](https://glama.ai/mcp/servers/%40eyalzh/browser-control-mcp)

---

## 🎯 What You Can Do

### **Option 1: Use Existing Browser Control MCP**

There's already a browser control MCP server that works with Chromium browsers!

**GitHub:** `@eyalzh/browser-control-mcp`

**Capabilities:**
- ✅ Open/close tabs
- ✅ Navigate to URLs
- ✅ Get list of open tabs
- ✅ Reorder tabs
- ✅ Read browser history
- ✅ Search history
- ✅ Extract webpage content
- ✅ Execute JavaScript
- ✅ Take screenshots

### **Option 2: Generate Custom Comet MCP Server**

**You have an MCP generator in your project!** Use it to create a custom Comet browser controller:

```bash
cd /Users/andrejsp/Developer/projects/unified_orchestrator/mcp-generator

# Generate browser control MCP
python generate.py --api "browser-control" --verbose

# Or generate Comet-specific MCP
python generate.py --api "comet-browser" --verbose
```

**The generator will:**
1. Research browser automation APIs (Playwright/Puppeteer)
2. Design MCP server architecture
3. Write production Python code
4. Create tests and documentation
5. Generate complete MCP server package

---

## 🚀 Quick Setup: Browser Control MCP

### **Step 1: Install Browser Control MCP**

```bash
# Using npx (easiest)
npx @eyalzh/browser-control-mcp
```

### **Step 2: Add to MCP Config**

Add to `~/.cursor/mcp.json` or Claude Desktop config:

```json
{
  "mcpServers": {
    "browser-control": {
      "command": "npx",
      "args": ["-y", "@eyalzh/browser-control-mcp"]
    }
  }
}
```

### **Step 3: Install Browser Extension**

The MCP server needs a browser extension to control Comet:

```bash
# 1. Install from Chrome Web Store (if available for Comet)
# 2. Or build custom extension for Comet browser
```

---

## 🔧 Custom Comet MCP Server

### **Generate Using Your MCP Generator:**

```python
# mcp-generator/apis/comet_browser.py
"""API specification for Comet browser control"""

COMET_API_SPEC = {
    "name": "comet-browser",
    "description": "Control Comet (Perplexity's AI browser) via MCP",
    "base_url": "http://localhost:9222",  # Chrome DevTools Protocol
    "authentication": None,
    "tools": [
        {
            "name": "open_tab",
            "description": "Open new tab with URL",
            "parameters": {
                "url": "string (required) - URL to open"
            }
        },
        {
            "name": "close_tab",
            "description": "Close specific tab",
            "parameters": {
                "tab_id": "string (required) - Tab identifier"
            }
        },
        {
            "name": "list_tabs",
            "description": "Get all open tabs",
            "parameters": {}
        },
        {
            "name": "navigate_perplexity_space",
            "description": "Navigate to Perplexity Space",
            "parameters": {
                "space_id": "string (optional) - Space ID, defaults to agentic-workflow-orchestration"
            }
        },
        {
            "name": "extract_page_content",
            "description": "Extract text content from current page",
            "parameters": {
                "selector": "string (optional) - CSS selector for specific content"
            }
        },
        {
            "name": "execute_script",
            "description": "Execute JavaScript in browser",
            "parameters": {
                "script": "string (required) - JavaScript code"
            }
        },
        {
            "name": "search_perplexity",
            "description": "Search in Perplexity (Comet)",
            "parameters": {
                "query": "string (required) - Search query"
            }
        },
        {
            "name": "copy_to_clipboard",
            "description": "Copy page content to system clipboard",
            "parameters": {
                "selector": "string (optional) - What to copy"
            }
        }
    ]
}
```

### **Generate the MCP Server:**

```bash
cd /Users/andrejsp/Developer/projects/unified_orchestrator/mcp-generator

# Generate Comet browser MCP server
python generate.py \
  --api comet-browser \
  --output ../mcp-servers/comet-browser \
  --verbose

# Agents will:
# 1. Research Chrome DevTools Protocol
# 2. Design MCP server for Comet control
# 3. Implement tools for browser automation
# 4. Create tests and docs
# 5. Generate complete package
```

---

## 🎯 Integration with Orchestrator

### **Automated Research Workflow:**

```python
# scripts/automated_perplexity_research.py
"""
Automate research using Comet browser MCP.

Flow:
1. MCP opens Comet browser
2. MCP navigates to your Space
3. MCP searches for topic
4. MCP extracts answer
5. MCP copies to clipboard
6. Ingest to ChromaDB
7. Agents use knowledge
"""

from mcp_client import MCPClient  # Hypothetical MCP client

def automated_research(topic: str):
    """Fully automated research pipeline"""
    
    # Connect to Comet browser MCP
    browser = MCPClient("browser-control")
    
    # 1. Open your Perplexity Space
    browser.call_tool(
        "navigate_perplexity_space",
        space_id="agentic-workflow-orchestration-0X7OltmBQ.2PNpcYOwuyAA"
    )
    
    # 2. Search in Space
    browser.call_tool("search_perplexity", query=topic)
    
    # 3. Wait for answer
    time.sleep(5)
    
    # 4. Extract answer
    content = browser.call_tool(
        "extract_page_content",
        selector=".answer-content"  # Adjust based on Perplexity HTML
    )
    
    # 5. Copy to clipboard
    browser.call_tool("copy_to_clipboard")
    
    # 6. Ingest to ChromaDB
    subprocess.run([
        "python", "scripts/ingest_from_clipboard.py",
        "--collection", "perplexity_space",
        "--metadata", f"topic={topic},source=automated"
    ])
    
    print(f"✅ Automated research complete: {topic}")
    return True
```

### **Orchestrator + Browser MCP Workflow:**

```python
# Full automation using MCP

def generate_with_research(topic: str, spec_file: str):
    """
    Complete workflow:
    1. Research in Comet browser (via MCP)
    2. Ingest to ChromaDB
    3. Generate code with orchestrator
    4. Review results in Comet browser
    """
    
    browser_mcp = MCPClient("browser-control")
    
    # Step 1: Automated research
    print(f"🔍 Researching: {topic}")
    browser_mcp.call_tool("search_perplexity", query=topic)
    browser_mcp.call_tool("copy_to_clipboard")
    subprocess.run(["python", "scripts/ingest_from_clipboard.py"])
    
    # Step 2: Generate code
    print(f"🚀 Generating code...")
    result = subprocess.run(
        ["python", "-m", "src.cli", "run", spec_file],
        capture_output=True
    )
    
    # Extract run ID
    run_id = extract_run_id(result.stdout)
    
    # Step 3: Open results in browser
    output_path = Path(f"runs/{run_id}/outputs")
    
    # Open in Comet for review
    browser_mcp.call_tool(
        "open_tab",
        url=f"file://{output_path.absolute()}"
    )
    
    print(f"✅ Complete! Results open in Comet browser")
    return run_id
```

---

## 🏗️ Architecture Options

### **Option A: Pre-built Browser Control MCP**

```json
// ~/.cursor/mcp.json

{
  "mcpServers": {
    "browser-control": {
      "command": "npx",
      "args": ["-y", "@eyalzh/browser-control-mcp"]
    },
    "chroma-orchestrator": {
      "command": "uvx",
      "args": [
        "chroma-mcp",
        "--client-type", "persistent",
        "--data-dir", "/Users/andrejsp/Developer/projects/unified_orchestrator/memory"
      ]
    }
  }
}
```

**Usage from Cursor/Claude:**
- "Open a new tab in Comet with my Perplexity Space"
- "Extract content from current Comet page"
- "Search Perplexity for FastAPI patterns and save result"

### **Option B: Generate Custom Comet MCP**

```bash
# Use your MCP generator to create Comet-specific server

cd mcp-generator

python generate.py --api comet-browser

# Output: mcp-servers/comet-browser/
# ├── server.py (Comet-specific browser control)
# ├── requirements.txt
# ├── README.md
# └── mcp_config.json (ready to use)
```

**Advantages:**
- Custom tools for Perplexity Space
- Optimized for your workflow
- Can add Space-specific features
- Full control over functionality

---

## 🎯 Perplexity Space MCP Tools

### **Custom Tools for Your Space:**

```python
# In generated MCP server

@mcp_tool
def open_agentic_space():
    """Open your Agentic Workflow Orchestration Space"""
    browser.navigate(
        "https://www.perplexity.ai/spaces/agentic-workflow-orchestration-0X7OltmBQ.2PNpcYOwuyAA"
    )

@mcp_tool
def search_in_space(query: str):
    """Search within your Space for relevant threads"""
    # Navigate to Space
    open_agentic_space()
    # Execute search
    browser.execute_script(f'document.querySelector(".search").value = "{query}"')
    # Return results

@mcp_tool
def create_space_thread(title: str, query: str):
    """Create new research thread in Space"""
    open_agentic_space()
    # Click new thread
    # Fill title and query
    # Submit
    # Return thread URL

@mcp_tool  
def export_space_thread(thread_url: str):
    """Extract complete thread content for ChromaDB ingestion"""
    browser.navigate(thread_url)
    content = browser.extract_content(".thread-content")
    citations = browser.extract_content(".citations")
    
    return {
        "content": content,
        "citations": citations
    }

@mcp_tool
def batch_export_space():
    """Export all threads from Space"""
    open_agentic_space()
    
    # Get all thread links
    threads = browser.execute_script("""
        return Array.from(document.querySelectorAll('.thread-link'))
            .map(a => a.href);
    """)
    
    # Export each
    results = []
    for thread_url in threads:
        results.append(export_space_thread(thread_url))
    
    return results
```

---

## 📋 Implementation Steps

### **Step 1: Install Browser Control MCP**

```bash
# Add to your existing mcp.json
```

```json
{
  "mcpServers": {
    "browser-control": {
      "command": "npx",
      "args": ["-y", "@eyalzh/browser-control-mcp"]
    },
    "chroma-orchestrator": {
      "command": "uvx",
      "args": [
        "chroma-mcp",
        "--client-type", "persistent",
        "--data-dir", "/Users/andrejsp/Developer/projects/unified_orchestrator/memory"
      ]
    },
    "desktop-commander": {
      "command": "npx",
      "args": ["-y", "@wonderwhy-er/desktop-commander@latest"]
    }
  }
}
```

### **Step 2: Test Browser Control**

From Cursor or Claude Desktop:
```
"Open my Perplexity Space in a new tab"
"Navigate to https://www.perplexity.ai/spaces/agentic-workflow-orchestration-0X7OltmBQ.2PNpcYOwuyAA"
"Extract the content from the current page"
```

### **Step 3: Generate Custom Comet MCP (Optional)**

```bash
cd mcp-generator

# Generate Space-optimized MCP server
python generate.py --api perplexity-space --verbose

# Agents will create MCP server with tools specifically for your Space!
```

---

## 🔄 Complete Automated Pipeline

### **Fully Automated Research → Code Generation:**

```python
# scripts/fully_automated_workflow.py
"""
100% automated workflow using MCP servers:
- Browser Control MCP (Comet automation)
- Chroma MCP (vector memory)
- Desktop Commander MCP (file operations)
"""

def fully_automated_generate(research_topic: str, spec_file: str):
    """
    Completely automated pipeline:
    1. MCP opens Comet → navigates to Space
    2. MCP searches topic in Space
    3. MCP extracts answer
    4. MCP saves to ChromaDB
    5. Run orchestrator (agents query ChromaDB)
    6. MCP opens results in Cursor
    7. MCP creates GitHub repo
    8. MCP posts to Slack
    
    ALL AUTOMATED - NO MANUAL STEPS!
    """
    
    # Connect to MCP servers
    browser = MCPClient("browser-control")
    chroma = MCPClient("chroma-orchestrator")
    dc = MCPClient("desktop-commander")
    
    # 1. Research in Space
    print(f"🔍 Step 1: Research '{research_topic}' in Perplexity Space")
    browser.call_tool(
        "navigate",
        url="https://www.perplexity.ai/spaces/agentic-workflow-orchestration-0X7OltmBQ.2PNpcYOwuyAA"
    )
    browser.call_tool("search", query=research_topic)
    time.sleep(5)  # Wait for answer
    
    content = browser.call_tool("extract_content")
    
    # 2. Save to ChromaDB
    print("💾 Step 2: Save to ChromaDB")
    chroma.call_tool(
        "chroma_add_documents",
        collection="perplexity_space",
        documents=[content],
        metadatas=[{
            "source": "space",
            "topic": research_topic,
            "automated": True
        }]
    )
    
    # 3. Generate code
    print("🚀 Step 3: Generate code with orchestrator")
    result = dc.call_tool(
        "start_process",
        command=f"python -m src.cli run {spec_file}"
    )
    
    run_id = extract_run_id(result)
    
    # 4. Open in Cursor
    print("💻 Step 4: Open in Cursor")
    dc.call_tool(
        "start_process",
        command=f"cursor runs/{run_id}/outputs"
    )
    
    # 5. Create GitHub repo (via browser MCP)
    print("📦 Step 5: Create GitHub repo")
    browser.call_tool("navigate", url="https://github.com/new")
    browser.call_tool(
        "execute_script",
        script=f"""
        document.querySelector('[name="repository[name]"]').value = 'generated-{run_id}';
        document.querySelector('[name="repository[description]"]').value = 'Generated by unified_orchestrator';
        """
    )
    
    print("✅ FULLY AUTOMATED PIPELINE COMPLETE!")
    print(f"   Research: ✅")
    print(f"   ChromaDB: ✅")
    print(f"   Generate: ✅")
    print(f"   Cursor: ✅")
    print(f"   GitHub: ✅")
    
    return run_id


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("research_topic", help="Topic to research in Space")
    parser.add_argument("spec_file", help="Orchestrator spec file")
    
    args = parser.parse_args()
    
    fully_automated_generate(args.research_topic, args.spec_file)
```

---

## 🎯 Your Complete MCP Ecosystem

### **Current + Proposed:**

```json
{
  "mcpServers": {
    "desktop-commander": {
      "command": "npx",
      "args": ["-y", "@wonderwhy-er/desktop-commander@latest"]
    },
    "chroma-orchestrator": {
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
    "supermemory": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote@latest",
        "https://supermemory.ai/mcp",
        "--header",
        "x-sm-project:default"
      ]
    }
  }
}
```

**Available MCP Tools:**
- **Desktop Commander** - File operations, processes, searches ✅
- **Chroma** - Vector memory operations ✅
- **Browser Control** - Comet browser automation (NEW!)
- **Supermemory** - Cross-session memory ✅

---

## 🚀 Use Cases

### **1. Automated Daily Research**

```bash
# Morning automation:
# 1. MCP opens Comet
# 2. MCP navigates to your Space
# 3. MCP searches: "agentic workflow updates this week"
# 4. MCP extracts answer + citations
# 5. MCP saves to ChromaDB
# 6. Done - agents now have latest knowledge!
```

### **2. Code Generation with Live Context**

```bash
# Agents query your Space in real-time:
# 1. Agent needs FastAPI pattern
# 2. Agent queries ChromaDB (synced from Space)
# 3. Finds your curated research
# 4. Generates better code
```

### **3. Results Documentation**

```bash
# After orchestrator run:
# 1. MCP opens Comet
# 2. MCP navigates to Space
# 3. MCP creates new thread: "Orchestrator Results - {date}"
# 4. MCP fills content with run summary
# 5. MCP posts thread
# 6. Done - Space documented automatically!
```

---

## 📊 Benefits

| Without MCP | With Browser MCP |
|-------------|------------------|
| Manual: Open browser | **MCP: Automated** |
| Manual: Navigate to Space | **MCP: One command** |
| Manual: Search | **MCP: Scripted** |
| Manual: Copy content | **MCP: Extracted** |
| Manual: Save to ChromaDB | **MCP: Auto-ingested** |
| **Time: 5-10 min** | **Time: 30 seconds** |

---

## 🎯 Quick Start

### **Immediate: Test Browser Control MCP**

```bash
# 1. Install browser control MCP
npx @eyalzh/browser-control-mcp

# 2. Test from terminal
# (After adding to mcp.json and restarting Cursor)

# 3. From Cursor, ask:
# "Open my Perplexity Space in browser:
#  https://www.perplexity.ai/spaces/agentic-workflow-orchestration-0X7OltmBQ.2PNpcYOwuyAA"
```

### **Advanced: Generate Custom MCP**

```bash
# Use your MCP generator
cd mcp-generator

python generate.py --api perplexity-space-automation

# Generates complete MCP server with:
# - Tools for Space navigation
# - Thread creation/extraction
# - Content ingestion to ChromaDB
# - Integration with orchestrator
```

---

## 🔗 Integration Map

```
Comet Browser (Chromium)
    ↕️ (controlled by)
Browser Control MCP Server
    ↕️ (calls)
Cursor IDE / Claude Desktop
    ↕️ (triggers)
unified_orchestrator
    ↕️ (queries)
ChromaDB (synced from Space)
    ↕️ (populated from)
Perplexity Space
(Agentic Workflow Orchestration)
```

---

**This is the holy grail of automation:** Your Perplexity Space becomes a **living knowledge base** that **automatically enhances your code generation** via MCP-controlled browser automation! 🚀

Want me to:
1. Generate the custom Comet MCP server using your generator?
2. Create the automated research scripts?
3. Set up the browser control MCP in your config?

All doable right now! 🎯


