# tests/pronun_model/test_utils/test_stt.py

import pytest
from unittest.mock import patch, mock_open
from pronun_model.utils.stt import STT
from fastapi import HTTPException

@patch("pronun_model.utils.stt.client.audio.transcriptions.create", return_value=type("Resp",(),{"text":"STT 결과"}))
def test_stt_success(mock_create):
    result = STT("dummy_audio_path.mp3")
    assert result == "STT 결과"

@patch("pronun_model.utils.stt.client.audio.transcriptions.create", side_effect=Exception("OpenAI Error"))
def test_stt_openai_error(mock_create):
    with pytest.raises(HTTPException) as exc:
        STT("dummy_audio_path.mp3")
    assert exc.value.status_code == 500 or exc.value.status_code == 502

@patch("pronun_model.utils.stt.client.audio.transcriptions.create", side_effect=ValueError("Unknown Error"))
def test_stt_unknown_error(mock_create):
    with pytest.raises(HTTPException) as exc:
        STT("dummy_audio_path.mp3")
    assert exc.value.status_code == 500
