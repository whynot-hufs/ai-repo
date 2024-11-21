# utils/convert_to_mp3.py

from pydub import AudioSegment
import os

def convert_to_mp3(file_path):
    """
    주어진 오디오 파일을 MP3 형식으로 변환합니다.

    Args:
        file_path (str): 입력 오디오 파일 경로.

    Returns:
        str: 변환된 MP3 파일 경로.
        None: 변환 실패 시.
    """
    file_extension = file_path.split('.')[-1].lower()  # 파일 확장자 확인
    supported_formats = ['flac', 'm4a', 'mp3', 'mp4', 'mpeg', 'mpga', 'oga', 'ogg', 'wav', 'webm']

    if file_extension == 'mp3':  # 이미 MP3이면 변환하지 않음
        return file_path
    elif file_extension not in supported_formats:  # 지원하지 않는 형식 처리
        print(f"지원되지 않는 파일 형식입니다: {file_extension}")
        return None
    try:
        # 오디오 파일을 읽어서 MP3로 변환
        audio = AudioSegment.from_file(file_path, format=file_extension)
        mp3_file_path = file_path.rsplit(".", 1)[0] + ".mp3"
        audio.export(mp3_file_path, format="mp3")
        return mp3_file_path
    except Exception as e:
        print(f"오류 발생: {e}")
        return None