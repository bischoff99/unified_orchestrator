"""CLI for Unified Orchestrator

Command-line interface using Typer for running jobs and inspecting results.
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, Optional

import typer
import yaml
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.core.models import JobSpec
from src.orchestrator.dag_orchestrator import run_orchestrator
from src.core.events import read_events, filter_events
from src.core.manifest import RunManager

app = typer.Typer(
    name="orchestrator",
    help="Multi-agent AI orchestration with DAG execution",
    add_completion=False
)
console = Console()


def _summarize_steps_from_events(
    events: list[dict],
    pending_from_manifest: Optional[list[str]] = None,
) -> list[Dict[str, Any]]:
    """
    Build step status summary from event stream.

    Args:
        events: List of event dicts loaded from events.jsonl
        pending_from_manifest: Optional list of pending steps to include

    Returns:
        List of step summary dicts sorted by first timestamp
    """
    summaries: Dict[str, Dict[str, Any]] = {}

    for event in events:
        step_id = event.get("step")
        if not step_id:
            continue

        entry = summaries.setdefault(
            step_id,
            {
                "step": step_id,
                "status": "pending",
                "started_ts": None,
                "finished_ts": None,
                "duration_s": None,
                "provider_calls": 0,
                "message": "",
                "first_ts": event.get("ts"),
            },
        )

        event_type = event.get("type")
        if event_type == "step.started":
            entry["status"] = "running"
            entry["started_ts"] = event.get("ts")
        elif event_type == "step.succeeded":
            entry["status"] = "succeeded"
            entry["finished_ts"] = event.get("ts")
            entry["duration_s"] = event.get("duration_s") or event.get("data", {}).get(
                "duration_s"
            )
            entry["provider_calls"] = event.get("provider_calls") or event.get(
                "data", {}
            ).get("provider_calls", 0)
        elif event_type == "step.failed":
            entry["status"] = "failed"
            entry["finished_ts"] = event.get("ts")
            entry["message"] = event.get("message") or event.get("data", {}).get(
                "message", ""
            )
        elif event_type == "step.skipped":
            entry["status"] = "skipped"
            entry["finished_ts"] = event.get("ts")
            entry["message"] = (
                event.get("data", {}).get("reason") if event.get("data") else ""
            )

    if pending_from_manifest:
        for step_id in pending_from_manifest:
            summaries.setdefault(
                step_id,
                {
                    "step": step_id,
                    "status": "pending",
                    "started_ts": None,
                    "finished_ts": None,
                    "duration_s": None,
                    "provider_calls": 0,
                    "message": "",
                    "first_ts": None,
                },
            )

    return sorted(
        summaries.values(),
        key=lambda item: (
            item["started_ts"] or item["finished_ts"] or item["first_ts"] or item["step"]
        ),
    )


@app.command()
def run(
    spec: Path = typer.Argument(
        ...,
        help="Path to job spec YAML file (e.g., examples/tiny_spec.yaml)",
        exists=True
    ),
    provider: str = typer.Option(
        None,
        "--provider",
        "-p",
        help="Override provider (ollama, openai, anthropic, mlx)"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed execution logs"
    ),
    resume: bool = typer.Option(
        False,
        "--resume",
        help="Resume a previously started run (skip completed steps)"
    )
):
    """
    Run an orchestration job from a spec file.
    
    Example:
        orchestrator run examples/tiny_spec.yaml
        orchestrator run my_spec.yaml --provider openai --verbose
    """
    console.print(f"\n[bold blue]🚀 Starting Orchestration[/bold blue]\n")
    
    # Load spec
    try:
        with open(spec, 'r') as f:
            spec_data = yaml.safe_load(f)
        
        job_spec = JobSpec(**spec_data)
        
        # Override provider if specified
        if provider:
            job_spec.provider = provider
        
        console.print(f"📋 Project: [green]{job_spec.project}[/green]")
        console.print(f"🎯 Task: {job_spec.task_description}")
        console.print(f"🤖 Provider: [yellow]{job_spec.provider}[/yellow]")
        console.print(f"⚡ Concurrency: {job_spec.concurrency}\n")
        if resume:
            console.print("[cyan]Resuming run: completed steps will be skipped[/cyan]\n")
        
    except Exception as e:
        console.print(f"[red]❌ Failed to load spec: {e}[/red]")
        raise typer.Exit(1)
    
    # Execute job
    try:
        job = run_orchestrator(job_spec, resume=resume)
        
        # Display results
        console.print(f"\n[bold green]✅ Job Complete[/bold green]\n")
        console.print(f"📁 Run ID: [cyan]{job.job_id}[/cyan]")
        console.print(f"📂 Run Directory: {job.run_dir}")
        console.print(f"⏱️  Duration: {job.duration_s:.1f}s")
        console.print(f"📊 Status: [{'green' if job.status.value == 'succeeded' else 'red'}]{job.status.value}[/]")
        console.print(f"📦 Artifacts: {len(job.artifacts)}")
        
        # Show artifacts
        if job.artifacts:
            console.print("\n[bold]Generated Files:[/bold]")
            for art in job.artifacts:
                console.print(f"  • {art.path} ({art.size_bytes} bytes)")
        
        # Show failures if any
        if job.failures:
            console.print(f"\n[red]⚠️  Failures: {len(job.failures)}[/red]")
            for failure in job.failures:
                console.print(f"  • [{failure.kind}] {failure.step}: {failure.message}")
        
        console.print(f"\n💡 Inspect with: [cyan]orchestrator show {job.job_id}[/cyan]\n")
        
    except Exception as e:
        console.print(f"\n[red]❌ Job Failed: {e}[/red]")
        if verbose:
            import traceback
            console.print(traceback.format_exc())
        raise typer.Exit(1)


@app.command()
def show(
    job_id: str = typer.Argument(
        ...,
        help="Job ID to inspect (e.g., job_a1b2c3d4e5f6)"
    ),
    events: bool = typer.Option(
        False,
        "--events",
        "-e",
        help="Show execution events timeline"
    ),
    files: bool = typer.Option(
        False,
        "--files",
        "-f",
        help="List all generated files with hashes"
    )
):
    """
    Show details of a completed job.
    
    Example:
        orchestrator show job_abc123
        orchestrator show job_abc123 --events
        orchestrator show job_abc123 --files
    """
    run_dir = Path("runs") / job_id
    
    if not run_dir.exists():
        console.print(f"[red]❌ Run not found: {job_id}[/red]")
        console.print(f"Available runs:")
        for run in Path("runs").iterdir():
            if run.is_dir():
                console.print(f"  • {run.name}")
        raise typer.Exit(1)
    
    # Read manifest
    manager = RunManager(job_id)
    manifest = manager.read_manifest()
    
    if not manifest:
        console.print(f"[red]❌ Manifest not found for {job_id}[/red]")
        raise typer.Exit(1)
    
    # Display job info
    panel = Panel(
        f"""[bold]Job ID:[/bold] {manifest['job_id']}
