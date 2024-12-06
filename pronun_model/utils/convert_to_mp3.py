# utils/convert_to_mp3.py

from pydub import AudioSegment
from pathlib import Path
import os
import subprocess
import uuid
from pronun_model.config import CONVERT_MP3_DIR  # config에서 가져오기
from pronun_model.exceptions import AudioImportingError
import logging

# 모듈별 로거 생성
logger = logging.getLogger(__name__) 

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
    try:
        input_path = Path(file_path)
        file_extension = input_path.suffix.lower().lstrip('.')  # 파일 확장자 확인 (예: '.wav' -> 'wav')
        supported_formats = ['flac', 'm4a', 'mp3', 'mp4', 'mpeg', 'mpga', 'oga', 'ogg', 'wav', 'webm']

        if file_extension == 'mp3':
            # 이미 MP3이면 변환하지 않음
            logger.info(f"파일이 이미 MP3 형식입니다: {input_path}")
            return str(input_path.resolve())

        if file_extension not in supported_formats:
            # 지원하지 않는 형식 처리
            logger.error(f"지원되지 않는 파일 형식입니다: {file_extension}", extra={
                "errorType": "UnsupportedFormatError",
                "error_message": f"지원되지 않는 파일 형식입니다: {file_extension}"
            })
            raise AudioImportingError(f"지원되지 않는 파일 형식입니다: {file_extension}")

        # 오디오 파일을 읽어서 MP3로 변환
        audio = AudioSegment.from_file(input_path, format=file_extension)
        # 고유한 MP3 파일 이름 생성
        filename = f"{video_id}.mp3"
        mp3_file_path = CONVERT_MP3_DIR / filename

        # MP3 파일로 변환 및 저장
        try:
            audio.export(mp3_file_path, format="mp3")
            logger.info(f"MP3 변환 완료: {mp3_file_path}")
        except Exception as export_error:
            logger.error(f"MP3 변환 및 저장 실패: {export_error}", extra={
                "errorType": type(export_error).__name__,
                "error_message": str(export_error)
            })
            raise AudioImportingError(f"MP3 변환 및 저장 실패: {export_error}") from export_error

        return str(mp3_file_path.resolve())

    except AudioImportingError as aie:
        # 이미 로깅되었으므로 다시 raise
        raise aie
    except Exception as e:
        logger.error(f"MP3 변환 오류: {e}", extra={
            "errorType": type(e).__name__,
            "error_message": str(e)
        })
        raise AudioImportingError("MP3 변환 오류가 발생했습니다.") from e