"""Code Validation Utility for Generated Code Quality Assessment"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Any


class CodeValidator:
    """Validates generated code for completeness and quality."""
    
    REQUIRED_FASTAPI_IMPORTS = [
        "FastAPI", "Depends", "HTTPException", "status"
    ]
    
    REQUIRED_SQLALCHEMY_IMPORTS = [
        "Column", "Integer", "String", "DateTime", "create_engine"
    ]
    
    REQUIRED_PYDANTIC_IMPORTS = ["BaseModel"]
    
    REQUIRED_OTHER_IMPORTS = ["datetime", "Session", "List"]
    
    def __init__(self, file_path: str):
        """Initialize validator with file path."""
        self.file_path = Path(file_path)
        self.content = ""
        self.issues = []
        self.score = 0
        
        if self.file_path.exists():
            self.content = self.file_path.read_text()
    
    def check_imports(self) -> Dict[str, Any]:
        """Check if all required imports are present."""
        missing_imports = []
        
        all_required = (
            self.REQUIRED_FASTAPI_IMPORTS +
            self.REQUIRED_SQLALCHEMY_IMPORTS +
            self.REQUIRED_PYDANTIC_IMPORTS +
            self.REQUIRED_OTHER_IMPORTS
        )
        
        for required_import in all_required:
            if required_import not in self.content:
                missing_imports.append(required_import)
        
        score = max(0, 20 - (len(missing_imports) * 2))
        
        return {
            "score": score,
            "max_score": 20,
            "missing": missing_imports,
            "passed": len(missing_imports) == 0
        }
    
    def check_endpoints(self) -> Dict[str, Any]:
        """Check if API endpoints are implemented."""
        decorators = {
            "POST": r"@app\.post\(",
            "GET": r"@app\.get\(",
            "PUT": r"@app\.put\(",
            "DELETE": r"@app\.delete\(",
        }
        
        found_endpoints = {}
        for method, pattern in decorators.items():
            matches = re.findall(pattern, self.content)
            found_endpoints[method] = len(matches)
        
        total_endpoints = sum(found_endpoints.values())
        expected_endpoints = 5  # POST, GET list, GET by ID, PUT, DELETE
        
        score = min(30, (total_endpoints / expected_endpoints) * 30)
        
        return {
            "score": int(score),
            "max_score": 30,
            "found": found_endpoints,
            "total": total_endpoints,
            "expected": expected_endpoints,
            "passed": total_endpoints >= expected_endpoints
        }
    
    def check_implementations(self) -> Dict[str, Any]:
        """Check if functions have actual implementations (not just pass)."""
        # Find function definitions
        func_pattern = r"def\s+\w+\([^)]*\):"
        functions = re.findall(func_pattern, self.content)
        
        # Check for pass statements (indicates incomplete)
        pass_statements = self.content.count("    pass")
        
        # Check for actual logic indicators
        has_db_operations = any(op in self.content for op in ["db.add(", "db.commit(", "db.query("])
        has_error_handling = "try:" in self.content and "except" in self.content
        has_return_statements = self.content.count("return ") > 2
        
        score = 0
        if has_db_operations:
            score += 10
        if has_error_handling:
            score += 5
        if has_return_statements:
            score += 5
        if pass_statements == 0:
            score += 10
        
        return {
            "score": min(score, 30),
            "max_score": 30,
            "function_count": len(functions),
            "has_db_operations": has_db_operations,
            "has_error_handling": has_error_handling,
            "pass_statements": pass_statements,
            "passed": score >= 20
        }
    
    def check_syntax(self) -> Dict[str, Any]:
        """Validate Python syntax using AST parser."""
        try:
            ast.parse(self.content)
            return {
                "score": 15,
                "max_score": 15,
                "errors": [],
                "passed": True
            }
        except SyntaxError as e:
            return {
                "score": 0,
                "max_score": 15,
                "errors": [str(e)],
                "passed": False
            }
    
    def check_code_structure(self) -> Dict[str, Any]:
        """Check for proper code organization."""
        checks = {
            "has_database_setup": "create_engine" in self.content,
            "has_models": "class " in self.content and "(Base)" in self.content,
            "has_pydantic_schemas": "class " in self.content and "(BaseModel)" in self.content,
            "has_dependency_injection": "def get_db" in self.content and "yield" in self.content,
            "has_table_creation": "Base.metadata.create_all" in self.content,
        }
        
        passed_checks = sum(1 for passed in checks.values() if passed)
        score = (passed_checks / len(checks)) * 15
        
        return {
            "score": int(score),
            "max_score": 15,
            "checks": checks,
            "passed": passed_checks >= 4
        }
    
    def validate(self) -> Dict[str, Any]:
        """Run all validation checks and return comprehensive report."""
        if not self.file_path.exists():
            return {
                "file": str(self.file_path),
                "exists": False,
                "total_score": 0,
                "max_score": 110,
                "grade": "F",
                "passed": False,
                "error": "File does not exist"
            }
        
        results = {
            "imports": self.check_imports(),
            "endpoints": self.check_endpoints(),
            "implementations": self.check_implementations(),
            "syntax": self.check_syntax(),
            "structure": self.check_code_structure(),
        }
        
        total_score = sum(r["score"] for r in results.values())
        max_score = sum(r["max_score"] for r in results.values())
        
        grade = self._get_grade(total_score)
        
        return {
            "file": str(self.file_path),
            "exists": True,
            "results": results,
            "total_score": total_score,
            "max_score": max_score,
            "percentage": (total_score / max_score) * 100 if max_score > 0 else 0,
            "grade": grade,
            "passed": total_score >= 70,  # 70% threshold for passing
        }
    
    def _get_grade(self, score: int) -> str:
        """Convert score to letter grade."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"


def validate_generated_code(file_path: str) -> Dict[str, Any]:
    """Convenience function to validate a generated code file."""
    validator = CodeValidator(file_path)
    return validator.validate()


if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) < 2:
        print("Usage: python code_validator.py <path_to_main.py>")
        sys.exit(1)
    
    result = validate_generated_code(sys.argv[1])
    print(json.dumps(result, indent=2))

