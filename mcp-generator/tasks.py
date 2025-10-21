"""
MCP Generator Tasks
Defines the specific tasks that agents will perform
"""

from crewai import Task


def create_research_task(agent, api_name: str) -> Task:
    """
    Task: Research API and extract specifications
    
    The researcher analyzes the API and provides complete specifications.
    """
    return Task(
        description=f"""Research the {api_name} API and extract complete specifications.

Your analysis should include:
1. API base URL and version
2. Authentication method (API key, OAuth, Bearer token, etc.)
3. 5-10 most useful endpoints for an MCP server
4. Request/response formats for each endpoint
5. Required parameters and optional parameters
6. Error handling patterns

Provide a structured specification document that the architect can use to design the MCP server.

API to research: {api_name}
""",
        expected_output="""A detailed API specification document including:
- Base URL
- Authentication details
- List of recommended endpoints with:
  * Endpoint path
  * HTTP method
  * Parameters
  * Response format
  * Use case description
""",
        agent=agent
    )


def create_architecture_task(agent, api_name: str, research_output: str = None) -> Task:
    """
    Task: Design MCP server architecture
    
    The architect designs the structure and tools for the MCP server.
    """
    context_note = ""
    if research_output:
        context_note = f"\nUse this research: {research_output}\n"
    
    return Task(
        description=f"""Design the architecture for the {api_name} MCP server.
{context_note}
Create a detailed design including:
1. List of 5-8 MCP tools (functions the server will provide)
2. Tool schemas (name, description, parameters)
3. Project structure (files and directories)
4. Dependencies needed
5. Error handling strategy

Each tool should:
- Have a clear, specific purpose
- Accept well-defined parameters
- Return structured data
- Handle errors gracefully

Design for: {api_name} MCP Server
""",
        expected_output="""Complete MCP server architecture design including:
- List of tools with schemas
- Project file structure
- Required dependencies
- Implementation notes
Format as structured document that developers can implement directly.
""",
        agent=agent
    )


def create_development_task(agent, api_name: str, architecture: str = None) -> Task:
    """
    Task: Implement the MCP server code
    
    The developer writes production-ready Python code.
    """
    context_note = ""
    if architecture:
        context_note = f"\nImplement this architecture: {architecture}\n"
    
    return Task(
        description=f"""Implement the {api_name} MCP server in Python.
{context_note}
Write complete, production-ready code including:
1. Main server.py file with MCP server implementation
2. Async functions for each tool
3. API client with proper authentication
4. Error handling and logging
5. Type hints and docstrings
6. Demo mode (works without API key)

Requirements:
- Use async/await for all API calls
- Include comprehensive docstrings
- Handle errors gracefully with fallbacks
- Follow PEP 8 style guidelines
- Make code readable and maintainable

Generate code for: {api_name} MCP Server
""",
        expected_output="""Complete server.py file containing:
- Import statements
- API client class
- MCP server implementation
- Tool functions (5-8 tools)
- Demo/fallback mode
- Proper error handling
- Full documentation
Ready to save and run.
""",
        agent=agent
    )


def create_testing_task(agent, api_name: str) -> Task:
    """
    Task: Test the MCP server
    
    The QA engineer tests the implementation.
    """
    return Task(
        description=f"""Test the {api_name} MCP server implementation.

Perform these tests:
1. Syntax validation (Python code is valid)
2. Import checks (all required libraries)
3. Function signature validation (tools are properly defined)
4. Error handling review (catches exceptions)
5. Documentation review (has docstrings)

Provide a test report with:
- What passed ✅
- What failed ❌
- Suggestions for improvements
- Overall quality assessment

Test: {api_name} MCP Server
""",
        expected_output="""Complete test report including:
- Syntax validation: PASS/FAIL
- Import checks: PASS/FAIL
- Function validation: PASS/FAIL
- Error handling: PASS/FAIL
- Documentation: PASS/FAIL
- Detailed findings and recommendations
""",
        agent=agent
    )


def create_configuration_task(agent, api_name: str) -> Task:
    """
    Task: Create configuration and documentation
    
    The DevOps specialist creates all configuration files and docs.
    """
    return Task(
        description=f"""Create complete configuration and documentation for {api_name} MCP server.

Generate these files:
1. requirements.txt (all Python dependencies)
2. .env.example (environment variable template)
3. README.md (comprehensive documentation)
4. mcp_config.json (Claude Desktop configuration)

README should include:
- Project description
- Features list
- Installation instructions
- Quick start guide
- Usage examples
- Claude Desktop integration
- Troubleshooting

Make documentation beginner-friendly and complete.

Configure: {api_name} MCP Server
""",
        expected_output="""Configuration package including:
- requirements.txt content
- .env.example content
- Complete README.md
- mcp_config.json for Claude Desktop
All files ready to be written to project.
""",
        agent=agent
    )


def create_coordination_task(agent, api_name: str) -> Task:
    """
    Task: Coordinate the entire generation process
    
    The coordinator ensures everything comes together.
    """
    return Task(
        description=f"""Coordinate the generation of a complete {api_name} MCP server.

Oversee these phases:
1. Research Phase: Ensure API is fully analyzed
2. Architecture Phase: Review and approve design
3. Development Phase: Ensure code quality
4. Testing Phase: Verify all tests pass
5. Configuration Phase: Complete project setup

Your role:
- Delegate tasks to appropriate agents
- Review outputs from each phase
- Ensure quality at each step
- Make decisions on approach
- Deliver complete, working MCP server

Coordinate: {api_name} MCP Server Generation
""",
        expected_output="""Final project status report including:
- Completion status of each phase
- Quality assessment
- List of generated files
- Next steps for user
- Overall success confirmation
""",
        agent=agent
    )
