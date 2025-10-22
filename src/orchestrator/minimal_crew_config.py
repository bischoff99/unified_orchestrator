"""Minimal 4-Agent Crew Configuration for Faster Iteration"""
from crewai import Agent, Task, Crew, Process
from config import get_llm_backend
from src.agents.architect_agent import ArchitectAgent
from src.tools.production_tools import (
    write_file, read_file, validate_python_code,
    test_code, create_project_structure, 
    generate_requirements, get_current_date, list_directory
)
from src.utils.code_scorer import score_code_tool

class MinimalCrew:
    """
    Streamlined 4-agent crew for faster development cycles.
    
    Workflow:
    1. Architect designs system (sequential start)
    2. Builder implements code + deployment (depends on architecture)
    3. QA tests and validates (depends on implementation)
    4. Docs writer creates documentation + final review (depends on all)
    """
    
    def __init__(self, task_description: str):
        self.task_description = task_description
        self.agents = self._create_agents()
        self.tasks = self._create_tasks()
    
    def _create_agents(self):
        """Initialize 4 streamlined agents"""
        agents = {
            'architect': ArchitectAgent().create(),
            'builder': self._create_builder_agent(),
            'qa': self._create_qa_agent(),
            'docs': self._create_docs_agent(),
        }
        return agents
    
    def _create_builder_agent(self):
        """Senior Full-Stack Engineer + DevOps - Delivers Complete, Runnable Code"""
        return Agent(
            role="Senior Full-Stack Implementation Engineer",
            goal="Create COMPLETE, RUNNABLE, production-quality code with ALL imports and endpoints fully implemented",
            backstory="""You are a senior full-stack engineer.

CRITICAL: You MUST call write_file(file_path, ACTUAL_CODE_CONTENT).
DO NOT call write_file() with empty string - PUT THE REAL CODE IN THE CONTENT PARAMETER!

Example of CORRECT tool usage:
Action: Write File
Action Input: {"file_path": "src/generated/notes_api/main.py", "content": "from fastapi import FastAPI\\nfrom sqlalchemy import Column, Integer, String, create_engine\\n\\napp = FastAPI()\\n\\n@app.post('/notes')\\ndef create_note():\\n    return {'status': 'created'}"}

Example of WRONG tool usage (DO NOT DO THIS):
Action: Write File
Action Input: {"file_path": "src/generated/notes_api/main.py", "content": ""}

Required FastAPI imports:
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import Session, sessionmaker, declarative_base
from pydantic import BaseModel

Workflow:
1. create_project_structure('src/generated/notes_api')
2. write_file('src/generated/notes_api/main.py', COMPLETE_CODE_HERE)
3. write_file('src/generated/notes_api/requirements.txt', 'fastapi\\nuvicorn[standard]\\nsqlalchemy\\npydantic')

NEVER put code in Final Answer - put it in write_file content parameter!""",
            tools=[write_file, read_file, validate_python_code, 
                   create_project_structure, generate_requirements],
            llm=get_llm_backend(),
            verbose=True,
            allow_delegation=False
        )
    
    def _create_qa_agent(self):
        """Quality Assurance + Testing"""
        return Agent(
            role="QA Engineer",
            goal="Validate implementation quality, test functionality, identify issues",
            backstory="""You are a thorough QA engineer who ensures production readiness.
            You:
            - Test all functionality with test_code()
            - Validate code quality and security
            - Check error handling and edge cases
            - Verify integration between components
            
            CRITICAL: Use read_file(), test_code(), and score_code_tool() to validate implementations.
            Example: read_file('src/generated/main.py') then score_code_tool('src/generated/main.py')
            
            The score_code_tool() provides objective quality metrics (0-100) with specific recommendations.
            
            You provide clear, actionable feedback on issues found.""",
            tools=[read_file, test_code, validate_python_code, list_directory, score_code_tool],
            llm=get_llm_backend(),
            verbose=True,
            allow_delegation=False
        )
    
    def _create_docs_agent(self):
        """Technical Writer + Light Review"""
        return Agent(
            role="Technical Documentation Specialist & Reviewer",
            goal="Create comprehensive documentation and perform final quality review",
            backstory="""You are a technical writer who documents AND reviews.
            After QA testing, you:
            1. Write clear, beginner-friendly documentation
            2. Perform final quality and security review
            3. Ensure deployment readiness
            
            CRITICAL: Use write_file() to create all documentation files.
            Example: write_file('src/generated/README.md', readme_content)
            
            Your documentation includes:
            - README with quickstart
            - API documentation
            - Setup and deployment guides
            - Troubleshooting common issues
            
            You also provide final recommendations for production deployment.""",
            tools=[write_file, read_file, get_current_date, list_directory],
            llm=get_llm_backend(),
            verbose=True,
            allow_delegation=False
        )
    
    def _validate_builder_output(self, output):
        """Callback to enforce file creation by Builder agent."""
        from pathlib import Path
        import os
        
        # Check if any files were created in src/generated/
        generated_dir = Path("src/generated")
        if not generated_dir.exists():
            raise ValueError(
                "❌ BUILDER FAILED: src/generated/ directory doesn't exist. "
                "Agent MUST call create_project_structure() first."
            )
        
        # Find project subdirectories
        project_dirs = [d for d in generated_dir.iterdir() if d.is_dir()]
        if not project_dirs:
            raise ValueError(
                "❌ BUILDER FAILED: No project created in src/generated/. "
                "Agent MUST call write_file() to create files."
            )
        
        # Check for main application file
        main_files = []
        for proj_dir in project_dirs:
            main_files.extend(list(proj_dir.glob("main.py")) + list(proj_dir.glob("app.py")))
        
        if not main_files:
            raise ValueError(
                "❌ BUILDER FAILED: No main.py or app.py found. "
                f"Agent MUST write application code. Found dirs: {[d.name for d in project_dirs]}"
            )
        
        # Validate main file has actual code (not empty)
        main_file = main_files[0]
        code_content = main_file.read_text()
        if len(code_content) < 100:
            raise ValueError(
                f"❌ BUILDER FAILED: {main_file.name} is too short ({len(code_content)} chars). "
                "Must contain complete implementation with imports, models, and endpoints."
            )
        
        # Check for critical imports in FastAPI projects
        if "fastapi" in self.task_description.lower() or "api" in self.task_description.lower():
            required_imports = ["FastAPI", "Column", "Integer", "String"]
            missing_imports = [imp for imp in required_imports if imp not in code_content]
            if missing_imports:
                raise ValueError(
                    f"❌ BUILDER FAILED: Missing critical imports: {missing_imports}. "
                    "FastAPI code must include all SQLAlchemy and FastAPI imports."
                )
        
        print(f"✅ VALIDATION PASSED: Found {main_file} with {len(code_content)} chars of code")
        return output
    
    def _create_tasks(self):
        """Create streamlined 4-phase workflow"""
        
        # Phase 1: Architecture Design
        arch_task = Task(
            description=f"""Design complete system architecture for: {self.task_description}
            
            Include:
            - Technology stack selection
            - Component architecture and data flow
            - Database schema and models
            - API endpoints (if applicable)
            - Basic security considerations
            """,
            expected_output="Complete architecture blueprint with tech stack, components, and data flow",
            agent=self.agents['architect']
        )
        
        # Phase 2: Implementation with Completeness Requirements
        build_task = Task(
            description="""Call write_file() to save complete FastAPI code.

CRITICAL: The "content" parameter of write_file() must contain the ACTUAL CODE, not empty string!

Step 1: create_project_structure('src/generated/notes_api')

Step 2: write_file('src/generated/notes_api/main.py', YOUR_COMPLETE_CODE)
WHERE YOUR_COMPLETE_CODE includes:
- from fastapi import FastAPI, Depends, HTTPException, status
- from sqlalchemy import Column, Integer, String, create_engine
- from sqlalchemy.orm import Session, sessionmaker, declarative_base
- from pydantic import BaseModel
- Database setup with create_engine
- Note model with Column(Integer, ...), Column(String, ...)
- Pydantic schemas (NoteCreate, NoteResponse)
- get_db() function with yield
- @app.post('/notes') with db.add(), db.commit()
- @app.get('/notes') with db.query().all()
- Full error handling

Step 3: write_file('src/generated/notes_api/requirements.txt', 'fastapi\\nuvicorn[standard]\\nsqlalchemy\\npydantic')

Your task is complete ONLY when write_file() is called WITH CODE CONTENT (not empty string).
DO NOT put code in Final Answer - put it in write_file() content parameter!""",
            expected_output="""FILES WRITTEN TO DISK using write_file() tool:
1. src/generated/notes_api/main.py (150-250 lines with ALL imports and endpoints)
2. src/generated/notes_api/requirements.txt
3. Optional: Dockerfile, docker-compose.yml

PROOF OF COMPLETION: List the write_file() calls you made with filenames.""",
            agent=self.agents['builder'],
            context=[arch_task],
            # Force tool usage
            output_file="src/generated/notes_api/main.py",
            callback=self._validate_builder_output
        )
        
        # Phase 3: Quality Assurance
        qa_task = Task(
            description="""Test and validate the implementation thoroughly.
            
            Validate:
            - Functional correctness of all components
            - Code quality and best practices
            - Error handling and edge cases
            - Security considerations
            - Integration between components
            
            Use test_code() and validate_python_code() tools.
            Provide detailed report of any issues found.
            """,
            expected_output="Comprehensive test report with validation results and identified issues",
            agent=self.agents['qa'],
            context=[build_task]
        )
        
        # Phase 4: Documentation + Final Review
        docs_task = Task(
            description="""Create documentation and perform final review.
            
            Documentation to create:
            - README.md with project overview and quickstart
            - Setup and installation instructions
            - API documentation (if applicable)
            - Deployment guide
            - Troubleshooting section
            
            Final Review:
            - Overall quality assessment
            - Production readiness checklist
            - Deployment recommendations
            
            Use write_file() for all documentation files.
            """,
            expected_output="Complete documentation set and final quality review with deployment recommendations",
            agent=self.agents['docs'],
            context=[arch_task, build_task, qa_task]
        )
        
        return [arch_task, build_task, qa_task, docs_task]
    
    def run(self):
        """Execute the minimal crew workflow"""
        print("\n🚀 Starting Minimal Crew Orchestration...")
        print(f"📊 Agents: 4 (Architect, Builder, QA, Docs)")
        print(f"📋 Tasks: {len(self.tasks)}")
        print(f"⚙️  Process: Sequential with context dependencies")
        print(f"🧠 Memory: Enabled with ChromaDB")
        print(f"💡 Optimized for faster iteration\n")

        # CrewAI v1.0.0 - simplified configuration
        crew = Crew(
            agents=list(self.agents.values()),
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=False,  # Disable memory for faster startup
            max_rpm=100,
        )

        result = crew.kickoff()

        print("\n✅ Minimal Crew orchestration complete!")
        return result

