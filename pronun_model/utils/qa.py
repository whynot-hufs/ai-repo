# pronun_model/utils/qa.py

from openai import OpenAI
from ..openai_config import OPENAI_API_KEY
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

client = OpenAI(api_key=OPENAI_API_KEY)

def ask_question(transcript: str, question: str) -> str:
    """
    STT로 얻은 전체 대본(transcript)과 사용자의 질문(question)을
    LLM에 보내고, 답변 문자열을 반환합니다.
    """
    try:
        messages = [
            {"role": "system", "content": "병원 방문 고객을 돕는 AI 어시스턴트입니다. 친절하게 답변해주세요."},
            {"role": "user", "content": f"Transcript: {transcript}"},
            {"role": "user", "content": f"Question: {question}"}
        ]
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=1024,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"STT 변환 오류: {e}", extra={
            "errorType": type(e).__name__,
            "error_message": str(e)
        })
        raise HTTPException(status_code=500, detail=f"LLM 질의 중 오류 발생: {e}")
