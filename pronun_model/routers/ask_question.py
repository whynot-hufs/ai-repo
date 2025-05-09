# pronun_model/routers/ask_question.py
import uuid, shutil, os, tempfile, logging
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse

from pronun_model.utils.stt import STT
from pronun_model.utils.correct_text_with_llm import correct_text_with_llm
from pronun_model.utils.qa import ask_question
from pronun_model.utils.tts import TTS
from pronun_model.schemas.feedback import AnswerResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/ask-question/", response_model=AnswerResponse, tags=["Q&A"])
async def ask_question_with_audio(
    question_audio: UploadFile = File(...),
    use_correction: bool = Query(
        True,
        description="LLM 보정 사용 여부 (False면 STT 결과를 그대로 질문으로 사용)"
    )
):
    # 1) 고유 ID 생성
    request_id = uuid.uuid4().hex

    # 2) 오디오 임시 저장
    suffix = Path(question_audio.filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(question_audio.file, tmp)
        tmp_path = tmp.name

    try:
        # 3) STT 변환
        raw_text = STT(tmp_path)
        if not raw_text:
            raise HTTPException(500, detail="STT 변환에 실패했습니다.")

        # 4) (선택) LLM 보정
        if use_correction:
            try:
                question = correct_text_with_llm(raw_text)
            except HTTPException:
                question = raw_text
        else:
            question = raw_text

        # 5) Q&A
        result = ask_question(question)
        answer = result["answer"]  # 답변 텍스트
        hospitals = result.get("hospitals", [])  # 병원 목록

        # 6) TTS 생성
        tts_path = TTS(answer, request_id)
        if not os.path.exists(tts_path):
            raise HTTPException(500, detail="TTS 음성 파일 생성에 실패했습니다.")

        # 7) 클라이언트에 제공할 URL 생성
        filename = Path(tts_path).name
        audio_url = f"/tts/{filename}"

        # 8) JSON 응답
        return AnswerResponse(
            video_id=request_id,
            question=question,
            answer=answer,
            hospitals=hospitals,  # 새로 추가된 필드
            audio_url=audio_url
        )

    finally:
        # 임시 파일 정리
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
