"""Pydantic schemas for API request/response models."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ============================================================================
# Channel Schemas
# ============================================================================


class ChannelCreate(BaseModel):
    """Request model for creating a channel."""

    url: str = Field(..., description="YouTube channel URL")


class ChannelResponse(BaseModel):
    """Response model for a channel."""

    id: int
    channel_id: str
    name: str
    url: str
    download_path: str
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
    page: int
    page_size: int


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
