"""Model training orchestrator with experiment tracking."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

logger = logging.getLogger(__name__)


class TrainingOrchestrator:
    """Orchestrates model training, evaluation, and artifact management."""

    def __init__(self, experiment_dir: str = "experiments"):
        """Initialize orchestrator.
        
        Args:
            experiment_dir: Directory to store experiments
        """
        self.experiment_dir = Path(experiment_dir)
        self.experiment_dir.mkdir(exist_ok=True)

    def create_experiment(
        self,
        name: str,
        config: Dict[str, Any],
        description: str = "",
    ) -> Dict[str, Any]:
        """Create new experiment tracking session.
        
        Args:
            name: Experiment name
            config: Training configuration (model type, hyperparams, etc)
            description: Experiment description
            
        Returns:
            Experiment metadata with ID, paths, timestamp
        """
        exp_id = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        exp_path = self.experiment_dir / exp_id
        exp_path.mkdir(exist_ok=True)
        
        metadata = {
            "id": exp_id,
            "name": name,
            "description": description,
            "config": config,
            "created_at": datetime.now().isoformat(),
            "status": "initialized",
            "paths": {
                "root": str(exp_path),
                "models": str(exp_path / "models"),
                "metrics": str(exp_path / "metrics"),
                "artifacts": str(exp_path / "artifacts"),
            },
        }
        
        # Create subdirectories
        for subdir in metadata["paths"].values():
            Path(subdir).mkdir(exist_ok=True)
        
        # Save metadata
        meta_path = exp_path / "metadata.json"
        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Experiment created: {exp_id}")
        return metadata

    def log_metrics(
        self,
        exp_id: str,
        metrics: Dict[str, float],
        step: int = 0,
    ) -> bool:
        """Log training metrics for experiment.
        
        Args:
            exp_id: Experiment ID
            metrics: Dict of metric_name -> value
            step: Training step/epoch
            
        Returns:
            Success flag
        """
        try:
            exp_path = self.experiment_dir / exp_id
            metrics_file = exp_path / "metrics" / f"metrics_step_{step}.json"
            
            metrics_data = {
                "step": step,
                "timestamp": datetime.now().isoformat(),
                "metrics": metrics,
            }
            
            with open(metrics_file, "w") as f:
                json.dump(metrics_data, f, indent=2)
            
            logger.info(f"Metrics logged for {exp_id} step {step}")
            return True
        except Exception as e:
            logger.error(f"Failed to log metrics: {e}")
            return False

    def save_model(
        self,
        exp_id: str,
        model_path: str,
        model_name: str = "model.pkl",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Save trained model with metadata.
        
        Args:
            exp_id: Experiment ID
            model_path: Path to model file
            model_name: Name to save model as
            metadata: Additional metadata (framework, version, etc)
            
        Returns:
            Success flag
        """
        try:
            import shutil
            
            exp_path = self.experiment_dir / exp_id
            model_dst = exp_path / "models" / model_name
            
            shutil.copy(model_path, model_dst)
            
            # Save model metadata
            meta_path = exp_path / "models" / f"{model_name}.meta.json"
            model_meta = {
                "name": model_name,
                "path": str(model_dst),
                "saved_at": datetime.now().isoformat(),
                "original_path": model_path,
                "metadata": metadata or {},
            }
            
            with open(meta_path, "w") as f:
                json.dump(model_meta, f, indent=2)
            
            logger.info(f"Model saved: {model_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            return False

    def evaluate_model(
        self,
        exp_id: str,
        test_df: pd.DataFrame,
        y_true: pd.Series,
        y_pred: pd.Series,
        task: str = "classification",
    ) -> Dict[str, float]:
        """Evaluate model performance.
        
        Args:
            exp_id: Experiment ID
            test_df: Test features
            y_true: True labels
            y_pred: Predictions
            task: "classification" or "regression"
            
        Returns:
            Dict of evaluation metrics
        """
        try:
            from sklearn.metrics import (
                accuracy_score,
                precision_score,
                recall_score,
                f1_score,
                mean_squared_error,
                mean_absolute_error,
                r2_score,
            )
            
            metrics = {}
            
            if task == "classification":
                metrics["accuracy"] = float(accuracy_score(y_true, y_pred))
                metrics["precision"] = float(
                    precision_score(y_true, y_pred, average="weighted", zero_division=0)
                )
                metrics["recall"] = float(
                    recall_score(y_true, y_pred, average="weighted", zero_division=0)
                )
                metrics["f1"] = float(
                    f1_score(y_true, y_pred, average="weighted", zero_division=0)
                )
            elif task == "regression":
                metrics["mse"] = float(mean_squared_error(y_true, y_pred))
                metrics["mae"] = float(mean_absolute_error(y_true, y_pred))
                metrics["r2"] = float(r2_score(y_true, y_pred))
            
            metrics["task"] = task
            metrics["n_samples"] = len(test_df)
            
            # Save evaluation report
            eval_path = self.experiment_dir / exp_id / "metrics" / "evaluation.json"
            eval_report = {
                "timestamp": datetime.now().isoformat(),
                "metrics": metrics,
                "test_size": len(test_df),
            }
            
            with open(eval_path, "w") as f:
                json.dump(eval_report, f, indent=2)
            
            logger.info(f"Model evaluated with {task} metrics")
            return metrics
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            return {}

    def get_experiment_summary(self, exp_id: str) -> Dict[str, Any]:
        """Get complete experiment summary.
        
        Args:
            exp_id: Experiment ID
            
        Returns:
            Summary with metadata, metrics, and status
        """
        try:
            exp_path = self.experiment_dir / exp_id
            meta_path = exp_path / "metadata.json"
            
            with open(meta_path) as f:
                metadata = json.load(f)
            
            # Collect all metrics
            metrics_dir = exp_path / "metrics"
            all_metrics = []
            if metrics_dir.exists():
                for mf in sorted(metrics_dir.glob("metrics_step_*.json")):
                    with open(mf) as f:
                        all_metrics.append(json.load(f))
            
            # Get evaluation if exists
            eval_file = metrics_dir / "evaluation.json"
            evaluation = {}
            if eval_file.exists():
                with open(eval_file) as f:
                    evaluation = json.load(f)
            
            return {
                "experiment": metadata,
                "training_metrics": all_metrics,
                "evaluation": evaluation,
                "model_files": [str(f) for f in (exp_path / "models").glob("*.pkl")],
            }
        except Exception as e:
            logger.error(f"Failed to get experiment summary: {e}")
            return {}

