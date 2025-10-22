"""Golden Tests - Compare Generated Code Against Fixtures

Tests that generated code matches expected templates byte-for-byte
(or semantically for structure/imports).
"""

import pytest
from pathlib import Path
from src.utils.code_scorer import CodeQualityScorer


class TestGoldenFixtures:
    """Test generated code against golden fixtures"""
    
    def test_fastapi_notes_structure(self):
        """Generated FastAPI notes app has expected structure"""
        golden_path = Path("tests/golden/fastapi_notes_main.py")
        assert golden_path.exists(), "Golden fixture missing"
        
        # Score the golden fixture
        scorer = CodeQualityScorer(str(golden_path))
        result = scorer.score()
        
        # Golden fixture should score highly
        assert result['total_score'] >= 90, f"Golden fixture scores {result['total_score']}/100"
        assert result['category_scores']['imports'] >= 18
        assert result['category_scores']['endpoints'] >= 12  # At least POST and GET
        assert result['category_scores']['pydantic'] >= 12  # Has models
        assert result['category_scores']['runnability'] >= 12  # Can run
    
    def test_golden_has_all_critical_elements(self):
        """Golden fixture contains all critical FastAPI elements"""
        golden_path = Path("tests/golden/fastapi_notes_main.py")
        code = golden_path.read_text()
        
        # Critical imports
        assert "from fastapi import FastAPI" in code
        assert "from sqlalchemy import" in code
        assert "from pydantic import BaseModel" in code
        
        # Database setup
        assert "create_engine" in code
        assert "sessionmaker" in code
        assert "declarative_base" in code
        assert "Base.metadata.create_all" in code  # Critical!
        
        # Models
        assert "class Note(Base):" in code
        assert "class NoteCreate(BaseModel):" in code
        assert "class NoteResponse(BaseModel):" in code
        
        # Endpoints
        assert "@app.post" in code
        assert "@app.get" in code
        
        # Database dependency
        assert "def get_db():" in code
        assert "yield" in code
        
        # Error handling
        assert "try:" in code
        assert "except" in code
        assert "HTTPException" in code
    
    def test_golden_imports_completeness(self):
        """Golden fixture has complete imports (no missing deps)"""
        golden_path = Path("tests/golden/fastapi_notes_main.py")
        code = golden_path.read_text()
        
        required_imports = [
            "FastAPI",
            "Depends",
            "HTTPException",
            "status",
            "Column",
            "Integer",
            "String",
            "create_engine",
            "Session",
            "sessionmaker",
            "declarative_base",
            "BaseModel",
        ]
        
        for imp in required_imports:
            assert imp in code, f"Missing import: {imp}"
    
    @pytest.mark.skipif(
        not Path("src/generated/notes_api/main.py").exists(),
        reason="No generated code to compare"
    )
    def test_compare_generated_to_golden(self):
        """Compare generated code structure to golden fixture"""
        golden_scorer = CodeQualityScorer("tests/golden/fastapi_notes_main.py")
        golden_result = golden_scorer.score()
        
        generated_scorer = CodeQualityScorer("src/generated/notes_api/main.py")
        generated_result = generated_scorer.score()
        
        # Generated should be within 15 points of golden
        score_diff = abs(golden_result['total_score'] - generated_result['total_score'])
        assert score_diff <= 15, (
            f"Generated score ({generated_result['total_score']}) differs too much "
            f"from golden ({golden_result['total_score']})"
        )
        
        # Generated should have similar category scores
        for category in ['imports', 'pydantic', 'endpoints']:
            gen_score = generated_result['category_scores'][category]
            gold_score = golden_result['category_scores'][category]
            assert gen_score >= gold_score * 0.7, (
                f"Category {category}: generated ({gen_score}) too far from golden ({gold_score})"
            )


class TestGoldenFunctionality:
    """Test that golden fixture actually works"""
    
    def test_golden_syntax_valid(self):
        """Golden fixture has valid Python syntax"""
        golden_path = Path("tests/golden/fastapi_notes_main.py")
        code = golden_path.read_text()
        
        # Should compile without errors
        import ast
        try:
            ast.parse(code)
        except SyntaxError as e:
            pytest.fail(f"Golden fixture has syntax error: {e}")
    
    def test_golden_imports_work(self):
        """Golden fixture imports can be resolved"""
        import sys
        from pathlib import Path
        
        golden_dir = Path("tests/golden")
        sys.path.insert(0, str(golden_dir))
        
        try:
            # This will fail if imports are broken
            import fastapi_notes_main
            
            # Check key objects exist
            assert hasattr(fastapi_notes_main, 'app')
            assert hasattr(fastapi_notes_main, 'Note')
            assert hasattr(fastapi_notes_main, 'NoteCreate')
            assert hasattr(fastapi_notes_main, 'create_note')
            assert hasattr(fastapi_notes_main, 'get_notes')
            
        finally:
            sys.path.pop(0)
            if 'fastapi_notes_main' in sys.modules:
                del sys.modules['fastapi_notes_main']

