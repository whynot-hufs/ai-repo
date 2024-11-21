# utils/adjust_audio_length.py

from pydub import AudioSegment

def adjust_audio_length(audio_path, target_duration):
    """
    TTS 음성 길이를 사용자 음성과 동기화합니다.

    Args:
        audio_path (str): TTS 음성 파일 경로.
        target_duration (float): 목표 길이 (초).

    Returns:
        str: 수정된 오디오 파일 경로.
    """
    audio = AudioSegment.from_file(audio_path)
    current_duration = len(audio) / 1000  # 밀리초 단위에서 초 단위로 변환

    if current_duration < target_duration:
        # 길이가 짧으면 침묵 추가
        silence = AudioSegment.silent(duration=(target_duration - current_duration) * 1000)
        adjusted_audio = audio + silence
    else:
        # 길이가 길면 자름
        adjusted_audio = audio[:int(target_duration * 1000)]

    adjusted_audio.export(audio_path, format="mp3")
    return audio_path
