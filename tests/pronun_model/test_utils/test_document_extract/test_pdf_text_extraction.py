from unittest.mock import patch
from pronun_model.utils.document_extract.pdf_text_extraction import get_pdf_text
from pronun_model.exceptions import DocumentProcessingError

@patch("pronun_model.utils.document_extract.pdf_text_extraction.PdfReader")
def test_get_pdf_text_success(mock_pdf_reader):
    mock_pdf_reader.return_value.pages = [
        type("Page", (), {"extract_text": lambda: "Page 1 text"}),
        type("Page", (), {"extract_text": lambda: "Page 2 text"}),
    ]
    result = get_pdf_text("test.pdf")
    assert result == "Page 1 text\nPage 2 text\n"

@patch("pronun_model.utils.document_extract.pdf_text_extraction.PdfReader", side_effect=Exception("Read error"))
def test_get_pdf_text_failure(mock_pdf_reader):
    try:
        get_pdf_text("test.pdf")
    except DocumentProcessingError as e:
        assert "PDF 파일에서 텍스트 추출 오류" in str(e)
