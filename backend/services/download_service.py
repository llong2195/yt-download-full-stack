"""Download service with business logic for video downloads."""

import uuid
from typing import List, Dict
from sqlalchemy.orm import Session

from repository import channel_repo, download_repo
from services import youtube_service, channel_service
from utils.logger import get_logger

logger = get_logger(__name__)


class DownloadServiceError(Exception):
    """Base exception for download service errors."""

    pass


class DuplicateDownloadError(DownloadServiceError):
    """Raised when trying to download an already downloaded video."""

    pass


class ActiveDownloadError(DownloadServiceError):
    """Raised when video is already being downloaded."""

    pass


def request_download(
    db: Session,
    video_url: str,
    channel_id: int,
) -> Dict:
    """Request a single video download.

    Args:
        db: Database session
        video_url: YouTube video URL
        channel_id: Channel ID to associate with

    Returns:
        Dict with task information

    Raises:
        DownloadServiceError: Various download-related errors
    """
    # Extract video metadata
    try:
        metadata = youtube_service.extract_video_metadata(video_url)
    except youtube_service.YouTubeServiceError as e:
        raise DownloadServiceError(f"Failed to fetch video metadata: {str(e)}")

    video_id = metadata["video_id"]

    # Check for active download
    active_task = download_repo.get_active_task_for_video(db, video_id)
    if active_task:
        raise ActiveDownloadError(
            f"Video is already being downloaded (task #{active_task.id})"
        )

    # Check if already downloaded
    existing = download_repo.get_successful_download_for_video(db, video_id)
    if existing:
        raise DuplicateDownloadError(f"Video already downloaded on {existing.download_date}")

    # Generate task ID
    task_id = str(uuid.uuid4())

    # Create download task record
    task = download_repo.create_download_task(
        db=db,
        task_id=task_id,
        channel_id=channel_id,
        video_id=video_id,
        video_url=video_url,
    )

    # Enqueue download task (will be implemented with Huey)
    # from tasks.download_tasks import perform_download
    # perform_download(task_id)

    logger.info(f"Download requested for video {video_id} (task {task_id})")

    return {
        "id": task.id,
        "task_id": task.task_id,
        "video_id": task.video_id,
        "video_url": task.video_url,
        "status": task.status,
    }


def request_batch_download_by_urls(
    db: Session,
    video_urls: List[str],
) -> Dict:
    """Request batch download by video URLs with auto-channel detection.

    Args:
        db: Database session
        video_urls: List of YouTube video URLs

    Returns:
        Dict with batch operation results
    """
    results = {
        "total_requested": len(video_urls),
        "total_created": 0,
        "total_skipped": 0,
        "tasks": [],
        "errors": [],
    }

    for url in video_urls:
        try:
            # Extract video metadata
            metadata = youtube_service.extract_video_metadata(url)
            video_id = metadata["video_id"]
            channel_id_str = metadata["channel_id"]

            # Check for active download
            active_task = download_repo.get_active_task_for_video(db, video_id)
            if active_task:
                results["total_skipped"] += 1
                results["errors"].append({
                    "url": url,
                    "reason": "Already being downloaded",
                })
                continue

            # Check if already downloaded
            existing = download_repo.get_successful_download_for_video(db, video_id)
            if existing:
                results["total_skipped"] += 1
                results["errors"].append({
                    "url": url,
                    "reason": "Already downloaded",
                })
                continue

            # Auto-create or find channel
            channel = channel_repo.get_channel_by_youtube_id(db, channel_id_str)
            if not channel:
                # Create channel automatically
                try:
                    channel_info = channel_service.validate_and_add_channel(
                        db, metadata["channel_url"]
                    )
                    channel = channel_repo.get_channel_by_id(db, channel_info["id"])
                except Exception as e:
                    logger.error(f"Failed to auto-create channel: {e}")
                    results["errors"].append({
                        "url": url,
                        "reason": f"Failed to create channel: {str(e)}",
                    })
                    continue

            # Create download task
            task_id = str(uuid.uuid4())
            task = download_repo.create_download_task(
                db=db,
                task_id=task_id,
                channel_id=channel.id,
                video_id=video_id,
                video_url=url,
            )

            # Enqueue download (Huey integration to be implemented)
            # from tasks.download_tasks import perform_download
            # perform_download(task_id)

            results["total_created"] += 1
            results["tasks"].append({
                "id": task.id,
                "task_id": task.task_id,
                "video_id": task.video_id,
                "video_url": task.video_url,
                "channel_id": task.channel_id,
                "status": task.status,
            })

            logger.info(f"Batch download: Created task for video {video_id}")

        except youtube_service.YouTubeServiceError as e:
            results["errors"].append({
                "url": url,
                "reason": str(e),
            })
        except Exception as e:
            logger.error(f"Unexpected error processing {url}: {e}")
            results["errors"].append({
                "url": url,
                "reason": f"Unexpected error: {str(e)}",
            })

    return results
