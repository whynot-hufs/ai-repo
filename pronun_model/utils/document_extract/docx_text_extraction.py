# utils/text_extract/docx_text_extraction.py

from docx import Document
from pronun_model.exceptions import DocumentProcessingError
import logging

logger = logging.getLogger(__name__)

def get_docx_text(filename):
    """
    DOCX 파일에서 텍스트를 추출합니다.

    Args:
        filename (str): DOCX 파일 경로.

    Returns:
        str: 추출된 텍스트 또는 빈 문자열 (추출 실패 시).
    """
    try:
        doc = Document(filename)
        text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        logger.info(f"Extracted text from DOCX file {filename}")
        return text
    except Exception as e:
        logger.error(f"DOCX 파일에서 텍스트 추출 오류: {filename}, 오류: {e}")
        raise DocumentProcessingError(f"DOCX 파일에서 텍스트 추출 오류: {e}") from e
