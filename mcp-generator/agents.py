"""
MCP Generator Agents
Specialized AI agents that work together to build MCP servers
"""

from crewai import Agent, LLM
from tools import (
    write_file,
    read_template,
    validate_python_code,
    create_project_structure,
    generate_requirements,
    test_mcp_server,
    format_json,
    check_api_documentation
)

# Configure Ollama LLM for local execution (FREE!)
def get_ollama_llm(model: str = "mistral") -> LLM:
    """
    Get Ollama LLM configuration for local model execution
    
    Args:
        model: Ollama model name (mistral, codellama, llama2)
        
    Returns:
        Configured LLM instance
    """
    return LLM(
        model=f"ollama/{model}",
        base_url="http://localhost:11434"
    )


def create_api_researcher() -> Agent:
    """
    API Research Specialist
    
    Analyzes API documentation and extracts specifications for MCP server design.
    Expert at understanding REST APIs, authentication methods, and endpoint structures.
    """
    return Agent(
        role="API Research Specialist",
        goal="Analyze API documentation and extract complete specifications for MCP server implementation",
        backstory="""You are an expert API analyst with 10 years of experience studying 
        REST APIs, GraphQL endpoints, and authentication systems. You excel at reading 
        API documentation, identifying key endpoints, understanding request/response 
        formats, and extracting authentication requirements. You provide clear, 
        structured specifications that developers can immediately use.""",
        tools=[check_api_documentation],
        llm=get_ollama_llm("mistral"),  # Using local Ollama model
        verbose=True,
        allow_delegation=False
    )


def create_mcp_architect() -> Agent:
    """
    MCP Server Architect
    
    Designs the structure, tools, and architecture of MCP servers.
    Expert at Model Context Protocol specifications and server design patterns.
    """
    return Agent(
        role="MCP Server Architect",
        goal="Design optimal MCP server architecture with well-defined tools and clear structure",
        backstory="""You are a senior software architect specializing in Model Context 
        Protocol (MCP) servers. You have designed dozens of MCP servers for various APIs. 
        You understand how to break down API capabilities into discrete MCP tools, design 
        clean interfaces, and create maintainable server architectures. You always consider 
        error handling, async operations, and user experience.""",
        tools=[format_json, read_template],
        llm=get_ollama_llm("mistral"),  # Using local Ollama model
        verbose=True,
        allow_delegation=False
    )


def create_python_developer() -> Agent:
    """
    Senior Python Developer
    
    Writes production-ready Python code for MCP servers.
    Expert at async programming, API integration, and clean code practices.
    """
    return Agent(
        role="Senior Python Developer",
        goal="Write clean, production-ready Python code that implements MCP server specifications",
        backstory="""You are a senior Python developer with expertise in async programming, 
        API clients, and server development. You write clean, well-documented code following 
        best practices. You're experienced with aiohttp, httpx, pydantic, and async/await 
        patterns. Your code is always readable, maintainable, and includes proper error 
        handling. You follow PEP 8 and write comprehensive docstrings.""",
        tools=[write_file, validate_python_code, read_template],
        llm=get_ollama_llm("codellama"),  # Using CodeLlama for code generation
        verbose=True,
        allow_delegation=False
    )


def create_qa_engineer() -> Agent:
    """
    QA Engineer & Testing Specialist
    
    Tests MCP servers and ensures quality.
    Expert at writing tests, finding bugs, and validating functionality.
    """
    return Agent(
        role="QA Engineer & Testing Specialist",
        goal="Test MCP servers thoroughly and ensure production quality",
        backstory="""You are a meticulous QA engineer with a keen eye for detail. You excel 
        at finding edge cases, writing comprehensive tests, and validating that code works as 
        expected. You understand both functional and integration testing. You always think 
        about error scenarios, edge cases, and real-world usage patterns. You provide clear, 
        actionable feedback to developers.""",
        tools=[test_mcp_server, validate_python_code],
        llm=get_ollama_llm("mistral"),  # Using local Ollama model
        verbose=True,
        allow_delegation=False
    )


def create_devops_configurator() -> Agent:
    """
    DevOps & Configuration Specialist
    
    Creates configuration files, documentation, and deployment setup.
    Expert at requirements, environment setup, and project configuration.
    """
    return Agent(
        role="DevOps & Configuration Specialist",
        goal="Create complete project configuration, documentation, and deployment setup",
        backstory="""You are a DevOps specialist who excels at project configuration and 
        documentation. You create clean requirements.txt files, environment configurations, 
        README documentation, and setup scripts. You understand dependency management, 
        environment variables, and deployment workflows. You write clear, beginner-friendly 
        documentation that helps users get started quickly.""",
        tools=[write_file, generate_requirements, create_project_structure, format_json],
        llm=get_ollama_llm("mistral"),  # Using local Ollama model
        verbose=True,
        allow_delegation=False
    )


def create_project_coordinator() -> Agent:
    """
    Project Coordinator
    
    Oversees the entire MCP generation process and coordinates between agents.
    Ensures all pieces come together properly.
    """
    return Agent(
        role="Project Coordinator",
        goal="Coordinate all agents to successfully generate a complete, working MCP server",
        backstory="""You are an experienced project coordinator who oversees technical projects. 
        You understand the big picture, keep track of progress, and ensure all team members 
        (agents) work together effectively. You can delegate tasks, review outputs, and make 
        decisions about next steps. You ensure the final deliverable is complete, tested, and 
        ready for use.""",
        tools=[],
        llm=get_ollama_llm("mistral"),  # Using local Ollama model
        verbose=True,
        allow_delegation=False  # Sequential process doesn't need delegation
    )


# Helper function to get all agents
def get_all_agents() -> dict:
    """
    Get all available agents as a dictionary.
    
    Returns:
        Dictionary of agent_name: agent_instance
    """
    return {
        "researcher": create_api_researcher(),
        "architect": create_mcp_architect(),
        "developer": create_python_developer(),
        "qa": create_qa_engineer(),
        "devops": create_devops_configurator(),
        "coordinator": create_project_coordinator()
    }
