"""
アプリケーション設定
"""

import os
from typing import Optional


class Settings:
    """アプリケーション設定クラス"""
    
    # アプリケーション基本設定
    APP_NAME: str = "AI旅行プランナー"
    VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv("DEBUG", "True") == "True"
    
    # サーバー設定
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # CORS設定
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ]
    
    # データベース設定（将来の拡張用）
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    # API Keys（将来の拡張用）
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    GOOGLE_MAPS_API_KEY: Optional[str] = os.getenv("GOOGLE_MAPS_API_KEY")
    WEATHER_API_KEY: Optional[str] = os.getenv("WEATHER_API_KEY")


settings = Settings()
