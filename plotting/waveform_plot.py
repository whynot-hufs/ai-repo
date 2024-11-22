# pronun_model/plotting/plot_waveform.py

import matplotlib.pyplot as plt
import librosa
import librosa.display
import os
from pronun_model.config import CONVERT_TTS_DIR, ENABLE_PLOTTING
import logging

def plot_waveform(audio_path, plot_name):
    """
    오디오 파일의 파형을 플롯하여 plots 디렉토리에 저장합니다.

    Args:
        audio_path (str): 오디오 파일 경로.
        plot_name (str): 플롯 이름 (파일명으로 사용).
    """
    try:
        # 오디오 파일 로드
        y, sr = librosa.load(audio_path, sr=None)

        plt.figure(figsize=(14, 5))
        librosa.display.waveshow(y, sr=sr)
        plt.title(plot_name)
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude")

        # plots 디렉토리에 저장
        plot_filename = f"{plot_name}.png"
        plot_dir = "plots"
        os.makedirs(plot_dir, exist_ok=True)
        plot_path = os.path.join(plot_dir, plot_filename)
        plt.savefig(plot_path)
        plt.close()
        logging.info(f"파형 플롯 저장 완료: {plot_path}")
    except Exception as e:
        logging.error(f"파형 플롯 생성 오류 ({audio_path}): {e}")
