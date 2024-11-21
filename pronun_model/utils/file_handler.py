# pronun_model/utils/file_handler.py

import os
import logging
from pronun_model.config import UPLOAD_DIR, CONVERT_MP3_DIR, CONVERT_TTS_DIR

def ensure_directories():
    """
    필요한 저장 디렉토리를 생성합니다.
    """
    try:
        for directory in [UPLOAD_DIR, CONVERT_MP3_DIR, CONVERT_TTS_DIR]:
            os.makedirs(directory, exist_ok=True)
        logging.info("All necessary directories are ensured.")
    except Exception as e:
        logging.error(f"Failed to create directories: {e}")
