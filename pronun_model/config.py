# pronun_model/config.py

from dotenv import load_dotenv
import os

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