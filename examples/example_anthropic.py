"""
Crew AI Example with Anthropic Claude
Uses Claude instead of OpenAI
"""

from crewai import Agent, Task, Crew, Process
from crewai_tools import tool
import os
from dotenv import load_dotenv

load_dotenv()

@tool
def get_today_date() -> str:
    """Get today's date"""
    from datetime import date
    return str(date.today())

# Create agents using Claude
writer = Agent(
    role="Content Writer",
    goal="Write engaging and clear content",
    backstory="You are a professional writer with 10 years of experience.",
    model="claude-3-5-sonnet-20241022",  # Using Claude instead of GPT
    verbose=True,
    allow_delegation=False
)

editor = Agent(
    role="Content Editor",
    goal="Edit and improve written content",
    backstory="You are an expert editor.",
    model="claude-3-5-sonnet-20241022",
    tools=[get_today_date],
    verbose=True,
    allow_delegation=False
)

# Create tasks
write_task = Task(
    description="Write a short blog post about why AI is important. Keep it to 3 paragraphs.",
    expected_output="A well-written blog post",
    agent=writer,
)

edit_task = Task(
    description="Review and edit the blog post.",
    expected_output="An edited and polished blog post",
    agent=editor,
)

# Create crew
crew = Crew(
    agents=[writer, editor],
    tasks=[write_task, edit_task],
    process=Process.sequential,
    verbose=True
)

if __name__ == "__main__":
    print("🚀 Starting Crew AI with Claude...")
    print("-" * 50)
    result = crew.kickoff()
    print("-" * 50)
    print("✅ Complete!")
    print(result)
