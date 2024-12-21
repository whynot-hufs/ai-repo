import pytest
from pronun_model.utils.preprocess_text import preprocess_text
from pronun_model.exceptions import AudioProcessingError

def test_preprocess_text_success():
    result = preprocess_text("Hello, World! 123 테스트.")
    assert result == "hello world 123 테스트"

def test_preprocess_text_empty():
    assert preprocess_text("") == ""

def test_preprocess_text_error():
    with pytest.raises(AudioProcessingError):
        preprocess_text(None)
