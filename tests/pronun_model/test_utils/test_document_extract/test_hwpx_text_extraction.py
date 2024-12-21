from unittest.mock import patch
from pronun_model.utils.document_extract.hwpx_text_extraction import get_hwpx_text
from pronun_model.exceptions import DocumentProcessingError

@patch("pronun_model.utils.document_extract.hwpx_text_extraction.gethwp.read_hwpx")
@patch("pronun_model.utils.document_extract.hwpx_text_extraction.clean_extracted_text")
def test_get_hwpx_text_success(mock_clean_text, mock_read_hwpx):
    mock_read_hwpx.return_value = "Raw HWPX text"
    mock_clean_text.return_value = "Cleaned HWPX text"
    result = get_hwpx_text("test.hwpx")
    assert result == "Cleaned HWPX text"

@patch("pronun_model.utils.document_extract.hwpx_text_extraction.gethwp.read_hwpx", side_effect=Exception("Read error"))
def test_get_hwpx_text_failure(mock_read_hwpx):
    try:
        get_hwpx_text("test.hwpx")
    except DocumentProcessingError as e:
        assert "HWPX 파일 읽기 오류" in str(e)
