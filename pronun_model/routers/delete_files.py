# pronun_model/routers/delete_files.py

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pathlib import Path
import logging
from pronun_model.schemas.feedback import DeleteResponse
from pronun_model.config import UPLOAD_DIR, CONVERT_MP3_DIR, CONVERT_TTS_DIR, SCRIPTS_DIR
from typing import Set

router = APIRouter()

logger = logging.getLogger(__name__)

# 지원하는 영상 파일 형식 정의
ALLOWED_EXTENSIONS: Set[str] = {
    "webm", "mov", "avi", "mkv", "mp4", "mpeg", "mpga", "oga", "ogg", "wav", "flac", "m4a"
}

# 지원하는 스크립트 파일 형식 정의
ALLOWED_SCRIPT_EXTENSIONS: Set[str] = {"docx", "txt", "pdf", "hwpx"}

@router.delete("/delete_files/{video_id}", response_class=JSONResponse)
async def delete_files(video_id: str):
    """
    특정 video_id와 연관된 파일들을 삭제하는 API.
    """
    try:
        # 지원하는 확장자를 기반으로 파일 찾기
        input_video_files = []
        for ext in ALLOWED_EXTENSIONS:
            input_video_files.extend(UPLOAD_DIR.glob(f"*{video_id}*.{ext}"))

        input_mp3_files = list(CONVERT_MP3_DIR.glob(f"*{video_id}*.mp3"))
        input_tts_files = list(CONVERT_TTS_DIR.glob(f"*{video_id}*.mp3"))

        # 스크립트 파일
        input_script_files = []
        for ext in ALLOWED_SCRIPT_EXTENSIONS:
            input_script_files.extend(SCRIPTS_DIR.glob(f"*{video_id}*.{ext}"))

        # 필수 파일 존재 여부 확인
        missing_mandatory = []
        if not input_video_files:
            missing_mandatory.append("영상 파일")
        if not input_mp3_files:
            missing_mandatory.append("MP3 파일")
        if not input_tts_files:
            missing_mandatory.append("TTS 파일")

        if missing_mandatory:
            missing_str = ", ".join(missing_mandatory)
            logger.error(f"{video_id}와 관련된 필수 파일이 없습니다: {missing_str}", extra={
                "errorType": "FileNotFoundError",
                "error_message": f"{video_id}와 관련된 필수 파일이 없습니다: {missing_str}",
            })
            raise HTTPException(status_code=404, detail=f"해당 video_id와 관련된 필수 파일이 없습니다: {missing_str}")

        # 스크립트 파일 존재 여부 로그
        if input_script_files:
            logger.debug(f"{video_id}와 관련된 스크립트 파일이 존재하므로 삭제합니다.")
        else:
            logger.debug(f"{video_id}와 관련된 스크립트 파일이 존재하지 않습니다.")

        # 모든 파일 리스트 합치기
        all_files = input_video_files + input_mp3_files + input_tts_files + input_script_files

        # 파일 삭제
        deleted_files = []
        for file in all_files:
            try:
                file.unlink()
                deleted_files.append(str(file))
                logger.debug(f"Deleted files related to the {video_id}")
            except Exception as e:
                logger.error(f"Failed to delete file related to the {video_id}: {file} {e}", extra={
                    "errorType": type(e).__name__,
                    "error_message": str(e)
                })
                raise HTTPException(status_code=500, detail=f"{file.name} 파일 삭제에 실패했습니다.") from e

        logger.info(f"{video_id}와 관련된 파일 삭제 성공.")
        return DeleteResponse(
            video_id=video_id,
            message=f"{video_id} video_id와 관련된 파일 삭제에 성공했습니다.",
        )

    except Exception as e:
        logger.error(f"Error in delete_files API: {e}", extra={
            "errorType": type(e).__name__,
            "error_message": str(e)
        })
        raise HTTPException(status_code=500, detail="내부 서버 오류가 발생했습니다.") from e
