"""DevOps Agent - Infrastructure and Deployment"""
from crewai import Agent
from config import get_llm_backend
from src.tools.production_tools import (
    create_project_structure,
    generate_requirements,
    write_file
)

class DevOpsAgent:
    def __init__(self):
        self.llm = get_llm_backend()
        self.tools = [create_project_structure, generate_requirements, write_file]

    def create(self) -> Agent:
        return Agent(
            role="DevOps & Infrastructure Engineer",
            goal="Create Dockerfile, docker-compose.yml, and CI/CD configs using write_file tool",
            backstory="""You are a DevOps specialist who ALWAYS uses tools to create configuration files.
            CRITICAL: You MUST use write_file() to save Dockerfile, docker-compose.yml, and CI/CD files.
            Example: write_file('Dockerfile', dockerfile_content)
            You create production-ready, secure, scalable deployment configurations.""",
            tools=self.tools,
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

