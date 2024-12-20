# tests/pronun_model/test_routers/test_upload_video.py

import pytest
from unittest.mock import patch, mock_open
from fastapi.testclient import TestClient
from pronun_model.routers.upload_video import router
from fastapi import FastAPI, UploadFile
import io

app = FastAPI()
app.include_router(router)
client = TestClient(app)

def create_upload_file(filename, content=b"file_content"):
    return UploadFile(filename=filename, file=io.BytesIO(content))

def test_upload_video_no_script():
    video = create_upload_file("test.mp4")
    response = client.post("/upload-video-with-script/", files={"video":("test.mp4",video.file,"video/mp4")})
    assert response.status_code == 200
    json_data = response.json()
    assert "video_id" in json_data

def test_upload_video_with_script():
    video = create_upload_file("test.mp4")
    script = create_upload_file("script.txt", b"script content")
    response = client.post("/upload-video-with-script/",
        files={
            "video":("test.mp4",video.file,"video/mp4"),
            "script":("script.txt",script.file,"text/plain")
        })
    assert response.status_code == 200

def test_upload_video_unsupported_video():
    video = create_upload_file("test.xyz")
    response = client.post("/upload-video-with-script/", files={"video":("test.xyz",video.file,"video/xyz")})
    assert response.status_code == 415
    assert "지원하지 않는 영상 파일 형식입니다." in response.text

def test_upload_video_unsupported_script():
    video = create_upload_file("test.mp4")
    script = create_upload_file("script.exe", b"malicious")
    response = client.post("/upload-video-with-script/",
        files={
            "video":("test.mp4",video.file,"video/mp4"),
            "script":("script.exe",script.file,"application/octet-stream")
        })
    assert response.status_code == 415
    assert "지원하지 않는 스크립트 파일 형식" in response.text

@patch("builtins.open", side_effect=Exception("File save error"))
def test_upload_video_file_save_failure(mock_open_file):
    video = create_upload_file("test.mp4")
    response = client.post("/upload-video-with-script/", files={"video":("test.mp4",video.file,"video/mp4")})
    assert response.status_code == 500
    assert "비디오 파일 저장 실패" in response.text
