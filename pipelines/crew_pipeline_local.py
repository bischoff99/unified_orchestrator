"""
Option 2: Crew AI + Ollama - Complete Local Multi-Agent Pipeline
Agents: Planner, Developer, Validator
Models: Mistral, CodeLlama, Llama2 (all local, no API keys)
"""

from crewai import Agent, Task, Crew, Process
from crewai_tools import tool
import json
import os
from pathlib import Path
from datetime import datetime

# ============================================================================
# TOOLS - File I/O and Process Management
# ============================================================================

@tool
def read_task_queue(queue_file: str = "task_queue.json") -> dict:
    """Read shared task queue from JSON file"""
    if os.path.exists(queue_file):
        with open(queue_file) as f:
            return json.load(f)
    return {"tasks": [], "status": "empty"}

@tool
def write_task_queue(tasks: list, status: str, queue_file: str = "task_queue.json"):
    """Write updated task queue"""
    data = {"tasks": tasks, "status": status, "updated": datetime.now().isoformat()}
    with open(queue_file, 'w') as f:
        json.dump(data, f, indent=2)
    return f"Queue updated with {len(tasks)} tasks"

@tool
def create_project_files(project_name: str, files_dict: dict) -> str:
    """Create project structure with files"""
    project_dir = Path(project_name)
    project_dir.mkdir(exist_ok=True)
    
    for filename, content in files_dict.items():
        file_path = project_dir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
    
    return f"Created {project_name} with {len(files_dict)} files"

@tool
def validate_code(code_sample: str) -> dict:
    """Validate Python code syntax"""
    try:
        compile(code_sample, '<string>', 'exec')
        return {"valid": True, "errors": []}
    except SyntaxError as e:
        return {"valid": False, "errors": [str(e)]}

# ============================================================================
# AGENTS
# ============================================================================

planner = Agent(
    role="Project Planner",
    goal="Break down projects into manageable tasks and create architecture documents",
    backstory="You are an expert project manager with 15 years of experience planning software projects.",
    model="ollama/mistral",
    tools=[read_task_queue, write_task_queue],
    verbose=True,
    allow_delegation=False
)

developer = Agent(
    role="Software Developer",
    goal="Write clean, well-structured code based on specifications",
    backstory="You are a senior software engineer with expertise in Python, APIs, and system design.",
    model="ollama/codellama",
    tools=[create_project_files, validate_code],
    verbose=True,
    allow_delegation=False
)

validator = Agent(
    role="QA & Code Validator",
    goal="Ensure code quality, test coverage, and architecture compliance",
    backstory="You are a QA lead with deep knowledge of testing, security, and code standards.",
    model="ollama/llama2",
    tools=[validate_code, read_task_queue],
    verbose=True,
    allow_delegation=False
)

# ============================================================================
# TASKS
# ============================================================================

planning_task = Task(
    description="""
    Create a project plan for: {project_name}
    Requirements: {requirements}
    
    Tasks:
    1. Define project structure
    2. Identify 3-5 main components
    3. Create a task breakdown in JSON format
    4. Estimate time for each component
    
    Output should be a detailed project plan with component breakdown.
    """,
    expected_output="Structured project plan with components and task breakdown",
    agent=planner,
    input_variables=["project_name", "requirements"]
)

development_task = Task(
    description="""
    Based on the project plan, generate code for:
    Project: {project_name}
    Focus: {focus_component}
    
    Requirements:
    - Create well-documented Python code
    - Follow PEP 8 standards
    - Include docstrings for all functions
    - Add type hints
    """,
    expected_output="Production-ready Python code with documentation",
    agent=developer,
    input_variables=["project_name", "focus_component"]
)

validation_task = Task(
    description="""
    Validate the generated code:
    - Check syntax
    - Verify documentation
    - Ensure no security issues
    - Validate against requirements
    
    Provide detailed feedback and improvement suggestions.
    """,
    expected_output="Code validation report with improvement suggestions",
    agent=validator,
)

# ============================================================================
# CREW & ORCHESTRATION
# ============================================================================

crew = Crew(
    agents=[planner, developer, validator],
    tasks=[planning_task, development_task, validation_task],
    process=Process.sequential,
    verbose=True
)

def run_pipeline(project_name: str, requirements: str, focus_component: str = "Core API"):
    """Run the complete multi-agent pipeline"""
    
    print("\n" + "="*70)
    print(f"🚀 Starting Multi-Agent Pipeline for: {project_name}")
    print("="*70)
    
    result = crew.kickoff(inputs={
        "project_name": project_name,
        "requirements": requirements,
        "focus_component": focus_component
    })
    
    print("\n" + "="*70)
    print("✅ Pipeline Complete!")
    print("="*70)
    
    return result

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Example: Build a REST API project
    project_name = "UserManagementAPI"
    requirements = """
    Build a REST API for user management with:
    - User CRUD operations
    - Authentication (JWT)
    - Rate limiting
    - Comprehensive logging
    - SQLite database integration
    """
    
    result = run_pipeline(
        project_name=project_name,
        requirements=requirements,
        focus_component="Authentication Module"
    )
    
    print("\n" + "-"*70)
    print("PIPELINE OUTPUT:")
    print("-"*70)
    print(result)
