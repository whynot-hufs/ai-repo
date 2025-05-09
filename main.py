from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from pronun_model.routers.upload_video import router as upload_video_router
from pronun_model.routers.ask_question import router as ask_question_router
from pronun_model.routers.delete_files import router as delete_files_router

from pathlib import Path
from dotenv import load_dotenv
import json
import uvicorn
import logging
import logging.config
import traceback
import os

# Load environment variables
load_dotenv()

# Configure logging from JSON file
logging_config_path = Path(__file__).resolve().parent / "logging_config.json"
with open(logging_config_path, "r") as f:
    logging_config = json.load(f)

# Remove any Sentry handlers
if logging_config.get("handlers") and "sentry" in logging_config["handlers"]:
    del logging_config["handlers"]["sentry"]
    for lg in logging_config.get("loggers", {}).values():
        if "sentry" in lg.get("handlers", []):
            lg["handlers"].remove("sentry")

logging.config.dictConfig(logging_config)
logger = logging.getLogger("pronun_model")

# Initialize FastAPI app
app = FastAPI(title="Pronun Q&A Service")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)

# Include routers
app.include_router(upload_video_router, prefix="/api/pronun", tags=["Upload"])
app.include_router(ask_question_router, prefix="/api/pronun", tags=["Q&A"])
app.include_router(delete_files_router, prefix="/api/pronun", tags=["Delete"])

# Root endpoint
@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Hello, Selina!"}

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.debug("Request received")
    try:
        response = await call_next(request)
        logger.info("Response sent", extra={
            "errorType": "",
            "error_message": ""
        })
        return response
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        if tb:
            filename, lineno, func, _ = tb[-1]
        else:
            filename, lineno, func = ("unknown", 0, "unknown")
        logger.error("Error processing request", extra={
            "errorType": type(e).__name__,
            "error_message": str(e)
        })
        raise

# Exception handler: catch-all HTTPException
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error("HTTP exception", extra={
        "errorType": type(exc).__name__,
        "error_message": str(exc.detail)
    })
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# Exception handler: catch-all
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception", extra={
        "errorType": type(exc).__name__,
        "error_message": str(exc)
    })
    return JSONResponse(
        status_code=500,
        content={"detail": "서버 내부 오류가 발생했습니다."},
    )

# Test logging endpoint
@app.get("/test-logging")
def test_logging():
    logger.debug("디버그 레벨 로그 테스트")
    logger.info("정보 레벨 로그 테스트")
    logger.error("오류 레벨 로그 테스트")
    return {"message": "로깅 테스트 완료"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True,
        log_config="logging_config.json"
    )

# uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-config logging_config.json
