from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid

from config.settings import settings

Base = declarative_base()
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Video(Base):
    __tablename__ = "videos"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    script = Column(Text, nullable=False)
    style = Column(String, nullable=False)
    voice = Column(String, nullable=False)
    keywords = Column(JSON, nullable=True)
    negative_keywords = Column(JSON, nullable=True)
    
    # Generated content
    prompts = Column(JSON, nullable=True)
    image_paths = Column(JSON, nullable=True)
    audio_path = Column(String, nullable=True)
    video_path = Column(String, nullable=True)
    duration = Column(Integer, nullable=True)  # Duration in seconds
    
    # Status
    status = Column(String, default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "script": self.script,
            "style": self.style,
            "voice": self.voice,
            "keywords": self.keywords,
            "negative_keywords": self.negative_keywords,
            "prompts": self.prompts,
            "image_paths": self.image_paths,
            "audio_path": self.audio_path,
            "video_path": self.video_path,
            "duration": self.duration,
            "status": self.status,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
