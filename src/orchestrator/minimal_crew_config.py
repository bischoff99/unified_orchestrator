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
        """Senior Full-Stack Engineer + DevOps - Delivers Complete, Runnable Code"""
        return Agent(
            role="Senior Full-Stack Implementation Engineer",
            goal="Create COMPLETE, RUNNABLE, production-quality code with ALL imports and endpoints fully implemented",
            backstory="""You are a SENIOR full-stack engineer with 10+ years of experience building production APIs.

YOUR CODE MUST BE COMPLETE AND RUNNABLE. This means:
1. ALL imports included (Column, Integer, String, DateTime, HTTPException, status, etc.)
2. ALL API endpoints FULLY implemented with actual logic (not just pass or comments)
3. Pydantic request/response models defined
4. Database dependency injection (get_db function with yield pattern)
5. Error handling on every endpoint (try/except blocks with HTTPException)
6. Database initialization (Base.metadata.create_all)

MANDATORY COMPLETE CODE EXAMPLE:
```python
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.orm import Session, sessionmaker, declarative_base
from pydantic import BaseModel
from datetime import datetime
from typing import List

SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

class NoteCreate(BaseModel):
    title: str
    content: str

class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    class Config:
        from_attributes = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

@app.post("/notes/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(note: NoteCreate, db: Session = Depends(get_db)):
    try:
        db_note = Note(title=note.title, content=note.content)
        db.add(db_note)
        db.commit()
        db.refresh(db_note)
        return db_note
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/notes/", response_model=List[NoteResponse])
def list_notes(db: Session = Depends(get_db)):
    return db.query(Note).all()
```

VALIDATION CHECKLIST BEFORE WRITING FILE:
□ Does code have ALL imports? (Column, Integer, String, DateTime, HTTPException, status)
□ Are ALL endpoints implemented with actual code? (not pass statements)
□ Is get_db() function defined with yield pattern?
□ Is Base.metadata.create_all() present for table creation?
□ Does each endpoint have try/except error handling?
□ Are Pydantic models defined for requests and responses?
□ Can it run immediately with: uvicorn main:app --reload

CRITICAL RULES:
- Use write_file() for EVERY file you create - NOT optional, MANDATORY
- NEVER skip imports - include Column, Integer, String, DateTime, etc.
- ALWAYS implement the actual route logic with database operations
- ALWAYS add error handling with HTTPException
- Test your code mentally before writing - it MUST run without errors

YOU MUST CALL write_file() TOOL - Your task is NOT complete until files are written to disk.

EXAMPLE OF PROPER TOOL USAGE:
Action: write_file('src/generated/notes_api/main.py', complete_code_content)

Your reputation depends on ACTUALLY WRITING FILES, not just describing them.""",
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
        
        # Phase 2: Implementation with Completeness Requirements
        build_task = Task(
            description="""Implement a COMPLETE, RUNNABLE system from the architecture blueprint.

YOU MUST DELIVER PRODUCTION-READY CODE THAT RUNS WITHOUT MODIFICATIONS.

MANDATORY REQUIREMENTS (ALL MUST BE INCLUDED):
1. Complete Imports Section:
   from fastapi import FastAPI, Depends, HTTPException, status
   from sqlalchemy import Column, Integer, String, DateTime, create_engine
   from sqlalchemy.orm import Session, sessionmaker, declarative_base
   from pydantic import BaseModel
   from datetime import datetime
   from typing import List

2. Database Configuration:
   - SQLALCHEMY_DATABASE_URL with proper path
   - create_engine with connect_args={{"check_same_thread": False}}
   - SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
   - Base = declarative_base()
   - Base.metadata.create_all(bind=engine) <- CRITICAL for table creation

3. ORM Models:
   - Complete SQLAlchemy model with ALL columns properly typed
   - Use Column(Integer, ...), Column(String, ...), Column(DateTime, ...)

4. Pydantic Request/Response Schemas:
   - Create schema (e.g., NoteCreate) for POST requests
   - Response schema (e.g., NoteResponse) with from_attributes=True

5. Database Dependency:
   def get_db():
       db = SessionLocal()
       try:
           yield db
       finally:
           db.close()

6. ALL API Endpoints FULLY IMPLEMENTED (not just defined):
   - POST endpoint with db.add(), db.commit(), db.refresh()
   - GET list endpoint with db.query(Model).all()
   - GET by ID with db.query(Model).filter(Model.id == id).first()
   - PUT endpoint with query, update, commit logic
   - DELETE endpoint with query, delete, commit logic
   - Each with try/except and HTTPException(status_code=..., detail=...)

7. Additional Files via write_file():
   - requirements.txt: fastapi, uvicorn[standard], sqlalchemy, pydantic
   - README.md with uvicorn startup command

VALIDATION BEFORE SUBMITTING:
- Run mental check: Does this code have NameError? (check all imports)
- Are functions implemented? (not just pass)
- Can it start with: uvicorn main:app --reload

Save main application to: src/generated/[project_name]/main.py""",
            expected_output="""FILES WRITTEN TO DISK using write_file() tool:
1. src/generated/notes_api/main.py (150-250 lines with ALL imports and endpoints)
2. src/generated/notes_api/requirements.txt
3. Optional: Dockerfile, docker-compose.yml

PROOF OF COMPLETION: List the write_file() calls you made with filenames.""",
            agent=self.agents['builder'],
            context=[arch_task],
            # Force tool usage
            output_file="src/generated/notes_api/main.py"
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

