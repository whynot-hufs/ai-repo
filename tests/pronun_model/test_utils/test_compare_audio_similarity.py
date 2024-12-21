import pytest
from unittest.mock import patch, MagicMock
from pronun_model.utils.compare_audio_similarity import compare_audio_similarity
from pronun_model.exceptions import AudioProcessingError

@patch("pronun_model.utils.compare_audio_similarity.librosa.load", return_value=(MagicMock(), 22050))
@patch("pronun_model.utils.compare_audio_similarity.librosa.feature.mfcc")
@patch("pronun_model.utils.compare_audio_similarity.cosine_similarity", return_value=[[0.85]])
def test_compare_audio_similarity_success(mock_mfcc, mock_similarity, mock_load):
    result = compare_audio_similarity("file1.mp3", "file2.mp3")
    assert result == 0.85

@patch("pronun_model.utils.compare_audio_similarity.librosa.load", side_effect=Exception("Librosa load failed"))
def test_compare_audio_similarity_load_error(mock_load):
    with pytest.raises(AudioProcessingError):
        compare_audio_similarity("file1.mp3", "file2.mp3")
