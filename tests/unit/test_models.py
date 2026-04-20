import pytest
from unittest.mock import patch, MagicMock
from src.utils.models import (
    fetch_available_openrouter_models, 
    fetch_available_groq_models,
    get_model_candidates_for_agent
)

@patch("src.utils.models.requests.get")
def test_fetch_available_openrouter_models_success(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": [
            {"id": "model1:free"},
            {"id": "model2:free"},
            {"id": "model3"}
        ]
    }
    mock_get.return_value = mock_response
    
    models = fetch_available_openrouter_models()
    assert "model1:free" in models
    assert "model2:free" in models
    assert "model3" not in models
    assert len(models) == 2

@patch("src.utils.models.requests.get")
def test_fetch_available_groq_models_success(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": [
            {"id": "llama3-8b-8192"},
            {"id": "mixtral-8x7b-32768"}
        ]
    }
    mock_get.return_value = mock_response
    
    with patch("src.utils.models.GROQ_API_KEY", "test-key"):
        models = fetch_available_groq_models()
        assert "llama3-8b-8192" in models
        assert len(models) == 2

def test_get_model_candidates_for_agent_groq():
    available_groq = {"llama3-8b-8192", "new-model"}
    candidates = get_model_candidates_for_agent(
        "architect_design", 
        available_openrouter_models=set(), 
        provider="Groq",
        available_groq_models=available_groq
    )
    assert candidates[0].startswith("groq/")
    # Preferred for architect on groq is usually llama3-70b or 8b
    assert any("llama3-8b" in c for c in candidates)
    assert "groq/new-model" in candidates

def test_get_model_candidates_for_agent_openrouter():
    available_or = {"google/gemini-2.0-flash:free", "meta-llama/llama-3-8b-instruct:free"}
    mock_prefs = {
        "report_synthesizer": {
            "openrouter": ["google/gemini-2.0-flash:free"]
        }
    }
    with patch("src.utils.models.FREE_MODEL_PREFERENCES", mock_prefs):
        candidates = get_model_candidates_for_agent(
            "report_synthesizer",
            available_openrouter_models=available_or,
            provider="OpenRouter"
        )
        assert candidates[0] == "openrouter/google/gemini-2.0-flash:free"
        assert "openrouter/meta-llama/llama-3-8b-instruct:free" in candidates
        assert len(candidates) >= 2
