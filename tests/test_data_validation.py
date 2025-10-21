"""Tests for data validation module."""

import json
import tempfile
from pathlib import Path

import pandas as pd
import pytest

from src.mcp.data_validation import DataValidator


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_train_data(temp_dir):
    """Create valid training dataset."""
    df = pd.DataFrame({
        "feature_1": [1.0, 2.0, 3.0, 4.0, 5.0],
        "feature_2": [10, 20, 30, 40, 50],
        "target": [0, 1, 0, 1, 0],
    })
    path = temp_dir / "train.csv"
    df.to_csv(path, index=False)
    return str(path)


@pytest.fixture
def sample_test_data(temp_dir):
    """Create valid test dataset."""
    df = pd.DataFrame({
        "feature_1": [1.5, 2.5, 3.5],
        "feature_2": [15, 25, 35],
        "target": [0, 1, 0],
    })
    path = temp_dir / "test.csv"
    df.to_csv(path, index=False)
    return str(path)


@pytest.fixture
def validator(temp_dir):
    """Create validator instance with temp report dir."""
    report_dir = temp_dir / "reports"
    return DataValidator(report_dir=str(report_dir))


class TestDataValidator:
    """Data validation tests."""

    def test_validate_valid_dataset(self, validator, sample_train_data):
        """Test validation passes for valid data."""
        result = validator.validate_dataset(sample_train_data)
        assert result["passed"] is True
        assert len(result["issues"]) == 0
        assert result["train_samples"] == 5

    def test_validate_with_test_data(self, validator, sample_train_data, sample_test_data):
        """Test validation with train and test data."""
        result = validator.validate_dataset(sample_train_data, sample_test_data)
        assert result["passed"] is True
        assert result["test_samples"] == 3

    def test_empty_dataset(self, validator, temp_dir):
        """Test validation fails for empty dataset."""
        df = pd.DataFrame({"col1": [], "col2": []})
        path = temp_dir / "empty.csv"
        df.to_csv(path, index=False)
        
        result = validator.validate_dataset(str(path))
        assert result["passed"] is False
        assert any("empty" in issue.lower() for issue in result["issues"])

    def test_missing_values_detection(self, validator, temp_dir):
        """Test detection of high missing value %."""
        df = pd.DataFrame({
            "col1": [1, 2, None, None, None],
            "col2": [10, 20, 30, 40, 50],
        })
        path = temp_dir / "missing.csv"
        df.to_csv(path, index=False)
        
        result = validator.validate_dataset(str(path))
        assert result["passed"] is False
        assert any("missing" in issue.lower() for issue in result["issues"])

    def test_duplicate_rows_detection(self, validator, temp_dir):
        """Test detection of high duplicate %."""
        df = pd.DataFrame({
            "col1": [1, 1, 1, 1, 2],
            "col2": [10, 10, 10, 10, 20],
        })
        path = temp_dir / "duplicates.csv"
        df.to_csv(path, index=False)
        
        result = validator.validate_dataset(str(path))
        assert result["passed"] is False
        assert any("duplicate" in issue.lower() for issue in result["issues"])

    def test_distribution_shift_detection(self, validator, temp_dir):
        """Test detection of distribution shift."""
        train_df = pd.DataFrame({
            "feature": [1.0, 2.0, 3.0, 4.0, 5.0],
            "target": [0, 1, 0, 1, 0],
        })
        test_df = pd.DataFrame({
            "feature": [100.0, 200.0, 300.0],
            "target": [0, 1, 0],
        })
        
        train_path = temp_dir / "train_shift.csv"
        test_path = temp_dir / "test_shift.csv"
        train_df.to_csv(train_path, index=False)
        test_df.to_csv(test_path, index=False)
        
        result = validator.validate_dataset(str(train_path), str(test_path))
        assert result["passed"] is False
        assert any("shift" in issue.lower() for issue in result["issues"])

    def test_report_generation(self, validator, sample_train_data):
        """Test validation report is generated."""
        result = validator.validate_dataset(sample_train_data)
        report_path = Path(result["report"])
        assert report_path.exists()
        
        with open(report_path) as f:
            report = json.load(f)
        assert "status" in report
        assert "train_path" in report
        assert "timestamp" in report

