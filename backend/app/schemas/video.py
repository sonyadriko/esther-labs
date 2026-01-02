from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from app.models.video import VideoStatus, VideoStyle


class VideoCreateRequest(BaseModel):
    """Request model for creating a new video."""
    product_name: str = Field(..., min_length=1, max_length=255)
    product_description: Optional[str] = None
    style: VideoStyle = VideoStyle.MINIMAL


class VideoResponse(BaseModel):
    """Response model for video data."""
    id: UUID
    product_name: str
    product_description: Optional[str]
    style: str
    status: str
    script: Optional[str]
    audio_url: Optional[str]
    video_url: Optional[str]
    thumbnail_url: Optional[str]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class VideoStatusResponse(BaseModel):
    """Response model for video status check."""
    id: UUID
    status: str
    video_url: Optional[str]
    error_message: Optional[str]
    progress_message: str = ""


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str = "1.0.0"
