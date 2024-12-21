import pytest
from unittest.mock import patch, MagicMock
from pronun_model.utils.analyze_low_accuracy import analyze_low_accuracy
from pronun_model.exceptions import AudioProcessingError

@patch("pronun_model.utils.analyze_low_accuracy.librosa.load", return_value=(MagicMock(), 22050))
@patch("pronun_model.utils.analyze_low_accuracy.librosa.get_duration", return_value=180)
@patch("pronun_model.utils.analyze_low_accuracy.analyze_pronunciation_accuracy", return_value=0.8)
@patch("pronun_model.utils.analyze_low_accuracy.count_words", return_value=100)
@patch("pronun_model.utils.analyze_low_accuracy.STT", return_value="dummy text")
@patch("pronun_model.utils.analyze_low_accuracy.shutil.rmtree")
@patch("pronun_model.utils.analyze_low_accuracy.sf.write")
def test_analyze_low_accuracy_success(mock_sf_write, mock_rmtree, mock_stt, mock_count_words, mock_accuracy, mock_duration, mock_load):
    audio_file_path = "dummy.mp3"
    script_text = "This is the reference text"
    result = analyze_low_accuracy(audio_file_path, script_text)
    assert len(result[0]) > 0  # 구간별 정확도 데이터
    assert result[2] > 0  # 평균 정확도
    mock_rmtree.assert_called_once()

def test_analyze_low_accuracy_exception():
    with patch("pronun_model.utils.analyze_low_accuracy.librosa.load", side_effect=Exception("Test error")):
        with pytest.raises(AudioProcessingError):
            analyze_low_accuracy("dummy.mp3", "reference")
