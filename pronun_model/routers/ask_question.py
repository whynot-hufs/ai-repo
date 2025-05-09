# pronun_model/routers/ask_question.py
import uuid
import shutil
import os
import tempfile
import logging
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from pronun_model.utils.stt import STT
from pronun_model.utils.correct_text_with_llm import correct_text_with_llm
from pronun_model.utils.qa import ask_question
from pronun_model.schemas.feedback import AnswerResponse
# from pronun_model.utils.tts import TTS  # 나중에 음성 응답 기능을 켤 때 활성화

router = APIRouter()
logger = logging.getLogger(__name__)

# UPLOAD_DIR 정의 - 이 디렉토리가 존재하는지 확인
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/ask-question/", response_model=AnswerResponse, tags=["Q&A"])
async def ask_question_with_audio(
    question_audio: UploadFile = File(...)
):
    """
    질문 오디오를 받아 처리하는 엔드포인트:
    1) 질문 음성(question_audio)을 받아 임시 저장
    2) STT 로 텍스트 변환
    3) 어눌한 텍스트를 LLM 으로 교정
    4) 교정된 질문을 LLM 에 전달 → 답변 반환
    """
    # 각 요청마다 고유한 ID 생성
    request_id = uuid.uuid4().hex
    
    # 질문 오디오 처리
    audio_suffix = Path(question_audio.filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=audio_suffix) as tmp:
        shutil.copyfileobj(question_audio.file, tmp)
        tmp_path = tmp.name
    
    # STT 처리
    raw_text = STT(tmp_path)
    if not raw_text:
        os.remove(tmp_path)
        raise HTTPException(500, detail="STT 변환에 실패했습니다.")
    
    # 임시 파일 삭제
    os.remove(tmp_path)
    
    # 어눌한 STT 텍스트를 문장으로 보정
    try:
        question = correct_text_with_llm(raw_text)
    except HTTPException as e:
        # 보정 실패 시, 원문의 STT 결과라도 질문으로 사용
        question = raw_text
    
    # Q&A
    answer = ask_question(question)
    
    # (옵션) 음성 응답으로 돌려줄 때:
    # tts_path = TTS(answer, request_id)
    # return FileResponse(tts_path, media_type="audio/mp3")
    
    return AnswerResponse(
        video_id=request_id,  # video_id 필드는 유지하되, 요청 ID로 대체
        question=question,
        answer=answer
    )