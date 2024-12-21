from pronun_model.utils.text_cleaning import clean_extracted_text

def test_clean_extracted_text():
    raw_text = """
    ^1. Example text with ^2) invalid data.
    Base64EncodedData1234567890==
    7 8 More invalid text. IAA Final text!
    """
    expected_cleaned_text = "Example text with invalid data. More invalid text. Final text!"
    cleaned_text = clean_extracted_text(raw_text)
    assert cleaned_text == expected_cleaned_text
