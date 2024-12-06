# utils/calculate_speed.py

from .calculate_audio_duration import calculate_audio_duration
from .count_words import count_words
from pronun_model.exceptions import AudioProcessingError
import logging

# 모듈별 로거 생성
logger = logging.getLogger(__name__) 

def calculate_speed(audio_file_path, text):
    """
    오디오 파일의 말하기 속도를 계산합니다 (단어/분 기준).

    Args:
        audio_file_path (str): 입력 오디오 파일 경로.
        text (str): 음성 텍스트.

    Returns:
        float: 말하기 속도 (WPM).
        None: 계산 실패 시.
    """
    try:
        # Step 1: 오디오 길이 계산 (무음 제거 안 함)
        duration_seconds = calculate_audio_duration(audio_file_path)
        logger.debug(f"Audio duration: {duration_seconds:.2f} seconds")

        # Step 2: 단어 수 계산
        word_count = count_words(text)
        logger.debug(f"Word count: {word_count}")

        # Step 3: WPM 계산
        duration_minutes = duration_seconds / 60.0
        if duration_minutes > 0:
            wpm = word_count / duration_minutes
        else:
            wpm = 0

        logger.info(f"Calculated speaking speed: {wpm:.2f} WPM")
        return wpm

    except AudioProcessingError as ape:
        logger.error(f"Audio processing error during speed calculation: {ape}", extra={
            "errorType": type(ape).__name__,
            "error_message": str(ape)
            }, exc_info=True)
        raise AudioProcessingError("오디오 처리 중 오류가 발생했습니다.") from ape

    except Exception as e:
        logger.error(f"Error calculating speaking speed: {e}", extra={
            "errorType": type(e).__name__,
            "error_message": str(e)
        }, exc_info=True)
        raise AudioProcessingError("말하기 속도 계산 중 오류가 발생했습니다.") from e