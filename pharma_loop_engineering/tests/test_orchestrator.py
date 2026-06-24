"""Tests for orchestrator agent."""

import pytest
from unittest.mock import Mock, MagicMock
from agents.orchestrator import OrchestratorAgent


@pytest.fixture
def config():
    return {
        "max_iterations": 10,
        "timeout": 3600
    }


@pytest.fixture
def orchestrator(config):
    return OrchestratorAgent(config)


def test_orchestrator_init(orchestrator):
    """Test orchestrator initialization."""
    assert orchestrator.config is not None
    assert orchestrator.agents == {}


def test_register_agent(orchestrator):
    """Test agent registration."""
    mock_agent = Mock()
    orchestrator.register_agent("test", mock_agent)
    assert "test" in orchestrator.agents
    assert orchestrator.agents["test"] == mock_agent


def test_run_workflow(orchestrator):
    """Test workflow execution."""
    mock_researcher = Mock()
    mock_researcher.research.return_value = {"topic": "test"}
    
    mock_designer = Mock()
    mock_designer.design.return_value = {"candidates": []}
    
    orchestrator.register_agent("researcher", mock_researcher)
    orchestrator.register_agent("designer", mock_designer)
    orchestrator.register_agent("implementer", Mock())
    orchestrator.register_agent("evaluator", Mock())
    orchestrator.register_agent("refiner", Mock())
    
    task = {"name": "test_task", "topic": "cancer"}
    result = orchestrator.run_workflow(task)
    
    assert "research" in result
    assert "design" in result
    assert mock_researcher.research.called
    assert mock_designer.design.called


def test_get_status(orchestrator):
    """Test status reporting."""
    status = orchestrator.get_status()
    assert "registered_agents" in status
    assert "config" in status