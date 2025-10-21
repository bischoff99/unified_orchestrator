"""Basic integration tests for the ProductionCrew orchestrator."""

import pytest

from src.orchestrator.crew_config import ProductionCrew


def test_agents_initialized():
    """Ensure the production crew initializes all expected agents."""
    crew = ProductionCrew("Test task")

    assert len(crew.agents) == 6
    assert "architect" in crew.agents
    assert "qa" in crew.agents

    print("✅ All 6 agents initialized")


def test_simple_task_ollama():
    """Run the production crew on a simple task and validate the output."""
    crew = ProductionCrew("Create a Python function that adds two numbers")

    result = crew.run()
    assert result is not None

    output_length = len(str(result))
    assert output_length > 50

    print(f"Output length: {output_length}")

