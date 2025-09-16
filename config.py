from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database settings
    DB_HOST: str 
    DB_PORT: int
    DB_NAME: str 
    DB_USER: str 
    DB_PASSWORD: str 
    
    # Telegram Bot settings
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHAT_ID: str
    TELEGRAM_ADMIN_ID: str

    # Security settings
    API_KEY_HEADER: str 
    
    # Application settings
    APP_HOST: str
    APP_PORT: int
    DEBUG: bool
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
