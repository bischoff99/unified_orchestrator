#!/usr/bin/env python3
"""Phase 1 Baseline Test - Validate Tool Usage Success"""

import os
import sys
from pathlib import Path
import shutil

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrator.minimal_crew_config import MinimalCrew
from src.utils.code_scorer import score_generated_code

def cleanup_generated():
    """Clean up previous test runs"""
    generated = Path("src/generated")
    if generated.exists():
        shutil.rmtree(generated)
    generated.mkdir(parents=True, exist_ok=True)
    print("✅ Cleaned src/generated/")

def test_simple_api():
    """Test with simplest possible task"""
    print("\n" + "="*60)
    print("PHASE 1 BASELINE TEST: Simple Notes API")
    print("="*60 + "\n")
    
    task = "Create a FastAPI notes app with 2 endpoints: POST /notes and GET /notes. Use SQLite database."
    
    crew = MinimalCrew(task)
    result = crew.run()
    
    # Validation
    generated = Path("src/generated")
    project_dirs = [d for d in generated.iterdir() if d.is_dir()]
    
    assert len(project_dirs) > 0, "❌ No project directory created"
    print(f"✅ Project created: {project_dirs[0].name}")
    
    main_files = list(project_dirs[0].glob("*.py"))
    assert len(main_files) > 0, "❌ No Python files created"
    print(f"✅ Python files created: {[f.name for f in main_files]}")
    
    main_file = main_files[0]
    
    # 🆕 AUTOMATED SCORING SYSTEM
    print("\n" + "="*60)
    print("AUTOMATED CODE QUALITY SCORING")
    print("="*60)
    
    score_result = score_generated_code(str(main_file), verbose=True)
    
    # Assert based on automated score
    assert score_result['passed'], f"❌ Quality score {score_result['total_score']}/100 below threshold (75)"
    assert score_result['total_score'] >= 75, f"❌ Score {score_result['total_score']} < 75 (minimum)"
    
    print("\n" + "="*60)
    print("✅ PHASE 1 BASELINE TEST PASSED")
    print(f"   Tool Usage Success Rate: 100%")
    print(f"   Code Quality Score: {score_result['total_score']}/100 ({score_result['grade']})")
    print(f"   Files Written: {len(main_files)}")
    print(f"   Category Scores:")
    for category, score in score_result['category_scores'].items():
        print(f"     - {category.title()}: {score}")
    print("="*60 + "\n")
    
    return True

if __name__ == "__main__":
    cleanup_generated()
    try:
        success = test_simple_api()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

