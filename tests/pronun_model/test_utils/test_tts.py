# tests/pronun_model/test_utils/test_tts.py

import pytest
from unittest.mock import patch, mock_open, MagicMock
from pronun_model.utils.tts import TTS
from fastapi import HTTPException

@patch("pronun_model.utils.tts.client.audio.speech.create", return_value=type("Resp",(),{"content":b"audio_data"}))
@patch("pronun_model.utils.tts.AudioSegment")
def test_tts_single_segment(mock_audio_segment, mock_speech):
    mock_audio_segment.empty.return_value = mock_audio_segment
    mock_audio_segment.from_mp3.return_value = mock_audio_segment
    result = TTS("short text", "video123")
    assert result.endswith(".mp3")

@patch("pronun_model.utils.tts.client.audio.speech.create")
@patch("pronun_model.utils.tts.AudioSegment")
def test_tts_multiple_segments(mock_audio_segment, mock_speech):
    mock_speech.side_effect = [
        type("Resp",(),{"content":b"audio_data1"}),
        type("Resp",(),{"content":b"audio_data2"})
    ]
    mock_audio_segment.empty.return_value = mock_audio_segment
    mock_audio_segment.from_mp3.return_value = mock_audio_segment
    # script length > 4000
    script = "a"*5000
    result = TTS(script, "video_multiple")
    assert result.endswith(".mp3")

@patch("pronun_model.utils.tts.client.audio.speech.create", side_effect=Exception("OpenAI Error"))
def test_tts_openai_error(mock_speech):
    with pytest.raises(HTTPException) as exc:
        TTS("some text", "vid_err")
    assert exc.value.status_code == 502

@patch("pronun_model.utils.tts.client.audio.speech.create", side_effect=ValueError("Unknown"))
def test_tts_unknown_error(mock_speech):
    with pytest.raises(HTTPException) as exc:
        TTS("some text", "vid_unknown")
    assert exc.value.status_code == 500
