import pytest
import io
from unittest.mock import patch, MagicMock
from src.utils.export import clean_for_pdf, export_to_docx

def test_clean_for_pdf():
    assert clean_for_pdf("**bold**") == "bold"
    assert clean_for_pdf("*italic*") == "italic"
    assert clean_for_pdf("`code`") == "code"
    # test character outside Latin-1
    assert clean_for_pdf("Hello\u2603") == "Hello "

@patch("src.utils.export.Document")
@patch("src.utils.export.get_mermaid_image_path")
def test_export_to_docx(mock_get_img, mock_document):
    mock_doc_instance = MagicMock()
    mock_document.return_value = mock_doc_instance
    mock_get_img.return_value = None # Simulate mermaid fetch skip
    
    markdown_content = "# Heading 1\n\n```mermaid\ngraph TD; A\n```\n\n| H1 | H2 |\n|---|---|\n| V1 | V2 |"
    
    result = export_to_docx(markdown_content, "run-123")
    
    assert isinstance(result, bytes)
    assert mock_document.called
    # Check if a heading was added
    assert mock_doc_instance.add_heading.called
    # Check if a table was added
    assert mock_doc_instance.add_table.called
    # Check if it tried to fetch mermaid
    assert mock_get_img.called

@patch("src.utils.export.requests.get")
@patch("src.utils.export.open", new_callable=MagicMock)
def test_get_mermaid_image_path_success(mock_open, mock_get):
    from src.utils.export import get_mermaid_image_path
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"fake-image-data"
    mock_get.return_value = mock_response
    
    # Mock context manager open
    mock_file = MagicMock()
    mock_open.return_value.__enter__.return_value = mock_file
    
    with patch("src.utils.export.os.path.exists", return_value=True):
        path = get_mermaid_image_path("graph TD; A", "run1", 0)
        assert path == "/tmp/mermaid_run1_0.png"
        mock_file.write.assert_called_with(b"fake-image-data")
