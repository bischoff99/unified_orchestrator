#!/usr/bin/env python3
"""Automated Code Quality Scorer for Generated Projects"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.code_validator import CodeValidator


class ProjectScorer:
    """Comprehensive scoring for generated projects."""
    
    def __init__(self, project_dir: str = "src/generated"):
        self.project_dir = Path(project_dir)
        self.results = {}
    
    def find_main_file(self) -> Path:
        """Find the main.py file in generated directory."""
        # Look for main.py in subdirectories
        main_files = list(self.project_dir.rglob("main.py"))
        
        if not main_files:
            raise FileNotFoundError(f"No main.py found in {self.project_dir}")
        
        # Return the first one (usually the main API file)
        return main_files[0]
    
    def score_documentation(self) -> Dict:
        """Score documentation completeness."""
        docs = {
            "README.md": 5,
            "API_Documentation.md": 5,
            "Setup_and_Installation_Guide.md": 4,
            "Deployment_Guide.md": 3,
            "requirements.txt": 3,
        }
        
        found_docs = {}
        score = 0
        
        for doc, points in docs.items():
            doc_path = self.project_dir / doc
            if doc_path.exists():
                found_docs[doc] = True
                score += points
            else:
                found_docs[doc] = False
        
        return {
            "score": score,
            "max_score": 20,
            "found_docs": found_docs,
            "passed": score >= 15
        }
    
    def score_project_structure(self) -> Dict:
        """Score project organization."""
        required_items = {
            "main.py": 5,
            "models": 3,  # models.py or models directory
            "tests": 3,    # tests directory
            "migrations": 2,
            "requirements.txt": 2,
        }
        
        score = 0
        found_items = {}
        
        for item, points in required_items.items():
            # Check if file or directory exists
            matches = list(self.project_dir.rglob(f"*{item}*"))
            if matches:
                found_items[item] = True
                score += points
            else:
                found_items[item] = False
        
        return {
            "score": score,
            "max_score": 15,
            "found_items": found_items,
            "passed": score >= 10
        }
    
    def generate_full_report(self) -> Dict:
        """Generate comprehensive scoring report."""
        try:
            main_file = self.find_main_file()
            print(f"Found main file: {main_file}")
        except FileNotFoundError as e:
            return {
                "error": str(e),
                "total_score": 0,
                "grade": "F",
                "passed": False
            }
        
        # Run code validation
        validator = CodeValidator(str(main_file))
        code_results = validator.validate()
        
        # Add documentation and structure scores
        doc_results = self.score_documentation()
        structure_results = self.score_project_structure()
        
        # Calculate total
        total_score = (
            code_results["total_score"] +
            doc_results["score"] +
            structure_results["score"]
        )
        max_score = (
            code_results["max_score"] +
            doc_results["max_score"] +
            structure_results["max_score"]
        )
        
        percentage = (total_score / max_score) * 100 if max_score > 0 else 0
        grade = self._get_grade(total_score)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "project_dir": str(self.project_dir),
            "main_file": str(main_file),
            "code_validation": code_results,
            "documentation": doc_results,
            "project_structure": structure_results,
            "total_score": total_score,
            "max_score": max_score,
            "percentage": round(percentage, 2),
            "grade": grade,
            "passed": total_score >= 105,  # 70% of 145
            "recommendations": self._generate_recommendations(code_results, doc_results, structure_results)
        }
        
        return report
    
    def _get_grade(self, score: int) -> str:
        """Convert total score to letter grade (out of 145)."""
        percentage = (score / 145) * 100
        
        if percentage >= 90:
            return "A"
        elif percentage >= 80:
            return "B"
        elif percentage >= 70:
            return "C"
        elif percentage >= 60:
            return "D"
        else:
            return "F"
    
    def _generate_recommendations(self, code, docs, structure) -> List[str]:
        """Generate actionable recommendations."""
        recs = []
        
        if not code.get("results", {}).get("imports", {}).get("passed"):
            missing = code["results"]["imports"]["missing"]
            recs.append(f"Add missing imports: {', '.join(missing[:5])}")
        
        if not code.get("results", {}).get("endpoints", {}).get("passed"):
            found = code["results"]["endpoints"]["total"]
            expected = code["results"]["endpoints"]["expected"]
            recs.append(f"Implement all endpoints: found {found}, need {expected}")
        
        if not code.get("results", {}).get("implementations", {}).get("passed"):
            recs.append("Replace pass statements with actual implementations")
        
        if not code.get("results", {}).get("syntax", {}).get("passed"):
            recs.append("Fix syntax errors before deployment")
        
        if not docs.get("passed"):
            recs.append("Add missing documentation files")
        
        if not structure.get("passed"):
            recs.append("Complete project structure (tests, migrations)")
        
        if not recs:
            recs.append("Code is excellent! Ready for production deployment.")
        
        return recs
    
    def print_report(self, report: Dict):
        """Print formatted report to console."""
        print("\n" + "="*70)
        print("CODE QUALITY EVALUATION REPORT")
        print("="*70)
        
        print(f"\nProject: {report['project_dir']}")
        print(f"Main File: {report['main_file']}")
        print(f"Timestamp: {report['timestamp']}")
        
        print("\n" + "-"*70)
        print("DETAILED SCORES")
        print("-"*70)
        
        # Code validation breakdown
        if "code_validation" in report and "results" in report["code_validation"]:
            cv = report["code_validation"]["results"]
            print(f"\n1. Imports:          {cv['imports']['score']}/{cv['imports']['max_score']}")
            if cv['imports']['missing']:
                print(f"   Missing: {', '.join(cv['imports']['missing'][:5])}")
            
            print(f"\n2. Endpoints:        {cv['endpoints']['score']}/{cv['endpoints']['max_score']}")
            print(f"   Found: {cv['endpoints']['found']}")
            
            print(f"\n3. Implementations:  {cv['implementations']['score']}/{cv['implementations']['max_score']}")
            print(f"   DB Operations: {cv['implementations']['has_db_operations']}")
            print(f"   Error Handling: {cv['implementations']['has_error_handling']}")
            
            print(f"\n4. Syntax:           {cv['syntax']['score']}/{cv['syntax']['max_score']}")
            if cv['syntax']['errors']:
                print(f"   Errors: {cv['syntax']['errors']}")
            
            print(f"\n5. Structure:        {cv['structure']['score']}/{cv['structure']['max_score']}")
            print(f"   Checks passed: {sum(1 for v in cv['structure']['checks'].values() if v)}/{len(cv['structure']['checks'])}")
        
        # Documentation
        print(f"\n6. Documentation:    {report['documentation']['score']}/{report['documentation']['max_score']}")
        
        # Project structure
        print(f"\n7. Project Struct:   {report['project_structure']['score']}/{report['project_structure']['max_score']}")
        
        print("\n" + "="*70)
        print("OVERALL RESULTS")
        print("="*70)
        print(f"Total Score:    {report['total_score']}/{report['max_score']} ({report['percentage']:.1f}%)")
        print(f"Grade:          {report['grade']}")
        print(f"Status:         {'✅ PASSED' if report['passed'] else '❌ FAILED'}")
        
        print("\n" + "-"*70)
        print("RECOMMENDATIONS")
        print("-"*70)
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"{i}. {rec}")
        
        print("\n" + "="*70 + "\n")


def main():
    """Main entry point for code evaluation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Evaluate generated code quality")
    parser.add_argument(
        "--project-dir",
        default="src/generated",
        help="Path to generated project directory"
    )
    parser.add_argument(
        "--output",
        default="logs/code_evaluation.json",
        help="Output file for JSON report"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed report to console"
    )
    
    args = parser.parse_args()
    
    scorer = ProjectScorer(args.project_dir)
    report = scorer.generate_full_report()
    
    # Print to console
    if args.verbose or True:  # Always print for now
        scorer.print_report(report)
    
    # Save JSON report
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Report saved to: {output_path}")
    
    # Exit with appropriate code
    sys.exit(0 if report.get("passed", False) else 1)


if __name__ == "__main__":
    main()

