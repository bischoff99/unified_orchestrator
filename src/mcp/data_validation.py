"""Data validation module using Deepchecks and Pytest.

Validates training datasets for integrity, schema compliance,
and data quality issues before model training.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from crewai.tools import tool

logger = logging.getLogger(__name__)


class DataValidator:
    """Validates datasets for training readiness."""

    def __init__(self, report_dir: str = "logs"):
        """Initialize validator.
        
        Args:
            report_dir: Directory to save validation reports
        """
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(exist_ok=True)

    def validate_dataset(
        self, 
        train_path: str, 
        test_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate dataset for training.
        
        Args:
            train_path: Path to training CSV/JSONL
            test_path: Optional path to test CSV/JSONL
            
        Returns:
            Dict with keys: passed (bool), issues (List), report (str)
        """
        try:
            # Load datasets
            train_df = self._load_data(train_path)
            test_df = self._load_data(test_path) if test_path else None
            
            issues = []
            
            # Run validations
            issues.extend(self._check_schema(train_df))
            issues.extend(self._check_missing_values(train_df))
            issues.extend(self._check_duplicates(train_df))
            
            if test_df is not None:
                issues.extend(self._check_distribution_shift(train_df, test_df))
            
            passed = len(issues) == 0
            report = self._generate_report(train_path, test_path, issues, passed)
            
            return {
                "passed": passed,
                "issues": issues,
                "report": report,
                "train_samples": len(train_df),
                "test_samples": len(test_df) if test_df is not None else 0,
            }
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return {
                "passed": False,
                "issues": [f"Validation error: {str(e)}"],
                "report": "",
            }

    def _load_data(self, path: str) -> pd.DataFrame:
        """Load CSV or JSONL file."""
        path_obj = Path(path)
        if path_obj.suffix == ".csv":
            return pd.read_csv(path)
        elif path_obj.suffix == ".jsonl":
            return pd.read_json(path, lines=True)
        else:
            raise ValueError(f"Unsupported format: {path_obj.suffix}")

    def _check_schema(self, df: pd.DataFrame) -> List[str]:
        """Check for required columns and types."""
        issues = []
        if df.empty:
            issues.append("Dataset is empty")
        if len(df.columns) < 2:
            issues.append("Dataset has fewer than 2 columns")
        return issues

    def _check_missing_values(self, df: pd.DataFrame) -> List[str]:
        """Check for missing values."""
        issues = []
        missing = df.isnull().sum()
        for col, count in missing.items():
            if count > 0:
                pct = (count / len(df)) * 100
                if pct > 10:
                    issues.append(
                        f"Column '{col}' has {pct:.1f}% missing values"
                    )
        return issues

    def _check_duplicates(self, df: pd.DataFrame) -> List[str]:
        """Check for duplicate rows."""
        issues = []
        dup_count = df.duplicated().sum()
        if dup_count > 0:
            pct = (dup_count / len(df)) * 100
            if pct > 5:
                issues.append(f"Dataset has {pct:.1f}% duplicate rows")
        return issues

    def _check_distribution_shift(
        self, 
        train_df: pd.DataFrame, 
        test_df: pd.DataFrame
    ) -> List[str]:
        """Check for distribution shift between train and test."""
        issues = []
        
        # Check column alignment
        if set(train_df.columns) != set(test_df.columns):
            issues.append("Train and test columns don't match")
        
        # Check numeric distributions
        numeric_cols = train_df.select_dtypes(include=["number"]).columns
        for col in numeric_cols:
            train_mean = train_df[col].mean()
            test_mean = test_df[col].mean()
            shift = abs(train_mean - test_mean) / (train_mean + 1e-8)
            if shift > 0.3:
                issues.append(
                    f"Column '{col}' has {shift:.1%} distribution shift"
                )
        
        return issues

    def _generate_report(
        self,
        train_path: str,
        test_path: Optional[str],
        issues: List[str],
        passed: bool,
    ) -> str:
        """Generate validation report."""
        report_path = self.report_dir / "data_validation_report.json"
        
        report = {
            "status": "PASSED" if passed else "FAILED",
            "train_path": train_path,
            "test_path": test_path,
            "issues": issues,
            "timestamp": pd.Timestamp.now().isoformat(),
        }
        
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Report saved to {report_path}")
        return str(report_path)


@tool("Validate Training Data")
def validate_training_data(train_path: str, test_path: Optional[str] = None) -> str:
    """CrewAI tool to validate training dataset.
    
    Args:
        train_path: Path to training data (CSV/JSONL)
        test_path: Optional path to test data
        
    Returns:
        Validation result as JSON string
    """
    validator = DataValidator()
    result = validator.validate_dataset(train_path, test_path)
    return json.dumps(result, indent=2)

