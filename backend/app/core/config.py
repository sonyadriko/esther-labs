from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/videogen"
    
    # API Keys
    gemini_api_key: str = ""
    
    # Storage
    upload_dir: str = "./uploads"
    output_dir: str = "./outputs"
    
    # Video settings
    video_width: int = 1080
    video_height: int = 1920
    video_fps: int = 30
    video_duration: int = 15  # seconds per scene
    
    # CORS
    allowed_origins: list[str] = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
