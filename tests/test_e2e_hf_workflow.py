"""End-to-end workflow tests for HF Pro + MCP integration.

Tests the complete pipeline: data validation → training → inference → monitoring
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from src.mcp import DataValidator, SafetyValidator
from src.utils import HFCostMonitor, HFProClient


@pytest.fixture
def temp_workspace():
    """Create temporary workspace for E2E testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        
        # Create subdirectories
        (workspace / "data").mkdir()
        (workspace / "models").mkdir()
        (workspace / "logs").mkdir()
        
        yield workspace


@pytest.fixture
def sample_training_data(temp_workspace):
    """Create sample training dataset."""
    data_dir = temp_workspace / "data"
    
    # Training data
    train_df = pd.DataFrame({
        "text": [
            "The quick brown fox jumps",
            "Machine learning is fascinating",
            "Python is a great language",
            "Neural networks can learn patterns",
            "Data science requires clean data",
        ],
        "label": [0, 1, 0, 1, 0],
    })
    train_path = data_dir / "train.csv"
    train_df.to_csv(train_path, index=False)
    
    # Test data
    test_df = pd.DataFrame({
        "text": ["Testing data quality", "Validation is important"],
        "label": [1, 1],
    })
    test_path = data_dir / "test.csv"
    test_df.to_csv(test_path, index=False)
    
    return {"train": str(train_path), "test": str(test_path)}


