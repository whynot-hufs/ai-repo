# utils/convert_to_mp3.py

from pydub import AudioSegment
import os
import logging
import subprocess
import uuid
from pronun_model.config import CONVERT_MP3_DIR  # config에서 가져오기

def convert_to_mp3(file_path: str, video_id: str) -> str:
    """
    주어진 오디오 파일을 MP3 형식으로 변환합니다.

    Args:
        file_path (str): 입력 오디오 파일 경로.
        video_id (str): 고유 비디오 ID.

    Returns:
        str: 변환된 MP3 파일 경로.
        None: 변환 실패 시.
    """
    file_extension = file_path.split('.')[-1].lower()  # 파일 확장자 확인
    supported_formats = ['flac', 'm4a', 'mp3', 'mp4', 'mpeg', 'mpga', 'oga', 'ogg', 'wav', 'webm']

    if file_extension == 'mp3':  # 이미 MP3이면 변환하지 않음
        logging.info(f"파일이 이미 MP3 형식입니다: {file_path}")
        return file_path
    elif file_extension not in supported_formats:  # 지원하지 않는 형식 처리
        logging.warning(f"지원되지 않는 파일 형식입니다: {file_extension}")
        return None
    try:
       # 오디오 파일을 읽어서 MP3로 변환
        audio = AudioSegment.from_file(file_path, format=file_extension)
        # 고유한 MP3 파일 이름 생성
        filename = f"{video_id}.mp3"
        mp3_file_path = os.path.join(CONVERT_MP3_DIR, filename)
        # MP3 디렉토리가 존재하지 않으면 생성
        os.makedirs(CONVERT_MP3_DIR, exist_ok=True)
        # MP3 파일로 변환 및 저장
        audio.export(mp3_file_path, format="mp3")
        logging.info(f"MP3 변환 완료: {mp3_file_path}")
        return mp3_file_path
    except Exception as e:
        logging.error(f"MP3 변환 오류: {e}")
        return None