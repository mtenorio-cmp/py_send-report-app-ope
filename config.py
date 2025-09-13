from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database settings
    DB_HOST: str = ""
    DB_PORT: int = 0
    DB_NAME: str = ""
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    
    # Security settings
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""

    # Security settings
    API_KEY_HEADER: str = "X-API-Key"
    
    # Application settings
    APP_HOST: str = ""
    APP_PORT: int = 0
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
