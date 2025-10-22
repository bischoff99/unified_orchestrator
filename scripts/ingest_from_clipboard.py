#!/usr/bin/env python3
"""
Ingest content from clipboard into ChromaDB

Useful for:
- Copying research from Perplexity Max
- Saving Claude.ai conversations
- Ingesting documentation from web
- Storing code snippets

Usage:
  # Copy content to clipboard, then run:
  python scripts/ingest_from_clipboard.py
  
  # Specify collection:
  python scripts/ingest_from_clipboard.py --collection research
  
  # Add metadata:
  python scripts/ingest_from_clipboard.py --metadata "source=perplexity,topic=FastAPI"
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import pyperclip
except ImportError:
    print("❌ pyperclip not installed")
    print("Install: pip install pyperclip")
    sys.exit(1)

from src.utils.vector_store import VectorMemory


def ingest_clipboard(collection_name: str = "clipboard", metadata: dict = None):
    """
    Ingest clipboard content into ChromaDB.
    
    Args:
        collection_name: ChromaDB collection
        metadata: Additional metadata dict
    """
    # Get clipboard content
    print("📋 Reading clipboard...")
    content = pyperclip.paste()
    
    if not content or not content.strip():
        print("❌ Clipboard is empty")
        return False
    
    print(f"✅ Clipboard content: {len(content)} characters")
    print(f"📝 Preview: {content[:200]}...")
    print()
    
    # Initialize vector memory
    print(f"💾 Storing in collection: {collection_name}")
    memory = VectorMemory(collection_name=collection_name)
    
    # Generate unique key
    timestamp = datetime.now().isoformat()
    key = f"clipboard_{timestamp}"
    
    # Prepare metadata
    full_metadata = {
        "source": "clipboard",
        "ingested_at": timestamp,
        "char_count": len(content),
        "type": "manual_ingest"
    }
    
    if metadata:
        full_metadata.update(metadata)
    
    # Store in ChromaDB
    memory.save(key=key, content=content, metadata=full_metadata)
    
    print(f"✅ Stored with key: {key}")
    print(f"📊 Total documents in collection: {memory.count()}")
    print()
    
    # Test retrieval
    print("🔍 Testing semantic search...")
    results = memory.query(content[:100], k=3)
    print(f"✅ Found {len(results)} related documents")
    
    return True


def parse_metadata_string(metadata_str: str) -> dict:
    """
    Parse metadata string into dict.
    
    Format: "key1=value1,key2=value2"
    Example: "source=perplexity,topic=FastAPI,priority=high"
    """
    metadata = {}
    if metadata_str:
        for pair in metadata_str.split(","):
            if "=" in pair:
                key, value = pair.split("=", 1)
                metadata[key.strip()] = value.strip()
    return metadata


def main():
    """CLI interface"""
    parser = argparse.ArgumentParser(
        description="Ingest clipboard content into ChromaDB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage (default collection: 'clipboard')
  python scripts/ingest_from_clipboard.py
  
  # Specify collection
  python scripts/ingest_from_clipboard.py --collection research
  
  # Add metadata
  python scripts/ingest_from_clipboard.py --collection research --metadata "source=perplexity,topic=FastAPI"
  
  # Preview only (don't save)
  python scripts/ingest_from_clipboard.py --preview

Workflow with Perplexity Max:
  1. Research topic in Perplexity Max (https://www.perplexity.ai)
  2. Copy comprehensive answer with citations (Cmd+A, Cmd+C)
  3. Run: python scripts/ingest_from_clipboard.py --collection research
  4. Content is now searchable by agents via vector memory
"""
    )
    
    parser.add_argument(
        "--collection",
        "-c",
        default="clipboard",
        help="ChromaDB collection name (default: clipboard)"
    )
    
    parser.add_argument(
        "--metadata",
        "-m",
        help='Additional metadata as "key=value,key=value"'
    )
    
    parser.add_argument(
        "--preview",
        "-p",
        action="store_true",
        help="Preview clipboard content without saving"
    )
    
    args = parser.parse_args()
    
    # Parse metadata
    metadata = parse_metadata_string(args.metadata) if args.metadata else {}
    
    # Preview mode
    if args.preview:
        print("🔍 PREVIEW MODE (not saving)")
        print("=" * 60)
        content = pyperclip.paste()
        if content:
            print(f"Length: {len(content)} characters")
            print(f"Lines: {len(content.splitlines())}")
            print()
            print("Content preview:")
            print("-" * 60)
            print(content[:500])
            if len(content) > 500:
                print("...")
                print(f"({len(content) - 500} more characters)")
            print("-" * 60)
        else:
            print("❌ Clipboard is empty")
        return
    
    # Ingest
    success = ingest_clipboard(args.collection, metadata)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

