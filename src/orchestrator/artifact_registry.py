"""Artifact versioning and lineage tracking system."""

import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ArtifactRegistry:
    """Manages versioning and lineage of all artifacts."""

    def __init__(self, registry_dir: str = "artifact_registry"):
        """Initialize artifact registry.
        
        Args:
            registry_dir: Directory to store artifact metadata
        """
        self.registry_dir = Path(registry_dir)
        self.registry_dir.mkdir(exist_ok=True)
        self.catalog_file = self.registry_dir / "catalog.json"
        self._load_catalog()

    def _load_catalog(self) -> None:
        """Load or initialize catalog."""
        if self.catalog_file.exists():
            with open(self.catalog_file) as f:
                self.catalog = json.load(f)
        else:
            self.catalog = {"artifacts": {}, "lineage": {}}

    def _save_catalog(self) -> None:
        """Persist catalog to disk."""
        with open(self.catalog_file, "w") as f:
            json.dump(self.catalog, f, indent=2)

    def _compute_hash(self, file_path: str) -> str:
        """Compute SHA256 hash of file."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def register_artifact(
        self,
        artifact_id: str,
        artifact_path: str,
        artifact_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        parent_artifacts: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Register artifact with versioning.
        
        Args:
            artifact_id: Unique identifier (e.g., "model_v1", "dataset_train_v2")
            artifact_path: Full path to artifact file/directory
            artifact_type: Type (model, dataset, report, metrics)
            metadata: Additional metadata (author, description, etc)
            parent_artifacts: IDs of artifacts this one depends on
            
        Returns:
            Registration record with hash, version, timestamp
        """
        artifact_path = Path(artifact_path)
        
        if not artifact_path.exists():
            raise FileNotFoundError(f"Artifact not found: {artifact_path}")
        
        # Compute hash
        artifact_hash = self._compute_hash(str(artifact_path))
        
        # Determine version
        version = 1
        if artifact_id in self.catalog["artifacts"]:
            version = len(self.catalog["artifacts"][artifact_id]["versions"]) + 1
        
        record = {
            "id": artifact_id,
            "type": artifact_type,
            "version": version,
            "hash": artifact_hash,
            "path": str(artifact_path),
            "size_bytes": artifact_path.stat().st_size,
            "registered_at": datetime.now().isoformat(),
            "metadata": metadata or {},
            "parent_artifacts": parent_artifacts or [],
        }
        
        if artifact_id not in self.catalog["artifacts"]:
            self.catalog["artifacts"][artifact_id] = {"versions": []}
        
        self.catalog["artifacts"][artifact_id]["versions"].append(record)
        
        # Track lineage
        if parent_artifacts:
            self.catalog["lineage"][artifact_id] = {
                "parents": parent_artifacts,
                "created_at": datetime.now().isoformat(),
            }
        
        self._save_catalog()
        logger.info(f"Artifact registered: {artifact_id} v{version}")
        
        return record

    def get_artifact(self, artifact_id: str, version: Optional[int] = None) -> Dict[str, Any]:
        """Get artifact record by ID and optional version.
        
        Args:
            artifact_id: Artifact identifier
            version: Specific version (defaults to latest)
            
        Returns:
            Artifact record
        """
        if artifact_id not in self.catalog["artifacts"]:
            raise ValueError(f"Artifact not found: {artifact_id}")
        
        versions = self.catalog["artifacts"][artifact_id]["versions"]
        
        if version is None:
            return versions[-1]
        else:
            for v in versions:
                if v["version"] == version:
                    return v
            raise ValueError(f"Version {version} not found for {artifact_id}")

    def get_lineage(self, artifact_id: str, depth: int = 999) -> Dict[str, Any]:
        """Get complete lineage tree for artifact.
        
        Args:
            artifact_id: Artifact ID
            depth: Recursion depth for parent traversal
            
        Returns:
            Lineage tree with dependencies
        """
        if depth == 0:
            return {}
        
        lineage = {}
        
        if artifact_id in self.catalog["lineage"]:
            parents = self.catalog["lineage"][artifact_id]["parents"]
            lineage["parents"] = parents
            lineage["children"] = self._get_children(artifact_id)
            
            for parent in parents:
                lineage[parent] = self.get_lineage(parent, depth - 1)
        
        return lineage

    def _get_children(self, artifact_id: str) -> List[str]:
        """Get all artifacts that depend on this one."""
        children = []
        for aid, lin in self.catalog["lineage"].items():
            if artifact_id in lin.get("parents", []):
                children.append(aid)
        return children

    def verify_artifact_integrity(self, artifact_id: str, version: Optional[int] = None) -> bool:
        """Verify artifact hasn't been corrupted.
        
        Args:
            artifact_id: Artifact ID
            version: Specific version
            
        Returns:
            True if hash matches
        """
        try:
            record = self.get_artifact(artifact_id, version)
            current_hash = self._compute_hash(record["path"])
            
            if current_hash == record["hash"]:
                logger.info(f"Integrity verified: {artifact_id}")
                return True
            else:
                logger.warning(f"Integrity check FAILED: {artifact_id}")
                return False
        except Exception as e:
            logger.error(f"Integrity check error: {e}")
            return False

    def list_artifacts(self, artifact_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all registered artifacts, optionally filtered by type.
        
        Args:
            artifact_type: Filter by type (model, dataset, etc)
            
        Returns:
            List of artifact records
        """
        artifacts = []
        for artifact_id, data in self.catalog["artifacts"].items():
            latest = data["versions"][-1]
            if artifact_type is None or latest["type"] == artifact_type:
                artifacts.append(latest)
        
        return artifacts

    def export_manifest(self, output_path: str) -> None:
        """Export complete artifact manifest for reproducibility.
        
        Args:
            output_path: Path to save manifest JSON
        """
        manifest = {
            "exported_at": datetime.now().isoformat(),
            "artifacts": self.catalog["artifacts"],
            "lineage": self.catalog["lineage"],
            "summary": {
                "total_artifacts": len(self.catalog["artifacts"]),
                "artifact_types": self._count_by_type(),
            },
        }
        
        with open(output_path, "w") as f:
            json.dump(manifest, f, indent=2)
        
        logger.info(f"Manifest exported to {output_path}")

    def _count_by_type(self) -> Dict[str, int]:
        """Count artifacts by type."""
        counts = {}
        for data in self.catalog["artifacts"].values():
            if data["versions"]:
                atype = data["versions"][-1]["type"]
                counts[atype] = counts.get(atype, 0) + 1
        return counts

