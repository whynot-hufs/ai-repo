# pronun_model/schemas/feedback.py

from pydantic import BaseModel
from typing import Optional

class UploadResponse(BaseModel):
    video_id: str
    message: str

class AnswerResponse(BaseModel):
    video_id: str
    question: str
    answer: str
    audio_url: str   # 추가


class DeleteResponse(BaseModel):
    success: bool
    message: str