[bold]Project:[/bold] {manifest['project']}
[bold]Status:[/bold] [{'green' if manifest['status'] == 'succeeded' else 'red'}]{manifest['status']}[/]
[bold]Provider:[/bold] {manifest['provider']}
[bold]Duration:[/bold] {manifest.get('duration_s', 0):.1f}s
[bold]Started:[/bold] {manifest['started_at']}
[bold]Task:[/bold] {manifest.get('task_description', 'N/A')}""",
        title=f"📊 Run Details",
        border_style="blue"
    )
    console.print(panel)
    
    events_path = run_dir / "events.jsonl"
    event_list = read_events(events_path)

    step_summaries = _summarize_steps_from_events(
        event_list,
        pending_from_manifest=manifest.get("pending_steps")
    )

    if step_summaries:
        console.print("\n[bold]Steps:[/bold]")
        table = Table(show_header=True)
        table.add_column("Step")
        table.add_column("Status")
        table.add_column("Duration")
        table.add_column("Calls")
        table.add_column("Note")

        status_styles = {
            "succeeded": ("green", "✅"),
            "failed": ("red", "❌"),
            "running": ("yellow", "⏳"),
            "pending": ("white", "…"),
            "skipped": ("cyan", "⏭"),
        }

        for summary in step_summaries:
            status = summary["status"]
            style, emoji = status_styles.get(status, ("white", "•"))
            duration = (
                f"{summary['duration_s']:.1f}s"
                if summary["duration_s"] is not None
                else "-"
            )
            table.add_row(
                summary["step"],
                f"[{style}]{emoji} {status}[/]",
                duration,
                str(summary.get("provider_calls", 0) or 0),
                summary.get("message", "") or "",
            )

        console.print(table)
    elif manifest.get("steps"):
        # Fallback to manifest data if event parsing failed
        console.print("\n[bold]Steps:[/bold]")
        table = Table(show_header=True)
        table.add_column("Step")
        table.add_column("Status")
        table.add_column("Duration")
        table.add_column("Calls")
        for step_id, step_data in manifest["steps"].items():
            table.add_row(
                step_id,
                step_data.get("status", "unknown"),
                f"{step_data.get('duration_s', 0):.1f}s",
                str(step_data.get("provider_calls", 0)),
            )
        console.print(table)
    
    # Show files if requested
    if files and manifest.get('files'):
        console.print("\n[bold]Generated Files:[/bold]")
        for file_info in manifest['files']:
            console.print(f"  📄 {file_info['path']}")
            console.print(f"     SHA256: {file_info['sha256'][:16]}...")
            console.print(f"     Size: {file_info['size_bytes']} bytes")
    
    # Show events if requested
    if events and event_list:
        console.print(f"\n[bold]Events Timeline ({len(event_list)} events):[/bold]")
        for event in event_list[:20]:
            timestamp = (event.get("ts") or "")[:19]
            event_type = event.get("type", "unknown")
            level = event.get("level", "INFO")
            step = event.get("step")

            if step:
                console.print(
                    f"  {timestamp} | [{level}] {event_type:20} | step={step}"
                )
            else:
                console.print(f"  {timestamp} | [{level}] {event_type}")

        if len(event_list) > 20:
            console.print(f"  ... and {len(event_list) - 20} more events")
    
    # Show failures
    if manifest.get('failures'):
        console.print(f"\n[red]⚠️  Failures:[/red]")
        for failure in manifest['failures']:
            console.print(f"  • [{failure['kind']}] {failure['step']}: {failure['message']}")
    
    console.print()


@app.command()
def list_runs(
    limit: int = typer.Option(
        10,
        "--limit",
        "-n",
        help="Number of recent runs to show"
    )
):
    """
    List recent job runs.
    
    Example:
        orchestrator list-runs
        orchestrator list-runs --limit 20
    """
    runs_dir = Path("runs")
    
    if not runs_dir.exists():
        console.print("[yellow]No runs found[/yellow]")
        return
    
    # Get all runs sorted by modification time
    runs = sorted(
        runs_dir.iterdir(),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )[:limit]
    
    if not runs:
        console.print("[yellow]No runs found[/yellow]")
        return
    
    console.print(f"\n[bold]Recent Runs (showing {len(runs)}):[/bold]\n")
    
    table = Table(show_header=True)
    table.add_column("Job ID")
    table.add_column("Project")
    table.add_column("Status")
    table.add_column("Duration")
    table.add_column("Started")
    
    for run_dir in runs:
        manifest_path = run_dir / "manifest.json"
        if manifest_path.exists():
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            status = manifest.get('status', 'unknown')
            status_display = f"[{'green' if status == 'succeeded' else 'red'}]{status}[/]"
            
            table.add_row(
                run_dir.name,
                manifest.get('project', 'N/A'),
                status_display,
                f"{manifest.get('duration_s', 0):.1f}s",
                manifest.get('started_at', 'N/A')[:19]
            )
    
    console.print(table)
    console.print()


@app.command()
def tail(
    job_id: str = typer.Argument(
        ...,
        help="Job ID to tail events for (e.g., job_a1b2c3d4e5f6)"
    ),
    event_type: Optional[str] = typer.Option(
        None,
        "--type",
        help="Filter by event type (e.g., step.succeeded)"
    ),
    step: Optional[str] = typer.Option(
        None,
        "--step",
        help="Filter by step identifier (e.g., architect)"
    ),
    level: Optional[str] = typer.Option(
        None,
        "--level",
        help="Filter by level (INFO, WARN, ERROR)"
    ),
    follow: bool = typer.Option(
        False,
        "--follow",
        "-f",
        help="Follow the event log (like tail -f)"
    ),
    interval: float = typer.Option(
        1.0,
        "--interval",
        help="Polling interval in seconds when using --follow"
    ),
):
    """
    Stream events from a job's events.jsonl file.

    Example:
        orchestrator tail job_abc123
        orchestrator tail job_abc123 --type step.succeeded --follow
    """
    events_path = Path("runs") / job_id / "events.jsonl"
    if not events_path.exists():
        console.print(f"[red]❌ Events log not found for {job_id}[/red]")
        raise typer.Exit(1)

    def parse_lines(lines: list[str]) -> list[dict]:
        parsed = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                parsed.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return parsed

    def emit(events_batch: list[dict]):
        for event in filter_events(events_batch, event_type, step, level):
            timestamp = (event.get("ts") or "")[:19]
            lvl = event.get("level", "INFO")
            etype = event.get("type", "unknown")
            step_id = event.get("step")
            detail = ""

            if event.get("data"):
                data_preview = str(event["data"])
                detail = f" {data_preview}"
            elif event.get("message"):
                detail = f" {event['message']}"

            if step_id:
                console.print(
                    f"{timestamp} [{lvl}] {etype} | step={step_id}{detail}"
                )
            else:
                console.print(f"{timestamp} [{lvl}] {etype}{detail}")

    try:
        with open(events_path, "r") as f:
            initial_lines = f.readlines()
        emit(parse_lines(initial_lines))

        if not follow:
            return

        console.print("[cyan]-- follow mode --[/cyan]")
        position = events_path.stat().st_size

        while True:
            with open(events_path, "r") as f:
                f.seek(position)
                new_lines = f.readlines()
                position = f.tell()

            if new_lines:
                emit(parse_lines(new_lines))

            time.sleep(interval)
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopped tailing events[/yellow]")


if __name__ == "__main__":
    app()
