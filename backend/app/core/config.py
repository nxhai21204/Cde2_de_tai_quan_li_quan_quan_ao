# app/core/config.py

import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

# Tự động tìm file .env
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, "..", ".env")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_PATH, extra='ignore')

    # Database
    DATABASE_URL: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: Literal["HS256"] = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # MinIO
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET: str
    MINIO_USE_SECURE: bool = False

    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str


settings = Settings()
