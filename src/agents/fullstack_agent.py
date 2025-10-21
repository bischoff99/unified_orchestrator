"""Full-Stack Agent - Implementation for CrewAI"""
from crewai import Agent
from config import get_llm_backend
from src.tools.production_tools import (
    write_file,
    read_file,
    validate_python_code,
    create_project_files
)

class FullStackAgent:
    def __init__(self):
        self.llm = get_llm_backend()
        self.tools = [write_file, read_file, validate_python_code, create_project_files]

    def create(self) -> Agent:
        """Create CrewAI agent for fullstack development"""
        return Agent(
            role="Full-Stack Developer",
            goal="Implement backend and frontend code, write files using the write_file tool",
            backstory="""You are a pragmatic engineer who ALWAYS uses tools to create actual files.
            When implementing code, you MUST use write_file() to save each file.
            CRITICAL: Every code file you create MUST be written using write_file tool.
            Example: write_file('src/generated/main.py', code_content)""",
            tools=self.tools,
            llm=self.llm,
            verbose=True,
        )
