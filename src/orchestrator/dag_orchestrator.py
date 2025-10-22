"""DAG-Based Orchestrator

Replaces linear sequential execution with parallel DAG execution.
Architecture: architect → parallel{builder, docs} → qa
"""

import asyncio
import uuid
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional

from config import get_provider, PROVIDER_OPTIONS
from src.core.models import Job, JobSpec, JobStatus, StepResult, Artifact, Failure
from src.core.dag import DAG, DAGNode, run_dag, read_completed_steps
from src.core.events import EventEmitter
from src.core.manifest import RunManager
from src.core.filestore import FileStore
from src.core.cache import compute_cache_key, cache_path, read_cache, write_cache


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
    
    async def execute(self, resume: bool = False) -> Job:
        """
        Execute the job using DAG-based orchestration.

        Args:
            resume: If True, skip steps that have already succeeded in
                previous runs (based on events.jsonl)

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
        
        dag: Optional[DAG] = None
        completed_steps: list[str] = []
        pending_steps: list[str] = []

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
                timeout_s=self.spec.timeout_s,
                resume=resume
            )
            
            # Collect results
            for step_id, result in results.items():
                job.add_step_result(result)

            completed_steps = sorted(results.keys())
            if dag is not None:
                pending_steps = sorted(
                    set(dag.nodes.keys()) - set(completed_steps)
                )
            
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

            # Derive completed/pending step lists for manifest
            completed_events = read_completed_steps(events_path)
            completed_steps = sorted(completed_events)
            if dag is not None:
                pending_steps = sorted(set(dag.nodes.keys()) - completed_events)
            else:
                pending_steps = []
        
        finally:
            # Update manifest
            self.run_manager.update_manifest(
                job,
                completed_steps=completed_steps,
                pending_steps=pending_steps
            )
            self.events.close()
        
        return job
    
    async def _call_provider_with_cache(
        self,
        step_id: str,
        messages: list[dict],
        context: dict,
        inputs: dict
    ) -> tuple[str, bool]:
        """
        Call provider with deterministic caching.
        
        Args:
            step_id: Step identifier (e.g., 'architect', 'builder')
            messages: Messages to send to provider
            context: Job context with provider, events, etc.
            inputs: Input data for cache key computation
            
        Returns:
            Tuple of (response, cache_hit)
        """
        provider = context["provider"]
        events = context["events"]
        job_id = context["job_id"]
        
        # Compute cache key
        provider_info = {
            "name": provider.name,
            "model": getattr(provider, "model", "unknown"),
            "opts": PROVIDER_OPTIONS,
        }
        
        cache_key = compute_cache_key(
            provider=provider_info,
            step_id=step_id,
            inputs=inputs
        )
        
        # Check cache
        cache_file = cache_path(job_id, cache_key)
        cached_data = read_cache(cache_file)
        
        if cached_data:
            # Cache hit
            events.cache_hit(job_id, step_id, cache_key)
            return cached_data.get("response", ""), True
        
        # Cache miss - call provider
        events.cache_miss(job_id, step_id, cache_key)

        # Emit llm.request event
        events.llm_request(
            job_id,
            step_id,
            provider.name,
            provider_info["model"]
        )

        start = datetime.utcnow()
        try:
            response = provider.generate(messages, **PROVIDER_OPTIONS)
            duration = (datetime.utcnow() - start).total_seconds()

            # Emit llm.response event (success)
            events.llm_response(
                job_id,
                step_id,
                provider.name,
                duration,
                success=True
            )

            # Log provider call (backward compatibility)
            events.provider_call(
                job_id,
                step_id,
                provider.name,
                duration
            )
        except Exception as e:
            duration = (datetime.utcnow() - start).total_seconds()

            # Emit llm.response event (failure)
            events.llm_response(
                job_id,
                step_id,
                provider.name,
                duration,
                success=False
            )
            raise
        
        # Cache response
        write_cache(cache_file, {
            "response": response,
            "cached_at": datetime.utcnow().isoformat(),
            "cache_key": cache_key,
        })
        
        return response, False
    
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
        
        # Call provider with caching
        response, cache_hit = await self._call_provider_with_cache(
            step_id="architect",
            messages=messages,
            context=context,
            inputs={"task": spec.task_description}
        )
        
        return {
            "architecture": response,
            "provider_calls": 0 if cache_hit else 1,
            "cache_hit": cache_hit
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
        
        # Call provider with caching
        code, cache_hit = await self._call_provider_with_cache(
            step_id="builder",
            messages=messages,
            context=context,
            inputs={"task": spec.task_description, "architecture": architecture[:500]}  # Truncate for key
        )
        
        # Write generated code
        write_result = filestore.safe_write(
            f"{spec.project}/main.py",
            code,
            mode="overwrite",
            emitter=context["events"],
            job_id=context["job_id"],
            step_id="builder"
        )

        # Create artifact
        artifact = Artifact(
            path=f"{spec.project}/main.py",
            sha256=write_result["sha256"],
            size_bytes=write_result["size_bytes"],
            media_type="text/x-python"
        )

        context["events"].artifact_created(
            context["job_id"],
            "builder",
            artifact.path,
            artifact.sha256,
            artifact.size_bytes
        )

        return {
            "files_created": 1,
            "main_file": str(write_result["path"]),
            "artifact": artifact,
            "provider_calls": 0 if cache_hit else 1,
            "cache_hit": cache_hit
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
        
        # Call provider with caching
        readme, cache_hit = await self._call_provider_with_cache(
            step_id="docs",
            messages=messages,
            context=context,
            inputs={"task": spec.task_description, "architecture": architecture[:500]}
        )
        
        # Write README
        write_result = filestore.safe_write(
            f"{spec.project}/README.md",
            readme,
            mode="overwrite",
            emitter=context["events"],
            job_id=context["job_id"],
            step_id="docs"
        )

        artifact = Artifact(
            path=f"{spec.project}/README.md",
            sha256=write_result["sha256"],
            size_bytes=write_result["size_bytes"],
            media_type="text/markdown"
        )

        context["events"].artifact_created(
            context["job_id"],
            "docs",
            artifact.path,
            artifact.sha256,
            artifact.size_bytes
        )

        return {
            "files_created": 1,
            "readme_file": str(write_result["path"]),
            "artifact": artifact,
            "provider_calls": 0 if cache_hit else 1,
            "cache_hit": cache_hit
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
        
        # Call provider with caching (use code hash for cache key)
        code_hash = hashlib.sha256(code.encode()).hexdigest()[:16]
        qa_report, cache_hit = await self._call_provider_with_cache(
            step_id="qa",
            messages=messages,
            context=context,
            inputs={"code_hash": code_hash}
        )
        
        return {
            "qa_report": qa_report,
            "code_reviewed": bool(code and code != "No code generated"),
            "provider_calls": 0 if cache_hit else 1,
            "cache_hit": cache_hit
        }


def run_orchestrator(spec: JobSpec, resume: bool = False) -> Job:
    """
    Convenience function to run orchestrator synchronously.
    
    Args:
        spec: Job specification
        resume: Whether to skip previously completed steps
        
    Returns:
        Completed Job instance
    """
    orchestrator = DAGOrchestrator(spec)
    return asyncio.run(orchestrator.execute(resume=resume))
