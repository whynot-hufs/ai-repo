# utils/calculate_audio_duration.py

from pydub import AudioSegment

def calculate_audio_duration(audio_path):
    """
    오디오 길이를 계산합니다 (무음 제거 안 함).
    """
    audio = AudioSegment.from_file(audio_path)
    duration_seconds = len(audio) / 1000.0  # 밀리초 단위에서 초 단위로 변환
    return duration_seconds