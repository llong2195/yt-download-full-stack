"""Pydantic schemas for API request/response models."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ============================================================================
# Global Settings Schemas
# ============================================================================


class GlobalSettingsSchema(BaseModel):
    """Response model for global settings."""

    id: int
    default_download_path: str
    default_subtitle_language: Optional[str] = None
    default_video_quality: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class GlobalSettingsUpdateSchema(BaseModel):
    """Request model for updating global settings."""

    default_download_path: str = Field(..., description="Base download directory")
    default_subtitle_language: Optional[str] = Field(
        None, description="Default subtitle language (ISO 639-1 code)"
    )
    default_video_quality: Optional[str] = Field(
        None, description="Default video quality"
    )


# ============================================================================
# Channel Schemas
# ============================================================================


class ChannelCreate(BaseModel):
    """Request model for creating a channel."""

    url: str = Field(..., description="YouTube channel URL")
    name: str = Field(..., description="Custom user-defined channel name")
    download_path: Optional[str] = Field(
        None, description="Custom download path (defaults to global setting)"
    )
    subtitle_language: Optional[str] = Field(
        None, description="Subtitle language (ISO 639-1 code)"
    )
    video_quality: Optional[str] = Field(None, description="Video quality setting")


class ChannelUpdate(BaseModel):
    """Request model for updating a channel."""

    name: Optional[str] = Field(None, description="Custom user-defined channel name")
    download_path: Optional[str] = Field(None, description="Custom download path")
    subtitle_language: Optional[str] = Field(
        None, description="Subtitle language (ISO 639-1 code)"
    )
    video_quality: Optional[str] = Field(None, description="Video quality setting")


class ChannelResponse(BaseModel):
    """Response model for a channel."""

    id: int
    channel_id: str
    title: str
    name: str
    url: str
    download_path: str
    subtitle_language: Optional[str] = None
    video_quality: Optional[str] = None
    date_added: datetime
    last_updated: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChannelListResponse(BaseModel):
    """Response model for channel list."""

    channels: list[ChannelResponse]
    total: int


# ============================================================================
# DownloadTask Schemas
# ============================================================================


class DownloadRequest(BaseModel):
    """Request model for single video download."""

    video_url: str = Field(..., description="YouTube video URL")
    channel_id: int = Field(..., description="Channel ID to associate with")


class BatchDownloadRequest(BaseModel):
    """Request model for batch download by video IDs."""

    video_ids: list[str] = Field(..., description="List of YouTube video IDs")
    channel_id: int = Field(..., description="Channel ID to associate with")


class BatchUrlDownloadRequest(BaseModel):
    """Request model for batch download by video URLs."""

    video_urls: list[str] = Field(..., description="List of YouTube video URLs")


class DownloadTaskResponse(BaseModel):
    """Response model for a download task."""

    id: int
    task_id: str
    channel_id: int
    video_id: str
    video_url: str
    status: str
    progress_percent: int
    error_message: Optional[str] = None
    retry_count: int
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BatchDownloadResponse(BaseModel):
    """Response model for batch download request."""

    tasks: list[DownloadTaskResponse]
    total_requested: int
    total_created: int
    total_skipped: int
    skipped_reason: Optional[str] = None


# ============================================================================
# Queue Schemas
# ============================================================================


class QueueStatusResponse(BaseModel):
    """Response model for queue status."""

    total_pending: int
    total_downloading: int
    total_completed: int
    total_failed: int
    active_tasks: list[DownloadTaskResponse]


class TaskRetryResponse(BaseModel):
    """Response model for task retry."""

    success: bool
    new_task_id: str
    message: str


# ============================================================================
# History Schemas
# ============================================================================


class DownloadHistoryResponse(BaseModel):
    """Response model for download history record."""

    id: int
    channel_id: int
    video_id: str
    video_title: str
    video_url: str
    task_id: Optional[str] = None
    download_date: datetime
    upload_date: Optional[datetime] = None
    duration: Optional[int] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    video_metadata: Optional[str] = None
    download_duration_seconds: int
    success: bool
    error_code: Optional[str] = None

    class Config:
        from_attributes = True


class HistoryListResponse(BaseModel):
    """Response model for history list."""

    history: list[DownloadHistoryResponse]
    total: int
    limit: int
    offset: int
    filters_applied: dict[str, str | bool]


class HistoryStatsResponse(BaseModel):
    """Response model for download statistics."""

    total_downloads: int
    successful_downloads: int
    failed_downloads: int
    total_size_bytes: int
    total_duration_seconds: int
    average_download_time_seconds: float


# ============================================================================
# Health Schemas
# ============================================================================


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str
    version: str
    database: str
    huey: str


# ============================================================================
# Error Schemas
# ============================================================================


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error_code: str
    message: str
    details: Optional[str] = None
