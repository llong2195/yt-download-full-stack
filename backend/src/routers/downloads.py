"""Downloads API router."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.models.database import get_db
from src.models.schemas import (
    BatchDownloadResponse,
    BatchUrlDownloadRequest,
    DownloadRequest,
    DownloadTaskResponse,
    ErrorResponse,
)
from src.services import download_service

router = APIRouter()


@router.post("/batch-urls", response_model=BatchDownloadResponse)
async def request_batch_download_by_urls(
    request: BatchUrlDownloadRequest,
    db: Session = Depends(get_db),
):
    """Request batch download by video URLs with auto-channel detection.

    This endpoint:
    - Accepts a list of YouTube video URLs
    - Extracts video metadata from each URL
    - Auto-detects and creates channels if they don't exist
    - Checks for duplicates (already downloaded or in progress)
    - Enqueues download tasks for valid videos
    """
    try:
        if not request.video_urls or len(request.video_urls) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="video_urls list cannot be empty",
            )

        results = download_service.request_batch_download_by_urls(
            db, request.video_urls
        )

        return BatchDownloadResponse(
            tasks=[
                DownloadTaskResponse(
                    id=task["id"],
                    task_id=task["task_id"],
                    channel_id=task["channel_id"],
                    video_id=task["video_id"],
                    video_url=task["video_url"],
                    status=task["status"],
                    progress_percent=0,
                    error_message=None,
                    retry_count=0,
                    created_at=None,  # Will be populated from DB
                    started_at=None,
                    completed_at=None,
                )
                for task in results["tasks"]
            ],
            total_requested=results["total_requested"],
            total_created=results["total_created"],
            total_skipped=results["total_skipped"],
            skipped_reason=(
                f"{len(results['errors'])} videos skipped (see errors)"
                if results["errors"]
                else None
            ),
        )

    except download_service.DownloadServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process batch download: {str(e)}",
        )


@router.post("", response_model=DownloadTaskResponse, status_code=status.HTTP_201_CREATED)
async def request_single_download(
    request: DownloadRequest,
    db: Session = Depends(get_db),
):
    """Request a single video download."""
    try:
        result = download_service.request_download(
            db, request.video_url, request.channel_id
        )

        # Fetch full task details
        from src.repository import download_repo
        task = download_repo.get_task_by_task_id(db, result["task_id"])
        if not task:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Task created but not found in database",
            )

        return DownloadTaskResponse.model_validate(task)

    except download_service.DuplicateDownloadError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )

    except download_service.ActiveDownloadError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )

    except download_service.DownloadServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to request download: {str(e)}",
        )
