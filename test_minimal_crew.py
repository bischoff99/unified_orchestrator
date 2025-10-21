#!/usr/bin/env python3
"""Quick test to validate minimal crew configuration"""

def test_imports():
    """Test that minimal crew can be imported"""
    try:
        from src.orchestrator.minimal_crew_config import MinimalCrew
        print("✅ MinimalCrew import successful")
        return True
    except Exception as e:
        print(f"❌ MinimalCrew import failed: {e}")
        return False

def test_initialization():
    """Test that minimal crew can be initialized"""
    try:
        from src.orchestrator.minimal_crew_config import MinimalCrew
        
        crew = MinimalCrew("Test task")
        
        # Check agents
        assert len(crew.agents) == 4, f"Expected 4 agents, got {len(crew.agents)}"
        assert 'architect' in crew.agents
        assert 'builder' in crew.agents
        assert 'qa' in crew.agents
        assert 'docs' in crew.agents
        
        # Check tasks
        assert len(crew.tasks) == 4, f"Expected 4 tasks, got {len(crew.tasks)}"
        
        print("✅ MinimalCrew initialization successful")
        print(f"   Agents: {list(crew.agents.keys())}")
        print(f"   Tasks: {len(crew.tasks)}")
        return True
    except Exception as e:
        print(f"❌ MinimalCrew initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agent_tools():
    """Test that agents have correct tools"""
    try:
        from src.orchestrator.minimal_crew_config import MinimalCrew
        
        crew = MinimalCrew("Test task")
        
        # Check builder has write tools
        builder_tools = [tool.name for tool in crew.agents['builder'].tools]
        assert 'write_file' in builder_tools, "Builder missing write_file"
        
        # Check QA has test tools
        qa_tools = [tool.name for tool in crew.agents['qa'].tools]
        assert 'test_code' in qa_tools, "QA missing test_code"
        
        # Check docs has write tools
        docs_tools = [tool.name for tool in crew.agents['docs'].tools]
        assert 'write_file' in docs_tools, "Docs missing write_file"
        
        print("✅ Agent tools validated")
        print(f"   Builder tools: {builder_tools}")
        print(f"   QA tools: {qa_tools}")
        print(f"   Docs tools: {docs_tools}")
        return True
    except Exception as e:
        print(f"❌ Agent tools validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_main_integration():
    """Test that main.py can use MinimalCrew"""
    try:
        import sys
        from io import StringIO
        
        # Capture help output
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        try:
            import main
            # This would normally parse args, but we just want to check imports work
        except SystemExit:
            pass  # argparse exits on --help
        
        sys.stdout = old_stdout
        
        print("✅ main.py integration successful")
        return True
    except Exception as e:
        sys.stdout = old_stdout
        print(f"❌ main.py integration failed: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("MINIMAL CREW VALIDATION")
    print("="*60 + "\n")
    
    tests = [
        ("Import Test", test_imports),
        ("Initialization Test", test_initialization),
        ("Agent Tools Test", test_agent_tools),
        ("Main.py Integration", test_main_integration),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\nRunning: {name}")
        print("-" * 60)
        success = test_func()
        results.append((name, success))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
    
    print("\n" + "="*60)
    print(f"Results: {passed}/{total} tests passed")
    print("="*60 + "\n")
    
    if passed == total:
        print("🎉 All tests passed! Minimal crew is ready to use.")
        print("\nTry it out:")
        print('  python main.py "Build a simple REST API" --minimal')
        return 0
    else:
        print("⚠️  Some tests failed. Check errors above.")
        return 1

if __name__ == "__main__":
    exit(main())

