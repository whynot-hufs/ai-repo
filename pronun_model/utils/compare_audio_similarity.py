# pronun_model/utils/compare_audio_similarity.py

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

import librosa
from sklearn.metrics.pairwise import cosine_similarity
import logging
from pronun_model.exceptions import AudioProcessingError

# 모듈별 로거 생성
logger = logging.getLogger(__name__) 

def compare_audio_similarity(file1, file2):
    """
    두 오디오 파일 간 유사도를 계산합니다.

    Args:
        file1 (str): 첫 번째 오디오 파일 경로.
        file2 (str): 두 번째 오디오 파일 경로.

    Returns:
        float: 유사도 점수 (0~1).
        None: 계산 실패 시.
    """
    try:
        # 오디오 로드
        y1, sr1 = librosa.load(file1, sr=None)
        y2, sr2 = librosa.load(file2, sr=None)

        # 두 파일 길이 맞추기
        min_len = min(len(y1), len(y2))
        y1, y2 = y1[:min_len], y2[:min_len]

        # MFCC 특징 추출 및 코사인 유사도 계산
        mfcc1 = librosa.feature.mfcc(y=y1, sr=sr1)
        mfcc2 = librosa.feature.mfcc(y=y2, sr=sr2)

        similarity = cosine_similarity(mfcc1.T, mfcc2.T).mean()
        logger.debug(f"Audio similarity: {similarity:.4f}")
        return similarity

    except Exception as e:
        logger.error(f"오디오 유사도 비교 오류: {e}")
        return None