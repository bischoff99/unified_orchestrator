"""
Simple Crew AI Example - Hello World
This example creates two agents that work together
"""

from crewai import Agent, Task, Crew, Process
from crewai_tools import tool
import os
from dotenv import load_dotenv

load_dotenv()

# Define a simple tool
@tool
def get_today_date() -> str:
    """Get today's date"""
    from datetime import date
    return str(date.today())

# Create first agent - Writer
writer = Agent(
    role="Content Writer",
    goal="Write engaging and clear content",
    backstory="You are a professional writer with 10 years of experience writing for various publications.",
    verbose=True,
    allow_delegation=False
)

# Create second agent - Editor
editor = Agent(
    role="Content Editor", 
    goal="Edit and improve written content",
    backstory="You are an expert editor who ensures content is clear, concise, and engaging.",
    tools=[get_today_date],
    verbose=True,
    allow_delegation=False
)

# Create tasks
write_task = Task(
    description="Write a short blog post about why AI is important. Keep it to 3 paragraphs.",
    expected_output="A well-written blog post",
    agent=writer,
    async_execution=False
)

edit_task = Task(
    description="Review and edit the blog post. Make it more engaging and add today's date at the end.",
    expected_output="An edited and polished blog post",
    agent=editor,
    async_execution=False
)

# Create the crew
crew = Crew(
    agents=[writer, editor],
    tasks=[write_task, edit_task],
    process=Process.sequential,  # Tasks run one after another
    verbose=True
)

# Run the workflow
if __name__ == "__main__":
    print("🚀 Starting Crew AI Workflow...")
    print("-" * 50)
    result = crew.kickoff()
    print("-" * 50)
    print("✅ Workflow Complete!")
    print(result)
