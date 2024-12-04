# utils/stt.py

from openai import OpenAI
from ..config import OPENAI_API_KEY
from .convert_to_mp3 import convert_to_mp3
from typing import Optional
import logging

# 모듈별 로거 생성
logger = logging.getLogger(__name__) 

client = OpenAI(api_key=OPENAI_API_KEY)

def STT(audio_file_path: str) -> Optional[str]:
    """
    주어진 오디오 파일을 텍스트로 변환(STT).

    Args:
        audio_file_path (str): 입력 오디오 파일 경로.

    Returns:
        str: 변환된 텍스트.
        None: 변환 실패 시.
    """
    try:
        with open(audio_file_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language='ko'
            )
        transcript = response.text
        return transcript
    except Exception as e:
        logger.error(f"STT 변환 오류: {e}")
        return None