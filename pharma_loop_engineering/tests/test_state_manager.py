"""Tests for state manager."""

import pytest
from unittest.mock import Mock
from worktrees.state_manager import StateManager


@pytest.fixture
def config():
    return {
        "max_worktrees": 10
    }


@pytest.fixture
def state_manager(config):
    return StateManager(config)


def test_state_manager_init(state_manager):
    """Test state manager initialization."""
    assert state_manager.config is not None
    assert state_manager.worktrees == {}


def test_create_worktree(state_manager):
    """Test worktree creation."""
    worktree = state_manager.create_worktree(
        name="test",
        branch="main",
        path="/tmp/test"
    )
    
    assert worktree["name"] == "test"
    assert worktree["branch"] == "main"
    assert worktree["status"] == "active"
    assert "test" in state_manager.worktrees


def test_register_experiment(state_manager):
    """Test experiment registration."""
    state_manager.create_worktree("test", "main", "/tmp/test")
    
    experiment = {
        "type": "test_experiment",
        "parameters": {"param": "value"}
    }
    
    state_manager.register_experiment("test", experiment)
    
    assert len(state_manager.worktrees["test"]["experiments"]) == 1
    assert "timestamp" in state_manager.worktrees["test"]["experiments"][0]


def test_get_state(state_manager):
    """Test state retrieval."""
    state_manager.create_worktree("test", "main", "/tmp/test")
    
    state = state_manager.get_state()
    
    assert "worktrees" in state
    assert "timestamp" in state
    assert "test" in state["worktrees"]