"""Cost Tracking for HuggingFace Pro Usage"""
import json
import time
from pathlib import Path
from typing import Dict, List


class CostTracker:
    """Track HuggingFace Pro API usage and costs"""
    
    def __init__(self, log_file: str = "logs/hf_usage.json"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.usage_data = self._load()
    
    def _load(self) -> List[Dict]:
        """Load existing usage data"""
        if self.log_file.exists():
            return json.loads(self.log_file.read_text())
        return []
    
    def track_call(self, model: str, tokens_in: int, tokens_out: int):
        """
        Track a HF Pro API call.
        
        Args:
            model: Model name
            tokens_in: Input tokens
            tokens_out: Output tokens
        """
        entry = {
            "timestamp": time.time(),
            "model": model,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "estimated_cost_usd": (tokens_in * 0.0001 + tokens_out * 0.0002)  # Rough estimate
        }
        self.usage_data.append(entry)
        self._save()
    
    def _save(self):
        """Save usage data"""
        self.log_file.write_text(json.dumps(self.usage_data, indent=2))
    
    def get_total_cost(self) -> float:
        """Get total estimated cost"""
        return sum(entry.get("estimated_cost_usd", 0) for entry in self.usage_data)
    
    def get_total_tokens(self) -> Dict[str, int]:
        """Get total token counts"""
        return {
            "input": sum(e.get("tokens_in", 0) for e in self.usage_data),
            "output": sum(e.get("tokens_out", 0) for e in self.usage_data)
        }

