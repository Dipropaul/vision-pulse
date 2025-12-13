from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class VideoCreateRequest(BaseModel):
    title: str = Field(..., description="Title of the video")
    script: str = Field(..., description="Script text for the video")
    style: str = Field(..., description="Visual style (e.g., 'cinematic', 'anime')")
    voice: str = Field(..., description="Narration voice (e.g., 'alloy', 'echo')")
    size: Optional[str] = Field(default="1280x720", description="Video resolution (e.g., '1280x720', '720x1280')")
    duration: Optional[int] = Field(default=8, description="Video duration in seconds (4, 8, or 12)")
    keywords: Optional[List[str]] = Field(default=[], description="Keywords to include")
    negative_keywords: Optional[List[str]] = Field(default=[], description="Keywords to avoid")

class VideoResponse(BaseModel):
    id: str
    title: str
    script: str
    style: str
    voice: str
    keywords: Optional[List[str]]
    negative_keywords: Optional[List[str]]
    prompts: Optional[List[str]]
    image_paths: Optional[List[str]]
    audio_path: Optional[str]
    video_path: Optional[str]
    duration: Optional[int]  # Duration in seconds
    status: str
    error_message: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]

class StyleResponse(BaseModel):
    id: str
    name: str
    description: str

class VoiceResponse(BaseModel):
    id: str
    name: str
    description: str
