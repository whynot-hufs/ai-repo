from unittest.mock import mock_open, patch
from pronun_model.utils.document_extract.rtf_text_extraction import get_rtf_text
from pronun_model.exceptions import DocumentProcessingError

@patch("pronun_model.utils.document_extract.rtf_text_extraction.open", new_callable=mock_open, read_data="RTF content")
@patch("pronun_model.utils.document_extract.rtf_text_extraction.rtf_to_text")
def test_get_rtf_text_success(mock_rtf_to_text, mock_open_file):
    mock_rtf_to_text.return_value = "Extracted text"
    result = get_rtf_text("test.rtf")
    assert result == "Extracted text"

@patch("pronun_model.utils.document_extract.rtf_text_extraction.open", side_effect=Exception("Read error"))
def test_get_rtf_text_failure(mock_open_file):
    try:
        get_rtf_text("test.rtf")
    except DocumentProcessingError as e:
        assert "rtf 파일에서 텍스트 추출 오류" in str(e)
