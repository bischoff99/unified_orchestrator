# Cursor Browser Automation - Quick Start

**🎯 Use Cursor IDE's built-in browser to automate your entire workflow!**

---

## ✅ What You Now Have

**MCP Servers (6 total):**
1. ✅ **Desktop Commander** - File operations, processes
2. ✅ **Chroma** - Vector memory (your Perplexity Space knowledge)
3. ✅ **Browser Control** - NEW! Automate any Chromium browser
4. ✅ **HuggingFace** - ML models and datasets
5. ✅ **Supermemory** - Cross-session memory
6. ✅ **Sequential Thinking** - Enhanced reasoning

**Browser Automation:**
- ✅ Playwright installed
- ✅ Automation scripts created
- ✅ MCP configured

---

## 🚀 Quick Start (5 minutes)

### **Step 1: Enable Cursor Browser** (1 min)

```
1. In Cursor: Cmd+, (Settings)
2. Go to "Beta" tab
3. Enable "Cursor Browser"
4. Restart Cursor
```

### **Step 2: Install Playwright** (2 min)

```bash
pip install playwright pytest-playwright
playwright install chromium
```

### **Step 3: Test Browser Automation** (2 min)

**Option A: Via Cursor Agent Mode**
```
1. Open Chat in Cursor (Cmd+L)
2. Select "Agent" mode
3. Prompt: "Open my Perplexity Space and show me what's there:
           https://www.perplexity.ai/spaces/agentic-workflow-orchestration-0X7OltmBQ.2PNpcYOwuyAA"
4. Watch Agent automate the browser!
```

**Option B: Via Playwright Script**
```bash
python scripts/playwright_space_sync.py --visible
```

---

## 🎯 Use Cases

### **1. Automated Research from Space**

**In Cursor Agent Mode:**
```
"Research 'FastAPI authentication patterns' in my Perplexity Space, 
extract the answer, and save to ChromaDB for my agents to use."
```

**Agent will:**
- ✅ Open browser via Playwright
- ✅ Navigate to your Space
- ✅ Search for topic
- ✅ Extract answer
- ✅ Save to ChromaDB
- ✅ Report completion

### **2. Test Generated API in Cursor Browser**

```
1. Generate API: python -m src.cli run examples/tiny_spec.yaml
2. Start server: uvicorn main:app --reload (in generated code)
3. In Cursor: View → Cursor Browser
4. Navigate: http://localhost:8000/docs
5. Test endpoints interactively!
```

**All without leaving Cursor IDE!**

### **3. Automated Perplexity → Code Generation**

**In Cursor Agent Mode:**
```
"Execute this workflow:
1. Research 'FastAPI WebSocket patterns' in my Perplexity Space
2. Save research to ChromaDB
3. Run orchestrator: python -m src.cli run examples/tiny_spec.yaml
4. Open results in Cursor Browser
5. Generate Playwright tests for the API
6. Run tests and report results"
```

**Cursor Agent does EVERYTHING!**

---

## 📋 Available Commands

### **From Cursor Chat (with Browser Control MCP):**

```
"Open a new browser tab with my Perplexity Space"
"Navigate to https://www.perplexity.ai"
"Extract content from current page"
"Take a screenshot of the current page"
"Close all browser tabs"
"Search Google for FastAPI patterns"
```

### **From Cursor Agent Mode:**

```
"Automate Perplexity research for [topic]"
"Generate and test FastAPI app in Cursor Browser"
"Create Playwright tests for my generated API"
"Sync my entire Perplexity Space to ChromaDB"
```

---

## 🎯 Complete Workflow Example

### **All in Cursor IDE:**

```
1. Open Cursor Chat (Cmd+L)

2. Select "Agent" mode

3. Paste this workflow:

"Complete automation workflow:

RESEARCH:
- Open browser to my Perplexity Space
- Search for 'multi-agent orchestration patterns'
- Extract comprehensive answer with citations
- Save to ChromaDB collection 'perplexity_space'

GENERATE:
- Run: python -m src.cli run examples/tiny_spec.yaml
- Capture run ID

TEST:
- Start generated FastAPI server
- Open in Cursor Browser
- Test POST /notes endpoint
- Test GET /notes endpoint
- Verify responses

DOCUMENT:
- Create summary in docs/
- Update PROJECT_PROGRESS.md with results

Execute all steps and report any issues."

4. Press Enter

5. Watch Cursor Agent:
   - Plan each step
   - Execute automation
   - Handle errors
   - Report completion

✅ EVERYTHING automated in Cursor IDE!
```

---

## 📊 MCP Server Status

**Your ~/.cursor/mcp.json now has:**

```json
{
  "mcpServers": {
    "desktop-commander": "✅ File operations",
    "chroma": "✅ Vector memory (fixed path!)",
    "browser-control": "✅ NEW! Browser automation",
    "hf-mcp-server": "✅ HuggingFace integration",
    "supermemory-mcp": "✅ Cross-session memory",
    "sequential-thinking": "✅ Enhanced reasoning"
  }
}
```

**Path fix:** Chroma now points to your actual memory directory:
`/Users/andrejsp/Developer/projects/unified_orchestrator/memory`

---

## 🎯 Next Steps

### **Immediate (Try Now):**

1. **Enable Cursor Browser:**
   - Cmd+, → Beta → Enable "Cursor Browser" → Restart

2. **Test Browser Control MCP:**
   - Restart Cursor (to load new mcp.json)
   - Open Chat
   - Ask: "Open my Perplexity Space in browser"

3. **Test Playwright Automation:**
   ```bash
   pip install playwright
   playwright install chromium
   python scripts/playwright_space_sync.py --visible
   ```

### **This Week:**

1. **Create Perplexity Collections:**
   - FastAPI Patterns
   - ChromaDB Optimization
   - Multi-Agent Coordination

2. **Sync to ChromaDB:**
   - Run automated sync daily
   - Agents query Space knowledge
   - Better code generation!

3. **Use Cursor Agent Mode:**
   - Full automation workflows
   - No manual steps
   - AI handles everything

---

## 💡 Pro Tips

### **Cursor Browser Shortcuts:**
- `Cmd+L` - Open Chat
- `View → Cursor Browser` - Open browser pane
- `Agent mode` - For autonomous execution
- `Composer` - Multi-file edits

### **Playwright Tips:**
- Use `--visible` flag while developing
- Take screenshots for debugging
- Adjust selectors based on actual HTML
- Add wait times for dynamic content

### **Agent Mode Tips:**
- Be specific in prompts
- Break down complex workflows
- Agent will plan and execute
- Review Agent's plan before execution

---

## 🎉 Achievement Unlocked!

**You now have:**
- ✅ 6 MCP servers configured
- ✅ Browser Control MCP added
- ✅ Chroma path fixed (points to ./memory)
- ✅ Playwright automation ready
- ✅ Scripts created and executable
- ✅ Cursor Browser enabled (after settings)
- ✅ Complete automation ecosystem **inside Cursor IDE**

**Everything happens in Cursor:**
- Research (via browser automation)
- Code generation (orchestrator)
- Testing (Cursor Browser)
- Debugging (integrated debugger)
- Version control (built-in git)

**No context switching. Full automation. One IDE.** 🚀

---

## 🔄 Restart Cursor

**To activate all MCP servers and browser features:**

1. Save all files (Cmd+S)
2. Quit Cursor (Cmd+Q)
3. Restart Cursor
4. MCP servers will auto-connect
5. Enable Cursor Browser in settings
6. Ready to use!

---

**Try it now:** Open Cursor Chat → Agent Mode → "Automate my Perplexity Space research" 🎯


