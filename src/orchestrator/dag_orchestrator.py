"""DAG-Based Orchestrator

Replaces linear sequential execution with parallel DAG execution.
Architecture: architect → parallel{builder, docs} → qa
"""

import asyncio
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional

from config import get_provider, PROVIDER_OPTIONS
from src.core.models import Job, JobSpec, JobStatus, StepResult, Artifact, Failure
from src.core.dag import DAG, DAGNode, run_dag
from src.core.events import EventEmitter
from src.core.manifest import RunManager
from src.core.filestore import FileStore


class DAGOrchestrator:
    """
    Main orchestrator using DAG for parallel execution.
    
    Workflow:
    1. Architect designs system (sequential start)
    2. Builder + Docs run in parallel (depend on architect)
    3. QA validates everything (depends on builder + docs)
    """
    
    def __init__(self, job_spec: JobSpec):
        self.spec = job_spec
        self.job_id = f"job_{uuid.uuid4().hex[:12]}"
        self.provider = None
        self.run_manager = None
        self.events = None
        self.filestore = None
    
    async def execute(self) -> Job:
        """
        Execute the job using DAG-based orchestration.
        
        Returns:
            Completed Job instance with all results
        """
        # Initialize job
        job = Job(
            job_id=self.job_id,
            spec=self.spec,
            status=JobStatus.RUNNING
        )
        
        # Setup run directory
        self.run_manager = RunManager(self.job_id)
        run_dir = self.run_manager.create_structure(self.spec)
        job.run_dir = str(run_dir)
        
        # Setup event logging
        events_path = run_dir / "events.jsonl"
        self.events = EventEmitter(events_path)
        
        # Setup file store
        self.filestore = FileStore(run_dir / "outputs")
        
        # Initialize provider
        self.provider = get_provider()
        
        # Emit job start event
        self.events.job_started(
            self.job_id,
            {
                "project": self.spec.project,
                "provider": self.spec.provider,
                "task_description": self.spec.task_description
            }
        )
        
        try:
            # Build DAG
            dag = self._build_dag()
            
            # Execute DAG
            context = {
                "job_id": self.job_id,
                "spec": self.spec,
                "provider": self.provider,
                "filestore": self.filestore,
                "events": self.events,
                "run_dir": run_dir,
            }
            
            results = await run_dag(
                dag=dag,
                job_id=self.job_id,
                context=context,
                events=self.events,
                concurrency=self.spec.concurrency,
                timeout_s=self.spec.timeout_s
            )
            
            # Collect results
            for step_id, result in results.items():
                job.add_step_result(result)
            
            # Mark success
            job.mark_completed(JobStatus.SUCCEEDED)
            self.events.job_succeeded(
                self.job_id,
                job.duration_s,
                len(job.artifacts)
            )
            
        except Exception as e:
            # Mark failure
            job.mark_completed(JobStatus.FAILED)
            self.events.job_failed(self.job_id, str(e), job.duration_s)
            
            # Add failure to job
            failure = Failure(
                kind="provider",
                step="orchestrator",
                message=str(e),
                data={"exception_type": type(e).__name__}
            )
            job.failures.append(failure)
        
        finally:
            # Update manifest
            self.run_manager.update_manifest(job)
            self.events.close()
        
        return job
    
    def _build_dag(self) -> DAG:
        """
        Build the execution DAG.
        
        DAG structure:
            architect (sequential start)
                ├─→ builder (parallel)
                └─→ docs (parallel)
                    └─→ qa (sequential end, needs both builder + docs)
        
        Returns:
            Configured DAG ready for execution
        """
        dag = DAG()
        
        # Node 1: Architect (no dependencies)
        dag.add_node(DAGNode(
            id="architect",
            fn=self._step_architect,
            needs=[],
            description="Design system architecture"
        ))
        
        # Node 2: Builder (depends on architect)
        dag.add_node(DAGNode(
            id="builder",
            fn=self._step_builder,
            needs=["architect"],
            description="Implement code based on architecture"
        ))
        
        # Node 3: Docs (depends on architect, runs in parallel with builder)
        dag.add_node(DAGNode(
            id="docs",
            fn=self._step_docs,
            needs=["architect"],
            description="Generate documentation"
        ))
        
        # Node 4: QA (depends on both builder and docs)
        dag.add_node(DAGNode(
            id="qa",
            fn=self._step_qa,
            needs=["builder", "docs"],
            description="Test and validate everything"
        ))
        
        return dag
    
    async def _step_architect(
        self,
        context: dict,
        dep_results: dict[str, StepResult]
    ) -> dict:
        """
        Architect step: Design system architecture.
        
        Args:
            context: Shared job context
            dep_results: Results from dependencies (empty for architect)
            
        Returns:
            Architecture design as dict
        """
        provider = context["provider"]
        spec = context["spec"]
        
        messages = [
            {
                "role": "system",
                "content": "You are a system architect. Design a complete system architecture."
            },
            {
                "role": "user",
                "content": f"Design architecture for: {spec.task_description}\n\n"
                          f"Include: tech stack, components, data flow, database schema, API endpoints."
            }
        ]
        
        start = datetime.utcnow()
        response = provider.generate(messages, **PROVIDER_OPTIONS)
        duration = (datetime.utcnow() - start).total_seconds()
        
        # Log provider call
        context["events"].provider_call(
            context["job_id"],
            "architect",
            provider.name,
            duration
        )
        
        return {
            "architecture": response,
            "provider_calls": 1
        }
    
    async def _step_builder(
        self,
        context: dict,
        dep_results: dict[str, StepResult]
    ) -> dict:
        """
        Builder step: Implement code based on architecture.
        
        Runs in parallel with docs step.
        """
        provider = context["provider"]
        spec = context["spec"]
        filestore = context["filestore"]
        
        # Get architecture from previous step
        architecture = dep_results["architect"].output.get("architecture", "")
        
        messages = [
            {
                "role": "system",
                "content": """You are a senior full-stack engineer.

CRITICAL: Generate complete, runnable code with ALL imports and implementations.
Include: FastAPI, SQLAlchemy, Pydantic models, endpoints, error handling."""
            },
            {
                "role": "user",
                "content": f"Architecture:\n{architecture}\n\n"
                          f"Task: {spec.task_description}\n\n"
                          f"Generate complete main.py with all imports, models, and endpoints."
            }
        ]
        
        start = datetime.utcnow()
        code = provider.generate(messages, **PROVIDER_OPTIONS)
        duration = (datetime.utcnow() - start).total_seconds()
        
        # Write generated code
        main_path, sha256, size = filestore.safe_write(
            f"{spec.project}/main.py",
            code,
            mode="overwrite"
        )
        
        # Create artifact
        artifact = Artifact(
            path=f"{spec.project}/main.py",
            sha256=sha256,
            size_bytes=size,
            media_type="text/x-python"
        )
        
        context["events"].artifact_created(
            context["job_id"],
            "builder",
            artifact.path,
            artifact.sha256,
            artifact.size_bytes
        )
        
        context["events"].provider_call(
            context["job_id"],
            "builder",
            provider.name,
            duration
        )
        
        return {
            "files_created": 1,
            "main_file": str(main_path),
            "artifact": artifact,
            "provider_calls": 1
        }
    
    async def _step_docs(
        self,
        context: dict,
        dep_results: dict[str, StepResult]
    ) -> dict:
        """
        Docs step: Generate documentation.
        
        Runs in parallel with builder step.
        """
        provider = context["provider"]
        spec = context["spec"]
        filestore = context["filestore"]
        
        architecture = dep_results["architect"].output.get("architecture", "")
        
        messages = [
            {
                "role": "system",
                "content": "You are a technical writer. Create clear, beginner-friendly documentation."
            },
            {
                "role": "user",
                "content": f"Create README.md for:\n{spec.task_description}\n\n"
                          f"Architecture:\n{architecture}\n\n"
                          f"Include: overview, quickstart, setup instructions, API documentation."
            }
        ]
        
        start = datetime.utcnow()
        readme = provider.generate(messages, **PROVIDER_OPTIONS)
        duration = (datetime.utcnow() - start).total_seconds()
        
        # Write README
        readme_path, sha256, size = filestore.safe_write(
            f"{spec.project}/README.md",
            readme,
            mode="overwrite"
        )
        
        artifact = Artifact(
            path=f"{spec.project}/README.md",
            sha256=sha256,
            size_bytes=size,
            media_type="text/markdown"
        )
        
        context["events"].artifact_created(
            context["job_id"],
            "docs",
            artifact.path,
            artifact.sha256,
            artifact.size_bytes
        )
        
        context["events"].provider_call(
            context["job_id"],
            "docs",
            provider.name,
            duration
        )
        
        return {
            "files_created": 1,
            "readme_file": str(readme_path),
            "artifact": artifact,
            "provider_calls": 1
        }
    
    async def _step_qa(
        self,
        context: dict,
        dep_results: dict[str, StepResult]
    ) -> dict:
        """
        QA step: Test and validate everything.
        
        Depends on both builder and docs completing.
        """
        provider = context["provider"]
        filestore = context["filestore"]
        
        # Get outputs from builder
        builder_output = dep_results["builder"].output
        main_file = builder_output.get("main_file", "")
        
        # Read the generated code
        if main_file:
            code_path = Path(main_file)
            if code_path.exists():
                code = code_path.read_text()
            else:
                code = "File not found"
        else:
            code = "No code generated"
        
        messages = [
            {
                "role": "system",
                "content": "You are a QA engineer. Test code quality, completeness, and correctness."
            },
            {
                "role": "user",
                "content": f"Review this code:\n\n```python\n{code}\n```\n\n"
                          f"Check: imports, endpoints, error handling, database setup. "
                          f"Provide validation report."
            }
        ]
        
        start = datetime.utcnow()
        qa_report = provider.generate(messages, **PROVIDER_OPTIONS)
        duration = (datetime.utcnow() - start).total_seconds()
        
        context["events"].provider_call(
            context["job_id"],
            "qa",
            provider.name,
            duration
        )
        
        return {
            "qa_report": qa_report,
            "code_reviewed": bool(code and code != "No code generated"),
            "provider_calls": 1
        }


def run_orchestrator(spec: JobSpec) -> Job:
    """
    Convenience function to run orchestrator synchronously.
    
    Args:
        spec: Job specification
        
    Returns:
        Completed Job instance
    """
    orchestrator = DAGOrchestrator(spec)
    return asyncio.run(orchestrator.execute())

