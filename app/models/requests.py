"""Processing request-related Pydantic models."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ProcessingStatus(str, Enum):
    """Processing status enumeration."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MusicRecommendation(BaseModel):
    """Music recommendation model."""

    title: str
    artist: str
    genre: str
    mood: str
    energy_level: float = Field(ge=0.0, le=1.0)
    valence: float = Field(ge=0.0, le=1.0)
    preview_url: Optional[str] = None
    spotify_id: Optional[str] = None
    confidence_score: float = Field(ge=0.0, le=1.0)


class ProcessingProgress(BaseModel):
    """Processing progress update model."""
    
    stage: str
    progress: float = Field(ge=0.0, le=100.0)
    message: str
    timestamp: datetime


class ProcessingResult(BaseModel):
    """Processing result model."""

    scene_description: Optional[str] = None
    scene_mood: Optional[str] = None
    visual_elements: List[str] = []
    transcription: Optional[str] = None
    ambient_tags: List[str] = []
    audio_features: Dict[str, Any] = {}
    recommendations: List[MusicRecommendation] = []
    reasoning: Optional[str] = None
    processing_duration: Optional[float] = None
    model_versions: Dict[str, str] = {}
    progress_updates: List[ProcessingProgress] = []


class ProcessingRequest(BaseModel):
    """Processing request model."""

    id: UUID
    user_id: UUID
    video_filename: str
    video_url: Optional[str] = None
    status: ProcessingStatus
    description: Optional[str] = None
    music_year_start: Optional[int] = Field(default=1980, ge=1950, le=2024)
    music_year_end: Optional[int] = Field(default=2024, ge=1950, le=2024)
    result: Optional[ProcessingResult] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None


class ProcessingRequestCreate(BaseModel):
    """Model for creating a new processing request."""

    video_filename: str
    video_content_type: str
    description: Optional[str] = None
    music_year_start: Optional[int] = Field(default=1980, ge=1950, le=2024)
    music_year_end: Optional[int] = Field(default=2024, ge=1950, le=2024)


class ProcessingRequestResponse(BaseModel):
    """Model for processing request API responses."""

    id: UUID
    user_id: UUID
    video_filename: str
    video_url: Optional[str] = None
    status: ProcessingStatus
    description: Optional[str] = None
    music_year_start: Optional[int] = None
    music_year_end: Optional[int] = None
    result: Optional[ProcessingResult] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        """Pydantic configuration."""

        from_attributes = True 