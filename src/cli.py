"""CLI for Unified Orchestrator

Command-line interface using Typer for running jobs and inspecting results.
"""

import typer
import json
import yaml
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

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
        
    except Exception as e:
        console.print(f"[red]❌ Failed to load spec: {e}[/red]")
        raise typer.Exit(1)
    
    # Execute job
    try:
        job = run_orchestrator(job_spec)
        
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
    
    # Show steps
    if manifest.get('steps'):
        console.print("\n[bold]Steps:[/bold]")
        table = Table(show_header=True)
        table.add_column("Step")
        table.add_column("Status")
        table.add_column("Duration")
        table.add_column("Calls")
        table.add_column("Artifacts")
        
        for step_id, step_data in manifest['steps'].items():
            status_emoji = "✅" if step_data['status'] == 'succeeded' else "❌"
            table.add_row(
                step_id,
                f"{status_emoji} {step_data['status']}",
                f"{step_data['duration_s']:.1f}s",
                str(step_data.get('provider_calls', 0)),
                str(step_data.get('artifacts', 0))
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
    if events:
        events_path = run_dir / "events.jsonl"
        if events_path.exists():
            event_list = read_events(events_path)
            
            console.print(f"\n[bold]Events Timeline ({len(event_list)} events):[/bold]")
            for event in event_list[:20]:  # Show first 20
                timestamp = event.get('timestamp', '')[:19]
                event_type = event.get('type', 'unknown')
                
                if event_type.startswith('step.'):
                    step = event.get('step', '?')
                    console.print(f"  {timestamp} | {event_type:20} | {step}")
                else:
                    console.print(f"  {timestamp} | {event_type:20}")
            
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


if __name__ == "__main__":
    app()

