# pronun_model/routers/send_feedback.py

from fastapi import APIRouter, HTTPException, BackgroundTasks, Response
from pronun_model.utils import calculate_presentation_score
from pronun_model.schemas.feedback import AnalysisResponse, AudioAnalysisResult, PronunciationScore, WPMScore
from pronun_model.config import UPLOAD_DIR, CONVERT_MP3_DIR, SCRIPTS_DIR
import os
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/send-feedback/{video_id}", response_model=AnalysisResponse)
async def send_feedback(video_id: str, response: Response):
    """
    주어진 video_id에 대해 오디오 분석 결과를 반환합니다 (3분 정도 소요).
    """
    # 응답 헤더 설정
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "False"

    logger.info(f"send_feedback 엔드포인트 호출됨 for video_id: {video_id}")

    # MP3 파일 경로 설정
    mp3_path = os.path.join(CONVERT_MP3_DIR, f"{video_id}.mp3")

    # MP3 파일 존재 여부 확인
    if not os.path.exists(mp3_path):
        logger.error(f"MP3 파일을 찾을 수 없습니다: {mp3_path}")
        raise HTTPException(status_code=404, detail="MP3 파일을 찾을 수 없습니다.")

    try:
        # 스크립트 파일 경로 설정
        script_path = os.path.join(SCRIPTS_DIR, f"{video_id}.txt")
        if os.path.exists(script_path):
            with open(script_path, "r", encoding="utf-8") as f:
                script_text = f.read()
            logger.info(f"스크립트를 사용하여 분석을 수행합니다: {script_path}")
        else:
            script_text = None
            logger.info("스크립트가 없으므로 STT 및 LLM을 사용하여 스크립트를 생성합니다.")

        # 발표 점수 계산 (핵심 유틸리티 호출)
        results = calculate_presentation_score(mp3_path, script_text=script_text)

        if not results:
            logger.error(f"비디오 ID {video_id}에 대한 분석이 실패했습니다.")
            raise HTTPException(status_code=500, detail="분석에 실패했습니다.")

        # 'pronunciation_scores' 키 존재 여부 확인
        if 'pronunciation_scores' not in results:
            logger.error(f"'pronunciation_scores' 키가 결과에 없습니다: {results}")
            raise HTTPException(status_code=500, detail="'pronunciation_scores' 데이터가 누락되었습니다.")

        # 결과 변환 (스키마 매핑)
        pronunciation_scores = [
            PronunciationScore(time_segment=segment["time_segment"], accuracy=segment["accuracy"])
            for segment in results["pronunciation_scores"]
        ]
        wpm_scores = [
            WPMScore(time_segment=segment["time_segment"], wpm=segment["wpm"])
            for segment in results["wpm_scores"]
        ]

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

    except Exception as e:
        logger.error(f"Error during feedback processing for video_id {video_id}: {e}")
        raise HTTPException(status_code=500, detail="An error occurred during feedback processing")
