"""Tests for HuggingFace Pro cost monitoring."""

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from src.utils.hf_cost_monitor import HFCostMonitor


@pytest.fixture
def temp_cache_dir():
    """Create temporary cache directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def monitor(temp_cache_dir):
    """Create cost monitor with temp cache."""
    return HFCostMonitor(
        budget_daily=10.0,  # £10 for testing
        budget_monthly=300.0,
        cache_dir=temp_cache_dir,
    )


class TestHFCostMonitor:
    """Test suite for cost monitoring."""

    def test_initialization(self, monitor):
        """Test monitor initializes correctly."""
        assert monitor.budget_daily == 10.0
        assert monitor.budget_monthly == 300.0
        assert monitor.warning_threshold == 0.8
        assert len(monitor.usage_log) == 0

    def test_record_inference(self, monitor):
        """Test recording inference calls."""
        monitor.record_inference(
            model_id="test-model",
            tokens_used=100,
            latency_ms=50.0,
            success=True,
        )
        
        assert len(monitor.usage_log) == 1
        entry = monitor.usage_log[0]
        assert entry["model_id"] == "test-model"
        assert entry["tokens"] == 100
        assert entry["latency_ms"] == 50.0
        assert entry["success"] is True
        assert "cost_gbp" in entry
        assert entry["cost_gbp"] > 0

    def test_get_usage_stats_empty(self, monitor):
        """Test usage stats when no data."""
        stats = monitor.get_usage_stats("daily")
        
        assert stats["total_requests"] == 0
        assert stats["total_tokens"] == 0
        assert stats["total_cost_gbp"] == 0.0
        assert stats["budget"] == 10.0
        assert stats["budget_used_pct"] == 0.0

    def test_get_usage_stats_with_data(self, monitor):
        """Test usage stats calculation."""
        # Record multiple inferences
        for i in range(5):
            monitor.record_inference(
                model_id="test-model",
                tokens_used=100,
                latency_ms=50.0,
                success=True,
            )
        
        stats = monitor.get_usage_stats("daily")
        
        assert stats["total_requests"] == 5
        assert stats["total_tokens"] == 500
        assert stats["total_cost_gbp"] > 0
        assert stats["success_rate"] == 1.0
        assert stats["avg_latency_ms"] == 50.0

    def test_check_budget_ok_status(self, monitor):
        """Test budget check returns OK when under threshold."""
        # Use 50% of budget
        monitor.record_inference(
            model_id="test-model",
            tokens_used=25000,  # £0.50 at £0.02/1K tokens
            latency_ms=100.0,
            success=True,
        )
        
        result = monitor.check_budget("daily")
        
        assert result["status"] == "OK"
        assert result["percentage"] < 80
        assert "Continue normal operations" in result["actions"]

    def test_check_budget_warning_status(self, monitor):
        """Test budget check returns WARNING at threshold."""
        # Use 85% of budget
        monitor.record_inference(
            model_id="test-model",
            tokens_used=425000,  # £8.50 at £0.02/1K tokens (85% of £10)
            latency_ms=100.0,
            success=True,
        )
        
        result = monitor.check_budget("daily")
        
        assert result["status"] == "WARNING"
        assert result["percentage"] >= 80
        assert result["percentage"] < 100
        assert any("Ollama" in action for action in result["actions"])

    def test_check_budget_exceeded_status(self, monitor):
        """Test budget check returns EXCEEDED when over limit."""
        # Use 110% of budget
        monitor.record_inference(
            model_id="test-model",
            tokens_used=550000,  # £11 at £0.02/1K tokens (110% of £10)
            latency_ms=100.0,
            success=True,
        )
        
        result = monitor.check_budget("daily")
        
        assert result["status"] == "EXCEEDED"
        assert result["percentage"] >= 100
        assert result["remaining"] == 0
        assert any("CRITICAL" in action for action in result["actions"])

    def test_estimate_cost(self, monitor):
        """Test cost estimation."""
        estimate = monitor.estimate_cost(tokens=1000, requests=10)
        
        assert estimate["tokens"] == 1000
        assert estimate["requests"] == 10
        assert estimate["total_cost_gbp"] > 0
        assert "daily_budget_pct" in estimate
        assert "monthly_budget_pct" in estimate

    def test_should_use_hf_pro_ok(self, monitor):
        """Test should_use_hf_pro returns True when budget OK."""
        # Small usage
        monitor.record_inference(
            model_id="test-model",
            tokens_used=1000,
            latency_ms=50.0,
            success=True,
        )
        
        assert monitor.should_use_hf_pro() is True

    def test_should_use_hf_pro_exceeded(self, monitor):
        """Test should_use_hf_pro returns False when budget exceeded."""
        # Exceed budget
        monitor.record_inference(
            model_id="test-model",
            tokens_used=600000,  # Over £10 budget
            latency_ms=50.0,
            success=True,
        )
        
        assert monitor.should_use_hf_pro() is False

    def test_usage_log_persistence(self, temp_cache_dir):
        """Test usage log persists across instances."""
        # Create first monitor and record usage
        monitor1 = HFCostMonitor(cache_dir=temp_cache_dir)
        monitor1.record_inference(
            model_id="test-model",
            tokens_used=100,
            latency_ms=50.0,
            success=True,
        )
        
        # Create second monitor (should load existing data)
        monitor2 = HFCostMonitor(cache_dir=temp_cache_dir)
        
        assert len(monitor2.usage_log) == 1
        assert monitor2.usage_log[0]["tokens"] == 100

    def test_get_summary_report(self, monitor):
        """Test summary report generation."""
        monitor.record_inference(
            model_id="test-model",
            tokens_used=50000,
            latency_ms=75.0,
            success=True,
        )
        
        report = monitor.get_summary_report()
        
        assert "HuggingFace Pro Cost Monitor" in report
        assert "DAILY" in report
        assert "MONTHLY" in report
        assert "£" in report
        assert isinstance(report, str)
        assert len(report) > 100

    def test_monthly_vs_daily_window(self, monitor):
        """Test different time windows."""
        # Record usage
        monitor.record_inference(
            model_id="test-model",
            tokens_used=10000,
            latency_ms=50.0,
            success=True,
        )
        
        daily_stats = monitor.get_usage_stats("daily")
        monthly_stats = monitor.get_usage_stats("monthly")
        
        # Both should show same usage for recent data
        assert daily_stats["total_tokens"] == monthly_stats["total_tokens"]
        assert daily_stats["budget"] != monthly_stats["budget"]  # Different budgets
        assert daily_stats["budget"] < monthly_stats["budget"]

    def test_success_rate_calculation(self, monitor):
        """Test success rate calculation."""
        # 3 successful, 2 failed
        for i in range(3):
            monitor.record_inference("test", 100, 50.0, success=True)
        for i in range(2):
            monitor.record_inference("test", 0, 50.0, success=False)
        
        stats = monitor.get_usage_stats("daily")
        
        assert stats["total_requests"] == 5
        assert stats["success_rate"] == 0.6  # 3/5

    def test_recommended_actions_warning(self, monitor):
        """Test recommended actions for WARNING status."""
        # 85% budget usage
        monitor.record_inference("test", 425000, 50.0, success=True)
        
        result = monitor.check_budget("daily")
        actions = monitor._get_recommended_actions(result["status"], result["percentage"])
        
        assert "WARNING" == result["status"]
        assert len(actions) > 0
        assert any("Ollama" in str(a) for a in actions)

    def test_recommended_actions_exceeded(self, monitor):
        """Test recommended actions for EXCEEDED status."""
        # 110% budget usage
        monitor.record_inference("test", 550000, 50.0, success=True)
        
        result = monitor.check_budget("daily")
        actions = monitor._get_recommended_actions(result["status"], result["percentage"])
        
        assert "EXCEEDED" == result["status"]
        assert len(actions) > 0
        assert any("CRITICAL" in str(a) for a in actions)
        assert any("Pause" in str(a) for a in actions)

