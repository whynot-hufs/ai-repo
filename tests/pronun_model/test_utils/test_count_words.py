import pytest
from pronun_model.utils.count_words import count_words
from pronun_model.exceptions import AudioProcessingError

def test_count_words_success():
    assert count_words("This is a test") == 4

def test_count_words_empty():
    assert count_words("") == 0

def test_count_words_error():
    with pytest.raises(AudioProcessingError):
        count_words(None)
