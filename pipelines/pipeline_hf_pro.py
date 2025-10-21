#!/usr/bin/env python3
"""
Production Pipeline: Crew AI + Hugging Face Pro
For M3 Max with local Ollama fallback

Usage:
    export HF_API_KEY=hf_your_token_here
    python pipeline_hf_pro.py --project "MyProject" --requirements "API with auth"
"""

import os
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

from crewai import Agent, Task, Crew, Process
from crewai_tools import tool
from huggingface_hub import InferenceClient

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

load_dotenv()

class Config:
    """Pipeline configuration from environment"""
    
    # Hugging Face
    HF_API_KEY = os.getenv("HF_API_KEY", "")
    HF_HOME = os.getenv("HF_HOME", str(Path.home() / ".cache" / "huggingface"))
    
    # Model Selection
    HF_MODEL_PLANNER = os.getenv("HF_MODEL_PLANNER", "mistralai/Mistral-7B-Instruct-v0.1")
    HF_MODEL_DEVELOPER = os.getenv("HF_MODEL_DEVELOPER", "Salesforce/codet5-base")
    HF_MODEL_REVIEWER = os.getenv("HF_MODEL_REVIEWER", "microsoft/codebert-base")
    
    # Ollama Fallback
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_ENABLED = os.getenv("OLLAMA_ENABLED", "True").lower() == "true"
    
    # Pipeline
    PIPELINE_MODE = os.getenv("PIPELINE_MODE", "hybrid")  # hybrid, hf_only, ollama_only
    VERBOSE = os.getenv("VERBOSE", "True").lower() == "true"
    SAVE_RESULTS = os.getenv("SAVE_RESULTS", "True").lower() == "true"
    RESULTS_DIR = os.getenv("RESULTS_DIR", "./pipeline_results")
    
    # Performance
    GPU_ENABLED = os.getenv("GPU_ENABLED", "True").lower() == "true"
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1024"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        if not cls.HF_API_KEY or cls.HF_API_KEY == "":
            logger.warning("⚠️  HF_API_KEY not set. Set with: export HF_API_KEY=hf_xxxxx")
            if cls.PIPELINE_MODE == "hf_only":
                raise ValueError("HF_API_KEY required for hf_only mode")
        
        if cls.PIPELINE_MODE == "hybrid" and not cls.OLLAMA_ENABLED:
            logger.warning("Hybrid mode selected but Ollama disabled. Will fallback to HF only.")

# ============================================================================
# HUGGING FACE CLIENT
# ============================================================================

class HFClient:
    """Wrapper for Hugging Face Inference with fallback"""
    
    def __init__(self):
        self.api_key = Config.HF_API_KEY
        self.client = InferenceClient(api_key=self.api_key) if self.api_key else None
        self.available = self.api_key is not None
        
        if not self.available:
            logger.warning("HF client not available. Will use Ollama fallback.")
    
    def generate(self, prompt: str, model: str, max_tokens: int = None) -> str:
        """Generate text with fallback"""
        if not self.available:
            return "[HF unavailable - using Ollama fallback]"
        
        try:
            response = self.client.text_generation(
                prompt,
                model=model,
                max_new_tokens=max_tokens or Config.MAX_TOKENS,
                temperature=Config.TEMPERATURE,
                top_p=0.9
            )
            return response
        except Exception as e:
            logger.error(f"HF generation error: {e}")
            return f"[Generation failed: {str(e)}]"

hf_client = HFClient()

# ============================================================================
# TOOLS
# ============================================================================

@tool
def generate_architecture_with_hf(project_spec: str) -> str:
    """Generate architecture using HF Mistral model"""
    prompt = f"""Design a scalable architecture for:
{project_spec}

Provide:
1. System components and interactions
2. Technology stack
3. Data flow diagram (ASCII)
4. Scalability approach
5. Security considerations

Format as JSON."""
    
    return hf_client.generate(
        prompt,
        model=Config.HF_MODEL_PLANNER
    )

@tool
def generate_code_with_hf(component_spec: str) -> str:
    """Generate production code using HF CodeT5"""
    prompt = f"""Generate production Python code for:
{component_spec}

Requirements:
- Type hints throughout
- Comprehensive docstrings
- Error handling
- Logging
- Unit test stubs
- SOLID principles

Output only the code."""
    
    return hf_client.generate(
        prompt,
        model=Config.HF_MODEL_DEVELOPER,
        max_tokens=2000
    )

@tool
def review_code_with_hf(code: str) -> str:
    """Review code using HF CodeBERT"""
    prompt = f"""Review this code for issues:

{code[:1000]}...

Check for:
1. Security vulnerabilities
2. Performance problems
3. Code quality issues
4. Test coverage gaps
5. Documentation completeness

Provide structured feedback."""
    
    return hf_client.generate(
        prompt,
        model=Config.HF_MODEL_REVIEWER,
        max_tokens=500
    )

