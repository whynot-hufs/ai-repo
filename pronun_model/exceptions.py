# pronun_model/exceptions.py

class DocumentProcessingError(Exception):
    """
    문서(스크립트)를 처리하는 중 발생하는 예외.

    Attributes:
        message (str): 예외에 대한 상세 메시지.
    """
    def __init__(self, message: str):
        self.message = message

class AudioProcessingError(Exception):
    """
    오디오를 처리하는 중 발생하는 예외.

    Attributes:
        message (str): 예외에 대한 상세 메시지.
    """
    def __init__(self, message: str):
        self.message = message


class AudioImportingError(Exception):
    """
    오디오 파일을 임포트하는 중 발생하는 예외.

    Attributes:
        message (str): 예외에 대한 상세 메시지.
    """
    def __init__(self, message: str):
        self.message = message
