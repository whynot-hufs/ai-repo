# pronun_model/routers/delete_files.py

from fastapi import APIRouter, HTTPException
from pronun_model.config import UPLOAD_DIR
from pronun_model.schemas.feedback import DeleteResponse
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.delete("/delete-video/{video_id}", response_model=DeleteResponse)
async def delete_video(video_id: str):
    """
    video_id와 관련된 업로드된 영상 파일만 삭제합니다.
    """
    files = list(UPLOAD_DIR.glob(f"{video_id}.*"))
    if not files:
        raise HTTPException(404, detail="삭제할 비디오를 찾을 수 없습니다.")
    
    for f in files:
        try:
            f.unlink()
        except Exception as e:
            logger.error(f"{f} 삭제 실패: {e}")
            raise HTTPException(500, detail=f"{f.name} 삭제 실패") from e

    return DeleteResponse(video_id=video_id, message="삭제 완료")
