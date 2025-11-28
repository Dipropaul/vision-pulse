import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    OPENAI_IMAGE_MODEL: str = os.getenv("OPENAI_IMAGE_MODEL", "dall-e-3")
    OPENAI_TTS_MODEL: str = os.getenv("OPENAI_TTS_MODEL", "tts-1")
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_RELOAD: bool = os.getenv("API_RELOAD", "True").lower() == "true"
    
    # Storage Configuration
    VIDEOS_DIR: Path = Path(os.getenv("VIDEOS_DIR", "./output/videos"))
    IMAGES_DIR: Path = Path(os.getenv("IMAGES_DIR", "./output/images"))
    AUDIO_DIR: Path = Path(os.getenv("AUDIO_DIR", "./output/audio"))
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./visionpulse.db")
    
    # Video Configuration
    DEFAULT_IMAGE_SIZE: str = "1024x1024"
    DEFAULT_VIDEO_FPS: int = 30
    DEFAULT_IMAGE_DURATION: float = 5.0  # seconds per image
    ENABLE_MOTION_EFFECTS: bool = os.getenv("ENABLE_MOTION_EFFECTS", "True").lower() == "true"
    
    # Note: OpenAI Sora is not yet publicly available via API
    # When Sora API becomes available, update OPENAI_VIDEO_MODEL setting
    # OPENAI_VIDEO_MODEL: str = os.getenv("OPENAI_VIDEO_MODEL", "sora-1.0")
    USE_SORA_WHEN_AVAILABLE: bool = False
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields from .env

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories if they don't exist
        self.VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
        self.IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        self.AUDIO_DIR.mkdir(parents=True, exist_ok=True)

settings = Settings()
