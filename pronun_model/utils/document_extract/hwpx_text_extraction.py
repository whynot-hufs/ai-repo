# utils/hwpx_text_extraction.py

import gethwp
from .text_cleaning import clean_extracted_text
from pronun_model.exceptions import DocumentProcessingError
import logging

# 모듈별 로거 생성
logger = logging.getLogger(__name__) 

def get_hwpx_text(filename):
    """
    HWPX 파일에서 텍스트를 추출하는 내부 함수.

    Args:
        file_path (str): HWPX 파일 경로.

    Returns:
        str: 추출된 텍스트.
    """
    try:
        hwpx = gethwp.read_hwpx(filename)
        hwpx_cleaned_text = clean_extracted_text(hwpx)
        logger.info(f"Extracted text from HWPX file {filename}")
        return hwpx_cleaned_text
    except Exception as e:
        logger.error(f"HWPX 파일 읽기 오류: {filename}, 오류: {e}", extra={
            "errorType": type(e).__name__,
            "error_message": f"HWPX 파일 읽기 오류: {filename}, 오류: {e}"
        })
        raise DocumentProcessingError(f"HWPX 파일 읽기 오류: {filename}, 오류: {e}") from e
