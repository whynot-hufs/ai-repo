# pronun_model/routers/upload_video.py

import uuid, shutil, os, logging
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from pronun_model.schemas.feedback import UploadResponse
from pronun_model.config import UPLOAD_DIR

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/upload-video/", response_model=UploadResponse)
async def upload_video(video: UploadFile = File(...)):
    """
    비디오 파일을 저장하고, video_id를 반환합니다.
    """
    # 허용 확장자 체크
    ext = video.filename.rsplit(".", 1)[-1].lower()
    if ext not in {"webm","mov","avi","mkv","mp4","mpeg","mpga","oga","ogg","wav","flac","m4a"}:
        raise HTTPException(415, detail="지원되지 않는 비디오 형식입니다.")
    
    video_id = uuid.uuid4().hex
    path = UPLOAD_DIR / f"{video_id}.{ext}"

    try:
        with open(path, "wb") as buf:
            shutil.copyfileobj(video.file, buf)
    except Exception as e:
        logger.error(f"비디오 저장 실패: {e}")
        raise HTTPException(500, detail="비디오 저장에 실패했습니다.")
    
    return UploadResponse(video_id=video_id, message="업로드 성공")
