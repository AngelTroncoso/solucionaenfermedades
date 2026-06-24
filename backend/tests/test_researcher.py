"""Tests for researcher agent."""

import pytest
from unittest.mock import Mock
from agents.researcher import ResearcherAgent


@pytest.fixture
def config():
    return {
        "max_papers": 100,
        "search_days_back": 365
    }


@pytest.fixture
def researcher(config):
    return ResearcherAgent(config)


def test_researcher_init(researcher):
    """Test researcher initialization."""
    assert researcher.config is not None


def test_research(researcher):
    """Test research workflow."""
    task = {
        "name": "test",
        "topic": "EGFR inhibitors"
    }
    
    result = researcher.research(task)
    
    assert "topic" in result
    assert result["topic"] == "EGFR inhibitors"
    assert "literature" in result
    assert "databases" in result
    assert "patents" in result