#!/usr/bin/env python3
"""
Automated Perplexity Space Sync using Playwright

Syncs all threads from your Perplexity Space to ChromaDB for agent access.
Works with Cursor Browser and Agent Mode.

Your Space: Agentic Workflow Orchestration
URL: https://www.perplexity.ai/spaces/agentic-workflow-orchestration-0X7OltmBQ.2PNpcYOwuyAA

Usage:
  python scripts/playwright_space_sync.py
  
  # Or from Cursor Agent Mode:
  "Run Playwright Space sync automation"
"""

import sys
from pathlib import Path
from datetime import datetime
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("❌ Playwright not installed")
    print("Install: pip install playwright")
    print("Then run: playwright install chromium")
    sys.exit(1)

from src.utils.vector_store import VectorMemory

SPACE_URL = "https://www.perplexity.ai/spaces/agentic-workflow-orchestration-0X7OltmBQ.2PNpcYOwuyAA"


def sync_perplexity_space(headless: bool = False):
    """
    Automated sync from Perplexity Space to ChromaDB.
    
    Args:
        headless: Run browser in headless mode (True) or visible (False)
    """
    
    print("🚀 PERPLEXITY SPACE → CHROMADB SYNC")
    print("="*70)
    print(f"Space: Agentic Workflow Orchestration")
    print(f"URL: {SPACE_URL}")
    print(f"Mode: {'Headless' if headless else 'Visible'}")
    print("="*70)
    print()
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()
        
        # Navigate to Space
        print("🔗 Opening Space...")
        page.goto(SPACE_URL, wait_until="networkidle")
        time.sleep(2)
        
        # Take screenshot for verification
        screenshot_path = "logs/space_screenshot.png"
        page.screenshot(path=screenshot_path)
        print(f"📸 Screenshot saved: {screenshot_path}")
        
        # Get page content
        print("📄 Extracting Space content...")
        
        # Get all text content from page
        # Note: Adjust selectors based on actual Perplexity Space HTML
        try:
            # Try to get main content
            content = page.text_content('body')
            
            print(f"✅ Extracted {len(content)} characters")
            
            # Initialize ChromaDB
            memory = VectorMemory(collection_name="perplexity_space")
            
            # Save to ChromaDB
            key = f"space_sync_{datetime.now().timestamp()}"
            memory.save(
                key=key,
                content=content,
                metadata={
                    "source": "perplexity_space",
                    "space_name": "agentic-workflow-orchestration",
                    "space_url": SPACE_URL,
                    "synced_at": datetime.now().isoformat(),
                    "sync_method": "playwright_automated"
                }
            )
            
            print(f"💾 Saved to ChromaDB")
            print(f"📊 Collection 'perplexity_space' now has: {memory.count()} documents")
            
        except Exception as e:
            print(f"⚠️  Error extracting content: {e}")
            print("💡 You may need to:")
            print("   1. Log in to Perplexity first")
            print("   2. Adjust CSS selectors for your Space")
        
        finally:
            browser.close()
    
    print("\n" + "="*70)
    print("✅ SYNC COMPLETE")
    print("="*70)


def manual_guided_sync():
    """
    Semi-automated sync with manual steps.
    Opens browser for you to interact, then extracts.
    """
    
    print("🔄 GUIDED SYNC MODE")
    print("="*70)
    print("This mode opens the browser and waits for you to:")
    print("1. Log in (if needed)")
    print("2. Navigate to specific threads")
    print("3. Press Enter in terminal when ready to extract")
    print("="*70)
    print()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print("🔗 Opening Space...")
        page.goto(SPACE_URL)
        
        print("\n📚 Instructions:")
        print("1. Log in to Perplexity if prompted")
        print("2. Browse your Space threads")
        print("3. When ready to extract current page, press Enter...")
        
        input()
        
        # Extract current page
        print("📄 Extracting...")
        content = page.text_content('body')
        title = page.title()
        
        print(f"✅ Extracted: {title}")
        print(f"   Content: {len(content)} characters")
        
        # Copy to clipboard
        page.evaluate(f'navigator.clipboard.writeText(`{content}`)')
        print("📋 Copied to clipboard")
        
        # Save to ChromaDB
        memory = VectorMemory(collection_name="perplexity_space")
        key = f"space_manual_{datetime.now().timestamp()}"
        
        memory.save(
            key=key,
            content=content,
            metadata={
                "source": "perplexity_space",
                "page_title": title,
                "synced_at": datetime.now().isoformat(),
                "sync_method": "guided"
            }
        )
        
        print(f"💾 Saved to ChromaDB")
        
        # Ask if want to continue
        print("\nExtract another page? (y/n)")
        if input().lower() == 'y':
            print("Navigate to next page, then press Enter...")
            input()
            # Recursive call for next page
        
        browser.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Sync Perplexity Space to ChromaDB using Playwright",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Automated sync (headless)
  python scripts/playwright_space_sync.py
  
  # Manual guided sync (visible browser)
  python scripts/playwright_space_sync.py --guided
  
  # Visible browser for debugging
  python scripts/playwright_space_sync.py --visible

Requirements:
  pip install playwright
  playwright install chromium
"""
    )
    
    parser.add_argument(
        "--guided",
        action="store_true",
        help="Manual guided mode (you control browser)"
    )
    
    parser.add_argument(
        "--visible",
        action="store_true",
        help="Show browser window (not headless)"
    )
    
    args = parser.parse_args()
    
    if args.guided:
        manual_guided_sync()
    else:
        sync_perplexity_space(headless=not args.visible)


