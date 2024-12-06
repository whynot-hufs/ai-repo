# vlm_model/openai_config.py

from dotenv import load_dotenv
from pathlib import Path
import os

# .env 파일의 경로 설정 (프로젝트 최상위 디렉토리 기준)
dotenv_path = Path(__file__).resolve().parent.parent / '.env'

# .env 파일 로드
load_dotenv(dotenv_path=dotenv_path)

# 환경 변수에서 API 키 가져오기
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables.")