# ─── 빌드 스테이지 ───────────────────────────────────────
FROM python:3.12-slim AS builder

# 환경 변수
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 시스템 빌드 종속성 (fuzzywuzzy[speedup]용 컴파일러)
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libssl-dev \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 의존성 설치 (패키지는 /app/dependencies 에 설치)
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt -t /app/dependencies

# ─── 런타임 스테이지 ────────────────────────────────────
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 런타임 종속성 (pydub 의존인 ffmpeg 등)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
  && rm -rf /var/lib/apt/lists/*

# 빌드 스테이지에서 설치한 Python 패키지와 스크립트 복사
COPY --from=builder /app/dependencies /usr/local/lib/python3.12/site-packages
COPY --from=builder /app/dependencies/bin /usr/local/bin

# 애플리케이션 소스 복사
COPY . .

# 로그 디렉터리 생성
RUN mkdir -p /app/logs

# PYTHONPATH 설정 (optional)
ENV PYTHONPATH=/app

# FastAPI 포트 개방
EXPOSE 8000

# 실행 명령
CMD ["uvicorn", "main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--reload", \
     "--log-config", "logging_config.json"]
