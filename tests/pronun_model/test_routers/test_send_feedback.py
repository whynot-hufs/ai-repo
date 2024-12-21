# tests/pronun_model/test_routers/test_send_feedback.py

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from pronun_model.routers.send_feedback import router
from fastapi import FastAPI
from pronun_model.exceptions import AudioProcessingError

app = FastAPI()
app.include_router(router)
client = TestClient(app)

@pytest.fixture
def mock_paths(mocker):
    mock_exists = mocker.patch("pathlib.Path.exists")
    mock_exists.return_value = True
    return mock_exists

@patch("pronun_model.routers.send_feedback.extract_text", return_value="script text")
@patch("pronun_model.routers.send_feedback.calculate_presentation_score", return_value={
    "audio_similarity":0.9,
    "original_speed":120,
    "tts_speed":110,
    "average_accuracy":0.85,
    "pronunciation_accuracy":0.88,
    "tts_file_path":"/fake/tts_path.mp3",
    "pronunciation_scores":[{"time_segment":"0-60s","accuracy":0.9}],
    "wpm_scores":[{"time_segment":"0-60s","wpm":120}]
})
def test_send_feedback_success(mock_calc_score, mock_ext, mock_paths, mocker):
    # MP3 존재
    response = client.get("/send-feedback/test_id")
    assert response.status_code == 200
    data = response.json()
    assert data["analysis_result"]["average_wpm"] == 120

@patch("pronun_model.routers.send_feedback.convert_to_mp3")
def test_send_feedback_original_video_not_found(mock_convert, mock_paths):
    # MP3 파일 없고, 원본 비디오도 없음
    mock_paths.side_effect = lambda: False
    response = client.get("/send-feedback/no_video")
    assert response.status_code == 404
    assert "원본 비디오 파일을 찾을 수 없습니다" in response.text

@patch("pronun_model.routers.send_feedback.calculate_presentation_score", return_value=None)
def test_send_feedback_analysis_failed(mock_calc, mock_paths):
    response = client.get("/send-feedback/fail_analysis")
    assert response.status_code == 500
    assert "비디오 분석에 실패했습니다" in response.text

@patch("pronun_model.routers.send_feedback.calculate_presentation_score", return_value={})
def test_send_feedback_missing_pronunciation_scores(mock_calc, mock_paths):
    response = client.get("/send-feedback/missing_key")
    assert response.status_code == 400
    assert "결과 데이터 키가 누락되었습니다" in response.text

@patch("pronun_model.routers.send_feedback.calculate_presentation_score", side_effect=Exception("Unknown error"))
def test_send_feedback_unknown_error(mock_calc, mock_paths):
    response = client.get("/send-feedback/unknown_err")
    assert response.status_code == 500
    assert "예기치 않은 오류 발생" in response.text
