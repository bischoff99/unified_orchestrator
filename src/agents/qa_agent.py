"""QA Agent - Testing and Quality Assurance"""
from crewai import Agent
from pathlib import Path
from config import get_llm_backend
from src.tools.production_tools import (
    test_code,
    read_file,
    validate_python_code
)

class QAAgent:
    def __init__(self):
        self.llm = get_llm_backend()
        self.tools = [test_code, read_file, validate_python_code]

    def create(self) -> Agent:
        return Agent(
            role="QA Engineer & Testing Specialist",
            goal="Test implementation thoroughly with >80% coverage and validate functionality",
            backstory="""You are a meticulous QA engineer with a keen eye for detail and edge cases.
            You excel at writing comprehensive tests, finding bugs, and ensuring code quality.
            You understand both functional and integration testing patterns. You always think
            about error scenarios, edge cases, and real-world usage patterns.""",
            tools=self.tools,
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def can_start_testing(self) -> bool:
        """Gate condition: wait for implementation to complete"""
        return Path("src/generated/main.py").exists()

