"""Safety validation module for model outputs.

Validates model outputs for toxicity, PII leakage, bias, and other
safety concerns before deployment.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from crewai.tools import tool

logger = logging.getLogger(__name__)


class SafetyValidator:
    """Validates model outputs for safety and bias."""

    def __init__(self, device: str = "mps"):
        """Initialize safety validator.
        
        Args:
            device: Device for model inference (mps, cuda, cpu)
        """
        self.device = device
        self.toxicity_detector = None
        self.pii_detector = None
        self._models_loaded = False

    def _load_models(self) -> None:
        """Lazy load safety models on first use."""
        if self._models_loaded:
            return
            
        try:
            from transformers import pipeline
            
            logger.info("Loading safety models...")
            
            # Toxicity detection
            self.toxicity_detector = pipeline(
                "text-classification",
                model="unitary/toxic-bert",
                device=self.device
            )
            
            # PII detection (NER for entities)
            try:
                self.pii_detector = pipeline(
                    "ner",
                    model="StanfordAIMI/stanford-deidentifier-base",
                    device=self.device,
                    aggregation_strategy="simple"
                )
            except Exception as e:
                logger.warning(f"PII detector not available: {e}")
                self.pii_detector = None
            
            self._models_loaded = True
            logger.info("Safety models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load safety models: {e}")
            raise

    def check_output_safety(self, text: str) -> Dict[str, Any]:
        """Validate model output for safety.
        
        Args:
            text: Model output text to validate
            
        Returns:
            Dict with keys: passed (bool), issues (List), scores (Dict)
        """
        self._load_models()
        
        results = {
            "passed": True,
            "issues": [],
            "scores": {},
        }
        
        try:
            # Check toxicity
            tox_result = self.toxicity_detector(text)[0]
            results["scores"]["toxicity"] = {
                "label": tox_result["label"],
                "score": float(tox_result["score"]),
            }
            
            if tox_result["label"] == "toxic" and tox_result["score"] > 0.7:
                results["passed"] = False
                results["issues"].append(
                    f"High toxicity detected: {tox_result['score']:.2f}"
                )
            
            # Check PII if detector available
            if self.pii_detector:
                pii_entities = self.pii_detector(text)
                sensitive_entities = [
                    e for e in pii_entities 
                    if e["entity_group"] in ["PER", "ORG", "LOC", "MISC"]
                    and e["score"] > 0.8
                ]
                
                if sensitive_entities:
                    results["passed"] = False
                    results["issues"].append(
                        f"PII detected: {len(sensitive_entities)} sensitive entities"
                    )
                    results["scores"]["pii_entities"] = [
                        {
                            "text": e["word"],
                            "type": e["entity_group"],
                            "score": float(e["score"]),
                        }
                        for e in sensitive_entities
                    ]
            
            # Check length (basic sanity)
            if len(text.strip()) == 0:
                results["passed"] = False
                results["issues"].append("Empty output detected")
            
            return results
            
        except Exception as e:
            logger.error(f"Safety check failed: {e}")
            return {
                "passed": False,
                "issues": [f"Safety check error: {str(e)}"],
                "scores": {},
            }

    def check_bias(
        self,
        predictions: List[Any],
        sensitive_features: List[Any],
        y_true: Optional[List[Any]] = None,
    ) -> Dict[str, Any]:
        """Check for demographic bias using fairlearn.
        
        Args:
            predictions: Model predictions
            sensitive_features: Protected attributes (gender, race, etc)
            y_true: True labels (if available)
            
        Returns:
            Dict with bias metrics and pass/fail status
        """
        try:
            from fairlearn.metrics import (
                demographic_parity_difference,
                equalized_odds_difference,
            )
            
            results = {
                "passed": True,
                "metrics": {},
                "threshold": 0.1,  # 10% maximum disparity
            }
            
            # Demographic parity (no ground truth needed)
            dp_diff = demographic_parity_difference(
                y_true=predictions if y_true is None else y_true,
                y_pred=predictions,
                sensitive_features=sensitive_features,
            )
            results["metrics"]["demographic_parity_difference"] = float(dp_diff)
            
            # Equalized odds (requires ground truth)
            if y_true is not None:
                eo_diff = equalized_odds_difference(
                    y_true=y_true,
                    y_pred=predictions,
                    sensitive_features=sensitive_features,
                )
                results["metrics"]["equalized_odds_difference"] = float(eo_diff)
            
            # Check if exceeded threshold
            for metric, value in results["metrics"].items():
                if abs(value) > results["threshold"]:
                    results["passed"] = False
                    break
            
            return results
            
        except Exception as e:
            logger.error(f"Bias check failed: {e}")
            return {
                "passed": False,
                "metrics": {},
                "error": str(e),
            }


@tool("Validate Model Safety")
def validate_model_safety(model_output: str) -> str:
    """CrewAI tool to run safety checks on model output.
    
    Args:
        model_output: Model-generated text to validate
        
    Returns:
        Validation result as JSON string
    """
    validator = SafetyValidator()
    result = validator.check_output_safety(model_output)
    
    if result["passed"]:
        return json.dumps({"status": "PASSED", "result": result}, indent=2)
    else:
        return json.dumps({"status": "FAILED", "result": result}, indent=2)

