# utils/stt.py

from openai import OpenAI
from ..config import OPENAI_API_KEY
from .convert_to_mp3 import convert_to_mp3

client = OpenAI(api_key=OPENAI_API_KEY)

def STT(file_path):
    """
    주어진 오디오 파일을 텍스트로 변환(STT).

    Args:
        file_path (str): 입력 오디오 파일 경로.

    Returns:
        str: 변환된 텍스트.
        None: 변환 실패 시.
    """
    try:
        mp3_path = convert_to_mp3(file_path)
        if not mp3_path:
            return None
        with open(mp3_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language='ko'
            )
        transcript = response.text
        return transcript
    except Exception as e:
        print(f"STT 변환 오류: {e}")
        return None