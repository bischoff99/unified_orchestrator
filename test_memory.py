#!/usr/bin/env python3
"""Test ChromaDB memory functionality for CrewAI"""
import os
import sys

def test_chromadb_basic():
    """Test basic ChromaDB functionality"""
    print("=" * 60)
    print("Test 1: ChromaDB Basic Functionality")
    print("=" * 60)

    try:
        import chromadb
        print(f"✅ ChromaDB {chromadb.__version__} imported")

        # Test in-memory client
        client = chromadb.Client()
        collection = client.create_collection(name="test_basic")
        print("✅ In-memory client created")

        # Test add/query
        collection.add(
            documents=["Test document"],
            ids=["test_1"]
        )
        print("✅ Document added to collection")

        return True
    except Exception as e:
        print(f"❌ ChromaDB basic test failed: {e}")
        return False

def test_persistent_storage():
    """Test ChromaDB persistent storage"""
    print("\n" + "=" * 60)
    print("Test 2: ChromaDB Persistent Storage")
    print("=" * 60)

    try:
        import chromadb
        from chromadb.config import Settings

        # Create persistent client
        persist_dir = "./memory"
        os.makedirs(persist_dir, exist_ok=True)

        client = chromadb.PersistentClient(path=persist_dir)
        print(f"✅ Persistent client created (dir: {persist_dir})")

        # Get or create collection
        collection = client.get_or_create_collection(name="test_persist")
        print("✅ Persistent collection created")

        # Add test data
        collection.upsert(
            documents=["Agent memory test"],
            metadatas=[{"source": "test", "type": "memory"}],
            ids=["persist_1"]
        )
        print("✅ Data persisted to collection")

        # Query
        results = collection.get(ids=["persist_1"])
        print(f"✅ Data retrieved: {results['documents']}")

        return True
    except Exception as e:
        print(f"❌ Persistent storage test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sentence_transformers():
    """Test sentence-transformers for embeddings"""
    print("\n" + "=" * 60)
    print("Test 3: Sentence Transformers (Embeddings)")
    print("=" * 60)

    try:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        print("✅ Sentence transformer model loaded")

        # Test embedding
        embedding = model.encode("Test sentence")
        print(f"✅ Embedding generated (dim: {len(embedding)})")

        return True
    except ImportError:
        print("⚠️  sentence-transformers not installed")
        print("   Install with: pip install sentence-transformers")
        return False
    except Exception as e:
        print(f"❌ Sentence transformers test failed: {e}")
        return False

def test_crewai_memory_config():
    """Test CrewAI memory configuration"""
    print("\n" + "=" * 60)
    print("Test 4: CrewAI Memory Configuration")
    print("=" * 60)

    try:
        from src.orchestrator.crew_config import ProductionCrew

        # Check if crew can be instantiated
        crew = ProductionCrew(task_description="Test task")
        print("✅ ProductionCrew instantiated")

        # Check agents
        print(f"✅ Agents created: {len(crew.agents)}")
        print(f"   - {', '.join(crew.agents.keys())}")

        # Check tasks
        print(f"✅ Tasks created: {len(crew.tasks)}")

        return True
    except Exception as e:
        print(f"❌ CrewAI config test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_env_config():
    """Test environment configuration"""
    print("\n" + "=" * 60)
    print("Test 5: Environment Configuration")
    print("=" * 60)

    env_vars = [
        "MODEL_BACKEND",
        "MODEL_NAME",
        "HF_TOKEN",
        "HF_EMBEDDING_MODEL",
        "MEMORY_TYPE"
    ]

    missing = []
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Don't print full token
            if "TOKEN" in var or "KEY" in var:
                display = f"{value[:10]}..." if len(value) > 10 else "***"
            else:
                display = value
            print(f"✅ {var}={display}")
        else:
            print(f"⚠️  {var} not set")
            missing.append(var)

    if "HF_TOKEN" in missing:
        print("\nNote: HF_TOKEN is optional for local embeddings")

    return len(missing) == 0 or (len(missing) == 1 and "HF_TOKEN" in missing)

def main():
    """Run all tests"""
    print("\n🧪 ChromaDB Memory Diagnostic Suite\n")

    results = {
        "ChromaDB Basic": test_chromadb_basic(),
        "Persistent Storage": test_persistent_storage(),
        "Sentence Transformers": test_sentence_transformers(),
        "CrewAI Config": test_crewai_memory_config(),
        "Environment": test_env_config()
    }

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! ChromaDB memory is working correctly.")
    else:
        print("\n⚠️  Some tests failed. See recommendations below:")

        if not results["Sentence Transformers"]:
            print("  - Install: pip install sentence-transformers")

        if not results["Environment"]:
            print("  - Create .env file from .env.example")
            print("  - Add HF_TOKEN (optional for local embeddings)")

        if not results["CrewAI Config"]:
            print("  - Check src/orchestrator/crew_config.py")
            print("  - Ensure all dependencies are installed")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
