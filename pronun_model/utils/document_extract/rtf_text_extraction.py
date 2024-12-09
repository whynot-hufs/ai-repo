# utils/document_extract/rtf_text_extraction.py

from striprtf.striprtf import rtf_to_text
from pronun_model.exceptions import DocumentProcessingError
import logging

logger = logging.getLogger(__name__)

def get_rtf_text(filename):
    """
    PDF 파일에서 텍스트를 추출합니다.

    Args:
        filename (str): PDF 파일 경로.

    Returns:
        str: 추출된 텍스트 또는 None (추출 실패 시).
    """
    try: 
        # 파일 열기 및 텍스트 추출
        with open(filename, 'r', encoding='utf-8') as file:
            rtf_content = file.read()

        # RTF에서 텍스트 추출
        rtf_text = rtf_to_text(rtf_content)
        logger.info(f"Extracted text from RTF file {filename}")
        return rtf_text
    except Exception as e:
        logger.error(f"rtf 파일에서 텍스트 추출 오류: {filename}, 오류: {e}")
        raise DocumentProcessingError(f"rtf 파일에서 텍스트 추출 오류: {e}") from e