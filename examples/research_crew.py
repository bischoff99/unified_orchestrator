from crewai import Agent, Task, Crew, Process
from crewai_tools import tool
import os
from dotenv import load_dotenv

load_dotenv()

# Define tools
@tool
def search_web(query: str) -> str:
    """Simulate web search"""
    return f"Search results for: {query}"

@tool
def analyze_data(data: str) -> str:
    """Analyze provided data"""
    return f"Analysis of: {data}"

# Define Agents
researcher = Agent(
    role="Research Analyst",
    goal="Find and compile relevant information on given topics",
    backstory="You are an expert researcher with deep knowledge across multiple domains. Your job is to find, analyze, and compile information accurately.",
    tools=[search_web],
    verbose=True
)

analyzer = Agent(
    role="Data Analyst",
    goal="Analyze research findings and provide insights",
    backstory="You are a skilled data analyst who can extract meaningful insights from raw information.",
    tools=[analyze_data],
    verbose=True
)

# Define Tasks
research_task = Task(
    description="Research the topic: {topic}. Find key information and compile a summary.",
    expected_output="A comprehensive summary of findings",
    agent=researcher,
    input_variables=["topic"]
)

analysis_task = Task(
    description="Analyze the research findings and provide key insights",
    expected_output="Key insights and recommendations",
    agent=analyzer,
)

# Create Crew
crew = Crew(
    agents=[researcher, analyzer],
    tasks=[research_task, analysis_task],
    process=Process.sequential,
    verbose=True
)

# Run workflow
if __name__ == "__main__":
    topic = "Artificial Intelligence trends in 2024"
    result = crew.kickoff(inputs={"topic": topic})
    print(result)