@tool
def save_results(component: str, results: dict) -> str:
    """Save pipeline results"""
    Path(Config.RESULTS_DIR).mkdir(exist_ok=True)
    
    filename = Path(Config.RESULTS_DIR) / f"{component}_{datetime.now().isoformat()}.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    return f"Results saved to {filename}"

# ============================================================================
# AGENTS
# ============================================================================

architect = Agent(
    role="Solutions Architect",
    goal="Design scalable, secure system architecture",
    backstory="20+ years designing enterprise systems. Expert in distributed systems, security, and scaling.",
    model="ollama/mistral" if Config.PIPELINE_MODE != "hf_only" else None,
    tools=[generate_architecture_with_hf],
    verbose=Config.VERBOSE,
    allow_delegation=False
)

developer = Agent(
    role="Senior Developer",
    goal="Write production-grade code following best practices",
    backstory="Expert full-stack engineer with deep Python expertise. Focuses on clean, testable code.",
    model="ollama/codellama" if Config.PIPELINE_MODE != "hf_only" else None,
    tools=[generate_code_with_hf, save_results],
    verbose=Config.VERBOSE,
    allow_delegation=False
)

reviewer = Agent(
    role="Code Quality Lead",
    goal="Ensure code quality, security, and maintainability",
    backstory="QA architect with 15+ years. Expert in security, performance, and code standards.",
    model="ollama/llama2" if Config.PIPELINE_MODE != "hf_only" else None,
    tools=[review_code_with_hf],
    verbose=Config.VERBOSE,
    allow_delegation=False
)

# ============================================================================
# TASKS
# ============================================================================

architecture_task = Task(
    description="""
    Design architecture for project: {project_name}
    Requirements: {requirements}
    
    Use HF Mistral for architecture generation.
    Create detailed, production-ready specification.
    """,
    expected_output="Complete architecture specification with components",
    agent=architect,
    input_variables=["project_name", "requirements"]
)

development_task = Task(
    description="""
    Generate code for component: {component}
    Based on architecture design.
    
    Use HF CodeT5 for code generation.
    Focus on production quality and maintainability.
    """,
    expected_output="Production-ready Python code with tests",
    agent=developer,
    input_variables=["component"]
)

review_task = Task(
    description="""
    Review generated code comprehensively.
    Check security, performance, and quality.
    
    Use HF CodeBERT for automated review.
    Provide actionable improvement suggestions.
    """,
    expected_output="Detailed code review with recommendations",
    agent=reviewer
)

# ============================================================================
# CREW
# ============================================================================

crew = Crew(
    agents=[architect, developer, reviewer],
    tasks=[architecture_task, development_task, review_task],
    process=Process.sequential,
    verbose=Config.VERBOSE
)

# ============================================================================
# MAIN
# ============================================================================

def run_pipeline(project_name: str, requirements: str, component: str = "Core Module"):
    """Run the orchestration pipeline"""
    
    print("\n" + "="*80)
    print(f"🚀 Crew AI + Hugging Face Pro Pipeline")
    print(f"📦 Project: {project_name}")
    print(f"⚙️  Mode: {Config.PIPELINE_MODE}")
    print("="*80)
    
    # Validate config
    try:
        Config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return None
    
    # Show capabilities
    print(f"\n📊 Capabilities:")
    print(f"  • HF Pro available: {hf_client.available}")
    print(f"  • GPU enabled: {Config.GPU_ENABLED}")
    print(f"  • Ollama fallback: {Config.OLLAMA_ENABLED}")
    print(f"  • Mode: {Config.PIPELINE_MODE}")
    
    # Run pipeline
    print(f"\n{'='*80}")
    print("Starting orchestration...")
    print(f"{'='*80}\n")
    
    result = crew.kickoff(inputs={
        "project_name": project_name,
        "requirements": requirements,
        "component": component
    })
    
    print("\n" + "="*80)
    print("✅ Pipeline Complete!")
    print("="*80)
    
    if Config.SAVE_RESULTS:
        save_results(project_name, {
            "project": project_name,
            "component": component,
            "timestamp": datetime.now().isoformat(),
            "mode": Config.PIPELINE_MODE,
            "result": str(result)[:500]  # First 500 chars
        })
    
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crew AI + HF Pro Pipeline")
    parser.add_argument("--project", default="SampleProject", help="Project name")
    parser.add_argument("--requirements", default="Build a REST API with authentication", help="Requirements")
    parser.add_argument("--component", default="AuthenticationModule", help="Component to develop")
    
    args = parser.parse_args()
    
    result = run_pipeline(
        project_name=args.project,
        requirements=args.requirements,
        component=args.component
    )
    
    if result:
        print("\n📋 RESULT:")
        print("-" * 80)
        print(result)
