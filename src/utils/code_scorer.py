"""Automated Code Quality Scoring System"""
import ast
import re
from pathlib import Path
from typing import Dict, List, Tuple
from crewai.tools import tool


class CodeQualityScorer:
    """
    Automated scoring system for generated code.
    Provides objective, verifiable quality metrics.
    """
    
    def __init__(self, code_path: str):
        self.code_path = Path(code_path)
        self.code_content = self._load_code()
        self.tree = None
        self.score_details = {}
    
    def _load_code(self) -> str:
        """Load code from file"""
        if not self.code_path.exists():
            return ""
        
        content = self.code_path.read_text()
        
        # Clean markdown code blocks if present
        if content.startswith('```'):
            lines = content.split('\n')
            # Remove first line if it's ```python or ```
            if lines[0].strip().startswith('```'):
                lines = lines[1:]
            # Remove last line if it's ```
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            # Remove trailing explanation text after final ```
            for i in range(len(lines) - 1, -1, -1):
                if lines[i].strip() == '```':
                    lines = lines[:i]
                    break
            content = '\n'.join(lines)
        
        return content
    
    def _parse_ast(self) -> bool:
        """Parse code into AST, return True if valid"""
        try:
            self.tree = ast.parse(self.code_content)
            return True
        except SyntaxError:
            return False
    
    def score(self) -> Dict:
        """
        Calculate comprehensive quality score.
        
        Returns:
            {
                'total_score': 85,
                'category_scores': {...},
                'details': {...},
                'grade': 'B+',
                'passed': True
            }
        """
        scores = {}
        
        # Category 1: Has All Imports (20 points)
        scores['imports'] = self._score_imports()
        
        # Category 2: Endpoints Implemented (30 points)
        scores['endpoints'] = self._score_endpoints()
        
        # Category 3: Error Handling (20 points)
        scores['error_handling'] = self._score_error_handling()
        
        # Category 4: Pydantic Models (15 points)
        scores['pydantic'] = self._score_pydantic_models()
        
        # Category 5: Runnability (15 points)
        scores['runnability'] = self._score_runnability()
        
        total = sum(scores.values())
        grade = self._calculate_grade(total)
        
        return {
            'total_score': total,
            'category_scores': scores,
            'details': self.score_details,
            'grade': grade,
            'passed': total >= 75,  # Pass threshold
            'file_path': str(self.code_path),
            'code_length': len(self.code_content),
            'line_count': len(self.code_content.splitlines())
        }
    
    def _score_imports(self) -> int:
        """
        Score: 20 points
        Check for critical imports needed for FastAPI + SQLAlchemy
        """
        required_imports = {
            'FastAPI': 4,           # 4 pts
            'Depends': 3,           # 3 pts
            'HTTPException': 3,     # 3 pts
            'status': 2,            # 2 pts (optional but good)
            'Column': 4,            # 4 pts
            'Integer': 1,           # 1 pt
            'String': 1,            # 1 pt
            'create_engine': 2,     # 2 pts
        }
        
        score = 0
        found_imports = []
        missing_imports = []
        
        for imp, points in required_imports.items():
            if imp in self.code_content:
                score += points
                found_imports.append(imp)
            else:
                missing_imports.append(imp)
        
        # Bonus points for good practices
        if 'from typing import' in self.code_content:
            score += 2  # Bonus for type hints
        
        self.score_details['imports'] = {
            'found': found_imports,
            'missing': missing_imports,
            'bonus': 'typing' if 'from typing import' in self.code_content else None
        }
        
        return min(score, 20)  # Cap at 20
    
    def _score_endpoints(self) -> int:
        """
        Score: 30 points
        Count and validate API endpoints
        """
        score = 0
        endpoints = {
            'POST': r'@app\.post\(',
            'GET': r'@app\.get\(',
            'PUT': r'@app\.put\(',
            'DELETE': r'@app\.delete\(',
            'PATCH': r'@app\.patch\('
        }
        
        found_endpoints = []
        for method, pattern in endpoints.items():
            matches = re.findall(pattern, self.code_content)
            if matches:
                found_endpoints.append(f"{method}({len(matches)})")
                score += 6 * len(matches)  # 6 pts per endpoint
        
        # Check for database operations in endpoints
        has_db_operations = all([
            'db.add' in self.code_content,      # CREATE
            'db.commit' in self.code_content,   # COMMIT
            'db.query' in self.code_content,    # READ
        ])
        
        if has_db_operations:
            score += 6  # Bonus for proper DB usage
        
        # Check for proper response models
        if 'response_model=' in self.code_content:
            score += 3  # Bonus for response typing
        
        self.score_details['endpoints'] = {
            'found': found_endpoints,
            'has_db_operations': has_db_operations,
            'has_response_models': 'response_model=' in self.code_content
        }
        
        return min(score, 30)  # Cap at 30
    
    def _score_error_handling(self) -> int:
        """
        Score: 20 points
        Check for error handling patterns
        """
        score = 0
        
        # Check for try/except blocks
        try_except_count = self.code_content.count('try:')
        score += min(try_except_count * 5, 10)  # 5 pts each, max 10
        
        # Check for HTTPException usage
        if 'HTTPException' in self.code_content:
            score += 5
        
        # Check for status codes
        if 'status_code=' in self.code_content or 'status.' in self.code_content:
            score += 3
        
        # Check for proper error messages
        if 'detail=' in self.code_content:
            score += 2
        
        self.score_details['error_handling'] = {
            'try_except_blocks': try_except_count,
            'uses_http_exception': 'HTTPException' in self.code_content,
            'has_status_codes': 'status_code=' in self.code_content,
            'has_error_details': 'detail=' in self.code_content
        }
        
        return min(score, 20)
    
    def _score_pydantic_models(self) -> int:
        """
        Score: 15 points
        Check for Pydantic model definitions
        """
        score = 0
        
        if not self._parse_ast():
            return 0
        
        pydantic_models = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                # Check if inherits from BaseModel
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == 'BaseModel':
                        pydantic_models.append(node.name)
        
        # Score based on model count
        model_count = len(pydantic_models)
        if model_count >= 2:  # Request and Response models
            score = 15
        elif model_count == 1:
            score = 10
        
        # Check for Config class (best practice)
        has_config = 'class Config:' in self.code_content
        if has_config and model_count >= 1:
            score = min(score + 2, 15)  # Bonus points
        
        self.score_details['pydantic'] = {
            'models_found': pydantic_models,
            'count': model_count,
            'has_config': has_config
        }
        
        return min(score, 15)
    
    def _score_runnability(self) -> int:
        """
        Score: 15 points
        Check if code can actually run
        """
        score = 0
        issues = []
        
        # 1. Syntax valid (5 pts)
        if self._parse_ast():
            score += 5
        else:
            issues.append('Syntax errors present')
            return 0  # Can't run if syntax error
        
        # 2. Database setup present (5 pts)
        required_db_setup = [
            'create_engine',
            'sessionmaker',
            'declarative_base',
        ]
        if all(setup in self.code_content for setup in required_db_setup):
            score += 5
        else:
            missing = [s for s in required_db_setup if s not in self.code_content]
            issues.append(f'Missing DB setup: {", ".join(missing)}')
        
        # 3. Check for common issues (5 pts)
        # Check for table creation
        if 'metadata.create_all' not in self.code_content:
            issues.append('Missing Base.metadata.create_all()')
            score -= 3
        
        # Check for get_db with yield
        if 'def get_db' in self.code_content and 'yield' in self.code_content:
            score += 3
        else:
            issues.append('get_db() missing or incorrect')
        
        # Check for FastAPI app initialization
        if 'app = FastAPI()' in self.code_content:
            score += 2
        else:
            issues.append('FastAPI app not initialized')
        
        # Check for incorrect patterns
        if 'app.run(' in self.code_content:
            issues.append('Incorrect app.run() - FastAPI uses uvicorn')
            score -= 2
        
        self.score_details['runnability'] = {
            'syntax_valid': self.tree is not None,
            'has_db_setup': all(s in self.code_content for s in required_db_setup),
            'issues': issues,
            'has_get_db': 'def get_db' in self.code_content,
            'has_app_init': 'app = FastAPI()' in self.code_content
        }
        
        return max(0, min(score, 15))  # Ensure non-negative, cap at 15
    
    def _calculate_grade(self, score: int) -> str:
        """Convert numerical score to letter grade"""
        if score >= 95:
            return 'A+'
        elif score >= 90:
            return 'A'
        elif score >= 85:
            return 'A-'
        elif score >= 80:
            return 'B+'
        elif score >= 75:
            return 'B'
        elif score >= 70:
            return 'B-'
        elif score >= 65:
            return 'C+'
        elif score >= 60:
            return 'C'
        else:
            return 'F'
    
    def generate_report(self) -> str:
        """Generate detailed scoring report"""
        result = self.score()
        
        report = f"""
╔═══════════════════════════════════════════════════════════════╗
║              CODE QUALITY SCORE REPORT                        ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  File: {Path(result['file_path']).name:<50} ║
║  Score: {result['total_score']}/100 ({result['grade']})                                      ║
║  Status: {'✅ PASS' if result['passed'] else '❌ FAIL'}                                             ║
║  Lines: {result['line_count']:<5} | Chars: {result['code_length']:<10}                    ║
║                                                               ║
╠═══════════════════════════════════════════════════════════════╣
║              CATEGORY BREAKDOWN                               ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  1. Has All Imports          {result['category_scores']['imports']:>3}/20  {'✅' if result['category_scores']['imports'] >= 16 else '⚠️' if result['category_scores']['imports'] >= 10 else '❌'}              ║
║  2. Endpoints Implemented    {result['category_scores']['endpoints']:>3}/30  {'✅' if result['category_scores']['endpoints'] >= 24 else '⚠️' if result['category_scores']['endpoints'] >= 15 else '❌'}              ║
║  3. Error Handling           {result['category_scores']['error_handling']:>3}/20  {'✅' if result['category_scores']['error_handling'] >= 16 else '⚠️' if result['category_scores']['error_handling'] >= 10 else '❌'}              ║
║  4. Pydantic Models          {result['category_scores']['pydantic']:>3}/15  {'✅' if result['category_scores']['pydantic'] >= 12 else '⚠️' if result['category_scores']['pydantic'] >= 8 else '❌'}              ║
║  5. Can Run Without Errors   {result['category_scores']['runnability']:>3}/15  {'✅' if result['category_scores']['runnability'] >= 12 else '⚠️' if result['category_scores']['runnability'] >= 8 else '❌'}              ║
║                                                               ║
╠═══════════════════════════════════════════════════════════════╣
║              DETAILS                                          ║
╠═══════════════════════════════════════════════════════════════╣
"""
        
        # Add detailed findings
        imports_found = self.score_details.get('imports', {}).get('found', [])[:5]
        imports_missing = self.score_details.get('imports', {}).get('missing', [])[:3]
        endpoints_found = self.score_details.get('endpoints', {}).get('found', [])
        pydantic_models = self.score_details.get('pydantic', {}).get('models_found', [])
        issues = self.score_details.get('runnability', {}).get('issues', [])
        
        report += f"""║                                                               ║
║  Imports: {', '.join(imports_found) if imports_found else 'None':<50}║
║  Missing: {', '.join(imports_missing) if imports_missing else 'None':<50}║
║                                                               ║
║  Endpoints: {', '.join(endpoints_found) if endpoints_found else 'None':<47}║
║  DB Ops: {'✅ Yes' if self.score_details.get('endpoints', {}).get('has_db_operations') else '❌ No':<52}║
║                                                               ║
║  Error Handling: {self.score_details.get('error_handling', {}).get('try_except_blocks', 0)} try/except blocks{'':>28}║
║  HTTPException: {'✅ Yes' if self.score_details.get('error_handling', {}).get('uses_http_exception') else '❌ No':<45}║
║                                                               ║
║  Pydantic: {', '.join(pydantic_models) if pydantic_models else 'None':<50}║
║                                                               ║
"""
        
        if issues:
            report += "║  Issues:                                                      ║\n"
            for issue in issues[:3]:  # Show max 3 issues
                report += f"║    • {issue:<56}║\n"
        
        report += "╚═══════════════════════════════════════════════════════════════╝\n"
        
        return report
    
    def _score_imports(self) -> int:
        """Score based on required imports"""
        required_imports = {
            'FastAPI': 4,
            'Depends': 3,
            'HTTPException': 3,
            'status': 2,
            'Column': 4,
            'Integer': 1,
            'String': 1,
            'create_engine': 2,
        }
        
        score = 0
        found_imports = []
        missing_imports = []
        
        for imp, points in required_imports.items():
            if imp in self.code_content:
                score += points
                found_imports.append(imp)
            else:
                missing_imports.append(imp)
        
        # Bonus for type hints
        if 'from typing import' in self.code_content:
            score += 2
        
        self.score_details['imports'] = {
            'found': found_imports,
            'missing': missing_imports,
            'bonus': 'typing' if 'from typing import' in self.code_content else None
        }
        
        return min(score, 20)
    
    def _score_endpoints(self) -> int:
        """Score based on endpoint implementation"""
        score = 0
        endpoints = {
            'POST': r'@app\.post\(',
            'GET': r'@app\.get\(',
            'PUT': r'@app\.put\(',
            'DELETE': r'@app\.delete\(',
        }
        
        found_endpoints = []
        for method, pattern in endpoints.items():
            matches = re.findall(pattern, self.code_content)
            if matches:
                found_endpoints.append(f"{method}({len(matches)})")
                score += 6 * len(matches)
        
        # Bonus for DB operations
        has_db_ops = all([
            'db.add' in self.code_content,
            'db.commit' in self.code_content,
            'db.query' in self.code_content,
        ])
        
        if has_db_ops:
            score += 6
        
        # Bonus for response models
        if 'response_model=' in self.code_content:
            score += 3
        
        self.score_details['endpoints'] = {
            'found': found_endpoints,
            'has_db_operations': has_db_ops,
            'has_response_models': 'response_model=' in self.code_content
        }
        
        return min(score, 30)
    
    def _score_error_handling(self) -> int:
        """Score based on error handling"""
        score = 0
        
        try_except_count = self.code_content.count('try:')
        score += min(try_except_count * 5, 10)
        
        if 'HTTPException' in self.code_content:
            score += 5
        
        if 'status_code=' in self.code_content or 'status.' in self.code_content:
            score += 3
        
        if 'detail=' in self.code_content:
            score += 2
        
        self.score_details['error_handling'] = {
            'try_except_blocks': try_except_count,
            'uses_http_exception': 'HTTPException' in self.code_content,
            'has_status_codes': 'status_code=' in self.code_content,
            'has_error_details': 'detail=' in self.code_content
        }
        
        return min(score, 20)
    
    def _score_pydantic_models(self) -> int:
        """Score based on Pydantic models"""
        score = 0
        
        if not self._parse_ast():
            return 0
        
        pydantic_models = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == 'BaseModel':
                        pydantic_models.append(node.name)
        
        model_count = len(pydantic_models)
        if model_count >= 2:
            score = 15
        elif model_count == 1:
            score = 10
        
        has_config = 'class Config:' in self.code_content
        if has_config and model_count >= 1:
            score = min(score + 2, 15)
        
        self.score_details['pydantic'] = {
            'models_found': pydantic_models,
            'count': model_count,
            'has_config': has_config
        }
        
        return min(score, 15)
    
    def _score_runnability(self) -> int:
        """Score based on code runnability"""
        score = 0
        issues = []
        
        if self._parse_ast():
            score += 5
        else:
            issues.append('Syntax errors present')
            return 0
        
        required_db_setup = ['create_engine', 'sessionmaker', 'declarative_base']
        if all(setup in self.code_content for setup in required_db_setup):
            score += 5
        else:
            missing = [s for s in required_db_setup if s not in self.code_content]
            issues.append(f'Missing: {", ".join(missing)}')
        
        if 'metadata.create_all' not in self.code_content:
            issues.append('Missing Base.metadata.create_all()')
            score -= 3
        
        if 'def get_db' in self.code_content and 'yield' in self.code_content:
            score += 3
        else:
            issues.append('get_db() missing or incorrect')
        
        if 'app = FastAPI()' in self.code_content:
            score += 2
        else:
            issues.append('FastAPI app not initialized')
        
        if 'app.run(' in self.code_content:
            issues.append('Incorrect app.run() - use uvicorn instead')
            score -= 2
        
        self.score_details['runnability'] = {
            'syntax_valid': self.tree is not None,
            'has_db_setup': all(s in self.code_content for s in required_db_setup),
            'issues': issues,
            'has_get_db': 'def get_db' in self.code_content,
            'has_app_init': 'app = FastAPI()' in self.code_content
        }
        
        return max(0, min(score, 15))
    
    def _calculate_grade(self, score: int) -> str:
        """Convert score to letter grade"""
        if score >= 95:
            return 'A+'
        elif score >= 90:
            return 'A'
        elif score >= 85:
            return 'A-'
        elif score >= 80:
            return 'B+'
        elif score >= 75:
            return 'B'
        elif score >= 70:
            return 'B-'
        elif score >= 65:
            return 'C+'
        elif score >= 60:
            return 'C'
        else:
            return 'F'
    
    def get_recommendations(self) -> List[str]:
        """Get improvement recommendations"""
        result = self.score()
        recommendations = []
        
        if result['category_scores']['imports'] < 20:
            missing = self.score_details.get('imports', {}).get('missing', [])
            if missing:
                recommendations.append(
                    f"Add missing imports: {', '.join(missing[:3])}"
                )
        
        if result['category_scores']['endpoints'] < 24:
            recommendations.append(
                "Implement more CRUD endpoints (GET by ID, PUT, DELETE)"
            )
        
        if result['category_scores']['error_handling'] < 16:
            recommendations.append(
                "Add try/except blocks in endpoints with HTTPException"
            )
        
        if result['category_scores']['pydantic'] < 12:
            recommendations.append(
                "Define both request and response Pydantic models"
            )
        
        if result['category_scores']['runnability'] < 12:
            issues = self.score_details.get('runnability', {}).get('issues', [])
            for issue in issues:
                recommendations.append(f"Fix: {issue}")
        
        return recommendations


