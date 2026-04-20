import pytest
from unittest.mock import patch, MagicMock
from src.agents.synthesizer import synthesize_report

@patch("src.agents.synthesizer.get_llm")
def test_synthesize_report_success_with_diagrams(mock_get_llm):
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "Final Report with ```mermaid\ngraph TD; A-->B\n``` and ```mermaid\ngraph LR; C-->D\n```"
    mock_llm.invoke.return_value = mock_response
    mock_get_llm.return_value = mock_llm
    
    result = synthesize_report(
        repo_url="http://repo",
        model_candidates=["model1"],
        specialist_outputs={"Agent1": "Output1"},
        memory_context="memory",
        max_attempts_per_model=1,
        base_backoff_seconds=1
    )
    
    assert "graph TD" in result
    assert "graph LR" in result
    mock_get_llm.assert_called_once_with(model_name="model1", temperature=0.1)

@patch("src.agents.synthesizer.get_llm")
def test_synthesize_report_mermaid_nudge(mock_get_llm):
    mock_llm = MagicMock()
    # First response: no diagrams. Second response: diagrams.
    resp1 = MagicMock(content="Missing diagrams here.")
    resp2 = MagicMock(content="Fixed with ```mermaid\ngraph TD; A;```")
    mock_llm.invoke.side_effect = [resp1, resp2]
    mock_get_llm.return_value = mock_llm
    
    result = synthesize_report(
        repo_url="http://repo",
        model_candidates=["model1"],
        specialist_outputs={"Agent1": "Output1"},
        memory_context="memory",
        max_attempts_per_model=1,
        base_backoff_seconds=1
    )
    
    assert "graph TD" in result
    # Should have invoked twice: original + nudge
    assert mock_llm.invoke.call_count == 2
    assert "CRITICAL" in mock_llm.invoke.call_args_list[1][0][0]

@patch("src.agents.synthesizer.get_llm")
@patch("src.agents.synthesizer.time.sleep")
def test_synthesize_report_fallback(mock_sleep, mock_get_llm):
    mock_llm1 = MagicMock()
    mock_llm2 = MagicMock()
    mock_llm1.invoke.side_effect = Exception("Model 1 dead")
    
    mock_response = MagicMock(content="Success ```mermaid\ngraph TD; A --> B; B --> C; C --> D;```")
    mock_llm2.invoke.return_value = mock_response
    
    mock_get_llm.side_effect = [mock_llm1, mock_llm2]
    
    result = synthesize_report(
        repo_url="http://repo",
        model_candidates=["m1", "m2"],
        specialist_outputs={},
        memory_context="",
        max_attempts_per_model=1,
        base_backoff_seconds=3
    )
    
    assert "Success" in result
    assert mock_llm1.invoke.call_count == 1
    assert mock_llm2.invoke.call_count == 1
    mock_sleep.assert_called_once_with(3)
