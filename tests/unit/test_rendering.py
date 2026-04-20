import pytest
from unittest.mock import patch, MagicMock
from src.utils.rendering import render_mermaid, display_enriched_report

@patch('src.utils.rendering.st.image')
@patch('src.utils.rendering.get_mermaid_url')
def test_render_mermaid_as_image(mock_get_url, mock_st_image):
    mock_get_url.return_value = "http://mermaid.ink/png/xyz"
    
    render_mermaid("graph TD; A-->B;", "test-key")
    
    mock_st_image.assert_called_once_with("http://mermaid.ink/png/xyz", use_container_width=True)

@patch('src.utils.rendering.render_mermaid')
@patch('src.utils.rendering.st.markdown')
def test_display_enriched_report_parsing(mock_markdown, mock_render_mermaid):
    report_text = """
# Header
Some text.
```mermaid
graph TD; A;
```
Footer.
"""
    display_enriched_report(report_text)
    
    # Check text parts
    assert any("Header" in str(c) for c in mock_markdown.call_args_list)
    assert any("Footer" in str(c) for c in mock_markdown.call_args_list)
    
    # Check mermaid part
    mock_render_mermaid.assert_called_once_with("graph TD; A;", key="diag-1")
