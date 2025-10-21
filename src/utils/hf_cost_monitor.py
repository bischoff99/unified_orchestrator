"""HuggingFace Pro cost monitoring and budget management.

Tracks HF Pro API usage, monitors costs against budget, and provides
automatic fallback to Ollama when budget limits are approached.

Thread-safe for concurrent agent usage.
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
from threading import Lock
import json

logger = logging.getLogger(__name__)


class HFCostMonitor:
    """Monitor HuggingFace Pro usage and costs with budget enforcement."""

    def __init__(
        self,
        budget_daily: float = 3.33,  # £100/month = £3.33/day
        budget_monthly: float = 100.0,
        cost_per_1k_tokens: float = 0.02,  # Estimated
        warning_threshold: float = 0.8,  # 80% of budget
        cache_dir: str = ".hf_cost_cache",
    ):
        """Initialize cost monitor.
        
        Args:
            budget_daily: Daily budget limit in GBP
            budget_monthly: Monthly budget limit in GBP
            cost_per_1k_tokens: Estimated cost per 1K tokens
            warning_threshold: Warning threshold as fraction of budget
            cache_dir: Directory to cache usage stats
        """
        self.budget_daily = budget_daily
        self.budget_monthly = budget_monthly
        self.cost_per_1k_tokens = cost_per_1k_tokens
        self.warning_threshold = warning_threshold
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        self.usage_file = self.cache_dir / "usage_log.json"
        self.usage_log = self._load_usage_log()
        
        # Thread safety for concurrent agent usage
        self._lock = Lock()

    def _load_usage_log(self) -> List[Dict[str, Any]]:
        """Load usage log from cache."""
        if self.usage_file.exists():
            try:
                with open(self.usage_file) as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load usage log: {e}")
        return []

    def _save_usage_log(self):
        """Save usage log to cache."""
        try:
            with open(self.usage_file, 'w') as f:
                json.dump(self.usage_log, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save usage log: {e}")

    def record_inference(
        self,
        model_id: str,
        tokens_used: int,
        latency_ms: float,
        success: bool = True,
    ) -> None:
        """Record an inference call (thread-safe).
        
        Args:
            model_id: HuggingFace model ID
            tokens_used: Number of tokens generated
            latency_ms: Inference latency in milliseconds
            success: Whether the call succeeded
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "model_id": model_id,
            "tokens": tokens_used,
            "latency_ms": latency_ms,
            "success": success,
            "cost_gbp": (tokens_used / 1000.0) * self.cost_per_1k_tokens,
        }
        
        # Thread-safe append and save
        with self._lock:
            self.usage_log.append(entry)
            self._save_usage_log()
        
        logger.info(
            f"Recorded inference: {model_id}, {tokens_used} tokens, "
            f"£{entry['cost_gbp']:.4f}, {latency_ms:.1f}ms"
        )

    def get_usage_stats(
        self,
        time_window: str = "daily",  # "daily" or "monthly"
    ) -> Dict[str, Any]:
        """Get usage statistics for time window.
        
        Args:
            time_window: "daily" or "monthly"
            
        Returns:
            Dict with usage stats
        """
        now = datetime.now()
        
        if time_window == "daily":
            cutoff = now - timedelta(days=1)
            budget = self.budget_daily
        else:  # monthly
            cutoff = now - timedelta(days=30)
            budget = self.budget_monthly
        
        # Filter entries within window
        recent_entries = [
            e for e in self.usage_log
            if datetime.fromisoformat(e["timestamp"]) > cutoff
        ]
        
        if not recent_entries:
            return {
                "total_requests": 0,
                "total_tokens": 0,
                "total_cost_gbp": 0.0,
                "avg_latency_ms": 0.0,
                "success_rate": 1.0,
                "budget": budget,
                "budget_used_pct": 0.0,
            }
        
        total_tokens = sum(e["tokens"] for e in recent_entries)
        total_cost = sum(e["cost_gbp"] for e in recent_entries)
        successful = sum(1 for e in recent_entries if e["success"])
        avg_latency = sum(e["latency_ms"] for e in recent_entries) / len(recent_entries)
        
        return {
            "total_requests": len(recent_entries),
            "total_tokens": total_tokens,
            "total_cost_gbp": total_cost,
            "avg_latency_ms": avg_latency,
            "success_rate": successful / len(recent_entries),
            "budget": budget,
            "budget_used_pct": (total_cost / budget) * 100,
            "time_window": time_window,
        }

    def check_budget(self, time_window: str = "daily") -> Dict[str, Any]:
        """Check budget status and recommend actions.
        
        Args:
            time_window: "daily" or "monthly"
            
        Returns:
            Dict with status and recommended actions
        """
        stats = self.get_usage_stats(time_window)
        budget = stats["budget"]
        spent = stats["total_cost_gbp"]
        pct = stats["budget_used_pct"]
        
        # Determine status
        if pct >= 100:
            status = "EXCEEDED"
        elif pct >= self.warning_threshold * 100:
            status = "WARNING"
        else:
            status = "OK"
        
        # Recommend actions
        actions = self._get_recommended_actions(status, pct)
        
        result = {
            "status": status,
            "time_window": time_window,
            "budget": budget,
            "spent": spent,
            "remaining": max(0, budget - spent),
            "percentage": pct,
            "warning_threshold": self.warning_threshold * 100,
            "actions": actions,
            "stats": stats,
        }
        
        # Log warnings
        if status != "OK":
            logger.warning(
                f"Budget {status}: {pct:.1f}% of {time_window} budget used "
                f"(£{spent:.2f}/£{budget:.2f})"
            )
        
        return result

    def _get_recommended_actions(self, status: str, percentage: float) -> List[str]:
        """Get recommended actions based on budget status.
        
        Args:
            status: Budget status (OK, WARNING, EXCEEDED)
            percentage: Percentage of budget used
            
        Returns:
            List of recommended action strings
        """
        if status == "OK":
            return ["Continue normal operations"]
        
        elif status == "WARNING":
            return [
                "Switch non-critical agents to Ollama backend",
                "Enable response caching to reduce token usage",
                "Reduce batch sizes for training",
                "Monitor usage more frequently",
            ]
        
        else:  # EXCEEDED
            return [
                "CRITICAL: Switch all agents to Ollama immediately",
                "Pause HuggingFace Pro endpoints",
                "Alert system administrator",
                "Resume HF Pro usage tomorrow (daily budget) or next month (monthly budget)",
                "Review usage patterns for optimization",
            ]

    def estimate_cost(
        self,
        tokens: int,
        requests: int = 1,
    ) -> Dict[str, float]:
        """Estimate cost for planned usage.
        
        Args:
            tokens: Number of tokens to generate
            requests: Number of requests
            
        Returns:
            Dict with cost estimates
        """
        cost_per_request = (tokens / 1000.0) * self.cost_per_1k_tokens
        total_cost = cost_per_request * requests
        
        return {
            "tokens": tokens,
            "requests": requests,
            "cost_per_request_gbp": cost_per_request,
            "total_cost_gbp": total_cost,
            "daily_budget": self.budget_daily,
            "monthly_budget": self.budget_monthly,
            "daily_budget_pct": (total_cost / self.budget_daily) * 100,
            "monthly_budget_pct": (total_cost / self.budget_monthly) * 100,
        }

    def should_use_hf_pro(self, time_window: str = "daily") -> bool:
        """Check if HF Pro should be used based on budget.
        
        Args:
            time_window: "daily" or "monthly"
            
        Returns:
            True if safe to use HF Pro, False if should fallback to Ollama
        """
        budget_check = self.check_budget(time_window)
        return budget_check["status"] != "EXCEEDED"

    def get_summary_report(self) -> str:
        """Generate human-readable summary report.
        
        Returns:
            Formatted summary string
        """
        daily = self.check_budget("daily")
        monthly = self.check_budget("monthly")
        
        report = []
        report.append("=" * 60)
        report.append("HuggingFace Pro Cost Monitor - Summary Report")
        report.append("=" * 60)
        
        # Daily stats
        report.append(f"\n📅 DAILY ({datetime.now().strftime('%Y-%m-%d')})")
        report.append(f"   Status: {daily['status']}")
        report.append(f"   Budget: £{daily['budget']:.2f}")
        report.append(f"   Spent: £{daily['spent']:.2f} ({daily['percentage']:.1f}%)")
        report.append(f"   Remaining: £{daily['remaining']:.2f}")
        report.append(f"   Requests: {daily['stats']['total_requests']}")
        report.append(f"   Tokens: {daily['stats']['total_tokens']:,}")
        
        # Monthly stats  
        report.append(f"\n📊 MONTHLY (Last 30 days)")
        report.append(f"   Status: {monthly['status']}")
        report.append(f"   Budget: £{monthly['budget']:.2f}")
        report.append(f"   Spent: £{monthly['spent']:.2f} ({monthly['percentage']:.1f}%)")
        report.append(f"   Remaining: £{monthly['remaining']:.2f}")
        report.append(f"   Requests: {monthly['stats']['total_requests']}")
        report.append(f"   Tokens: {monthly['stats']['total_tokens']:,}")
        
        # Actions
        if daily['status'] != "OK" or monthly['status'] != "OK":
            report.append(f"\n⚠️  RECOMMENDED ACTIONS:")
            for action in daily['actions'] if daily['status'] != "OK" else monthly['actions']:
                report.append(f"   - {action}")
        
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)


# Convenience function for CrewAI integration
def check_hf_budget() -> str:
    """Check HF Pro budget and return formatted status.
    
    Returns:
        Formatted budget status string
    """
    monitor = HFCostMonitor()
    return monitor.get_summary_report()

