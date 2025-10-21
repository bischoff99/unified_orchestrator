#!/usr/bin/env python3
"""Compare ChromaDB vs FAISS performance for vector search"""
import time
import sys
from typing import List

def test_chromadb(num_docs: int = 1000):
    """Test ChromaDB performance"""
    print(f"\n{'='*60}")
    print(f"ChromaDB Test ({num_docs} documents)")
    print('='*60)

    try:
        from src.utils.vector_store import VectorMemory

        # Create test documents
        docs = [f"Test document {i} about AI and machine learning" for i in range(num_docs)]
        metadata = [{"id": i, "type": "test"} for i in range(num_docs)]

        # Create memory
        memory = VectorMemory(collection_name="chromadb_test")
        memory.clear()

        # Test add
        start = time.time()
        for i, (doc, meta) in enumerate(zip(docs, metadata)):
            memory.save(f"doc_{i}", doc, meta)
        add_time = time.time() - start

        print(f"✅ Add time: {add_time:.3f}s ({num_docs/add_time:.0f} docs/sec)")

        # Test search
        start = time.time()
        results = memory.query("machine learning AI", k=5)
        search_time = time.time() - start

        print(f"✅ Search time: {search_time*1000:.2f}ms")
        print(f"✅ Results: {len(results)}")

        # Cleanup
        memory.clear()

        return {
            'add_time': add_time,
            'search_time': search_time,
            'docs_per_sec': num_docs / add_time
        }

    except Exception as e:
        print(f"❌ ChromaDB test failed: {e}")
        return None


def test_faiss(num_docs: int = 1000):
    """Test FAISS performance"""
    print(f"\n{'='*60}")
    print(f"FAISS Test ({num_docs} documents)")
    print('='*60)

    try:
        from src.utils.faiss_store import FAISSVectorStore
        import shutil
        import os

        # Create test documents
        docs = [f"Test document {i} about AI and machine learning" for i in range(num_docs)]
        metadata = [{"id": i, "type": "test"} for i in range(num_docs)]

        # Create store
        store = FAISSVectorStore(index_path="./faiss_benchmark")

        # Test add
        start = time.time()
        store.add(docs, metadata)
        add_time = time.time() - start

        print(f"✅ Add time: {add_time:.3f}s ({num_docs/add_time:.0f} docs/sec)")

        # Test search
        start = time.time()
        results = store.search("machine learning AI", k=5)
        search_time = time.time() - start

        print(f"✅ Search time: {search_time*1000:.2f}ms")
        print(f"✅ Results: {len(results)}")

        # Cleanup
        if os.path.exists("./faiss_benchmark"):
            shutil.rmtree("./faiss_benchmark")

        return {
            'add_time': add_time,
            'search_time': search_time,
            'docs_per_sec': num_docs / add_time
        }

    except Exception as e:
        print(f"❌ FAISS test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def compare_backends():
    """Compare ChromaDB and FAISS performance"""
    print("\n🏁 Vector Store Performance Benchmark")
    print("="*60)

    test_sizes = [100, 1000, 5000]

    for size in test_sizes:
        print(f"\n\n📊 Testing with {size} documents...")

        chroma_result = test_chromadb(size)
        faiss_result = test_faiss(size)

        if chroma_result and faiss_result:
            print(f"\n{'='*60}")
            print(f"Comparison ({size} docs)")
            print('='*60)

            add_speedup = chroma_result['add_time'] / faiss_result['add_time']
            search_speedup = chroma_result['search_time'] / faiss_result['search_time']

            print(f"\n⚡ Add Speed:")
            print(f"   ChromaDB: {chroma_result['add_time']:.3f}s")
            print(f"   FAISS:    {faiss_result['add_time']:.3f}s")
            print(f"   Speedup:  {add_speedup:.1f}x faster")

            print(f"\n🔍 Search Speed:")
            print(f"   ChromaDB: {chroma_result['search_time']*1000:.2f}ms")
            print(f"   FAISS:    {faiss_result['search_time']*1000:.2f}ms")
            print(f"   Speedup:  {search_speedup:.1f}x faster")

            # Recommendation
            print(f"\n💡 Recommendation for {size} documents:")
            if size < 1000:
                print("   ✅ Use ChromaDB - simpler, adequate performance")
            elif size < 5000:
                print("   ⚖️  Either works - ChromaDB for simplicity, FAISS for speed")
            else:
                print("   ✅ Use FAISS - significantly faster at this scale")


def main():
    """Run benchmark"""
    print("Starting vector store benchmark...")
    print("This will test ChromaDB and FAISS with different dataset sizes\n")

    try:
        compare_backends()

        print("\n\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print("""
✅ Current Setup: ChromaDB (optimal for CrewAI agents)
🚀 Alternative: FAISS (use for >10K vectors)

When to use each:

ChromaDB (Current):
- ✅ <10,000 vectors
- ✅ Need metadata filtering
- ✅ CrewAI native integration
- ✅ Simpler code
- ✅ Built-in persistence

FAISS (Optional):
- 🚀 >10,000 vectors
- 🚀 Speed critical (milliseconds)
- 🚀 Custom semantic search
- 🚀 Research/retrieval agents

Recommendation: Keep using ChromaDB for agent memory!
        """)

    except KeyboardInterrupt:
        print("\n\nBenchmark cancelled by user")
        sys.exit(0)


if __name__ == "__main__":
    main()
