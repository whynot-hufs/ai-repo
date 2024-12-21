import pytest
from unittest.mock import patch
from pronun_model.utils.calculate_speed import calculate_speed
from pronun_model.exceptions import AudioProcessingError

@patch("pronun_model.utils.calculate_speed.calculate_audio_duration", return_value=60)
@patch("pronun_model.utils.calculate_speed.count_words", return_value=120)
def test_calculate_speed_success(mock_duration, mock_count_words):
    result = calculate_speed("dummy_audio_path.mp3", "This is a test text")
    assert result == 120

@patch("pronun_model.utils.calculate_speed.calculate_audio_duration", side_effect=AudioProcessingError("Duration error"))
def test_calculate_speed_duration_error(mock_duration):
    with pytest.raises(AudioProcessingError):
        calculate_speed("dummy_audio_path.mp3", "This is a test text")
