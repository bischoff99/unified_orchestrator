"""
Crew AI Example with Ollama (Local Models)
No API key needed - runs entirely locally!
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

# Create agents using Ollama (local models)
# Make sure you have Ollama running: ollama run mistral
writer = Agent(
    role="Content Writer",
    goal="Write engaging and clear content",
    backstory="You are a professional writer.",
    model="ollama/mistral",  # Using Ollama locally
    base_url="http://localhost:11434",  # Ollama default port
    verbose=True,
    allow_delegation=False
)

editor = Agent(
    role="Content Editor",
    goal="Edit and improve written content",
    backstory="You are an expert editor.",
    model="ollama/mistral",
    base_url="http://localhost:11434",
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
    print("🚀 Starting Crew AI with Local Ollama...")
    print("⚠️  Make sure Ollama is running: 'ollama run mistral'")
    print("-" * 50)
    try:
        result = crew.kickoff()
        print("-" * 50)
        print("✅ Complete!")
        print(result)
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTo use Ollama, first install it and run a model:")
        print("1. Download Ollama from https://ollama.ai")
        print("2. Run: ollama run mistral")
        print("3. Then run this script again")
