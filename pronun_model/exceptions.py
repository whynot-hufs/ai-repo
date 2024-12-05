# app/exceptions.py

class DocumentProcessingError(Exception):
    def __init__(self, message: str):
        self.message = message

class AudioProcessingError(Exception):
    def __init__(self, message: str):
        self.message = message

class AudioImportingError(Exception):
    def __init__(self, message: str):
        self.message = message
