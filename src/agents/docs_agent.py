"""Docs Agent - Technical Documentation"""
from crewai import Agent
from config import get_llm_backend
from src.tools.production_tools import (
    write_file,
    read_file,
    get_current_date
)

class DocsAgent:
    def __init__(self):
        self.llm = get_llm_backend()
        self.tools = [write_file, read_file, get_current_date]

    def create(self) -> Agent:
        return Agent(
            role="Technical Documentation Specialist",
            goal="Write documentation files using write_file tool - README, setup guides, API docs",
            backstory="""You are a technical writer who ALWAYS uses tools to create files.
            CRITICAL: You MUST use write_file() to save every documentation file you create.
            Example: write_file('src/generated/README.md', readme_content)
            You excel at creating clear, beginner-friendly docs with examples and troubleshooting.""",
            tools=self.tools,
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

