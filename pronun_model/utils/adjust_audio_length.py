# utils/adjust_audio_length.py

from pydub import AudioSegment
from pronun_model.exceptions import AudioProcessingError
import logging

# 모듈별 로거 생성
logger = logging.getLogger(__name__)

def adjust_audio_length(audio_path, target_duration):
    """
    TTS 음성 길이를 사용자 음성과 동기화합니다.

    Args:
        audio_path (str): TTS 음성 파일 경로.
        target_duration (float): 목표 길이 (초).

    Returns:
        str: 수정된 오디오 파일 경로.
    """
    try:   
        audio = AudioSegment.from_file(audio_path)
        current_duration = len(audio) / 1000  # 밀리초 단위에서 초 단위로 변환
        logger.debug(f"Original audio duration: {current_duration}")

        if current_duration < target_duration:
            # 길이가 짧으면 침묵 추가
            silence_duration = target_duration - current_duration  # 초 단위
            silence = AudioSegment.silent(duration=silence_duration * 1000)
            adjusted_audio = audio + silence
            logger.debug(f"Added {silence_duration} seconds of silence")
        else:
            # 길이가 길면 자름
            adjusted_audio = audio[:int(target_duration * 1000)]
            logger.debug(f"Trimmed audio to {target_duration} seconds")

        adjusted_audio.export(audio_path, format="mp3")
        logger.info(f"Adjusted audio saved at: {audio_path}")
        return audio_path

    except Exception as e:
        logger.error(f"오디오 길이 측정 오류: {audio_path}: {e}", extra={
            "errorType": type(e).__name__,
            "error_message": str(e)
        })
        raise AudioProcessingError(f"오디오 길이 측정에 실패했습니다. {e}") from e
