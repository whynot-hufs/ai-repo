# tests/conftest.py

import pytest
import sys
import os
import logging
from pathlib import Path
from fastapi.testclient import TestClient

# 로그 레벨 설정 (필요 시 레벨 변경 가능)
@pytest.fixture(scope="session", autouse=True)
def configure_logging():
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    yield

# 현재 파일 기준으로 상위 디렉토리가 프로젝트 루트라고 가정
# tests 디렉토리와 pronun_model, main.py가 같은 루트에 있다고 가정:
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# main.py가 프로젝트 루트에 있고, main.py 내에 FastAPI 'app'이 정의되어 있다고 가정
from main import app

@pytest.fixture
def client():
    return TestClient(app)
