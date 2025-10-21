"""
Custom Tools for MCP Generator
Tools that agents use to generate, test, and configure MCP servers
"""

from crewai.tools import tool
import os
import json
from pathlib import Path


@tool("Write File")
def write_file(file_path: str, content: str) -> str:
    """
    Write content to a file. Creates parent directories if needed.
    
    Args:
        file_path: Relative path from project root (e.g., 'server.py')
        content: File content to write
        
    Returns:
        Success message with file path
    """
    try:
        # Create parent directories
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        with open(path, 'w') as f:
            f.write(content)
        
        return f"✅ File written successfully: {file_path} ({len(content)} chars)"
    except Exception as e:
        return f"❌ Error writing file: {str(e)}"


@tool("Read Template")
def read_template(template_name: str) -> str:
    """
    Read a template file from the templates directory.
    
    Args:
        template_name: Name of template (e.g., 'server_base.py')
        
    Returns:
        Template content as string
    """
    try:
        template_path = Path(__file__).parent / "templates" / template_name
        
        if not template_path.exists():
            return f"❌ Template not found: {template_name}"
        
        with open(template_path, 'r') as f:
            content = f.read()
        
        return content
    except Exception as e:
        return f"❌ Error reading template: {str(e)}"


@tool("Validate Python Code")
def validate_python_code(code: str) -> str:
    """
    Validate Python code syntax without executing it.
    
    Args:
        code: Python code to validate
        
    Returns:
        Validation result message
    """
    try:
        import ast
        ast.parse(code)
        return "✅ Python code syntax is valid"
    except SyntaxError as e:
        return f"❌ Syntax error: {e.msg} at line {e.lineno}"
    except Exception as e:
        return f"❌ Validation error: {str(e)}"


@tool("Create Project Structure")
def create_project_structure(project_name: str, base_path: str) -> str:
    """
    Create basic directory structure for an MCP server project.
    
    Args:
        project_name: Name of the MCP server project (e.g., 'stripe-mcp-server')
        base_path: Base directory path
        
    Returns:
        Success message with created structure
    """
    try:
        base = Path(base_path) / project_name
        
        # Create directories
        dirs = [
            base,
            base / "docs",
            base / "tests"
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        structure = "\n".join([f"  {d.relative_to(base.parent)}" for d in dirs])
        return f"✅ Project structure created:\n{structure}"
    except Exception as e:
        return f"❌ Error creating structure: {str(e)}"


@tool("Generate Requirements")
def generate_requirements(dependencies: list) -> str:
    """
    Generate requirements.txt content from list of dependencies.
    
    Args:
        dependencies: List of package names with optional versions
                     e.g., ['aiohttp>=3.8.0', 'pydantic>=2.0.0']
        
    Returns:
        Formatted requirements.txt content
    """
    try:
        if isinstance(dependencies, str):
            dependencies = json.loads(dependencies)
        
        content = "# MCP Server Dependencies\n\n"
        content += "\n".join(dependencies)
        content += "\n"
        
        return content
    except Exception as e:
        return f"❌ Error generating requirements: {str(e)}"


@tool("Test MCP Server")
def test_mcp_server(server_path: str) -> str:
    """
    Run basic tests on an MCP server (check imports, syntax).
    
    Args:
        server_path: Path to server.py file
        
    Returns:
        Test results
    """
    try:
        # Check if file exists
        path = Path(server_path)
        if not path.exists():
            return f"❌ Server file not found: {server_path}"
        
        # Read and validate
        with open(path, 'r') as f:
            code = f.read()
        
        # Check syntax
        import ast
        ast.parse(code)
        
        # Check for required components
        checks = {
            "has_imports": any(x in code for x in ['import', 'from']),
            "has_async": 'async' in code or 'await' in code,
            "has_function": 'def ' in code,
            "has_docstring": '"""' in code or "'''" in code
        }
        
        results = []
        for check, passed in checks.items():
            status = "✅" if passed else "⚠️"
            results.append(f"{status} {check.replace('_', ' ').title()}: {passed}")
        
        return "\n".join(results)
    except Exception as e:
        return f"❌ Test error: {str(e)}"


@tool("Format JSON")
def format_json(data: dict) -> str:
    """
    Format a dictionary as pretty-printed JSON.
    
    Args:
        data: Dictionary to format
        
    Returns:
        Formatted JSON string
    """
    try:
        if isinstance(data, str):
            data = json.loads(data)
        
        return json.dumps(data, indent=2)
    except Exception as e:
        return f"❌ Error formatting JSON: {str(e)}"


@tool("Check API Documentation")
def check_api_documentation(api_name: str) -> str:
    """
    Provide guidance on where to find API documentation.
    
    Args:
        api_name: Name of the API (e.g., 'stripe', 'github', 'easyship')
        
    Returns:
        Information about API documentation
    """
    api_docs = {
        "stripe": {
            "url": "https://stripe.com/docs/api",
            "auth": "API Key",
            "base": "https://api.stripe.com/v1",
            "tools": ["create_payment", "list_customers", "create_subscription"]
        },
        "github": {
            "url": "https://docs.github.com/en/rest",
            "auth": "Token",
            "base": "https://api.github.com",
            "tools": ["create_repo", "list_issues", "create_pr"]
        },
        "easyship": {
            "url": "https://developers.easyship.com/reference",
            "auth": "Bearer Token",
            "base": "https://api.easyship.com/2023-01",
            "tools": ["get_rates", "create_shipment", "track_shipment"]
        },
        "openai": {
            "url": "https://platform.openai.com/docs/api-reference",
            "auth": "API Key",
            "base": "https://api.openai.com/v1",
            "tools": ["chat_completion", "create_embedding", "generate_image"]
        }
    }
    
    if api_name.lower() in api_docs:
        info = api_docs[api_name.lower()]
        return f"""API: {api_name.title()}
Documentation: {info['url']}
Authentication: {info['auth']}
Base URL: {info['base']}
Suggested Tools: {', '.join(info['tools'])}
"""
    else:
        return f"""API: {api_name.title()}
Status: Not in database
Suggestion: Search for "{api_name} API documentation" to find:
  - Base URL
  - Authentication method
  - Available endpoints
  - Request/response formats
"""
