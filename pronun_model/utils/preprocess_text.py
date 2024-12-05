# utils/preprocess_text.py

import re
import logging
from pronun_model.exceptions import AudioProcessingError

# 모듈별 로거 생성
logger = logging.getLogger(__name__) 

def preprocess_text(text):
    """
    텍스트 전처리 함수: 소문자 변환 및 일부 특수 문자 제거

    Args:
        text (str): 입력 텍스트.

    Returns:
        str: 전처리된 텍스트.
    """
    try:
        text = text.lower()
        # 한국어의 조사나 어미를 유지하기 위해 특수 문자를 일부만 제거
        text = re.sub(r'[^\w\s가-힣]', '', text)
        return text
    except Exception as e:
        logger.error(f"텍스트 전처리 오류: {e}")
        return text