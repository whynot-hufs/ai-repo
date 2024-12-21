# utils/correct_text_with_llm.py

from openai import OpenAI
from openai import (
    AuthenticationError,
    APIError,
    APITimeoutError,
    APIConnectionError,
    RateLimitError,
    BadRequestError,
    OpenAIError,
    ConflictError,
    InternalServerError,
    NotFoundError,
    PermissionDeniedError,
    UnprocessableEntityError
)
from ..openai_config import OPENAI_API_KEY
import logging
from fastapi import HTTPException

# 모듈별 로거 생성
logger = logging.getLogger(__name__) 

client = OpenAI(api_key=OPENAI_API_KEY)

def correct_text_with_llm(text):
    """
    텍스트를 LLM을 사용하여 보정합니다.

    Args:
        text (str): 보정할 텍스트.

    Returns:
        str: 보정된 텍스트.
        원본 텍스트: 보정 실패 시.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "너는 한국어 문법을 정확하게 교정하지만, 어떤 내용도 삭제하거나 요약하지 않는 어시스턴트야. 텍스트에 부족한 내용을 보충한다는 느낌으로 원본 텍스트보다는 늘려도 되지만 절대 줄이지 말고 자연스럽게 교정해줘."
                },
                {
                    "role": "user",
                    "content": f"다음 텍스트의 문법을 자연스럽게 교정하세요. 단, **어떤 단어도 삭제하거나 요약하지 말고, 부자연스러운 표현은 고쳐줘, 텍스트의 길이는 원본 텍스트보다 길어도 돼, 그리고 텍스트는 절대 문단을 나누지 말고 무조건 하나의 텍스트로 만들어줘**.:\n\n{text}"
                }
            ],
            max_tokens=4000,
        )
        corrected_text = response.choices[0].message.content.strip()
        logger.info("LLM 문법 교정이 성공했습니다.")
        return corrected_text

    except AuthenticationError as e:
        # 401 - Invalid Authentication
        logger.error(f"문법 보정 중 인증 오류 발생: {e}", extra={
            "errorType": "AuthenticationError",
            "error_message": str(e)
        })
        raise HTTPException(status_code=401, detail="인증 오류: API 키를 확인해주세요.") from e

    except PermissionDeniedError as e:
        # 403 - Permission Denied
        logger.error(f"문법 보정 중 권한 오류 발생: {e}", extra={
            "errorType": "PermissionDeniedError",
            "error_message": str(e)
        })
        raise HTTPException(status_code=403, detail="권한 오류: API 사용 권한을 확인해주세요.") from e

    except RateLimitError as e:
        # 429 - Rate Limit Exceeded
        logger.error(f"문법 보정 중 Rate Limit 초과: {e}", extra={
            "errorType": "RateLimitError",
            "error_message": str(e)
        })
        raise HTTPException(status_code=429, detail="요청 제한 초과: 요청 속도를 줄여주세요.") from e

    except BadRequestError as e:
        # 400 - Bad Request
        logger.error(f"문법 보정 중 잘못된 요청 오류 발생: {e}", extra={
            "errorType": "BadRequestError",
            "error_message": str(e)
        })
        raise HTTPException(status_code=400, detail="잘못된 요청: 요청 데이터를 확인해주세요.") from e

    except ConflictError as e:
        # 409 - Conflict
        logger.error(f"문법 보정 중 충돌 오류 발생: {e}", extra={
            "errorType": "ConflictError",
            "error_message": str(e)
        })
        raise HTTPException(status_code=409, detail="충돌 오류: 요청을 다시 시도해주세요.") from e

    except InternalServerError as e:
        # 500 - Internal Server Error
        logger.error(f"문법 보정 중 내부 서버 오류 발생: {e}", extra={
            "errorType": "InternalServerError",
            "error_message": str(e)
        })
        raise HTTPException(status_code=502, detail="내부 서버 오류: 나중에 다시 시도해주세요.") from e

    except NotFoundError as e:
        # 404 - Not Found
        logger.error(f"문법 보정 중 자원 미존재 오류 발생: {e}", extra={
            "errorType": "NotFoundError",
            "error_message": str(e)
        })
        raise HTTPException(status_code=404, detail="자원이 존재하지 않습니다.") from e

    except UnprocessableEntityError as e:
        # 422 - Unprocessable Entity
        logger.error(f"문법 보정 중 처리 불가능한 엔티티 오류 발생: {e}", extra={
            "errorType": "UnprocessableEntityError",
            "error_message": str(e)
        })
        raise HTTPException(status_code=422, detail="처리 불가능한 데이터입니다.") from e

    except APIError as e:
        # 502 - Bad Gateway
        logger.error(f"문법 보정 중 API 오류 발생: {e}", extra={
            "errorType": "APIError",
            "error_message": str(e)
        })
        raise HTTPException(status_code=502, detail="서버 오류: 나중에 다시 시도해주세요.") from e

    except APITimeoutError as e:
        # 504 - Gateway Timeout
        logger.error(f"문법 보정 중 API 타임아웃 오류 발생: {e}", extra={
            "errorType": "APITimeoutError",
            "error_message": str(e)
        })
        raise HTTPException(status_code=504, detail="서버 응답 지연: 나중에 다시 시도해주세요.") from e

    except APIConnectionError as e:
        # 503 - Service Unavailable
        logger.error(f"문법 보정 중 API 연결 오류 발생: {e}", extra={
            "errorType": "APIConnectionError",
            "error_message": str(e)
        })
        raise HTTPException(status_code=503, detail="연결 오류: 네트워크 상태를 확인해주세요.") from e

    except OpenAIError as e:
        # 500 - 기타 OpenAI 라이브러리 오류
        logger.error(f"문법 보정 중 OpenAI 라이브러리 오류 발생: {e}", extra={
            "errorType": "OpenAIError",
            "error_message": str(e)
        })
        raise HTTPException(status_code=500, detail="OpenAI 처리 중 알 수 없는 오류가 발생했습니다.") from e

    except Exception as e:
        # 기타 모든 예외
        logger.error(f"문법 보정 처리 중 예기치 않은 오류 발생: {e}", extra={
            "errorType": type(e).__name__,
            "error_message": str(e)
        })
        raise HTTPException(status_code=500, detail="문법 보정 처리 중 오류가 발생.") from e