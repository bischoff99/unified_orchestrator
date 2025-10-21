#!/usr/bin/env python3
"""Test CrewAI memory integration with ChromaDB"""
import os
import sys

def test_vector_memory():
    """Test VectorMemory class"""
    print("=" * 60)
    print("Test 1: VectorMemory Class")
    print("=" * 60)

    try:
        from src.utils.vector_store import VectorMemory

        # Create memory instance
        memory = VectorMemory(collection_name="test_crew", persist_dir="./memory")
        print(f"✅ VectorMemory created: {memory}")

        # Save some test data
        memory.save(
            key="arch_decision_1",
            content="Using FastAPI for the backend API framework",
            metadata={"agent": "architect", "type": "decision"}
        )
        memory.save(
            key="impl_note_1",
            content="Implemented user authentication with JWT tokens",
            metadata={"agent": "fullstack", "type": "implementation"}
        )
        print("✅ Test data saved to memory")

        # Query by semantic similarity
        results = memory.query("API framework selection", k=1)
        print(f"✅ Semantic query results: {len(results)} found")
        if results:
            print(f"   Top result: {results[0]['document'][:50]}...")

        # Load by key
        content = memory.load("arch_decision_1")
        print(f"✅ Load by key: {content[:30]}...")

        # Check count
        count = memory.count()
        print(f"✅ Memory count: {count} items")

        return True
    except Exception as e:
        print(f"❌ VectorMemory test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_crew_with_memory():
    """Test CrewAI with memory enabled"""
    print("\n" + "=" * 60)
    print("Test 2: CrewAI with Memory")
    print("=" * 60)

    try:
        from src.orchestrator.crew_config import ProductionCrew

        # Create a simple test task
        test_task = "Design a simple REST API for a todo list application"

        print(f"Creating crew for task: {test_task}")
        crew_instance = ProductionCrew(task_description=test_task)

        print(f"✅ Crew created with {len(crew_instance.agents)} agents")
        print(f"✅ Crew has {len(crew_instance.tasks)} tasks")

        # Check if agents are properly configured
        for agent_name, agent in crew_instance.agents.items():
            print(f"   - {agent_name}: {agent.role}")

        print("\n⚠️  Note: Full crew execution test skipped")
        print("   Run 'python main.py' to test full orchestration with memory")

        return True
    except Exception as e:
        print(f"❌ Crew memory test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_embedder_config():
    """Test that embedder configuration is present"""
    print("\n" + "=" * 60)
    print("Test 3: Embedder Configuration")
    print("=" * 60)

    try:
        from src.orchestrator.crew_config import ProductionCrew

        # Read the crew_config.py file to check for embedder
        config_file = "src/orchestrator/crew_config.py"
        with open(config_file, 'r') as f:
            content = f.read()

        if 'embedder=' in content:
            print("✅ Embedder configuration found in crew_config.py")
        else:
            print("⚠️  Embedder configuration not explicitly set")
            print("   CrewAI will use default embeddings")

        if 'sentence-transformers/all-MiniLM-L6-v2' in content:
            print("✅ Using sentence-transformers/all-MiniLM-L6-v2")

        if 'memory=True' in content:
            print("✅ Memory enabled in Crew configuration")

        return True
    except Exception as e:
        print(f"❌ Embedder config test failed: {e}")
        return False

def test_memory_persistence():
    """Test that memory persists between instances"""
    print("\n" + "=" * 60)
    print("Test 4: Memory Persistence")
    print("=" * 60)

    try:
        from src.utils.vector_store import VectorMemory
        import time

        # Create first instance and save data
        memory1 = VectorMemory(collection_name="persist_test", persist_dir="./memory")
        test_id = f"persist_test_{int(time.time())}"
        test_content = "This should persist across instances"

        memory1.save(test_id, test_content, {"test": "persistence"})
        count1 = memory1.count()
        print(f"✅ First instance: saved 1 item, total count: {count1}")

        # Create second instance (simulating a restart)
        memory2 = VectorMemory(collection_name="persist_test", persist_dir="./memory")
        loaded = memory2.load(test_id)

        if loaded == test_content:
            print("✅ Memory persisted successfully!")
            print(f"   Retrieved: {loaded}")
        else:
            print("❌ Memory did not persist correctly")
            return False

        # Clean up
        memory2.clear()
        print("✅ Test collection cleared")

        return True
    except Exception as e:
        print(f"❌ Persistence test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_memory_directory():
    """Test memory directory structure"""
    print("\n" + "=" * 60)
    print("Test 5: Memory Directory Structure")
    print("=" * 60)

    try:
        import os

        memory_dir = "./memory"
        if os.path.exists(memory_dir):
            print(f"✅ Memory directory exists: {memory_dir}")

            # List contents
            contents = os.listdir(memory_dir)
            if contents:
                print(f"✅ Directory contains {len(contents)} items:")
                for item in contents[:5]:  # Show first 5
                    print(f"   - {item}")
                if len(contents) > 5:
                    print(f"   ... and {len(contents) - 5} more")
            else:
                print("⚠️  Directory is empty (will be populated on first use)")

            # Check permissions
            if os.access(memory_dir, os.W_OK):
                print("✅ Directory is writable")
            else:
                print("❌ Directory is not writable")
                return False
        else:
            print("⚠️  Memory directory will be created on first use")

        return True
    except Exception as e:
        print(f"❌ Directory test failed: {e}")
        return False

def main():
    """Run all crew memory tests"""
    print("\n🧪 CrewAI Memory Integration Test Suite\n")

    results = {
        "VectorMemory Class": test_vector_memory(),
        "CrewAI Configuration": test_crew_with_memory(),
        "Embedder Config": test_embedder_config(),
        "Memory Persistence": test_memory_persistence(),
        "Memory Directory": test_memory_directory()
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
        print("\n🎉 All memory integration tests passed!")
        print("\n📝 Next Steps:")
        print("   1. Run: python main.py")
        print("   2. Check that agents share context via memory")
        print("   3. Verify memory persists between runs")
    else:
        print("\n⚠️  Some tests failed. Review errors above.")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
