# tests/pronun_model/test_routers/test_delete_files.py

import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from pronun_model.routers.delete_files import router
from pronun_model.schemas.feedback import DeleteResponse
from fastapi import FastAPI, HTTPException
from pathlib import Path

app = FastAPI()
app.include_router(router)

client = TestClient(app)

@pytest.fixture
def mock_paths(mocker):
    """Path.glob과 Path.unlink를 Mocking하는 Fixture."""
    # glob 모의
    mock_glob = mocker.patch("pathlib.Path.glob")
    # unlink 모의
    mock_unlink = mocker.patch("pathlib.Path.unlink")
    return mock_glob, mock_unlink

def test_delete_files_success(mock_paths):
    mock_glob, mock_unlink = mock_paths
    video_id = "testvideo123"

    # 영상, mp3, tts 파일, 스크립트 파일 모두 존재
    mock_video_files = [Path(f"/fake/upload_dir/{video_id}_1.mp4")]
    mock_mp3_files = [Path(f"/fake/convert_mp3_dir/{video_id}_audio.mp3")]
    mock_tts_files = [Path(f"/fake/convert_tts_dir/{video_id}_tts.mp3")]
    mock_script_files = [Path(f"/fake/scripts_dir/{video_id}.txt")]

    def side_effect(pattern):
        if "UPLOAD_DIR" in str(pattern):
            return mock_video_files
        elif "CONVERT_MP3_DIR" in str(pattern):
            return mock_mp3_files
        elif "CONVERT_TTS_DIR" in str(pattern):
            return mock_tts_files
        elif "SCRIPTS_DIR" in str(pattern):
            return mock_script_files
        return []

    mock_glob.side_effect = side_effect

    response = client.delete(f"/delete_files/{video_id}")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["message"] == f"{video_id} video_id와 관련된 파일 삭제에 성공했습니다."

    # unlink 호출 횟수 확인
    assert mock_unlink.call_count == 4

def test_delete_files_missing_files(mock_paths):
    mock_glob, mock_unlink = mock_paths
    video_id = "missing123"

    # 영상 파일 없음, mp3 있음, tts 없음 -> 필수 파일 누락
    mock_video_files = []
    mock_mp3_files = [Path(f"/fake/convert_mp3_dir/{video_id}_audio.mp3")]
    mock_tts_files = []
    mock_script_files = []

    def side_effect(pattern):
        if "UPLOAD_DIR" in str(pattern):
            return mock_video_files
        elif "CONVERT_MP3_DIR" in str(pattern):
            return mock_mp3_files
        elif "CONVERT_TTS_DIR" in str(pattern):
            return mock_tts_files
        elif "SCRIPTS_DIR" in str(pattern):
            return mock_script_files
        return []

    mock_glob.side_effect = side_effect

    response = client.delete(f"/delete_files/{video_id}")
    assert response.status_code == 404
    assert "필수 파일이 없습니다" in response.json()["detail"]
    mock_unlink.assert_not_called()

def test_delete_files_no_script_files(mock_paths):
    mock_glob, mock_unlink = mock_paths
    video_id = "noscript"

    # 필수 파일은 모두 존재, 스크립트 파일 없음
    mock_video_files = [Path(f"/fake/upload_dir/{video_id}_video.mp4")]
    mock_mp3_files = [Path(f"/fake/convert_mp3_dir/{video_id}_audio.mp3")]
    mock_tts_files = [Path(f"/fake/convert_tts_dir/{video_id}_tts.mp3")]
    mock_script_files = []

    def side_effect(pattern):
        if "UPLOAD_DIR" in str(pattern):
            return mock_video_files
        elif "CONVERT_MP3_DIR" in str(pattern):
            return mock_mp3_files
        elif "CONVERT_TTS_DIR" in str(pattern):
            return mock_tts_files
        elif "SCRIPTS_DIR" in str(pattern):
            return mock_script_files
        return []

    mock_glob.side_effect = side_effect

    response = client.delete(f"/delete_files/{video_id}")
    assert response.status_code == 200
    assert "성공했습니다" in response.json()["message"]
    # 스크립트 파일 없으므로 3개 파일만 삭제
    assert mock_unlink.call_count == 3

def test_delete_files_unlink_error(mock_paths):
    mock_glob, mock_unlink = mock_paths
    video_id = "unlinkerror"

    # 모든 파일 존재
    mock_video_files = [Path(f"/fake/upload_dir/{video_id}_video.mp4")]
    mock_mp3_files = [Path(f"/fake/convert_mp3_dir/{video_id}_audio.mp3")]
    mock_tts_files = [Path(f"/fake/convert_tts_dir/{video_id}_tts.mp3")]
    mock_script_files = [Path(f"/fake/scripts_dir/{video_id}.txt")]

    def side_effect(pattern):
        if "UPLOAD_DIR" in str(pattern):
            return mock_video_files
        elif "CONVERT_MP3_DIR" in str(pattern):
            return mock_mp3_files
        elif "CONVERT_TTS_DIR" in str(pattern):
            return mock_tts_files
        elif "SCRIPTS_DIR" in str(pattern):
            return mock_script_files
        return []

    mock_glob.side_effect = side_effect

    # 첫 파일 삭제는 성공, 두 번째 파일 삭제시 예외 발생
    mock_unlink.side_effect = [None, Exception("File deletion failed")]

    response = client.delete(f"/delete_files/{video_id}")
    assert response.status_code == 500
    assert "파일 삭제에 실패했습니다" in response.json()["detail"]
    assert mock_unlink.call_count == 2

def test_delete_files_no_related_files(mock_paths):
    mock_glob, mock_unlink = mock_paths
    video_id = "norelated"

    # 관련 파일 전혀 없음
    def side_effect(pattern):
        return []
    mock_glob.side_effect = side_effect

    response = client.delete(f"/delete_files/{video_id}")
    assert response.status_code == 404
    assert "필수 파일이 없습니다" in response.json()["detail"]
    mock_unlink.assert_not_called()
