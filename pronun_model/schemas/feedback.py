# pronun_model/schemas/feedback.py

from pydantic import BaseModel

class UploadResponse(BaseModel):
    video_id: str
    message: str

class AnswerResponse(BaseModel):
    video_id: str
    question: str
    answer: str

class DeleteResponse(BaseModel):
    success: bool
    message: str