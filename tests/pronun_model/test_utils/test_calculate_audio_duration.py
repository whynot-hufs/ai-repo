import pytest
from unittest.mock import patch, MagicMock
from pronun_model.utils.calculate_audio_duration import calculate_audio_duration
from pronun_model.exceptions import AudioProcessingError

@patch("pronun_model.utils.calculate_audio_duration.AudioSegment.from_file")
def test_calculate_audio_duration_success(mock_from_file):
    mock_audio = MagicMock()
    mock_audio.__len__.return_value = 5000  # 5초
    mock_from_file.return_value = mock_audio

    result = calculate_audio_duration("dummy.mp3")
    assert result == 5.0

def test_calculate_audio_duration_exception():
    with patch("pronun_model.utils.calculate_audio_duration.AudioSegment.from_file", side_effect=Exception("Test error")):
        with pytest.raises(AudioProcessingError):
            calculate_audio_duration("dummy.mp3")
