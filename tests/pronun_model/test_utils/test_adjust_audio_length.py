import pytest
from unittest.mock import patch, MagicMock
from pydub import AudioSegment
from pronun_model.utils.adjust_audio_length import adjust_audio_length
from pronun_model.exceptions import AudioProcessingError

@patch("pronun_model.utils.adjust_audio_length.AudioSegment")
def test_adjust_audio_length_add_silence(mock_audio_segment):
    mock_audio = MagicMock()
    mock_audio.__len__.return_value = 5000  # 5초
    mock_audio_segment.from_file.return_value = mock_audio

    target_duration = 10  # 10초
    audio_path = "dummy.mp3"
    mock_audio.export.return_value = None

    result = adjust_audio_length(audio_path, target_duration)
    assert result == audio_path
    mock_audio_segment.from_file.assert_called_with(audio_path)
    mock_audio.export.assert_called_once()

def test_adjust_audio_length_exception():
    with patch("pronun_model.utils.adjust_audio_length.AudioSegment.from_file", side_effect=Exception("Test error")):
        with pytest.raises(AudioProcessingError):
            adjust_audio_length("dummy.mp3", 10)
