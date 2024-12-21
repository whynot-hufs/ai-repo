# pronun_model/schemas/feedback.py

from pydantic import BaseModel
from typing import List, Optional

class UploadResponse(BaseModel):
    video_id: str
    message: str

class PronunciationScore(BaseModel):
    time_segment: str  # 예: "0분 0초 - 1분 0초"
    accuracy: float  # 발음 정확도

class WPMScore(BaseModel):
    time_segment: str  # 예: "0분 0초 - 1분 0초"
    wpm: float  # WPM 점수

class AudioAnalysisResult(BaseModel):
    audio_similarity: float  # 오디오 유사도 점수
    average_wpm: float  # 평균 말하기 속도
    tts_wpm: float  # TTS 속도
    average_pronunciation_accuracy: float  # 평균 발음 정확도
    script_similarity: float  # 대본 텍스트와 일치도
    pronunciation_scores: List[PronunciationScore]  # 구간별 발음 정확도
    wpm_scores: List[WPMScore]  # 구간별 WPM 점수

class AnalysisResponse(BaseModel):
    video_id: str # video_id
    message: str  # 처리 상태 메시지
    analysis_result: Optional[AudioAnalysisResult] = None  # 분석 결과
    problem: Optional[str] = None  # 분석 중 발생한 문제 (없을 경우 None)

class DeleteResponse(BaseModel):
    video_id: str
    message: str