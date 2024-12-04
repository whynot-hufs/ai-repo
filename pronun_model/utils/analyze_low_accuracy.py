# utils/analyze_low_accuracy.py

import warnings

# PySoundFile 관련 UserWarning 무시
warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    message=".*PySoundFile failed.*"
)

# librosa.core.audio.__audioread_load 관련 FutureWarning 무시
warnings.filterwarnings(
    "ignore",
    category=FutureWarning,
    message=".*librosa.core.audio.__audioread_load.*"
)

from .stt import STT
from .analyze_pronunciation_accuracy import analyze_pronunciation_accuracy
from .count_words import count_words
from pronun_model.exceptions import AudioProcessingError
import os
import librosa
import traceback
import soundfile as sf
from tempfile import mkdtemp
import shutil  # 디렉토리 삭제용
import logging

# 모듈별 로거 생성
logger = logging.getLogger(__name__) 

def analyze_low_accuracy(audio_file_path, script_text, chunk_size=60):
    """
    60초 단위로 오디오를 분할하여 발음 정확도를 분석하고 평균을 계산합니다.

    Args:
        audio_file_path (str): 입력 오디오 파일 경로.
        script_text (str): 기준 텍스트.
        chunk_size (int, optional): 구간 길이 (초). 기본값은 60초.

    Returns:
        tuple: 각 구간의 (시간, 정확도) 리스트와 평균 정확도.
    """
    accuracies = []  # 정확도 정보를 저장할 리스트
    wpms = []  # (시간, WPM) 정보를 저장할 리스트
    temp_dir = mkdtemp()  # 임시 디렉토리 생성

    try:
        y, sr = librosa.load(audio_file_path, sr=None)  # 오디오 파일 로드
        duration = librosa.get_duration(y=y, sr=sr)  # 오디오 파일 길이 계산

        for i in range(0, int(duration), chunk_size):
            # chunk_size 초 단위로 오디오 분할
            segment = y[i * sr:(i + chunk_size) * sr]

            try:
                # 임시 디렉토리에 파일 저장
                temp_audio_path = os.path.join(temp_dir, f"segment_{i}.mp3")  # MP3 파일 형식으로 저장
                sf.write(temp_audio_path, segment, sr)

                # STT 처리
                segment_text = STT(temp_audio_path)
                
                if not segment_text:
                    logger.error(f"Segment {i} STT 변환에 실패했습니다.")
                    continue
            
            except Exception as file_error:
                logger.error(f"임시 파일 처리 중 오류 발생: {file_error}")
                logger.error(traceback.format_exc())
                continue

            # 구간별 정확도 계산
            accuracy = analyze_pronunciation_accuracy(segment_text, script_text)

            # 구간별 WPM 계산
            word_count = count_words(segment_text)  # 해당 구간의 단어 수 계산
            wpm = word_count / (chunk_size / 60)  # 분당 단어 수 계산

            # 시간 표시
            start_min = i // 60
            start_sec = i % 60
            end_min = (i + chunk_size) // 60
            end_sec = (i + chunk_size) % 60
            time_str = f"{start_min}분 {start_sec}초 - {end_min}분 {end_sec}초"

            # 결과 저장
            accuracies.append((time_str, accuracy))
            wpms.append((time_str, wpm))

            logger.debug(f"Segment {time_str}: Accuracy={accuracy:.2f}, WPM={wpm:.2f}")

    except Exception as e:
        logger.error(f"정확도 및 WPM 분석 오류: {e}")
        logger.error(traceback.format_exc())
        return [], [], 0.0

    finally:
        # 임시 디렉토리 및 모든 파일 삭제
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)  # 디렉토리와 내부 파일 모두 삭제
                logger.debug(f"Temporary directory {temp_dir} deleted.")
        except Exception as delete_error:
            logger.error(f"Failed to delete temporary directory {temp_dir}: {delete_error}")
            logger.debug(traceback.format_exc())

        # 평균 발음 정확도 계산
        if accuracies:
            average_accuracy = sum(accuracy for _, accuracy in accuracies) / len(accuracies)
        else:
            average_accuracy = 0.0
        
        logger.info(f"Average pronunciation accuracy: {average_accuracy:.2f}")

        return accuracies, wpms, average_accuracy