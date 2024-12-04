# utils/calculate_audio_duration.py

from pydub import AudioSegment
import logging
from pronun_model.exceptions import AudioProcessingError

# 모듈별 로거 생성
logger = logging.getLogger(__name__)

def calculate_audio_duration(audio_path):
    """
    오디오 길이를 계산합니다 (무음 제거 안 함).
    """
    try:
        audio = AudioSegment.from_file(audio_path)
        duration_seconds = len(audio) / 1000.0  # 밀리초 단위에서 초 단위로 변환
        logger.info(f"Audio duration for {audio_path}: {duration_seconds:.2f} seconds")
        return duration_seconds
    except Exception as e:
        logger.error(f"Failed to calculate audio duration for {audio_path}: {e}", exc_info=True)
        raise AudioProcessingError(f"Failed to calculate audio duration: {e}")