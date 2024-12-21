# tests/pronun_model/test_utils/document_extract/test_docs_text_extraction.py

import pytest
from unittest.mock import patch, MagicMock
from pronun_model.utils.document_extract.docx_text_extraction import get_docx_text
from pronun_model.exceptions import DocumentProcessingError
from docx import Document

@patch("pronun_model.utils.document_extract.docx_text_extraction.Document")
def test_get_docx_text_success(mock_document):
    mock_doc_instance = MagicMock()
    mock_doc_instance.paragraphs = [
        type("Paragraph", (), {"text": "Paragraph 1"}),
        type("Paragraph", (), {"text": "Paragraph 2"})
    ]
    mock_document.return_value = mock_doc_instance

    result = get_docx_text("test.docx")
    assert result == "Paragraph 1\nParagraph 2"

@patch("pronun_model.utils.document_extract.docx_text_extraction.Document", side_effect=Exception("Read error"))
def test_get_docx_text_failure(mock_document):
    with pytest.raises(DocumentProcessingError) as exc:
        get_docx_text("test.docx")
    assert "DOCX 파일에서 텍스트 추출 오류" in str(exc.value)
