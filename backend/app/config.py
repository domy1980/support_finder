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
    
    # Google Custom Search設定
    GOOGLE_API_KEY: str = "AIzaSyA1uVr9Rgu973gMxA1guk8QyvqKw2oEQTU"
    GOOGLE_CSE_ID: str = "727e4904427e9457a"  # Custom Search Engine ID
    GOOGLE_API_MAX_RESULTS: int = 10
    GOOGLE_API_RATE_LIMIT: int = 100  # 1日あたりの最大リクエスト数
    
    # スクレイピング設定
    USER_AGENT: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
    REQUEST_TIMEOUT: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()
