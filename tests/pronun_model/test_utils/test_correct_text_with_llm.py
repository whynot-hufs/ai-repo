# tests/pronun_model/test_utils/test_correct_text_with_llm.py

import pytest
from unittest.mock import patch
from pronun_model.utils.correct_text_with_llm import correct_text_with_llm
from fastapi import HTTPException

@patch("pronun_model.utils.correct_text_with_llm.client.chat.completions.create", return_value={
    "choices":[{"message":{"content":"교정된 텍스트"}}]
})
def test_correct_text_with_llm_success(mock_create):
    result = correct_text_with_llm("원본 텍스트")
    assert result == "교정된 텍스트"

@patch("pronun_model.utils.correct_text_with_llm.client.chat.completions.create", side_effect=Exception("OpenAI Error"))
def test_correct_text_with_llm_openai_error(mock_create):
    with pytest.raises(HTTPException) as exc:
        correct_text_with_llm("오류 텍스트")
    assert exc.value.status_code == 500 or exc.value.status_code == 502

@patch("pronun_model.utils.correct_text_with_llm.client.chat.completions.create", side_effect=ValueError("Unknown Error"))
def test_correct_text_with_llm_unknown_error(mock_create):
    with pytest.raises(HTTPException) as exc:
        correct_text_with_llm("오류 텍스트")
    assert exc.value.status_code == 500
