# pronun_model/routers/ask_question.py

from fastapi import APIRouter, HTTPException
from pronun_model.config import UPLOAD_DIR
from pronun_model.utils.stt import STT
from pronun_model.utils.qa import ask_question
from pronun_model.schemas.feedback import AnswerResponse  # 새로 만든 스키마

import os

router = APIRouter()

@router.post("/ask/{video_id}", response_model=AnswerResponse)
async def ask(video_id: str, payload: dict):
    """
    video_id에 저장된 영상을 STT로 텍스트 변환 → payload['question']을 LLM에 질의 → 답변 반환
    """
    question = payload.get("question")
    if not question:
        raise HTTPException(400, detail="question 필드는 필수입니다.")
    
    # 업로드된 비디오 파일 찾기 (확장자는 upload step과 일치)
    candidates = list(UPLOAD_DIR.glob(f"{video_id}.*"))
    if not candidates:
        raise HTTPException(404, detail="저장된 비디오를 찾을 수 없습니다.")
    video_path = str(candidates[0])

    # 1) STT
    transcript = STT(video_path)
    if transcript is None:
        raise HTTPException(500, detail="STT 변환에 실패했습니다.")

    # 2) Q&A
    answer = ask_question(transcript, question)

    return AnswerResponse(
        video_id=video_id,
        transcript=transcript,
        question=question,
        answer=answer
    )
