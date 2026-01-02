import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
import enum

from app.core.database import Base


class VideoStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    GENERATING_SCRIPT = "generating_script"
    GENERATING_AUDIO = "generating_audio"
    GENERATING_VIDEO = "generating_video"
    DONE = "done"
    FAILED = "failed"


class VideoStyle(str, enum.Enum):
    LUXURY = "luxury"
    MINIMAL = "minimal"
    TECH = "tech"
    LIFESTYLE = "lifestyle"


class Video(Base):
    """Video model for storing video generation requests."""
    
    __tablename__ = "videos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_name = Column(String(255), nullable=False)
    product_description = Column(Text, nullable=True)
    style = Column(String(50), default=VideoStyle.MINIMAL.value)
    status = Column(String(30), default=VideoStatus.PENDING.value)
    
    # Generated content
    script = Column(Text, nullable=True)
    audio_url = Column(Text, nullable=True)
    video_url = Column(Text, nullable=True)
    thumbnail_url = Column(Text, nullable=True)
    
    # Image paths (stored as JSON string)
    image_paths = Column(Text, nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Video {self.id}: {self.product_name}>"
