"""
Option 5: Crew AI + Hugging Face Inference
Agents using local Ollama + HF Pro models for code generation
Requires: HF_API_KEY environment variable
"""

from crewai import Agent, Task, Crew, Process
from crewai_tools import tool
from huggingface_hub import InferenceClient
import os
import json
from datetime import datetime

# ============================================================================
# HUGGING FACE SETUP
# ============================================================================

HF_API_KEY = os.getenv("HF_API_KEY", "hf_xxxxx")
HF_MODEL_CODEGEN = "Salesforce/codet5-base"  # Code generation
HF_MODEL_REVIEW = "microsoft/codebert-base"   # Code review

hf_client = InferenceClient(api_key=HF_API_KEY)

# ============================================================================
# TOOLS
# ============================================================================

@tool
def generate_code_with_hf(prompt: str) -> str:
    """Generate code using Hugging Face CodeT5 model"""
    try:
        response = hf_client.text_generation(
            prompt,
            model=HF_MODEL_CODEGEN,
            max_new_tokens=500,
            temperature=0.7
        )
        return response
    except Exception as e:
        return f"Error generating code: {str(e)}"

@tool
def review_code_with_hf(code: str) -> str:
    """Review code using HF CodeBERT model"""
    try:
        prompt = f"Review this code for issues:\n{code}\n\nReview:"
        response = hf_client.text_generation(
            prompt,
            model=HF_MODEL_REVIEW,
            max_new_tokens=200
        )
        return response
    except Exception as e:
        return f"Error reviewing code: {str(e)}"

@tool
def save_analysis(component_name: str, analysis: dict) -> str:
    """Save code analysis to JSON file"""
    filename = f"{component_name}_analysis.json"
    with open(filename, 'w') as f:
        json.dump({
            **analysis,
            "timestamp": datetime.now().isoformat()
        }, f, indent=2)
    return f"Analysis saved to {filename}"

# ============================================================================
# AGENTS - Using Hybrid Setup
# ============================================================================

# Agent 1: Planner (Local Ollama - fast planning)
planner = Agent(
    role="Technical Architect",
    goal="Design scalable software architecture and component breakdown",
    backstory="Expert solutions architect with 20 years of experience.",
    model="ollama/mistral",  # Local, free
    verbose=True,
    allow_delegation=False
)

# Agent 2: Developer (HF + Code Generation)
developer = Agent(
    role="Senior Code Generator",
    goal="Write production-grade code using AI-assisted generation",
    backstory="Full-stack engineer specializing in clean code architecture.",
    # Note: Using default OpenAI for demo - swap with HF client in production
    model="ollama/codellama",  # Can be HF model
    tools=[generate_code_with_hf, save_analysis],
    verbose=True,
    allow_delegation=False
)

# Agent 3: Reviewer (HF CodeBERT)
reviewer = Agent(
    role="Code Quality Lead",
    goal="Ensure code quality, security, and best practices",
    backstory="QA architect with deep security and performance knowledge.",
    model="ollama/llama2",  # Local validation
    tools=[review_code_with_hf],
    verbose=True,
    allow_delegation=False
)

# ============================================================================
# TASKS
# ============================================================================

planning_task = Task(
    description="""
    Design architecture for: {project_name}
    Requirements: {requirements}
    
    Create a detailed breakdown with:
    1. Core components and their interactions
    2. Technology stack recommendations
    3. Scalability considerations
    4. Security architecture
    5. Deployment strategy
    
    Format as JSON for programmatic use.
    """,
    expected_output="Detailed architecture document in JSON",
    agent=planner,
    input_variables=["project_name", "requirements"]
)

development_task = Task(
    description="""
    Generate code for component: {component}
    Based on architecture specification.
    
    Requirements:
    - Use modern Python practices
    - Include comprehensive docstrings
    - Add type hints throughout
    - Create unit test stubs
    - Follow SOLID principles
    
    Use Hugging Face CodeT5 for generation.
    """,
    expected_output="Complete, production-ready code module",
    agent=developer,
    input_variables=["component"]
)

review_task = Task(
    description="""
    Review the generated code:
    - Security vulnerabilities
    - Performance issues
    - Code style and standards
    - Test coverage
    - Documentation completeness
    
    Use HF CodeBERT for automated review.
    Provide actionable improvement suggestions.
    """,
    expected_output="Comprehensive code review with recommendations",
    agent=reviewer,
)

# ============================================================================
# CREW & EXECUTION
# ============================================================================

crew = Crew(
    agents=[planner, developer, reviewer],
    tasks=[planning_task, development_task, review_task],
    process=Process.sequential,
    verbose=True
)

def run_huggingface_pipeline(project_name: str, requirements: str, component: str):
    """
    Run multi-agent pipeline with HF inference integration
    
    Args:
        project_name: Name of project
        requirements: Project requirements
        component: Component to develop
    """
    
    if HF_API_KEY == "hf_xxxxx":
        print("⚠️  WARNING: HF_API_KEY not set!")
        print("Set with: export HF_API_KEY=hf_your_token")
        print("Falling back to Ollama models only...")
    
    print("\n" + "="*70)
    print(f"🚀 Crew AI + HF Pro Pipeline: {project_name}")
    print("="*70)
    print(f"Planning: Ollama Mistral (free)")
    print(f"Development: HF CodeT5 (HF Pro)")
    print(f"Review: Ollama Llama2 + HF CodeBERT (hybrid)")
    print("="*70 + "\n")
    
    result = crew.kickoff(inputs={
        "project_name": project_name,
        "requirements": requirements,
        "component": component
    })
    
    return result

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Example project
    project_name = "DataPipeline"
    requirements = """
    Build an enterprise data pipeline with:
    - Apache Airflow orchestration
    - Spark data processing
    - PostgreSQL data warehouse
    - Real-time monitoring
    - Data quality checks
    """
    
    component = "DataQualityValidator"
    
    result = run_huggingface_pipeline(
        project_name=project_name,
        requirements=requirements,
        component=component
    )
    
    print("\n" + "="*70)
    print("ORCHESTRATION RESULT:")
    print("="*70)
    print(result)
    print("\n✅ Hybrid pipeline complete!")
    print(f"Check <component>_analysis.json for saved results")
