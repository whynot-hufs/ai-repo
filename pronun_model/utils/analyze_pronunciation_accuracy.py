# utils/analyze_pronunciation_accuracy.py

from pronun_model.exceptions import AudioProcessingError
from .preprocess_text import preprocess_text
from fuzzywuzzy import fuzz
import logging

# 모듈별 로거 생성
logger = logging.getLogger(__name__) 

def analyze_pronunciation_accuracy(stt_text, reference_text):
    """
    사용자가 실제로 말한 텍스트(STT 변환 결과)와 기준 텍스트(대본) 간의 일치도를 계산합니다.

    Args:
        stt_text (str): STT로 변환된 사용자의 발화 텍스트.
        reference_text (str): 기준이 되는 대본 텍스트.

    Returns:
        float: 두 텍스트 간의 유사도(0~1)로 표현된 일치도 점수.
        None: 계산 중 오류 발생 시.
    """
    try:
        # 텍스트 전처리: 공백, 구두점 제거 등 비교를 위한 정규화
        stt_text_processed = preprocess_text(stt_text)
        reference_text_processed = preprocess_text(reference_text)

        if not stt_text_processed or not reference_text_processed:
            logger.warning("One or both texts are empty after preprocessing.")
            return 0.0

        # 유사도 계산: 텍스트 간 단어 집합 비교를 통한 유사도 산출
        accuracy = fuzz.token_set_ratio(stt_text_processed, reference_text_processed) / 100.0
        logger.debug(f"accuracy score: {accuracy:.2f}")
        return accuracy
        
    except Exception as e:
        logger.error(f"일치도 계산 오류: {e}")
        return None
