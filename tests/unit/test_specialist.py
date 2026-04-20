import pytest
from unittest.mock import patch, MagicMock
from src.agents.specialists.factory import SpecialistFactory
from src.agents.specialists.base import BaseSpecialistAgent

class MockAgent(BaseSpecialistAgent):
    def __init__(self):
        super().__init__("mock_id", "Mock Title", "Mock Objective")

def test_base_specialist_prompt_building():
    agent = MockAgent()
    prompt = agent.build_prompt("http://github.com/test", "Past memory context")
    
    assert "Mock Title" in prompt
    assert "Mock Objective" in prompt
    assert "http://github.com/test" in prompt
    assert "Past memory context" in prompt
    assert "### Score" in prompt
    assert "**CRITICAL**: Do NOT generate any Mermaid" in prompt

@patch("src.agents.specialists.base.get_llm")
@patch("src.agents.specialists.base.create_agent")
def test_base_specialist_run(mock_create_agent, mock_get_llm):
    mock_llm = MagicMock()
    mock_get_llm.return_value = mock_llm
    
    mock_executor = MagicMock()
    mock_executor.invoke.return_value = {"messages": [MagicMock(content="Agent analysis result")]}
    mock_create_agent.return_value = mock_executor
    
    agent = MockAgent()
    result = agent.run("http://repo", "model-abc", "memory")
    
    assert result == "Agent analysis result"
    mock_get_llm.assert_called_once_with(model_name="model-abc", temperature=0)
    mock_create_agent.assert_called_once()

def test_factory_get_agent():
    agent = SpecialistFactory.get_agent("architect_design")
    assert agent.id == "architect_design"
    assert "Architect" in agent.title

    with pytest.raises(ValueError, match="Unknown specialist agent ID"):
        SpecialistFactory.get_agent("non_existent_agent")

def test_factory_get_active_definitions():
    defs = SpecialistFactory.get_active_definitions(["architect_design", "security_quality"])
    assert len(defs) == 2
    assert defs[0]["id"] == "architect_design"
    assert defs[1]["id"] == "security_quality"

@patch("src.agents.specialists.factory.SpecialistFactory.get_agent")
@patch("src.agents.specialists.factory.time.sleep")
def test_run_agent_with_retries_success(mock_sleep, mock_get_agent):
    mock_agent = MagicMock()
    mock_agent.run.return_value = "Success content"
    mock_get_agent.return_value = mock_agent
    
    content, model_name = SpecialistFactory.run_agent_with_retries(
        "http://repo", "id", ["m1", "m2"], 1, 1, "memory"
    )
    
    assert content == "Success content"
    assert model_name == "m1"
    mock_agent.run.assert_called_once_with("http://repo", "m1", "memory")

@patch("src.agents.specialists.factory.SpecialistFactory.get_agent")
@patch("src.agents.specialists.factory.time.sleep")
def test_run_agent_with_retries_fallback(mock_sleep, mock_get_agent):
    mock_agent = MagicMock()
    # First model fails, second model succeeds
    mock_agent.run.side_effect = [Exception("Error1"), "Success content"]
    mock_get_agent.return_value = mock_agent
    
    content, model_name = SpecialistFactory.run_agent_with_retries(
        "http://repo", "id", ["m1", "m2"], 1, 1, "memory"
    )
    
    assert content == "Success content"
    assert model_name == "m2"
    assert mock_agent.run.call_count == 2
    mock_sleep.assert_called_once()

@patch("src.agents.specialists.factory.SpecialistFactory.get_agent")
@patch("src.agents.specialists.factory.time.sleep")
def test_run_agent_with_retries_exhausted(mock_sleep, mock_get_agent):
    mock_agent = MagicMock()
    mock_agent.run.side_effect = Exception("Persistent error")
    mock_get_agent.return_value = mock_agent
    
    with pytest.raises(Exception, match="execution failed after trying all fallback models"):
        SpecialistFactory.run_agent_with_retries(
            "http://repo", "id", ["m1"], 1, 1, "memory"
        )
