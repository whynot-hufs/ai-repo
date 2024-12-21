import pytest
from unittest.mock import patch, MagicMock
from pronun_model.utils.convert_to_mp3 import convert_to_mp3
from pronun_model.exceptions import AudioImportingError

@patch("pronun_model.utils.convert_to_mp3.AudioSegment.from_file")
@patch("pronun_model.utils.convert_to_mp3.AudioSegment.export")
@patch("pronun_model.utils.convert_to_mp3.Path.exists", return_value=True)
def test_convert_to_mp3_success(mock_exists, mock_export, mock_from_file):
    mock_audio = MagicMock()
    mock_from_file.return_value = mock_audio
    result = convert_to_mp3("dummy_file.wav", "dummy_video_id")
    assert "dummy_video_id.mp3" in result

@patch("pronun_model.utils.convert_to_mp3.AudioSegment.from_file", side_effect=Exception("Conversion failed"))
def test_convert_to_mp3_conversion_error(mock_from_file):
    with pytest.raises(AudioImportingError):
        convert_to_mp3("dummy_file.wav", "dummy_video_id")
