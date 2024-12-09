# utils/text_extract/pdf_text_extraction.py

from PyPDF2 import PdfReader
from pronun_model.exceptions import DocumentProcessingError
import logging

logger = logging.getLogger(__name__)

def get_pdf_text(filename):
    """
    PDF 파일에서 텍스트를 추출합니다.

    Args:
        filename (str): PDF 파일 경로.

    Returns:
        str: 추출된 텍스트 또는 None (추출 실패 시).
    """
    try:
        reader = PdfReader(filename)
        text = ""
        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        logger.debug(f"Extracted text from PDF file {filename}")
        return text
    except Exception as e:
        logger.error(f"PDF 파일에서 텍스트 추출 오류: {filename}, 오류: {e}")
        raise DocumentProcessingError(f"PDF 파일에서 텍스트 추출 오류: {e}") from e
