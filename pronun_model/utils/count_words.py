# utils/count_words.py

import logging

# 모듈별 로거 생성
logger = logging.getLogger(__name__) 

def count_words(text):
    """
    텍스트의 단어 수를 계산합니다.

    Args:
        text (str): 입력 텍스트.

    Returns:
        int: 단어 수.
    """
    try:
        words = text.split()
        return len(words)
    except Exception as e:
        print(f"단어 수 계산 오류: {e}")
        return 0