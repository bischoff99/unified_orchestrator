"""Production Crew Configuration - 6-Agent Parallel Workflow"""
from crewai import Agent, Task, Crew, Process
from src.agents.architect_agent import ArchitectAgent
from src.agents.fullstack_agent import FullStackAgent
from src.agents.qa_agent import QAAgent
from src.agents.critic_agent import CriticAgent
from src.agents.devops_agent import DevOpsAgent
from src.agents.docs_agent import DocsAgent

class ProductionCrew:
    """
    Production-ready multi-agent crew with parallel execution.
    
    Workflow:
    1. Architect designs system architecture (sequential)
    2. FullStack, DevOps execute in parallel (based on architecture)
    3. QA tests implementation (waits for FullStack)
    4. Docs generates documentation (uses architecture + implementation)
    5. Critic reviews everything (sequential end)
    """
    
    def __init__(self, task_description: str):
        self.task_description = task_description
        self.agents = self._create_agents()
        self.tasks = self._create_tasks()
    
    def _create_agents(self):
        """Initialize all 6 production agents"""
        return {
            'architect': ArchitectAgent().create(),
            'fullstack': FullStackAgent().create(),
            'qa': QAAgent().create(),
            'critic': CriticAgent().create(),
            'devops': DevOpsAgent().create(),
            'docs': DocsAgent().create()
        }
    
    def _create_tasks(self):
        """Create task workflow with dependencies"""
        
        # Phase 1: Architecture (sequential start)
        arch_task = Task(
            description=f"""Design complete system architecture for: {self.task_description}
            
            Include:
            - Technology stack selection
            - Component architecture and data flow
            - Database schema and models
            - API endpoints and contracts
            - Security considerations
            - Deployment strategy
            """,
            expected_output="Complete architecture blueprint with tech stack, components, data flow, and deployment strategy",
            agent=self.agents['architect']
        )
        
        # Phase 2: Parallel implementation tasks
        impl_task = Task(
            description="""Implement the complete system from the architecture blueprint.
            
            Create:
            - Backend API implementation
            - Frontend interface (if applicable)
            - Database models and migrations
            - Configuration files
            - Working code in src/generated/ directory
            """,
            expected_output="Complete, working implementation in src/generated/ with all components integrated",
            agent=self.agents['fullstack'],
            context=[arch_task]
        )
        
        devops_task = Task(
            description="""Create complete deployment and infrastructure setup.
            
            Provide:
            - Dockerfile for containerization
            - docker-compose.yml for local development
            - CI/CD pipeline configuration (GitHub Actions)
            - Environment variable templates
            - Deployment scripts
            """,
            expected_output="Complete deployment configuration with Dockerfile, compose file, and CI/CD setup",
            agent=self.agents['devops'],
            context=[arch_task]
        )
        
        # Phase 3: Quality assurance (depends on implementation)
        qa_task = Task(
            description="""Test the implementation thoroughly and ensure quality.
            
            Validate:
            - Functional correctness
            - Edge cases and error handling
            - Integration between components
            - Test coverage >80%
            - Performance benchmarks
            """,
            expected_output="Comprehensive test results with coverage report and identified issues",
            agent=self.agents['qa'],
            context=[impl_task]
        )
        
        # Phase 4: Documentation (uses architecture and implementation)
        docs_task = Task(
            description="""Generate comprehensive project documentation.
            
            Create:
            - README.md with quickstart guide
            - API documentation
            - Architecture diagram explanation
            - Setup and deployment instructions
            - Troubleshooting guide
            """,
            expected_output="Complete documentation set including README, API docs, and setup guides",
            agent=self.agents['docs'],
            context=[arch_task, impl_task]
        )
        
        # Phase 5: Final review (sequential end)
        review_task = Task(
            description="""Review all outputs for quality, security, and best practices.

            Evaluate:
            - Code quality and maintainability
            - Security vulnerabilities
            - Performance optimization opportunities
            - Documentation completeness
            - Deployment readiness

            Provide actionable recommendations for improvements.
            """,
            expected_output="Comprehensive review with security assessment, quality evaluation, and improvement recommendations",
            agent=self.agents['critic'],
            context=[impl_task, qa_task, devops_task, docs_task]
        )
        
        return [arch_task, impl_task, qa_task, devops_task, docs_task, review_task]
    
    def run(self):
        """Execute the production crew workflow with M3 Max optimizations"""
        print("\n🚀 Starting CrewAI orchestration...")
        print(f"📊 Agents: {len(self.agents)}")
        print(f"📋 Tasks: {len(self.tasks)}")
        print(f"⚙️  Process: Sequential with context-based parallelism")
        print(f"🧠 Memory: Enabled with ChromaDB + sentence-transformers")
        print(f"💾 Cache: Enabled\n")

        # Configure embedder for memory system
        embedder_config = {
            "provider": "huggingface",
            "config": {
                "model": "sentence-transformers/all-MiniLM-L6-v2"
            }
        }

        crew = Crew(
            agents=list(self.agents.values()),
            tasks=self.tasks,
            process=Process.sequential,  # Sequential with context dependencies for parallelism
            verbose=True,
            memory=True,  # Enable crew memory with ChromaDB backend
            embedder=embedder_config,  # Explicit embedder for consistent memory
            max_rpm=100,  # M3 Max can handle high throughput
            share_crew=True  # Enable context sharing between agents
        )

        result = crew.kickoff()

        print("\n✅ Orchestration complete!")
        return result

