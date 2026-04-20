import pytest
import json
from unittest.mock import patch, MagicMock
from src.ui.components import build_json_export, render_sidebar, render_export_downloads

def test_build_json_export():
    json_str = build_json_export(
        repo_url="http://x",
        run_id="123",
        generated_at_utc="time",
        active_preset="Reliable",
        max_attempts_per_model=1,
        base_backoff_seconds=1,
        selected_models={"agent": "model1"},
        synthesizer_model="model2",
        specialist_results={"agent": "res"},
        final_report="final md",
    )
    data = json.loads(json_str)
    assert data["repository"] == "http://x"
    assert data["run_metadata"]["run_id"] == "123"
    assert data["run_configuration"]["retry_attempts_per_model"] == 1
    assert data["models"]["specialists"]["agent"] == "model1"
    assert data["final_report_markdown"] == "final md"

@patch("src.ui.components.st")
def test_render_sidebar_default(mock_st):
    class MockSessionState(dict):
        def __getattr__(self, key):
            if key in self:
                return self[key]
            raise AttributeError(key)
        def __setattr__(self, key, value):
            self[key] = value
    
    session = MockSessionState()
    mock_st.session_state = session
    
    # Setup mock returns
    mock_st.sidebar.__enter__ = MagicMock()
    mock_st.sidebar.__exit__ = MagicMock()
    
    mock_st.radio.return_value = "Groq"
    mock_st.checkbox.return_value = False
    mock_st.number_input.side_effect = [1, 3] # max_attempts, backoff
    
    result = render_sidebar()
    
    assert result["llm_provider"] == "Groq"
    assert result["run_in_parallel"] == False
    assert result["max_parallel_workers"] == 1
    assert result["max_attempts_per_model"] == 1
    assert result["base_backoff_seconds"] == 3

@patch("src.ui.components.st")
@patch("src.ui.components.get_docx_bytes")
def test_render_export_downloads(mock_get_docx_bytes, mock_st):
    mock_get_docx_bytes.return_value = b"bytes"
    
    render_export_downloads("report", "123")
    
    mock_get_docx_bytes.assert_called_once_with("report", "123")
    assert mock_st.download_button.call_count == 1
    call_args = mock_st.download_button.call_args[1]
    assert ".docx" in call_args["file_name"]
    assert call_args["mime"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
