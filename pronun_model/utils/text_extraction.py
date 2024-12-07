# utils/text_extraction.py

import zlib
import struct
import re
from docx import Document
from PyPDF2 import PdfReader
import gethwp
import re
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
        logger.error(f"DOCX 파일에서 텍스트 추출 오류: {filename}, 오류: {e}", extra={
            "errorType": type(e).__name__,
            "error_message": f"DOCX 파일에서 텍스트 추출 오류: {e}"
        })
        raise DocumentProcessingError(f"DOCX 파일에서 텍스트 추출 오류: {e}") from e

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
        logger.error(f"TXT 파일에서 텍스트 추출 오류: {filename}, 오류: {e}", extra={
            "errorType": type(e).__name__,
            "error_message": f"TXT 파일에서 텍스트 추출 오류: {e}"
        })
        raise DocumentProcessingError(f"TXT 파일에서 텍스트 추출 오류: {e}") from e

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
        logger.error(f"PDF 파일에서 텍스트 추출 오류: {filename}, 오류: {e}", extra={
            "errorType": type(e).__name__,
            "error_message": f"PDF 파일에서 텍스트 추출 오류: {e}"
        })
        raise DocumentProcessingError(f"PDF 파일에서 텍스트 추출 오류: {e}") from e

def extract_text(file_path):
    """
    파일 형식에 따라 적절한 텍스트 추출 함수를 호출합니다.

    Args:
        file_path (str): 분석할 파일의 경로.

    Returns:
        str: 추출된 텍스트 또는 None (지원되지 않는 파일 형식 또는 추출 실패 시).
    """
    try:
        extension = file_path.split('.')[-1].lower()
        if extension == 'docx':
            return get_docx_text(file_path)
        elif extension == 'txt':
            return get_txt_text(file_path)
        elif extension == 'pdf':
            return get_pdf_text(file_path)
        elif extension == 'hwpx':
            return get_hwpx_text(file_path)
        else:
            logger.error(f"지원되지 않는 파일 형식으로 텍스트 추출을 시도했습니다: {extension}", extra={
                "errorType": "UnsupportedFileTypeError",
                "error_message": f"지원되지 않는 파일 형식입니다: {extension}"
            })
            raise DocumentProcessingError(f"지원되지 않는 파일 형식입니다: {extension}")
    except Exception as e:
        logger.error(f"파일에서 텍스트 추출 중 예상치 못한 오류 발생: {file_path}, 오류: {e}", extra={
            "errorType": type(e).__name__,
            "error_message": f"파일에서 텍스트 추출 중 오류 발생: {e}"
        })
        raise DocumentProcessingError(f"파일에서 텍스트 추출 중 오류 발생: {e}") from e