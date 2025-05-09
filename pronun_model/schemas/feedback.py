from pydantic import BaseModel
from typing import Optional

class UploadResponse(BaseModel):
    video_id: str
    message: str

class AnswerResponse(BaseModel):
    video_id: str
    transcript: str      # STT로 변환된 전체 텍스트
    question: str        # 클라이언트가 보낸 질문
    answer: str          # LLM이 반환한 답변

class DeleteResponse(BaseModel):
    video_id: str
    message: str