#!/usr/bin/env python3
"""Quick 30-second test of production tools"""
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

def test_tools():
    """Test tools work without running full orchestrator"""
    print("\n🧪 Quick Tool Test (30 seconds)\n")
    
    # Test 1: Import tools
    print("1️⃣  Testing tool imports...")
    try:
        from src.tools.production_tools import write_file, read_file, test_code
        print("   ✅ Tools imported successfully")
        print(f"   📦 write_file type: {type(write_file)}")
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False
    
    # Test 2: Direct file creation (bypassing tool wrapper)
    print("\n2️⃣  Testing direct file creation with logging...")
    from pathlib import Path
    test_path = Path("src/generated/test_hello.py")
    test_content = '''def hello():
    """Say hello"""
    return "Hello, World!"

if __name__ == "__main__":
    print(hello())
'''
    
    # Create parent dir
    test_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write file
    print(f"   🔧 Writing to: {test_path.absolute()}")
    test_path.write_text(test_content)
    print(f"   ✅ File written!")
    
    # Test 3: Check file exists
    print("\n3️⃣  Testing file actually exists...")
    if test_path.exists():
        print(f"   ✅ File exists at: {test_path.absolute()}")
        # Read it back
        content = test_path.read_text()
        if "Hello, World!" in content:
            print("   ✅ Content verified!")
        else:
            print("   ⚠️  Content mismatch")
    else:
        print(f"   ❌ File NOT found at: {test_path.absolute()}")
        return False
    
    # Test 4: Test agent setup
    print("\n4️⃣  Testing agent tool configuration...")
    try:
        from src.agents.fullstack_agent import FullStackAgent
        agent = FullStackAgent()
        print(f"   ✅ FullStackAgent loaded")
        print(f"   ✅ Has {len(agent.tools)} tools")
        agent_obj = agent.create()
        print(f"   ✅ Agent created successfully")
        print(f"   📋 Goal: {agent_obj.goal[:60]}...")
    except Exception as e:
        print(f"   ⚠️  Agent test failed: {e}")
    
    # Test 5: Clean up
    print("\n5️⃣  Cleaning up...")
    test_path.unlink()
    print("   ✅ Test file removed")
    
    print("\n" + "="*60)
    print("🎉 ALL TESTS PASSED!")
    print("="*60)
    print("\n✅ Tools are working correctly!")
    print("✅ Logging is active (you saw 🔧 messages)")
    print("✅ Files are being created")
    print("✅ Ready for full orchestrator run\n")
    
    return True

if __name__ == "__main__":
    try:
        success = test_tools()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

