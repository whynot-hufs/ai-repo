from unittest.mock import mock_open, patch
from pronun_model.utils.document_extract.txt_text_extraction import get_txt_text
from pronun_model.exceptions import DocumentProcessingError

@patch("pronun_model.utils.document_extract.txt_text_extraction.open", new_callable=mock_open, read_data="Sample text")
def test_get_txt_text_success(mock_open_file):
    result = get_txt_text("test.txt")
    assert result == "Sample text"

@patch("pronun_model.utils.document_extract.txt_text_extraction.open", side_effect=Exception("Read error"))
def test_get_txt_text_failure(mock_open_file):
    try:
        get_txt_text("test.txt")
    except DocumentProcessingError as e:
        assert "TXT 파일에서 텍스트 추출 오류" in str(e)
