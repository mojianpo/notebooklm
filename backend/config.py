from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./notebooklm.db"
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: list = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
        "text/markdown",
        "text/html"
    ]
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:5000", "http://localhost:3000"]
    
    # LLM Configuration
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-3.5-turbo"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 2000
    LLM_TIMEOUT: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
