# plotting/waveform_plot.py

import matplotlib.pyplot as plt
import librosa
import librosa.display
import os

def plot_waveform(audio_path, title, output_dir="plots"):
    """
    오디오 파일의 파형을 플롯하고 저장합니다.

    Args:
        audio_path (str): 오디오 파일 경로.
        title (str): 플롯 제목.
        output_dir (str): 플롯을 저장할 디렉토리.
    """
    try:
        data, sample_rate = librosa.load(audio_path, sr=16000)
        plt.figure(figsize=(16, 6))
        librosa.display.waveshow(y=data, sr=sample_rate)
        plt.title(title)
        
        # plots 디렉토리가 없으면 생성
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        plt.savefig(os.path.join(output_dir, f"{title}.png"))
        plt.close()
        print(f"{title} 플롯이 {output_dir} 디렉토리에 저장되었습니다.")
    except Exception as e:
        print(f"파형 플롯 오류: {e}")
