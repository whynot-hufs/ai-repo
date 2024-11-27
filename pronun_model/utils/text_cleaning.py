# utils/text_cleaning.py

import re

def clean_extracted_text(raw_text):
    """
    추출된 텍스트를 정제하여 불필요한 단어와 인코딩된 데이터를 제거하고, 문장 부호를 보존하며,
    문장을 자연스럽게 재구성합니다.

    Args:
        raw_text (str): 정제할 원본 텍스트.

    Returns:
        str: 정제된 깨끗한 텍스트.
    """

    # 0. '^숫자'로 시작하는 모든 라인 제거
    # 예: '^1.\n^2.\n^3)\n' 등과 같은 패턴을 제거
    text = re.sub(r'^\^\(?\d+[.\)]*\n?', '', raw_text, flags=re.MULTILINE)

    # 1. '7 8 ' 패턴 제거 (남아있을 경우)
    text = re.sub(r'\b7\s*8\b\s*', '', text)

    # 2. 'IAA'와 같은 특정 단어 제거 (대소문자 구분 없이)
    text = re.sub(r'\bIAA\b', '', text, flags=re.IGNORECASE)

    # 3. Base64와 유사한 인코딩된 데이터 제거 (10자 이상)
    # 숫자만으로 이루어진 긴 문자열은 제거하지 않도록 패턴 수정
    text = re.sub(r'\b(?=.*[A-Za-z])[A-Za-z0-9+/=]{10,}\b', '', text)

    # 4. 불필요한 기호 패턴 제거
    # 예: '^1.', '^2)', '(^5)', '(^6)' 등 제거
    text = re.sub(r'\^\d+[.)]', '', text)
    text = re.sub(r'\(\^\d+\)', '', text)

    # 5. 허용된 문자 외의 문자 제거
    # 한글, 영문, 숫자, 공백, '.', ',', '!', '?', '-' 제외한 모든 문자 제거
    text = re.sub(r'[^\uAC00-\uD7A3a-zA-Z0-9\s.,!?-]', ' ', text)

    # 6. 여러 공백을 단일 공백으로 축소
    text = re.sub(r'\s+', ' ', text)

    # 7. 문장 부호 앞뒤의 공백 제거
    # 예: '안녕하세요 . ' -> '안녕하세요.'
    text = re.sub(r'\s*([.,!?])\s*', r'\1', text)

    # 8. 문장 부호 뒤에 단일 공백 추가 (문장 끝은 제외)
    # 예: '안녕하세요.저는' -> '안녕하세요. 저는'
    text = re.sub(r'([.,!?])(?!$)', r'\1 ', text)

    # 9. 앞뒤 공백 제거
    text = text.strip()

    return text