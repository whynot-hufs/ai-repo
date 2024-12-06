# pronun_model/routers/send_feedback.py

from fastapi import APIRouter, HTTPException, BackgroundTasks, Response
from pronun_model.utils import calculate_presentation_score, extract_text
from pronun_model.schemas.feedback import AnalysisResponse, AudioAnalysisResult, PronunciationScore, WPMScore
from pronun_model.exceptions import AudioProcessingError
from pronun_model.config import CONVERT_MP3_DIR, SCRIPTS_DIR
import os
import logging
import logging.config
import json
from pathlib import Path

router = APIRouter()

logger = logging.getLogger(__name__)  # 'pronun_model.routers.send_feedback' 로거 사용

ALLOWED_SCRIPT_EXTENSIONS = {"docx", "txt", "pdf", "hwp", "hwpx"}

@router.get("/send-feedback/{video_id}", response_model=AnalysisResponse)
async def send_feedback(video_id: str, response: Response):
    """
    주어진 video_id에 대해 오디오 분석 결과를 반환합니다 (3분 정도 소요).
    """
    # 응답 헤더 설정
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "False"

    logger.info(f"send_feedback 엔드포인트 호출됨 for video_id: {video_id}")

    # MP3 파일 경로 설정
    mp3_path = CONVERT_MP3_DIR / f"{video_id}.mp3"

    # MP3 파일 존재 여부 확인
    if not mp3_path.exists():
        logger.error("MP3 파일을 찾을 수 없습니다.", extra={
            "errorType": "FileNotFoundError",
            "error_message": "MP3 파일을 찾을 수 없습니다."
        })
        raise AudioProcessingError("MP3 파일을 찾을 수 없습니다.")

    try:
        # 스크립트 파일 찾기
        script_text = None
        script_found = False

        for ext in ALLOWED_SCRIPT_EXTENSIONS:
            script_path = os.path.join(SCRIPTS_DIR, f"{video_id}.{ext}")
            if os.path.exists(script_path):
                logger.debug(f"스크립트 파일을 발견했습니다: {script_path}")
                extracted_text = extract_text(script_path)
                if extracted_text:
                    script_text = extracted_text
                    logger.info("스크립트 텍스트 추출 성공")
                    script_found = True
                else:
                    logger.info("스크립트 텍스트 추출 실패", extra={
                        "errorType": "TextExtractionFailed",
                        "error_message": "스크립트 텍스트 추출 실패"
                    })
                break

        if not script_found:
            logger.info(f"스크립트 파일이 없거나 텍스트 추출에 실패했습니다. {video_id} 파일은 LLM을 이용해 문법을 보정한 텍스트를 사용합니다.")

        # 발표 점수 계산 (script_text가 존재하면 전달, 아니면 None 전달)
        results = calculate_presentation_score(mp3_path, script_text=script_text)

        if not results:
            logger.error(f"비디오 ID {video_id}에 대한 분석이 실패했습니다.", extra={
                "errorType": "AnalysisFailed",
                "error_message": "비디오 ID에 대한 분석 실패"
            })
            raise HTTPException(status_code=500, detail="비디오 분석에 실패했습니다.")

        # 'pronunciation_scores' 키 존재 여부 확인
        if 'pronunciation_scores' not in results:
            logger.error(f"'pronunciation_scores' 키가 결과에 없습니다: {results}", extra={
                "errorType": "KeyError",
                "error_message": "'pronunciation_scores' 데이터가 누락되었습니다."
            })
            raise AudioProcessingError("'pronunciation_scores' 데이터가 누락되었습니다.")

        # 결과 변환 (스키마 매핑)
        pronunciation_scores = [
            PronunciationScore(time_segment=segment["time_segment"], accuracy=segment["accuracy"])
            for segment in results["pronunciation_scores"]
        ]
        wpm_scores = [
            WPMScore(time_segment=segment["time_segment"], wpm=segment["wpm"])
            for segment in results["wpm_scores"]
        ]

        # TTS 생성 방식에 따라 로그 메시지 설정
        if script_text:
            tts_source = "Script"
        else:
            tts_source = "LLM"

        analysis_result = AudioAnalysisResult(
            audio_similarity=results["audio_similarity"],
            average_wpm=results["original_speed"],
            tts_wpm=results["tts_speed"],
            average_pronunciation_accuracy=results["average_accuracy"],
            script_similarity=results["pronunciation_accuracy"],
            pronunciation_scores=pronunciation_scores,
            wpm_scores=wpm_scores,
        )

        logger.info(f"비디오 ID {video_id}에 대한 분석이 성공적으로 완료되었습니다.")
        return AnalysisResponse(
            message="Analysis completed successfully",
            analysis_result=analysis_result
        )

    except FileNotFoundError as e:
        logger.error(f"파일 관련 오류: {e}", extra={
            "errorType": "FileNotFoundError",
            "error_message": f"파일 관련 오류 발생: {e}"
        })
        raise HTTPException(status_code=404, detail="파일 관련 오류 발생") from e

    except KeyError as e:
        logger.error(f"결과 데이터 키 누락: {e}", extra={
            "errorType": "KeyError",
            "error_message": f"결과 데이터 키 누락: {e}"
        })
        raise HTTPException(status_code=400, detail="결과 데이터 키가 누락되었습니다.") from e

    except Exception as e:
        logger.error(f"알 수 없는 오류 발생: {e}", extra={
            "errorType": type(e).__name__,
            "error_message": str(e)
        })
        raise HTTPException(status_code=500, detail="예기치 않은 오류 발생") from e