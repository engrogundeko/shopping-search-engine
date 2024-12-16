import os
from pydantic_settings import BaseSettings
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

# import chromadb

class Settings(BaseSettings):
    PROJECT_NAME: str = "Volera API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./volera.db"
    REDIS_URL: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache
def get_settings() -> Settings:
    return Settings()

