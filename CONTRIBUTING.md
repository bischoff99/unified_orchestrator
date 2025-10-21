# Contributing to Unified Orchestrator

Thank you for your interest in contributing to the Unified Orchestrator! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Making Changes](#making-changes)
- [Testing Guidelines](#testing-guidelines)
- [Code Style](#code-style)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Adding New Agents](#adding-new-agents)
- [Adding New Tools](#adding-new-tools)

## Code of Conduct

This project adheres to a code of conduct that all contributors are expected to follow:

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive criticism
- Respect differing viewpoints and experiences
- Show empathy towards other community members

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/unified_orchestrator.git
   cd unified_orchestrator
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/original-owner/unified_orchestrator.git
   ```

## Development Setup

### Prerequisites

- Python 3.9+
- macOS with Apple Silicon (for MLX features) or any OS for other backends
- Ollama (for local LLM) or API keys for cloud providers

### Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-asyncio pytest-cov black flake8 isort mypy

# Install Tier 1 performance libraries (recommended)
pip install faiss-cpu beautifulsoup4 lxml numba orjson

# Configure environment
cp .env.example .env
# Edit .env with your settings
```

### Setup Ollama (Local Development)

```bash
# Install Ollama
brew install ollama

# Start Ollama server
ollama serve

# Pull development model
ollama pull llama3.1:8b-instruct-q5_K_M
```

## Project Structure

```
unified_orchestrator/
├── src/
│   ├── agents/           # Agent implementations
│   ├── orchestrator/     # Crew configuration
│   ├── tools/            # Agent tools
│   ├── utils/            # Utilities
│   └── generated/        # Agent outputs (gitignored)
├── tests/                # Test suite
├── examples/             # Usage examples
├── docs/                 # Documentation
├── main.py              # Entry point
├── config.py            # Configuration
└── requirements.txt     # Dependencies
```

## Making Changes

### Branch Naming Convention

- **Feature**: `feature/description`
- **Bug fix**: `fix/description`
- **Documentation**: `docs/description`
- **Performance**: `perf/description`
- **Refactor**: `refactor/description`

Example:
```bash
git checkout -b feature/add-monitoring-agent
```

### Development Workflow

1. **Create a branch** from `develop`:
   ```bash
   git checkout develop
   git pull upstream develop
   git checkout -b feature/your-feature
   ```

2. **Make your changes** following the code style guidelines

3. **Write tests** for your changes

4. **Run tests locally**:
   ```bash
   pytest tests/ -v
   ```

5. **Format your code**:
   ```bash
   black src/
   isort src/
   ```

6. **Lint your code**:
   ```bash
   flake8 src/
   ```

7. **Commit your changes** (see commit message guidelines)

8. **Push to your fork**:
   ```bash
   git push origin feature/your-feature
   ```

9. **Create a Pull Request** on GitHub

## Testing Guidelines

### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Use descriptive test names: `test_agent_creates_valid_output()`
- Aim for >80% code coverage

### Test Structure

```python
import pytest
from src.agents.architect_agent import ArchitectAgent

def test_architect_agent_initialization():
    """Test that ArchitectAgent initializes correctly."""
    agent = ArchitectAgent()
    assert agent is not None
    assert agent.create() is not None

@pytest.mark.asyncio
async def test_architect_agent_execution():
    """Test that ArchitectAgent can execute tasks."""
    # Your async test here
    pass
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_orchestration.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Code Style

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line length**: 127 characters (not 79)
- **String quotes**: Use double quotes `"` for strings
- **Docstrings**: Use triple double quotes `"""`

### Code Formatting

Use **Black** for automatic formatting:

```bash
black src/
```

### Import Sorting

Use **isort** for import organization:

```bash
isort src/
```

### Type Hints

Use type hints for function signatures:

```python
def create_agent(name: str, role: str) -> Agent:
    """Create a new agent with the specified role."""
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def execute_task(task: str, backend: str = "ollama") -> dict:
    """Execute a task using the specified LLM backend.
    
    Args:
        task: Natural language description of the task
        backend: LLM backend to use (default: "ollama")
    
    Returns:
        Dictionary containing execution results and metrics
    
    Raises:
        ValueError: If backend is not supported
        RuntimeError: If execution fails
    """
    pass
```

## Commit Messages

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, missing semicolons, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### Examples

```
feat(agents): Add monitoring agent for system health

- Implements MonitoringAgent with health check capabilities
- Adds system metrics collection
- Integrates with existing orchestrator workflow

Closes #123
```

```
fix(vector-store): Resolve FAISS initialization error

- Fix path resolution for FAISS index
- Add error handling for missing index files
- Update documentation

Fixes #456
```

## Pull Request Process

### Before Submitting

- [ ] All tests pass locally
- [ ] Code is formatted with Black
- [ ] Imports are sorted with isort
- [ ] Linting passes (flake8)
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated (if applicable)

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe how you tested your changes

## Checklist
- [ ] Tests pass locally
- [ ] Code is formatted (black, isort)
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
```

### Review Process

1. Automated CI/CD checks must pass
2. At least one maintainer review required
3. All review comments must be addressed
4. No merge conflicts with base branch

## Adding New Agents

### Agent Template

```python
"""MyAgent - Description of agent purpose"""
from crewai import Agent
from config import get_llm_backend
from src.utils.llm_tools import get_llm_tools

class MyAgent:
    def __init__(self):
        self.tools = get_llm_tools()
        self.llm = get_llm_backend()

    def create(self) -> Agent:
        """Create CrewAI agent for specific task"""
        return Agent(
            role="Agent Role",
            goal="Specific goal for this agent",
            backstory="Background that defines agent expertise",
            tools=self.tools,
            llm=self.llm,
            verbose=True,
        )
```

### Integration Steps

1. Create agent file in `src/agents/`
2. Add agent to `src/orchestrator/crew_config.py`
3. Create tasks for the agent
4. Write tests in `tests/`
5. Update documentation

## Adding New Tools

### Tool Template

```python
from crewai_tools import BaseTool

class MyCustomTool(BaseTool):
    name: str = "Tool Name"
    description: str = "What this tool does"
    
    def _run(self, argument: str) -> str:
        """Execute tool with given argument."""
        # Tool implementation
        return result
```

### Tool Guidelines

- Keep tools focused on a single responsibility
- Provide clear descriptions for LLM understanding
- Handle errors gracefully
- Add comprehensive docstrings
- Write tests for tool functionality

### Adding to Agents

```python
# In src/tools/production_tools.py
from crewai_tools import tool

@tool("tool_name")
def my_custom_tool(input_param: str) -> str:
    """Tool description for LLM."""
    # Implementation
    return result

# Register in get_llm_tools()
def get_llm_tools():
    return [my_custom_tool, other_tools...]
```

## Performance Considerations

### M3 Max Optimization

- Use MLX backend for Apple Silicon when possible
- Configure Ollama for optimal performance (see M3_MAX_OPTIMIZATION_GUIDE.md)
- Use FAISS for vector operations >10K items
- Enable parallel execution for independent tasks

### Memory Management

- Clean up large objects after use
- Use generators for large datasets
- Monitor memory usage with `memory_profiler`

## Documentation

### Required Documentation

- **Docstrings**: All public functions and classes
- **README updates**: For new features
- **API.md updates**: For API changes
- **Examples**: For new capabilities

### Documentation Style

- Use clear, concise language
- Include code examples
- Add diagrams for complex concepts (Mermaid)
- Keep documentation up to date with code

## Questions?

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and ideas
- **Documentation**: See `docs/` directory

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

**Thank you for contributing to Unified Orchestrator!** 🚀