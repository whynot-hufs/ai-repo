# utils/text_extract/txt_text_extraction.py

from pronun_model.exceptions import DocumentProcessingError
import logging

logger = logging.getLogger(__name__)

def get_txt_text(filename):
    """
    TXT 파일에서 텍스트를 추출합니다.

    Args:
        filename (str): TXT 파일 경로.

    Returns:
        str: 추출된 텍스트 또는 빈 문자열 (추출 실패 시).
    """
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            text = file.read()
        logger.info(f"Extracted text from TXT file {filename}")
        return text
    except Exception as e:
        logger.error(f"TXT 파일에서 텍스트 추출 오류: {filename}, 오류: {e}")
        raise DocumentProcessingError(f"TXT 파일에서 텍스트 추출 오류: {e}") from e
