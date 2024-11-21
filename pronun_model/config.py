# pronun_model/config.py

from dotenv import load_dotenv
import os
import logging

# .env 파일에서 환경 변수 로드
load_dotenv()

# OpenAI API 키 가져오기
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# API 키가 설정되지 않은 경우 에러 발생
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API Key가 설정되지 않았습니다. .env 파일에 설정해주세요.")

# 추가 설정
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 60))  # 기본값 60초
AVERAGE_WPM = int(os.getenv("AVERAGE_WPM", 100))  # 기본값 100 WPM

# 플롯 기능 활성화 여부
ENABLE_PLOTTING = os.getenv("ENABLE_PLOTTING", "False").lower() in ["true", "1", "yes"]

# 저장 디렉토리 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # config.py의 절대 경로
UPLOAD_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", os.getenv("UPLOAD_DIR", "storage/input_video")))
CONVERT_MP3_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", os.getenv("CONVERT_MP3_DIR", "storage/convert_mp3")))
CONVERT_TTS_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", os.getenv("CONVERT_TTS_DIR", "storage/convert_tts")))

# 디렉토리 존재 여부 확인 및 생성
def ensure_directories():
    """
    필요한 저장 디렉토리를 생성합니다.
    """
    try:
        for directory in [UPLOAD_DIR, CONVERT_MP3_DIR, CONVERT_TTS_DIR]:
            os.makedirs(directory, exist_ok=True)
        logging.info("All necessary directories are ensured.")
    except Exception as e:
        logging.error(f"Failed to create directories: {e}")

ensure_directories()