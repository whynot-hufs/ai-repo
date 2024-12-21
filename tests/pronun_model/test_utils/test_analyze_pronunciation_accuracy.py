import pytest
from unittest.mock import patch
from pronun_model.utils.analyze_pronunciation_accuracy import analyze_pronunciation_accuracy
from pronun_model.exceptions import AudioProcessingError

@patch("pronun_model.utils.analyze_pronunciation_accuracy.preprocess_text", side_effect=lambda x: x.lower())
@patch("pronun_model.utils.analyze_pronunciation_accuracy.fuzz.token_set_ratio", return_value=85)
def test_analyze_pronunciation_accuracy(mock_fuzz, mock_preprocess_text):
    stt_text = "This is a test"
    reference_text = "This is a test reference"
    result = analyze_pronunciation_accuracy(stt_text, reference_text)
    assert result == 0.85
    mock_fuzz.assert_called_once()

def test_analyze_pronunciation_accuracy_exception():
    with patch("pronun_model.utils.analyze_pronunciation_accuracy.preprocess_text", side_effect=Exception("Test error")):
        with pytest.raises(AudioProcessingError):
            analyze_pronunciation_accuracy("dummy", "reference")
