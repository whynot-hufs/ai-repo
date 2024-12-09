# utils/text_extraction.py

from .hwpx_text_extraction import get_hwpx_text
from .docx_text_extraction import get_docx_text
from .txt_text_extraction import get_txt_text
from .pdf_text_extraction import get_pdf_text
from pronun_model.exceptions import DocumentProcessingError

import logging

# 모듈별 로거 생성
logger = logging.getLogger(__name__) 

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