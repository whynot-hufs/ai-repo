# utils/count_words.py

import logging
from pronun_model.exceptions import AudioProcessingError

# 모듈별 로거 생성
logger = logging.getLogger(__name__) 

def count_words(text):
    """
    텍스트의 단어 수를 계산합니다.

    Args:
        text (str): 입력 텍스트.

    Returns:
        int: 단어 수.
    """
    try:
        words = text.split()
        return len(words)
    except Exception as e:
        logger.error(f"텍스트 전처리 오류: {e}", extra={
            "errorType": type(e).__name__,
            "error_message": str(e)
        })
        raise AudioProcessingError("텍스트 전처리 중 오류가 발생했습니다.") from e