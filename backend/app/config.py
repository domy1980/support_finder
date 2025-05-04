#backend/config.py

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API設定
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Disease Support Finder"
    
    # データベース設定
    DATABASE_URL: str = "sqlite:///./disease_support.db"
    
    # LM Studio設定
    LM_STUDIO_BASE_URL: str = "http://localhost:1234/v1"
    LM_STUDIO_MODEL: str = "qwen2.5-7b-instruct-q4_k_m"
    
    # スクレイピング設定
    USER_AGENT: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
    REQUEST_TIMEOUT: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()