class TestEndToEndWorkflow:
    """E2E integration tests for complete MCP + HF Pro workflow."""

    def test_e2e_data_validation_workflow(self, sample_training_data, temp_workspace):
        """E2E Test 1: Data validation before training."""
        # Step 1: Validate dataset using MCP DataValidator
        validator = DataValidator(report_dir=str(temp_workspace / "logs"))
        
        result = validator.validate_dataset(
            train_path=sample_training_data["train"],
            test_path=sample_training_data["test"],
        )
        
        # Assertions
        assert result["passed"] is True, f"Validation failed: {result['issues']}"
        assert result["train_samples"] == 5
        assert result["test_samples"] == 2
        assert len(result["issues"]) == 0
        
        # Check report generated
        report_path = Path(result["report"])
        assert report_path.exists()
        
        with open(report_path) as f:
            report = json.load(f)
        assert report["status"] == "PASSED"

    def test_e2e_safety_validation_workflow(self):
        """E2E Test 2: Safety validation on model outputs."""
        # Step 1: Initialize safety validator
        validator = SafetyValidator(device="cpu")  # Use CPU for CI
        
        # Step 2: Test safe output
        safe_text = "This is a helpful and informative response about Python programming."
        safe_result = validator.check_output_safety(safe_text)
        
        assert safe_result["passed"] is True
        assert len(safe_result["issues"]) == 0
        
        # Step 3: Test empty output (should fail)
        empty_result = validator.check_output_safety("")
        
        assert empty_result["passed"] is False
        assert any("empty" in issue.lower() for issue in empty_result["issues"])

    def test_e2e_cost_monitoring_workflow(self, temp_workspace):
        """E2E Test 3: Cost monitoring throughout inference lifecycle."""
        # Step 1: Initialize cost monitor
        monitor = HFCostMonitor(
            budget_daily=5.0,
            cache_dir=str(temp_workspace / "cost_cache"),
        )
        
        # Step 2: Estimate cost before usage
        estimate = monitor.estimate_cost(tokens=1000, requests=5)
        assert estimate["total_cost_gbp"] > 0
        assert estimate["daily_budget_pct"] < 100
        
        # Step 3: Record usage
        for i in range(3):
            monitor.record_inference(
                model_id="test-model",
                tokens_used=200,
                latency_ms=50.0,
                success=True,
            )
        
        # Step 4: Check budget status
        budget_check = monitor.check_budget("daily")
        assert budget_check["status"] in ["OK", "WARNING", "EXCEEDED"]
        assert budget_check["stats"]["total_requests"] == 3
        assert budget_check["stats"]["total_tokens"] == 600
        
        # Step 5: Get summary report
        report = monitor.get_summary_report()
        assert "HuggingFace Pro Cost Monitor" in report
        assert "£" in report

    @patch('httpx.post')
    def test_e2e_inference_with_all_mcp_checks(self, mock_post, temp_workspace):
        """E2E Test 4: Complete inference with all MCP validations."""
        # Mock successful HF API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"generated_text": "This is a helpful response about machine learning."}
        ]
        mock_post.return_value = mock_response
        
        # Step 1: Initialize client with all MCP components
        client = HFProClient(
            model_id="test-model",
            hf_token="test_token",
            enable_cost_tracking=True,
            enable_safety_checks=True,
        )
        client.cost_monitor.cache_dir = temp_workspace / "cost"
        client.cost_monitor.budget_daily = 10.0
        
        # Step 2: Check budget before request
        assert client.cost_monitor.should_use_hf_pro() is True
        
        # Step 3: Generate with all checks enabled
        result = client.generate(
            prompt="Explain machine learning",
            max_tokens=100,
            check_budget=True,
            validate_safety=True,
        )
        
        # Step 4: Validate result structure
        assert result["status"] == "success"
        assert "text" in result
        assert "latency_ms" in result
        assert "tokens_used" in result
        assert "safety_check" in result
        
        # Step 5: Validate safety check ran
        safety = result["safety_check"]
        assert safety is not None
        assert "passed" in safety
        assert "issues" in safety
        assert "scores" in safety
        
        # Step 6: Verify cost was tracked
        assert len(client.cost_monitor.usage_log) > 0
        latest_entry = client.cost_monitor.usage_log[-1]
        assert latest_entry["tokens"] == result["tokens_used"]

    def test_e2e_training_to_inference_workflow(self, sample_training_data, temp_workspace):
        """E2E Test 5: Complete workflow from training to inference.
        
        Simulates: validate data → train model → validate output → monitor cost
        """
        # Step 1: Validate training data
        validator = DataValidator(report_dir=str(temp_workspace / "logs"))
        validation_result = validator.validate_dataset(
            train_path=sample_training_data["train"],
            test_path=sample_training_data["test"],
        )
        
        assert validation_result["passed"] is True, "Data validation should pass"
        
        # Step 2: Simulate training (would use HFTrainerAgent.train_with_profiling)
        # For E2E test, we just verify the structure exists
        from src.agents.hf_trainer_agent import HFTrainerAgent
        
        agent = HFTrainerAgent()
        assert agent.llm is not None
        assert hasattr(HFTrainerAgent, 'train_with_profiling')
        
        # Step 3: Simulate inference with cost monitoring
        monitor = HFCostMonitor(cache_dir=str(temp_workspace / "cost"))
        
        # Estimate cost
        estimate = monitor.estimate_cost(tokens=100)
        assert estimate["total_cost_gbp"] > 0
        
        # Record simulated inference
        monitor.record_inference(
            model_id="trained-model",
            tokens_used=100,
            latency_ms=75.0,
            success=True,
        )
        
        # Step 4: Validate output safety
        safety_validator = SafetyValidator(device="cpu")
        safety_result = safety_validator.check_output_safety(
            "This is a safe, helpful model output about machine learning."
        )
        
        assert safety_result["passed"] is True
        
        # Step 5: Final budget check
        final_budget = monitor.check_budget("daily")
        assert final_budget["status"] in ["OK", "WARNING", "EXCEEDED"]
        assert final_budget["stats"]["total_requests"] == 1
        
        # Workflow complete - all steps passed
        print("✅ E2E workflow validation complete")

    def test_e2e_budget_exceeded_fallback(self, temp_workspace):
        """E2E Test 6: Budget exceeded triggers fallback."""
        # Step 1: Setup with low budget
        monitor = HFCostMonitor(
            budget_daily=0.10,  # Very low budget
            cache_dir=str(temp_workspace / "cost"),
        )
        
        # Step 2: Exceed budget
        monitor.record_inference("test", 10000, 50.0, True)  # > £0.10
        
        # Step 3: Check budget
        budget_check = monitor.check_budget("daily")
        assert budget_check["status"] == "EXCEEDED"
        
        # Step 4: Verify should_use_hf_pro returns False
        assert monitor.should_use_hf_pro() is False
        
        # Step 5: Verify recommended actions include fallback
        actions = budget_check["actions"]
        assert any("Ollama" in str(a) for a in actions)
        assert any("CRITICAL" in str(a) or "Pause" in str(a) for a in actions)
        
        print("✅ Budget exceeded fallback workflow validated")

