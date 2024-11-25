# main.py

import logging
from pronun_model.utils import calculate_presentation_score, ensure_directories
from pronun_model.config import ENABLE_PLOTTING
import os

if ENABLE_PLOTTING:
    from pronun_model.plotting.plot_waveform import plot_waveform  # 정확한 경로로 수정

def main():
    # 디렉토리 생성 확인
    ensure_directories()
    
    # 예시 오디오 파일 경로
    audio_file = "/Users/daehyunkim_kakao/Desktop/Kakao Business (Project)/AIM-14-AI-Pronun/storage/input_video/25ba260c5a5f4ceebdbdcdcc14eaf49c.mp4"

    # 스크립트가 제공된 경우
    user_script = None  # 실제 스크립트로 교체하거나 None으로 설정

    # 음성 평가 처리
    results = calculate_presentation_score(audio_file, script_text=user_script)

    if results:
        print("\n- 평가 결과 -")
        print(f"오디오 유사도: {results['audio_similarity']:.2f}")
        print(f"평균 사용자 말하기 속도 (WPM): {results['original_speed']:.2f}")
        print(f"TTS 속도 (WPM): {results['tts_speed']:.2f}")
        print(f"평균 사용자 발음 정확도: {results['average_accuracy']:.2f}")  # 평균 발음 정확도
        print(f"대본 텍스트와 일치도 (대본 미 제공 시 문법 일치도): {results['pronunciation_accuracy']:.2f}")  # 대본 텍스트와 일치도

        if ENABLE_PLOTTING:
            # 플롯 기능 활성화
            plot_waveform(audio_file, "Original_Audio_Waveform")
            tts_file_path = results.get('tts_file_path')
            if tts_file_path:
                plot_waveform(tts_file_path, "TTS_Audio_Waveform")
            else:
                print("TTS 파일 경로가 존재하지 않습니다.")
    else:
        print("발표 점수 계산에 실패했습니다.")

if __name__ == "__main__":
    # plots 디렉토리가 없으면 생성
    if ENABLE_PLOTTING and not os.path.exists("plots"):
        os.makedirs("plots")
    main()