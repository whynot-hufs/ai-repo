# pronun_model/schemas/feedback.py

from pydantic import BaseModel
from typing import Optional, List

class UploadResponse(BaseModel):
    video_id: str
    message: str

class AnswerResponse(BaseModel):
    video_id: str
    question: str
    answer: str
    hospitals: List[str]  # 병원 이름 목록을 포함하는 새 필드
    audio_url: str   # 추가

class DeleteResponse(BaseModel):
    success: bool
    message: str