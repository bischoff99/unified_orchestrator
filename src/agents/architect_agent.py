"""Architect Agent - System architecture design for CrewAI"""
from crewai import Agent
from config import MODEL_BACKEND, get_llm_backend
from src.tools.production_tools import (
    read_file,
    list_directory,
    get_current_date
)

class ArchitectAgent:
    def __init__(self):
        self.llm = get_llm_backend()
        self.tools = [read_file, list_directory, get_current_date]

    def create(self) -> Agent:
        """Create CrewAI agent for architecture design"""
        return Agent(
            role="System Architect",
            goal="Define system architecture, dependencies, and data models using list_directory and read_file tools",
            backstory="""Seasoned architect optimizing for local-first workflows and Apple Silicon.
            CRITICAL: You MUST use list_directory() to understand project structure and read_file() to review existing code.
            Example: list_directory('src') then read_file('src/main.py')
            You excel at designing scalable, maintainable systems that leverage M3 Max hardware.""",
            tools=self.tools,
            llm=self.llm,
            verbose=True,
        )
