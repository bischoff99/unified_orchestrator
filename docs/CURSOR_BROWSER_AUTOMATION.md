# Cursor IDE Browser Automation Integration

**Status:** 🎯 Built-in Browser Automation Available  
**Last Updated:** 2025-10-22

**Source:** [Cursor IDE Advanced Techniques](https://developertoolkit.ai/en/cursor-ide/advanced-techniques/agent-modes-deep-dive)

---

## 🎯 Cursor IDE Built-In Browser Features

### **What Cursor IDE Provides:**

1. **Cursor Browser (Beta)** - In-app browser
   - Test changes in real-time
   - No context switching
   - Visual debugging
   - Responsive testing

2. **Agent Mode** - AI autonomous execution
   - AI plans and executes tasks
   - Can generate Playwright scripts
   - Automates browser testing
   - Natural language → automated tests

3. **Playwright Integration** - Browser automation framework
   - E2E testing
   - Cross-browser support
   - Headless automation
   - Screenshot/video capture

---

## 🚀 Enabling Cursor Browser

### **Step 1: Enable in Settings**

```
1. Open Cursor Settings (Cmd+,)
2. Navigate to "Beta" tab
3. Enable "Cursor Browser"
4. Restart Cursor if prompted
```

### **Step 2: Access Browser**

```
- View Menu → Cursor Browser
- Or: Cmd+Shift+P → "Cursor Browser: Open"
```

### **Step 3: Test with Orchestrator**

```bash
# Generate code
python -m src.cli run examples/tiny_spec.yaml

# Open generated FastAPI app
cd runs/$(ls -t runs/ | head -1)/outputs/tiny_notes_api

# Run server
uvicorn main:app --reload

# Open in Cursor Browser:
# View → Cursor Browser → Navigate to http://localhost:8000/docs
```

---

## 🤖 Agent Mode for Browser Automation

### **What Agent Mode Can Do:**

**In Cursor, open chat and select "Agent" mode**, then:

```
Prompt examples:

1. "Generate Playwright tests for my FastAPI notes API at localhost:8000"
   → Agent writes complete test suite

2. "Automate opening my Perplexity Space and extracting the latest thread"
   → Agent creates automation script

3. "Create browser automation to test the generated FastAPI endpoints"
   → Agent writes E2E tests

4. "Build a script that opens Comet browser, navigates to my Space, and copies content"
   → Agent creates full automation
```

**Agent will:**
- ✅ Plan the automation
- ✅ Write Playwright code
- ✅ Create test files
- ✅ Execute and verify
- ✅ Provide feedback

---

## 🔧 Playwright Integration

### **Install Playwright**

```bash
cd /Users/andrejsp/Developer/projects/unified_orchestrator

# Install Playwright
pip install playwright pytest-playwright

# Install browsers
playwright install chromium
```

### **Create Browser Automation Scripts**

```python
# scripts/browser_automation.py
"""
Browser automation using Playwright (Cursor IDE compatible)

Can be executed:
1. Directly from terminal
2. Via Cursor Agent Mode
3. From Cursor Browser
"""

from playwright.sync_api import sync_playwright
import time

class CometBrowserAutomation:
    """
    Automate Comet browser (or any Chromium browser) using Playwright.
    
    Works with:
    - Comet (Perplexity's browser)
    - Chrome
    - Chromium
    - Edge
    """
    
    def __init__(self, browser_path: str = None):
        """
        Initialize Playwright automation.
        
        Args:
            browser_path: Path to Comet/Chrome executable (optional)
        """
        self.browser_path = browser_path
        self.playwright = None
        self.browser = None
        self.page = None
    
    def __enter__(self):
        """Context manager for automatic cleanup"""
        self.playwright = sync_playwright().start()
        
        # Launch browser
        if self.browser_path:
            # Connect to specific browser (Comet)
            self.browser = self.playwright.chromium.launch(
                executable_path=self.browser_path,
                headless=False
            )
        else:
            # Use default Chromium
            self.browser = self.playwright.chromium.launch(headless=False)
        
        self.page = self.browser.new_page()
        return self
    
    def __exit__(self, *args):
        """Cleanup"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def open_perplexity_space(self, space_id: str = "agentic-workflow-orchestration-0X7OltmBQ.2PNpcYOwuyAA"):
        """Navigate to Perplexity Space"""
        url = f"https://www.perplexity.ai/spaces/{space_id}"
        print(f"🔗 Opening Space: {url}")
        self.page.goto(url)
        time.sleep(2)  # Wait for load
    
    def search_in_space(self, query: str):
        """Search within Perplexity Space"""
        print(f"🔍 Searching: {query}")
        
        # Click search box
        self.page.click('[data-testid="search-input"]')  # Adjust selector
        
        # Type query
        self.page.fill('[data-testid="search-input"]', query)
        
        # Press Enter
        self.page.press('[data-testid="search-input"]', 'Enter')
        
        # Wait for results
        time.sleep(3)
    
    def extract_answer(self) -> str:
        """Extract answer content from Perplexity"""
        print("📄 Extracting answer...")
        
        # Wait for answer to load
        self.page.wait_for_selector('.answer-container', timeout=10000)
        
        # Extract text
        answer = self.page.text_content('.answer-container')
        
        return answer
    
    def extract_citations(self) -> list[str]:
        """Extract citation URLs"""
        print("📚 Extracting citations...")
        
        # Get all citation links
        citations = self.page.eval_on_selector_all(
            '.citation-link',
            'elements => elements.map(el => el.href)'
        )
        
        return citations
    
    def copy_to_clipboard(self, content: str):
        """Copy content to system clipboard"""
        # Use Playwright's clipboard API
        self.page.evaluate(f'navigator.clipboard.writeText("{content}")')
        print("📋 Copied to clipboard")
    
    def take_screenshot(self, path: str):
        """Capture screenshot"""
        self.page.screenshot(path=path)
        print(f"📸 Screenshot saved: {path}")


def automated_space_research(topic: str) -> dict:
    """
    Fully automated Perplexity Space research.
    
    Returns:
        dict with 'answer' and 'citations'
    """
    
    with CometBrowserAutomation() as browser:
        # 1. Open Space
        browser.open_perplexity_space()
        
        # 2. Search topic
        browser.search_in_space(topic)
        
        # 3. Extract answer
        answer = browser.extract_answer()
        
        # 4. Extract citations
        citations = browser.extract_citations()
        
        # 5. Copy to clipboard
        browser.copy_to_clipboard(answer)
        
        # 6. Screenshot for reference
        browser.take_screenshot(f"logs/perplexity_{topic[:20]}.png")
        
        return {
            "answer": answer,
            "citations": citations
        }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Automate Perplexity Space research")
    parser.add_argument("topic", help="Topic to research")
    
    args = parser.parse_args()
    
    result = automated_space_research(args.topic)
    
    print("\n" + "="*70)
    print("✅ RESEARCH COMPLETE")
    print("="*70)
    print(f"\nAnswer ({len(result['answer'])} chars):")
    print(result['answer'][:500])
    print(f"\n...\n\nCitations ({len(result['citations'])}):")
    for i, url in enumerate(result['citations'], 1):
        print(f"{i}. {url}")
    
    # Auto-ingest to ChromaDB
    print("\n💾 Saving to ChromaDB...")
    import subprocess
    subprocess.run(["python", "scripts/ingest_from_clipboard.py", "--collection", "perplexity_space"])
```

---

## 🎯 Integration with Orchestrator

### **Workflow: Cursor Agent → Browser → Orchestrator**

```python
# scripts/cursor_agent_workflow.py
"""
Leverage Cursor Agent Mode for complete automation.

Usage in Cursor:
1. Open Chat (Cmd+L)
2. Select "Agent" mode
3. Paste this workflow description
"""

CURSOR_AGENT_PROMPT = """
Execute this automated workflow:

STEP 1: Browser Research
- Use Playwright to open Perplexity Space: 
  https://www.perplexity.ai/spaces/agentic-workflow-orchestration-0X7OltmBQ.2PNpcYOwuyAA
- Search for: "FastAPI authentication patterns 2025"
- Extract the comprehensive answer
- Copy to clipboard

STEP 2: Ingest to ChromaDB
- Run: python scripts/ingest_from_clipboard.py --collection perplexity_space
- Verify ingestion successful

STEP 3: Generate Code
- Run: python -m src.cli run examples/tiny_spec.yaml
- Extract run ID from output

STEP 4: Open in Cursor Browser
- Open Cursor Browser (View → Cursor Browser)
- Navigate to generated FastAPI docs
- Test endpoints interactively

STEP 5: Report Results
- Create summary of what was generated
- Save to logs/automation_results.json

Execute all steps autonomously and report completion.
"""


def run_via_cursor_agent():
    """
    Instructions for using Cursor Agent Mode.
    
    This leverages Cursor's built-in AI agent capabilities
    to execute the entire workflow.
    """
    
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║       CURSOR AGENT MODE AUTOMATION                         ║
    ╚════════════════════════════════════════════════════════════╝
    
    Steps to run this workflow in Cursor IDE:
    
    1. Open Cursor Chat (Cmd+L)
    
    2. Select "Agent" mode from mode picker
    
    3. Paste this prompt:
    ───────────────────────────────────────────────────────────
    """)
    
    print(CURSOR_AGENT_PROMPT)
    
    print("""
    ───────────────────────────────────────────────────────────
    
    4. Press Enter
    
    5. Watch Cursor Agent:
       - Plan the workflow
       - Execute each step
       - Handle errors
       - Report completion
    
    ✅ Cursor Agent will execute EVERYTHING automatically!
    
    No manual intervention needed - the Agent Mode handles:
    - Browser automation (Playwright)
    - File operations
    - Running commands
    - Error handling
    - Result reporting
    """)


if __name__ == "__main__":
    run_via_cursor_agent()
```

---

## 📋 Cursor Browser Use Cases

### **1. Test Generated APIs in Real-Time**

```
Workflow in Cursor:

1. Generate API: orchestrator run examples/tiny_spec.yaml
2. Start server: uvicorn main:app --reload
3. Open Cursor Browser: View → Cursor Browser
4. Navigate: http://localhost:8000/docs
5. Test endpoints interactively
6. See changes live (no external browser needed!)
```

### **2. Visual Debugging**

```
In Cursor Browser:
- Set breakpoints in code
- Trigger endpoint in browser
- Debug executes in Cursor
- See both code and browser side-by-side
```

### **3. Responsive Testing**

```
In Cursor Browser:
- Toggle device emulation
- Test mobile vs desktop
- See CSS changes live
- No need for external tools
```

---

## 🤖 Cursor Agent Mode Examples

### **Example 1: Generate Playwright Tests**

```
Cursor Agent Prompt:

"Create Playwright tests for the FastAPI notes API at runs/job_a44e32b65ff9/outputs/tiny_notes_api/:

Tests needed:
1. Test POST /notes - create a note
2. Test GET /notes - retrieve notes
3. Test error handling
4. Test database persistence

Save tests to: tests/e2e/test_generated_api.py"

→ Agent generates complete test suite
→ Agent can run tests
→ Agent reports results
```

### **Example 2: Automate Perplexity Research**

```
Cursor Agent Prompt:

"Automate Perplexity Space research:

1. Use Playwright to open:
   https://www.perplexity.ai/spaces/agentic-workflow-orchestration-0X7OltmBQ.2PNpcYOwuyAA

2. Search for: 'multi-agent coordination patterns'

3. Wait for answer to load

4. Extract answer text and citations

5. Save to: research/perplexity_{date}.md

6. Ingest to ChromaDB:
   python scripts/ingest_from_clipboard.py --collection perplexity_space

Execute all steps and confirm completion."

→ Cursor Agent does EVERYTHING
→ No manual intervention
→ Research automatically saved
```

### **Example 3: End-to-End Workflow**

```
Cursor Agent Prompt:

"Execute complete workflow:

RESEARCH PHASE:
1. Open Perplexity Space (Playwright)
2. Search 'FastAPI WebSocket authentication'
3. Extract answer + citations
4. Save to ChromaDB

GENERATION PHASE:
5. Run: python -m src.cli run examples/tiny_spec.yaml
6. Get run ID from output

TESTING PHASE:
7. Start generated API server
8. Open in Cursor Browser
9. Test all endpoints
10. Generate Playwright test suite

DOCUMENTATION PHASE:
11. Create summary in docs/
12. Update PROJECT_PROGRESS.md

Report all results and any errors encountered."

→ Cursor Agent executes ENTIRE pipeline autonomously!
```

---

## 🔗 Combined: MCP + Cursor Browser

### **Architecture:**

```
┌──────────────────────────────────────────┐
│         Cursor IDE (Hub)                 │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │      Agent Mode (AI Control)       │ │
│  └─────────────┬──────────────────────┘ │
│                ↓                         │
│  ┌────────────────────────────────────┐ │
│  │    Cursor Browser (Built-in)       │ │
│  │  • Test generated APIs             │ │
│  │  • Debug visually                  │ │
│  │  • Responsive testing              │ │
│  └────────────────────────────────────┘ │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  Playwright Automation             │ │
│  │  • E2E testing                     │ │
│  │  • Browser control                 │ │
│  │  • Screenshot/video                │ │
│  └────────────────────────────────────┘ │
└──────────────────┬───────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    ↓              ↓               ↓
┌─────────┐  ┌──────────┐  ┌────────────┐
│ Browser │  │  Chroma  │  │  Desktop   │
│ Control │  │   MCP    │  │ Commander  │
│   MCP   │  │          │  │    MCP     │
└─────────┘  └──────────┘  └────────────┘
```

**All controlled from Cursor IDE!**

---

## 📝 Practical Implementations

### **Script 1: Automated Perplexity Space Sync**

```python
# scripts/playwright_space_sync.py
"""
Automated Perplexity Space → ChromaDB sync using Playwright.

Can be triggered:
1. Manually: python scripts/playwright_space_sync.py
2. Via Cursor Agent: "Run Space sync automation"
3. Via cron: Daily automated sync
"""

from playwright.sync_api import sync_playwright
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.utils.vector_store import VectorMemory
from datetime import datetime

SPACE_URL = "https://www.perplexity.ai/spaces/agentic-workflow-orchestration-0X7OltmBQ.2PNpcYOwuyAA"

def sync_space_automated():
    """Fully automated Space sync"""
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print("🔗 Opening Perplexity Space...")
        page.goto(SPACE_URL)
        
        # Wait for page load
        page.wait_for_load_state("networkidle")
        
        # Get all threads
        print("📚 Finding threads...")
        threads = page.query_selector_all('.thread-item')  # Adjust selector
        
        print(f"Found {len(threads)} threads")
        
        memory = VectorMemory(collection_name="perplexity_space")
        synced = 0
        
        for i, thread in enumerate(threads, 1):
            try:
                # Click thread
                thread.click()
                time.sleep(2)
                
                # Get thread title
                title = page.text_content('.thread-title')  # Adjust selector
                
                # Get answer content
                answer = page.text_content('.answer-content')  # Adjust selector
                
                # Get citations
                citations = page.eval_on_selector_all(
                    '.citation-link',
                    'elements => elements.map(el => el.href)'
                )
                
                # Save to ChromaDB
                key = f"space_thread_{datetime.now().timestamp()}"
                memory.save(
                    key=key,
                    content=answer,
                    metadata={
                        "source": "perplexity_space",
                        "thread_title": title,
                        "citations": ",".join(citations),
                        "synced_at": datetime.now().isoformat(),
                        "space_url": SPACE_URL
                    }
                )
                
                synced += 1
                print(f"  ✅ Synced {i}/{len(threads)}: {title}")
                
                # Go back to list
                page.go_back()
                time.sleep(1)
                
            except Exception as e:
                print(f"  ⚠️  Error on thread {i}: {e}")
                continue
        
        browser.close()
        
        print("\n" + "="*70)
        print(f"✅ SYNC COMPLETE")
        print("="*70)
        print(f"Threads synced: {synced}/{len(threads)}")
        print(f"Collection: perplexity_space")
        print(f"Total documents: {memory.count()}")


if __name__ == "__main__":
    sync_space_automated()
```

### **Script 2: Test Generated API**

```python
# tests/e2e/test_generated_fastapi.py
"""
E2E tests for generated FastAPI using Playwright + Cursor Browser.

Run in Cursor:
- pytest tests/e2e/test_generated_fastapi.py
- Or: Cursor Agent → "Run E2E tests for generated API"
"""

import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture
def browser():
    """Setup browser for testing"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        yield page
        browser.close()

def test_fastapi_docs(browser):
    """Test that FastAPI docs are accessible"""
    browser.goto("http://localhost:8000/docs")
    
    # Verify Swagger UI loaded
    assert browser.is_visible('.swagger-ui')
    
    # Check endpoints exist
    endpoints = browser.text_content('body')
    assert '/notes' in endpoints

def test_post_note(browser):
    """Test POST /notes endpoint"""
    browser.goto("http://localhost:8000/docs")
    
    # Find POST /notes
    browser.click('text=POST /notes')
    
    # Click "Try it out"
    browser.click('button:has-text("Try it out")')
    
    # Fill request body
    browser.fill('textarea', '{"title": "Test", "content": "Test content"}')
    
    # Execute
    browser.click('button:has-text("Execute")')
    
    # Verify response
    response = browser.text_content('.response-body')
    assert '201' in response or 'created' in response.lower()

def test_get_notes(browser):
    """Test GET /notes endpoint"""
    browser.goto("http://localhost:8000/docs")
    
    # Find GET /notes
    browser.click('text=GET /notes')
    
    # Try it out
    browser.click('button:has-text("Try it out")')
    browser.click('button:has-text("Execute")')
    
    # Verify response
    response = browser.text_content('.response-body')
    assert '200' in response
```

---

## 🎯 MCP.json Configuration

### **Update Your MCP Config:**

```json
{
  "mcpServers": {
    "desktop-commander": {
      "command": "npx",
      "args": ["-y", "@wonderwhy-er/desktop-commander@latest"]
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
    },
    "supermemory-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://api.supermemory.ai/mcp"
      ]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    }
  }
}
```

---

## 🚀 Complete Cursor IDE Workflow

### **All-in-Cursor Automation:**

```
1. CURSOR CHAT (Agent Mode)
   Prompt: "Research FastAPI patterns in my Perplexity Space, 
            generate code, and test in Cursor Browser"
   
   ↓
   
2. CURSOR AGENT EXECUTES:
   - Opens browser via MCP
   - Navigates to your Space
   - Searches topic
   - Extracts research
   - Saves to ChromaDB
   - Runs orchestrator
   - Opens results in Cursor Browser
   - Runs Playwright tests
   
   ↓
   
3. CURSOR BROWSER SHOWS:
   - Generated FastAPI docs
   - Interactive testing
   - Live endpoint execution
   
   ↓
   
4. RESULTS:
   - Code generated
   - Tests passed
   - Documentation created
   - All in Cursor IDE!
```

---

## 💡 Advantages of Cursor Browser

**vs External Browser:**
- ✅ No context switching
- ✅ Integrated debugging
- ✅ Side-by-side code + browser
- ✅ Cursor Agent can control it
- ✅ Playwright tests run in same environment
- ✅ All tools in one IDE

**vs Manual Automation:**
- ✅ Cursor Agent executes autonomously
- ✅ Natural language → automated actions
- ✅ Error handling built-in
- ✅ No scripting required (just describe the task)

---

## 🎯 Quick Start

### **Enable Cursor Browser (1 min)**

```
1. Cmd+, (Settings)
2. Beta tab
3. Enable "Cursor Browser"
4. Restart Cursor
```

### **Test in Cursor Agent (2 min)**

```
1. Cmd+L (Chat)
2. Select "Agent" mode
3. Prompt: "Open Cursor Browser and navigate to 
           http://localhost:8000/docs"
4. Watch Agent execute!
```

### **Install Playwright (1 min)**

```bash
pip install playwright pytest-playwright
playwright install chromium
```

### **Test Automation (1 min)**

```bash
# Run automated Space sync
python scripts/playwright_space_sync.py
```

---

## 📊 Complete Integration Summary

**You now have:**

1. ✅ **Cursor Browser** - Built-in browser in IDE
2. ✅ **Cursor Agent** - AI autonomous execution
3. ✅ **Playwright** - Browser automation framework
4. ✅ **Browser Control MCP** - MCP for browser control
5. ✅ **Chroma MCP** - Vector memory MCP
6. ✅ **Desktop Commander MCP** - File operations MCP
7. ✅ **Your Perplexity Space** - Curated knowledge base

**This is a COMPLETE automation ecosystem inside Cursor IDE!**

No external tools needed - everything in one IDE:
- Research (Perplexity Space via browser automation)
- Knowledge (ChromaDB via MCP)
- Generation (unified_orchestrator)
- Testing (Cursor Browser + Playwright)
- Debugging (Integrated debugger)
- Version Control (Built-in git)

**Want me to create the Playwright automation scripts and enable browser control MCP in your config?** 🚀


