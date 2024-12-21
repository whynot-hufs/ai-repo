import pytest
from unittest.mock import patch
from pronun_model.utils.text_extraction import extract_text
from pronun_model.exceptions import DocumentProcessingError

@patch("pronun_model.utils.text_extraction.get_docx_text")
def test_extract_text_docx(mock_get_docx_text):
    mock_get_docx_text.return_value = "Sample text from docx"
    result = extract_text("sample.docx")
    assert result == "Sample text from docx"

def test_extract_text_unsupported_format():
    with pytest.raises(DocumentProcessingError):
        extract_text("unsupported.xyz")
