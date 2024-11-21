# utils/correct_text_with_llm.py

from openai import OpenAI
from ..config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def correct_text_with_llm(text):
    """
    텍스트를 LLM을 사용하여 보정합니다.

    Args:
        text (str): 보정할 텍스트.

    Returns:
        str: 보정된 텍스트.
        원본 텍스트: 보정 실패 시.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "너는 한국어 문법을 정확하게 교정하지만, 어떤 내용도 삭제하거나 요약하지 않는 어시스턴트야. 텍스트에 부족한 내용을 보충한다는 느낌으로 원본 텍스트보다는 늘려도 되지만 절대 줄이지 말고 자연스럽게 교정해줘."
                },
                {
                    "role": "user",
                    "content": f"다음 텍스트의 문법을 자연스럽게 교정하세요. 단, **어떤 단어도 삭제하거나 요약하지 말고, 부자연스러운 표현은 고쳐줘, 텍스트의 길이는 원본 텍스트보다 길어도 돼, 그리고 텍스트는 절대 문단을 나누지 말고 무조건 하나의 텍스트로 만들어줘**.:\n\n{text}"
                }
            ],
            max_tokens=4000,
        )
        corrected_text = response.choices[0].message.content.strip()
        return corrected_text
    except Exception as e:
        print(f"LLM 보정 오류: {e}")
        return text