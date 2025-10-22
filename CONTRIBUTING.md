# Contributing to Unified Orchestrator

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## 🚀 Quick Start

### Development Setup

```bash
# Clone the repository
git clone https://github.com/USER/unified_orchestrator.git
cd unified_orchestrator

# Create virtual environment (Python 3.11+)
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Verify installation
pytest -q
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_resume.py

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run golden tests
pytest tests/test_golden.py

# Run tests in parallel
pytest -n auto
```

## 📁 Project Structure

```
unified_orchestrator/
├── src/
│   ├── core/              # Core systems (DAG, events, cache, filestore)
│   ├── orchestrator/       # Orchestration logic
│   ├── providers/          # LLM provider adapters
│   ├── agents/             # Agent implementations
│   ├── tools/              # LangChain and production tools
│   └── utils/              # Utilities
├── tests/                  # Test suite
│   ├── golden/             # Golden test fixtures
│   └── test_*.py           # Test modules
├── docs/                   # Documentation
├── examples/               # Usage examples
└── pyproject.toml          # Project configuration
```

## 🧪 Testing Guidelines

### Writing Tests

1. **Use pytest** for all tests
2. **Follow naming convention**: `test_<feature>_<scenario>.py`
3. **Use fixtures** for setup/teardown
4. **Test one thing** per test function
5. **Use descriptive names**: `test_resume_skips_completed_steps_correctly()`

### Test Categories

- **Unit Tests**: Test individual functions/classes in isolation
- **Integration Tests**: Test interactions between components
- **Golden Tests**: Verify output against known-good fixtures
- **Async Tests**: Use `@pytest.mark.asyncio` for async code

### Example Test

```python
import pytest
from src.core.cache import compute_cache_key

def test_cache_key_deterministic():
    """Cache keys should be stable for identical inputs."""
    provider = {"name": "ollama", "model": "llama3"}
    
    key1 = compute_cache_key(provider, "architect", {"task": "test"})
    key2 = compute_cache_key(provider, "architect", {"task": "test"})
    
    assert key1 == key2
    assert len(key1) == 64  # SHA256 hex length
```

## 💻 Code Style

### Python Standards

- **Python Version**: 3.11+ (use modern type hints)
- **Type Hints**: Required for all public functions
- **Docstrings**: Google-style docstrings for modules, classes, functions
- **Line Length**: 100 characters (soft limit)

### Formatting

We use **black** for code formatting and **ruff** for linting:

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Auto-fix issues
ruff check --fix src/ tests/
```

### Type Checking

```bash
# Run mypy (optional but recommended)
mypy src/
```

## 📝 Commit Conventions

We follow [Conventional Commits](https://www.conventionalcommits.org/):

### Commit Format

```
<type>(<scope>): <subject>

<body (optional)>

<footer (optional)>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions/changes
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `ci`: CI/CD changes
- `chore`: Maintenance tasks

### Scopes

- `events`: Event system changes
- `dag`: DAG execution changes
- `cache`: Caching system changes
- `providers`: Provider adapter changes
- `cli`: CLI changes
- `filestore`: FileStore changes

### Examples

```bash
feat(events): add llm.request and llm.response events

- Emit llm.request before provider call
- Emit llm.response after provider returns
- Include duration, tokens, and success status

Closes #123
```

```bash
fix(cache): handle missing cache directory gracefully

Previously crashed if .cache/ didn't exist. Now creates it automatically.
```

```bash
test(resume): add comprehensive resume-from-failure tests

- test_resume_skips_completed_steps
- test_resume_after_failure
- test_resume_parallel_steps
```

## 🔄 Pull Request Process

### Before Submitting

1. **Create a feature branch**: `git checkout -b feat/your-feature`
2. **Write tests**: Ensure new code has test coverage
3. **Update docs**: Update README, docstrings, or docs/ as needed
4. **Run tests locally**: `pytest` should pass
5. **Format code**: Run `black` and `ruff`
6. **Write good commits**: Follow commit conventions

### PR Title Format

Use conventional commit format:
- `feat: add resume-from-failure functionality`
- `fix: correct cache key computation for nested inputs`
- `docs: update ARCHITECTURE.md with caching strategy`

### PR Description Template

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Added/updated unit tests
- [ ] Added/updated integration tests
- [ ] Manual testing performed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings introduced
- [ ] Tests pass locally
```

### Review Process

1. **CI must pass**: All tests, linting, formatting checks
2. **Code review**: At least one maintainer approval
3. **No merge conflicts**: Rebase on main if needed
4. **Squash commits**: For clean history (optional)

## 🐛 Reporting Bugs

### Bug Report Template

```markdown
**Describe the bug**
Clear description of the bug.

**To Reproduce**
Steps to reproduce:
1. Run command '...'
2. Observe error '...'

**Expected behavior**
What you expected to happen.

**Environment**
- OS: [e.g., macOS 14.0, Ubuntu 22.04]
- Python version: [e.g., 3.11.5]
- Package version: [e.g., 2.1.0]

**Additional context**
Logs, screenshots, or other relevant information.
```

## 💡 Feature Requests

### Feature Request Template

```markdown
**Problem Statement**
Describe the problem or limitation.

**Proposed Solution**
Your suggested approach.

**Alternatives Considered**
Other approaches you've thought about.

**Additional Context**
Use cases, examples, or related issues.
```

## 📚 Documentation

### When to Update Docs

- **New features**: Update README, add examples
- **Breaking changes**: Update MIGRATION.md
- **Architecture changes**: Update docs/ARCHITECTURE.md
- **API changes**: Update docstrings and type hints

### Documentation Standards

- **Clear and concise**: Avoid jargon
- **Code examples**: Include runnable examples
- **Keep it current**: Update docs with code changes
- **Use markdown**: Follow GitHub markdown syntax

## 🔐 Security

If you discover a security vulnerability:

1. **Do NOT** open a public issue
2. Email security@example.com (replace with actual)
3. Include detailed description and reproduction steps
4. Allow time for fix before public disclosure

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and general discussion
- **Discord**: [Link to Discord server] (if available)

## 📄 License

By contributing, you agree that your contributions will be licensed under the project's MIT License.

---

**Thank you for contributing to Unified Orchestrator!** 🎉
