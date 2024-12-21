# utils/stt.py

from fastapi import HTTPException
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
from .convert_to_mp3 import convert_to_mp3
from typing import Optional
import logging

# 모듈별 로거 생성
logger = logging.getLogger(__name__) 

client = OpenAI(api_key=OPENAI_API_KEY)

def STT(audio_file_path: str) -> Optional[str]:
    """
    주어진 오디오 파일을 텍스트로 변환(STT).

    Args:
        audio_file_path (str): 입력 오디오 파일 경로.

    Returns:
        str: 변환된 텍스트.
        None: 변환 실패 시.
    """
    try:
        with open(audio_file_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language='ko'
            )
        transcript = response.text
        return transcript

    except AuthenticationError as e:
        logger.error(f"STT 변환 중 인증 오류 발생: {e}", extra={
            "errorType": "AuthenticationError",
            "error_message": str(e)
        })
        raise HTTPException(status_code=401, detail="인증 오류: API 키를 확인해주세요.") from e

    except PermissionDeniedError as e:
        logger.error(f"STT 변환 중 권한 오류 발생: {e}", extra={
            "errorType": "PermissionDeniedError",
            "error_message": str(e)
        })
        raise HTTPException(status_code=403, detail="권한 오류: API 사용 권한을 확인해주세요.") from e

    except RateLimitError as e:
        logger.error(f"STT 변환 중 Rate Limit 초과: {e}", extra={
            "errorType": "RateLimitError",
            "error_message": str(e)
        })
        raise HTTPException(status_code=429, detail="요청 제한 초과: 요청 속도를 줄여주세요.") from e

    except BadRequestError as e:
        logger.error(f"STT 변환 중 잘못된 요청 오류 발생: {e}", extra={
            "errorType": "BadRequestError",
            "error_message": str(e)
        })
        raise HTTPException(status_code=400, detail="잘못된 요청: 요청 데이터를 확인해주세요.") from e

    except ConflictError as e:
        logger.error(f"STT 변환 중 충돌 오류 발생: {e}", extra={
            "errorType": "ConflictError",
            "error_message": str(e)
        })
        raise HTTPException(status_code=409, detail="충돌 오류: 요청을 다시 시도해주세요.") from e

    except InternalServerError as e:
        logger.error(f"STT 변환 중 내부 서버 오류 발생: {e}", extra={
            "errorType": "InternalServerError",
            "error_message": str(e)
        })
        raise HTTPException(status_code=502, detail="내부 서버 오류: 나중에 다시 시도해주세요.") from e

    except NotFoundError as e:
        logger.error(f"STT 변환 중 자원 미존재 오류 발생: {e}", extra={
            "errorType": "NotFoundError",
            "error_message": str(e)
        })
        raise HTTPException(status_code=404, detail="자원이 존재하지 않습니다.") from e

    except UnprocessableEntityError as e:
        logger.error(f"STT 변환 중 처리 불가능한 엔티티 오류 발생: {e}", extra={
            "errorType": "UnprocessableEntityError",
            "error_message": str(e)
        })
        raise HTTPException(status_code=422, detail="처리 불가능한 데이터입니다.") from e

    except APIError as e:
        logger.error(f"STT 변환 중 API 오류 발생: {e}", extra={
            "errorType": "APIError",
            "error_message": str(e)
        })
        raise HTTPException(status_code=502, detail="서버 오류: 나중에 다시 시도해주세요.") from e

    except APITimeoutError as e:
        logger.error(f"STT 변환 중 API 타임아웃 오류 발생: {e}", extra={
            "errorType": "APITimeoutError",
            "error_message": str(e)
        })
        raise HTTPException(status_code=504, detail="서버 응답 지연: 나중에 다시 시도해주세요.") from e

    except APIConnectionError as e:
        logger.error(f"STT 변환 중 API 연결 오류 발생: {e}", extra={
            "errorType": "APIConnectionError",
            "error_message": str(e)
        })
        raise HTTPException(status_code=503, detail="연결 오류: 네트워크 상태를 확인해주세요.") from e

    except OpenAIError as e:
        logger.error(f"STT 변환 중 OpenAI 라이브러리 오류 발생: {e}", extra={
            "errorType": "OpenAIError",
            "error_message": str(e)
        })
        raise HTTPException(status_code=500, detail="OpenAI 처리 중 알 수 없는 오류가 발생했습니다.") from e

    except Exception as e:
        logger.error(f"STT 변환 오류: {e}", extra={
            "errorType": type(e).__name__,
            "error_message": str(e)
        })
        raise HTTPException(status_code=500, detail="STT 변환 중 오류 발생") from e