def score_generated_code(file_path: str, verbose: bool = True) -> Dict:
    """
    Score generated code and return results.
    
    Args:
        file_path: Path to code file to score
        verbose: Print detailed report
        
    Returns:
        Scoring results dictionary
    """
    scorer = CodeQualityScorer(file_path)
    result = scorer.score()
    
    if verbose:
        print(scorer.generate_report())
        
        recommendations = scorer.get_recommendations()
        if recommendations:
            print("\n📋 RECOMMENDATIONS FOR IMPROVEMENT:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        print()
    
    return result


@tool("Score Generated Code")
def score_code_tool(file_path: str) -> str:
    """
    Automated code quality scoring tool for agents.
    
    Args:
        file_path: Path to code file to score
        
    Returns:
        Scoring report with grade and recommendations
    """
    try:
        scorer = CodeQualityScorer(file_path)
        result = scorer.score()
        recommendations = scorer.get_recommendations()
        
        return f"""
Code Quality Score: {result['total_score']}/100 ({result['grade']})
Status: {'✅ PASS' if result['passed'] else '❌ FAIL'}

Category Breakdown:
- Imports: {result['category_scores']['imports']}/20
- Endpoints: {result['category_scores']['endpoints']}/30
- Error Handling: {result['category_scores']['error_handling']}/20
- Pydantic Models: {result['category_scores']['pydantic']}/15
- Runnability: {result['category_scores']['runnability']}/15

Recommendations:
{chr(10).join(f'- {r}' for r in recommendations) if recommendations else '- None - Code quality is excellent!'}
"""
    except Exception as e:
        return f"❌ Scoring failed: {str(e)}"


if __name__ == "__main__":
    # Test the scorer
    import sys
    if len(sys.argv) > 1:
        result = score_generated_code(sys.argv[1])
        print(f"\nFinal Score: {result['total_score']}/100 ({result['grade']})")
        print(f"Passed: {result['passed']}")
    else:
        print("Usage: python code_scorer.py <path_to_code.py>")

