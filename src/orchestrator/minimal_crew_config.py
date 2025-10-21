"""Minimal 4-Agent Crew Configuration for Faster Iteration"""
from crewai import Agent, Task, Crew, Process
from config import get_llm_backend
from src.agents.architect_agent import ArchitectAgent
from src.tools.production_tools import (
    write_file, read_file, validate_python_code,
    test_code, create_project_structure, 
    generate_requirements, get_current_date, list_directory
)

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
        """FullStack Developer + Basic DevOps"""
        return Agent(
            role="Full-Stack Builder",
            goal="Implement complete system: code + basic deployment configs",
            backstory="""You are a versatile full-stack developer who builds end-to-end.
            You implement:
            - Backend APIs and business logic
            - Frontend interfaces (if needed)
            - Database models and schemas
            - Basic deployment files (Dockerfile, docker-compose.yml, requirements.txt)
            
            CRITICAL: Use write_file() for EVERY file you create.
            Example: write_file('src/generated/main.py', code_content)
            
            You prioritize working code over perfection, knowing QA will test thoroughly.""",
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
            
            CRITICAL: Use read_file() and test_code() to validate implementations.
            Example: read_file('src/generated/main.py') then test_code(code_content)
            
            You provide clear, actionable feedback on issues found.""",
            tools=[read_file, test_code, validate_python_code, list_directory],
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
        
        # Phase 2: Implementation
        build_task = Task(
            description="""Implement the complete system from architecture blueprint.
            
            Create:
            - All backend code (API, business logic, models)
            - Frontend code (if applicable)
            - Database setup and migrations
            - Dockerfile for containerization
            - docker-compose.yml for local development
            - requirements.txt with all dependencies
            - Basic configuration files
            
            Save everything to src/generated/ using write_file tool.
            Focus on working functionality, QA will handle testing.
            """,
            expected_output="Complete working implementation in src/generated/ with deployment files",
            agent=self.agents['builder'],
            context=[arch_task]
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

