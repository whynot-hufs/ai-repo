# pronun_model/utils/qa.py

from openai import OpenAI
from fastapi import HTTPException
from ..openai_config import OPENAI_API_KEY
import logging

logger = logging.getLogger(__name__)

client = OpenAI(api_key=OPENAI_API_KEY)

def ask_question(question: str) -> str:
    """
    사용자의 질문(question)만 LLM에 전달하고, 답변 문자열을 반환합니다.
    """
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "병원 방문 고객을 돕는 AI 어시스턴트입니다. "
                    "사용자가 명확하고 간결한 답변을 받을 수 있도록 도와주세요."
                )
            },
            {"role": "user", "content": question}
        ]
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=1024,
        )
        return resp.choices[0].message.content.strip()

    except Exception as e:
        logger.error(f"LLM 질의 중 오류 발생: {e}", extra={
            "errorType": type(e).__name__,
            "error_message": str(e)
        })
        raise HTTPException(status_code=500, detail=f"LLM 질의 중 오류 발생: {e}")
