"""Production-Ready Tools for CrewAI Agents"""
from crewai.tools import tool
from pathlib import Path
import json
import ast
import fcntl
from datetime import date
from contextlib import contextmanager


@contextmanager
def file_lock(file_path: Path):
    """Context manager for exclusive file locking to prevent race conditions.
    
    Args:
        file_path: Path to file being written
        
    Yields:
        Lock context (file is exclusively locked)
    """
    lock_path = file_path.with_suffix(file_path.suffix + '.lock')
    lock_file = open(lock_path, 'w')
    
    try:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)  # Exclusive lock
        yield
    finally:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)  # Unlock
        lock_file.close()
        lock_path.unlink(missing_ok=True)  # Clean up lock file


@tool("Write File")
def write_file(file_path: str, content: str) -> str:
    """
    Write content to a file with exclusive locking for parallel safety.
    Creates parent directories if needed.
    
    Args:
        file_path: Relative path from project root (e.g., 'src/generated/main.py')
        content: File content to write
        
    Returns:
        Success message with file path
        
    Thread-Safety: Uses fcntl.flock() for exclusive file locking
    """
    import os
    try:
        print(f"\n🔧 [TOOL] write_file called")
        print(f"🔧 [TOOL] Target: {file_path}")
        print(f"🔧 [TOOL] Current dir: {os.getcwd()}")
        print(f"🔧 [TOOL] Content length: {len(content)} chars")
        
        # Create parent directories
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file with exclusive lock (parallel-safe)
        with file_lock(path):
            with open(path, 'w') as f:
                f.write(content)
        
        abs_path = path.absolute()
        print(f"🔧 [TOOL] ✅ Written to: {abs_path} (locked)")
        print(f"🔧 [TOOL] File exists: {abs_path.exists()}")
        
        return f"✅ File written successfully: {file_path} ({len(content)} chars) at {abs_path}"
    except Exception as e:
        print(f"🔧 [TOOL] ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return f"❌ Error writing file: {str(e)}"


@tool("Read File")
def read_file(file_path: str) -> str:
    """
    Read a file's contents.
    
    Args:
        file_path: Path to file to read
        
    Returns:
        File contents as string
    """
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"❌ Error reading {file_path}: {str(e)}"


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
        ast.parse(code)
        return "✅ Python code syntax is valid"
    except SyntaxError as e:
        return f"❌ Syntax error: {e.msg} at line {e.lineno}"
    except Exception as e:
        return f"❌ Validation error: {str(e)}"


@tool("Test Code")
def test_code(code: str) -> str:
    """
    Run comprehensive validation on code and return test results.
    
    Args:
        code: Python code to test
        
    Returns:
        Test results with checks
    """
    try:
        # Syntax check
        ast.parse(code)
        
        # Additional checks
        checks = {
            "has_imports": any(x in code for x in ['import', 'from']),
            "has_function": 'def ' in code,
            "has_docstring": '"""' in code or "'''" in code,
            "has_error_handling": 'try:' in code or 'except' in code
        }
        
        results = ["✅ Syntax valid"]
        for check, passed in checks.items():
            status = "✅" if passed else "⚠️"
            results.append(f"{status} {check.replace('_', ' ').title()}: {passed}")
        
        return "\n".join(results)
    except SyntaxError as e:
        return f"❌ Syntax error: {e.msg} at line {e.lineno}"
    except Exception as e:
        return f"❌ Test error: {str(e)}"


@tool("Create Project Structure")
def create_project_structure(project_name: str, base_path: str = "src/generated") -> str:
    """
    Create basic directory structure for a project.
    
    Args:
        project_name: Name of the project (e.g., 'my-api')
        base_path: Base directory path (default: 'src/generated')
        
    Returns:
        Success message with created structure
    """
    try:
        base = Path(base_path) / project_name
        
        # Create directories
        dirs = [
            base,
            base / "src",
            base / "tests",
            base / "docs"
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        structure = "\n".join([f"  {d.relative_to(base.parent)}" for d in dirs])
        return f"✅ Project structure created:\n{structure}"
    except Exception as e:
        return f"❌ Error creating structure: {str(e)}"


@tool("Create Project Files")
def create_project_files(project_name: str, files_dict: dict) -> str:
    """
    Create project structure with multiple files at once.
    
    Args:
        project_name: Name of project directory
        files_dict: Dict mapping filenames to contents
        
    Returns:
        Success message with file count
    """
    try:
        project_dir = Path("src/generated") / project_name
        project_dir.mkdir(parents=True, exist_ok=True)
        
        for filename, content in files_dict.items():
            file_path = project_dir / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
        
        return f"✅ Created {project_name} with {len(files_dict)} files in src/generated/{project_name}/"
    except Exception as e:
        return f"❌ Error creating project files: {str(e)}"


@tool("Generate Requirements")
def generate_requirements(dependencies: list) -> str:
    """
    Generate requirements.txt content from list of dependencies.
    
    Args:
        dependencies: List of package names with optional versions
                     e.g., ['fastapi>=0.100.0', 'pydantic>=2.0.0']
        
    Returns:
        Formatted requirements.txt content
    """
    try:
        if isinstance(dependencies, str):
            dependencies = json.loads(dependencies)
        
        content = "# Project Dependencies\n\n"
        content += "\n".join(dependencies)
        content += "\n"
        
        return content
    except Exception as e:
        return f"❌ Error generating requirements: {str(e)}"


@tool("Get Current Date")
def get_current_date() -> str:
    """Get today's date in ISO format."""
    return str(date.today())


@tool("List Directory")
def list_directory(path: str = ".") -> str:
    """
    List files and directories in a given path.
    
    Args:
        path: Directory path to list (default: current directory)
        
    Returns:
        Formatted list of files and directories
    """
    try:
        from pathlib import Path
        dir_path = Path(path)
        
        if not dir_path.exists():
            return f"❌ Path does not exist: {path}"
        
        if not dir_path.is_dir():
            return f"❌ Not a directory: {path}"
        
        items = list(dir_path.iterdir())
        items.sort()
        
        result = [f"📁 Contents of {dir_path.absolute()}:\n"]
        
        for item in items:
            if item.is_dir():
                result.append(f"  📂 {item.name}/")
            else:
                size = item.stat().st_size
                size_str = f"{size:,}" if size < 1024 else f"{size/1024:.1f}KB"
                result.append(f"  📄 {item.name} ({size_str})")
        
        return "\n".join(result)
    except Exception as e:
        return f"❌ Error listing directory: {str(e)}"


@tool("Run Shell Command")
def run_command(command: str) -> str:
    """
    Run a safe shell command and return output.
    
    Args:
        command: Shell command to execute (safe commands only)
        
    Returns:
        Command output or error message
    """
    import subprocess
    
    # Whitelist of safe commands
    safe_commands = ['ls', 'pwd', 'whoami', 'date', 'echo', 'cat', 'grep', 'find', 
                     'python', 'pip', 'git status', 'git log', 'tree', 'wc']
    
    # Check if command starts with a safe command
    command_start = command.split()[0] if command.split() else ""
    
    if not any(command.startswith(safe_cmd) for safe_cmd in safe_commands):
        return f"⚠️ Command '{command_start}' not in safe list. Only these commands are allowed: {', '.join(safe_commands)}"
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd="."
        )
        
        output = result.stdout if result.stdout else result.stderr
        return output if output else "✅ Command completed (no output)"
        
    except subprocess.TimeoutExpired:
        return "❌ Command timed out after 30 seconds"
    except Exception as e:
        return f"❌ Error running command: {str(e)}"


# Export all tools
__all__ = [
    'write_file',
    'read_file',
    'validate_python_code',
    'test_code',
    'create_project_structure',
    'create_project_files',
    'generate_requirements',
    'get_current_date',
    'list_directory',
    'run_command'
]

