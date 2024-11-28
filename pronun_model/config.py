# pronun_model/config.py

from dotenv import load_dotenv
from pathlib import Path
import os
import logging
from fastapi import HTTPException

# .env 파일에서 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,  # 필요에 따라 DEBUG로 변경 가능
    format='%(asctime)s - %(levelname)s - %(message)s'
)

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

# Docker 환경 감지 및 경로 설정
try:
    with open('/proc/1/cgroup', 'rt') as f:
        cgroup_content = f.read()
    if 'docker' in cgroup_content:
        # Docker 환경
        BASE_DIR = Path("/app")
        logging.info("Docker 환경으로 감지되었습니다.")
    else:
        # 로컬 환경
        BASE_DIR = Path(__file__).resolve().parent.parent
        logging.info("로컬 환경으로 감지되었습니다.")
except FileNotFoundError:
    # 로컬 환경
    BASE_DIR = Path(__file__).resolve().parent.parent
    logging.info("로컬 환경으로 간주합니다. 기본 경로로 설정합니다.")
except Exception as e:
    logging.error(f"환경 감지 중 오류 발생: {e}")
    raise HTTPException(status_code=500, detail="환경 감지 중 오류 발생")

# 저장 디렉토리 설정
UPLOAD_DIR = BASE_DIR / os.getenv("UPLOAD_DIR", "storage/input_video")
CONVERT_MP3_DIR = BASE_DIR / os.getenv("CONVERT_MP3_DIR", "storage/convert_mp3")
CONVERT_TTS_DIR = BASE_DIR / os.getenv("CONVERT_TTS_DIR", "storage/convert_tts")
SCRIPTS_DIR = BASE_DIR / os.getenv("SCRIPTS_DIR", "storage/scripts")

# 디렉토리 존재 여부 확인 및 생성
try:
    for directory in [UPLOAD_DIR, CONVERT_MP3_DIR, CONVERT_TTS_DIR, SCRIPTS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
        logging.info(f"디렉토리가 준비되었습니다: {directory}")
except Exception as e:
    logging.error(f"디렉토리 생성 실패: {e}")
    raise HTTPException(status_code=500, detail="디렉토리 생성 실패")