# tests/pronun_model/test_utils/test_calculate_presentation_score.py

import pytest
from unittest.mock import patch, MagicMock
from pronun_model.utils.calculate_presentation_score import calculate_presentation_score
from pronun_model.exceptions import AudioProcessingError

@patch("pronun_model.utils.calculate_presentation_score.STT", return_value="stt text")
@patch("pronun_model.utils.calculate_presentation_score.correct_text_with_llm", return_value="corrected text")
@patch("pronun_model.utils.calculate_presentation_score.calculate_audio_duration", return_value=60)
@patch("pronun_model.utils.calculate_presentation_score.count_words", return_value=120)
@patch("pronun_model.utils.calculate_presentation_score.calculate_speed", return_value=120)
@patch("pronun_model.utils.calculate_presentation_score.TTS", return_value="/fake/tts_path.mp3")
@patch("pronun_model.utils.calculate_presentation_score.adjust_audio_length")
@patch("pronun_model.utils.calculate_presentation_score.compare_audio_similarity", return_value=0.9)
@patch("pronun_model.utils.calculate_presentation_score.analyze_low_accuracy", return_value=([("0-60s",0.9)], [("0-60s",120)],0.85))
@patch("pronun_model.utils.calculate_presentation_score.analyze_pronunciation_accuracy", return_value=0.88)
def test_calculate_presentation_score_success(*mocks):
    result = calculate_presentation_score("dummy.mp3", "video_id")
    assert result is not None
    assert result["average_accuracy"] == 0.85

@patch("pronun_model.utils.calculate_presentation_score.STT", return_value=None)
def test_calc_score_stt_fail(mock_stt):
    with pytest.raises(AudioProcessingError):
        calculate_presentation_score("dummy.mp3", "video_id")

@patch("pronun_model.utils.calculate_presentation_score.TTS", return_value=None)
@patch("pronun_model.utils.calculate_presentation_score.STT", return_value="stt text")
@patch("pronun_model.utils.calculate_presentation_score.correct_text_with_llm", return_value="text")
@patch("pronun_model.utils.calculate_presentation_score.calculate_audio_duration", return_value=60)
@patch("pronun_model.utils.calculate_presentation_score.count_words", return_value=120)
@patch("pronun_model.utils.calculate_presentation_score.calculate_speed", return_value=120)
def test_calc_score_tts_fail(*mocks):
    with pytest.raises(AudioProcessingError):
        calculate_presentation_score("dummy.mp3", "video_id")

@patch("pronun_model.utils.calculate_presentation_score.analyze_low_accuracy", side_effect=Exception("Low accuracy error"))
@patch("pronun_model.utils.calculate_presentation_score.STT", return_value="stt text")
@patch("pronun_model.utils.calculate_presentation_score.correct_text_with_llm", return_value="text")
@patch("pronun_model.utils.calculate_presentation_score.calculate_audio_duration", return_value=60)
@patch("pronun_model.utils.calculate_presentation_score.count_words", return_value=120)
@patch("pronun_model.utils.calculate_presentation_score.calculate_speed", return_value=120)
@patch("pronun_model.utils.calculate_presentation_score.TTS", return_value="/fake/tts_path.mp3")
@patch("pronun_model.utils.calculate_presentation_score.adjust_audio_length")
@patch("pronun_model.utils.calculate_presentation_score.compare_audio_similarity", return_value=0.9)
def test_calc_score_analyze_low_accuracy_fail(*mocks):
    with pytest.raises(AudioProcessingError):
        calculate_presentation_score("dummy.mp3", "video_id")

@patch("pronun_model.utils.calculate_presentation_score.analyze_pronunciation_accuracy", return_value=None)
@patch("pronun_model.utils.calculate_presentation_score.STT", return_value="stt text")
@patch("pronun_model.utils.calculate_presentation_score.correct_text_with_llm", return_value="text")
@patch("pronun_model.utils.calculate_presentation_score.calculate_audio_duration", return_value=60)
@patch("pronun_model.utils.calculate_presentation_score.count_words", return_value=120)
@patch("pronun_model.utils.calculate_presentation_score.calculate_speed", return_value=120)
@patch("pronun_model.utils.calculate_presentation_score.TTS", return_value="/fake/tts_path.mp3")
@patch("pronun_model.utils.calculate_presentation_score.adjust_audio_length")
@patch("pronun_model.utils.calculate_presentation_score.compare_audio_similarity", return_value=0.9)
@patch("pronun_model.utils.calculate_presentation_score.analyze_low_accuracy", return_value=([("0-60s",0.9)], [("0-60s",120)],0.85))
def test_calc_score_pronunciation_accuracy_fail(*mocks):
    with pytest.raises(AudioProcessingError):
        calculate_presentation_score("dummy.mp3", "video_id")

@patch("pronun_model.utils.calculate_presentation_score.STT", side_effect=Exception("Unknown"))
def test_calc_score_unknown_error(mock_stt):
    with pytest.raises(AudioProcessingError):
        calculate_presentation_score("dummy.mp3", "video_id")
