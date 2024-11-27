# pronun_model/routers/upload_video.py

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Response, Request
from pronun_model.utils.convert_to_mp3 import convert_to_mp3
from pronun_model.schemas.feedback import UploadResponse
from pronun_model.config import UPLOAD_DIR, CONVERT_MP3_DIR, SCRIPTS_DIR
from typing import Optional
import os
import uuid
import logging
import shutil

router = APIRouter()

# 로깅 설정
logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

@router.post("/upload-video-with-script/", response_model=UploadResponse)
async def upload_video_with_optional_script(
    request: Request,
    response: Response,
    video: UploadFile = File(...),
    script: Optional[str] = Form(None)
):
    """
    비디오 파일을 업로드하고, MP3로 변환하여 저장한 후 video_id를 반환합니다.
    """
    # 응답 헤더에 CORS 설정 추가
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "False"

    logger.info("upload_video_with_optional_script 엔드포인트 호출됨")
    logger.info(f"수신된 비디오 파일: {video.filename}")
    if script:
        logger.info(f"수신된 스크립트 길이: {len(script)} 문자")
    else:
        logger.info("스크립트가 제공되지 않았습니다. STT 및 LLM을 사용하여 스크립트를 생성합니다.")

    # 지원하는 파일 형식 확인
    ALLOWED_EXTENSIONS = {"webm", "mov", "avi", "mkv", "flac", "m4a", "mp3", "mp4", "mpeg", "mpga", "oga", "ogg", "wav"}
    file_extension = video.filename.split(".")[-1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        logger.warning(f"지원하지 않는 파일 형식: {file_extension}")
        raise HTTPException(status_code=400, detail="지원하지 않는 파일 형식입니다.")

    # 고유한 video_id 생성
    video_id = uuid.uuid4().hex

    # 비디오 파일 저장 경로 설정
    video_path = os.path.join(UPLOAD_DIR, f"{video_id}.{file_extension}")

    # 비디오 파일 저장
    try:
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)
        logger.info(f"비디오 파일이 성공적으로 저장되었습니다: {video_path}")

        # 파일 저장 여부 확인
        if not os.path.exists(video_path):
            logger.error(f"파일이 저장되지 않았습니다: {video_path}")
            raise HTTPException(status_code=500, detail="파일이 저장되지 않았습니다.")

        # MP3 변환
        mp3_path = convert_to_mp3(str(video_path), video_id)
        if not mp3_path:
            logger.error("MP3 변환이 실패했습니다. failed.")
            raise HTTPException(status_code=500, detail="MP3 변환이 실패했습니다.")
        logger.info(f"MP3 변환이 성공했습니다: {mp3_path}")

        # 스크립트 저장 (선택적)
        if script:
            script_path = os.path.join(SCRIPTS_DIR, f"{video_id}.txt")
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script)
            logger.info(f"스크립트가 성공적으로 저장되었습니다: {script_path}")

        # 성공 응답
        return UploadResponse(
            video_id=video_id,
            message=f"비디오 업로드 및 MP3 변환 완료. 피드백 데이터를 받으려면 pronun/send-feedback/{video_id} 엔드포인트를 호출하세요."
        )

    except Exception as e:
        logger.error(f"알 수 없는 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="파일 처리 중 예기치 않은 오류 발생")
