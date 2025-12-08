"""Huey background tasks for video downloads."""

import os
import time
from datetime import datetime
from pathlib import Path

import yt_dlp
import yt_dlp.utils
from sqlalchemy.orm import Session
from src.models.database import SessionLocal
from src.models.download_task import DownloadTask
from src.repository import channel_repo, download_repo
from src.utils.logger import get_logger
from src.utils.validators import sanitize_filename

from .huey_instance import huey

logger = get_logger(__name__)


class DownloadProgress:
    """Track download progress for yt-dlp hook."""

    def __init__(self, task_id: str, db: Session):
        self.task_id = task_id
        self.db = db
        self.last_update = 0

    def __call__(self, d):
        """Progress hook callback for yt-dlp."""
        if d["status"] == "downloading":
            # Update progress every 2 seconds to avoid excessive DB writes
            current_time = time.time()
            if current_time - self.last_update >= 2:
                try:
                    percent_str = d.get("_percent_str", "0%").strip().replace("%", "")
                    progress = int(float(percent_str))
                    download_repo.update_task_status(
                        self.db,
                        self.task_id,
                        status="downloading",
                        progress_percent=progress,
                    )
                    self.db.commit()
                    self.last_update = current_time
                except (ValueError, KeyError) as e:
                    logger.warning(f"Failed to parse progress: {e}")

        elif d["status"] == "finished":
            logger.info(f"Download finished for task {self.task_id}")


@huey.task(retries=3, retry_delay=60)
def download_video(task_id: str) -> bool:
    """
    Download video from YouTube using yt-dlp.

    Args:
        task_id: Internal database ID of the DownloadTask

    Returns:
        bool: True if download succeeded, False otherwise

    Retry Logic:
        - Max 3 retries
        - Delay: 60s (first), 120s (second), 240s (third) - handled by Huey's exponential backoff
    """
    db = SessionLocal()
    start_time = datetime.now()

    try:
        # Get task from database
        task = download_repo.get_task_by_id(db, task_id)
        if not task:
            print(
                f"No task found for task_id {task_id} during unexpected error handling."
            )
            logger.error(f"Task {task_id} not found in database")
            return False

        # Get channel info for download path
        channel = channel_repo.get_channel_by_id(db, task.channel_id)
        if not channel:
            logger.error(f"Channel {task.channel_id} not found for task {task_id}")
            download_repo.update_task_status(
                db, task.task_id, status="failed", error_message="Channel not found"
            )
            db.commit()
            return False

        # Update status to downloading (started_at is set automatically in update_task_status)
        download_repo.update_task_status(db, task.task_id, status="downloading")
        db.commit()

        logger.info(f"Starting download for task {task_id}: {task.video_url}")

        # Ensure download directory exists
        download_path = Path(channel.download_path)
        download_path.mkdir(parents=True, exist_ok=True)

        # Prepare output filename
        output_template = str(download_path / f"{task.video_id}.%(ext)s")

        # Configure yt-dlp options
        ydl_opts: yt_dlp._Params = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "outtmpl": output_template,
            "progress_hooks": [DownloadProgress(task_id, db)],
            "quiet": False,
            "no_warnings": False,
            "extract_flat": False,
            "writethumbnail": False,
            "writesubtitles": False,
            "writeautomaticsub": False,
            "postprocessors": [
                {
                    "key": "FFmpegVideoConvertor",
                    "preferedformat": "mp4",
                }
            ],
            "retries": 3,
            "fragment_retries": 3,
            "skip_unavailable_fragments": True,
        }

        # Download video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(task.video_url, download=True)

            # Get actual downloaded file path
            downloaded_file = ydl.prepare_filename(info)
            if not os.path.exists(downloaded_file):
                # Try with .mp4 extension
                downloaded_file = str(download_path / f"{task.video_id}.mp4")

            file_size = (
                os.path.getsize(downloaded_file)
                if os.path.exists(downloaded_file)
                else 0
            )

            # Calculate download duration
            end_time = datetime.now()
            download_duration = int((end_time - start_time).total_seconds())

            # Update task status to completed (completed_at is set automatically)
            download_repo.update_task_status(
                db,
                task.task_id,
                status="completed",
                progress_percent=100,
            )
            db.commit()

            # Create history record
            upload_date = None
            if info.get("upload_date"):
                try:
                    # Convert to datetime then format as ISO string
                    upload_date_dt = datetime.strptime(
                        info.get("upload_date", None), "%Y%m%d"
                    )
                    upload_date = upload_date_dt.strftime("%Y-%m-%d")
                except (ValueError, TypeError):
                    pass

            download_repo.create_history_record(
                db,
                channel_id=task.channel_id,
                video_id=task.video_id,
                video_title=info.get("title", "Unknown") or "Unknown",
                video_url=task.video_url,
                task_id=task.task_id,
                upload_date=upload_date,
                duration=info.get("duration"),
                file_path=downloaded_file,
                file_size=file_size,
                video_metadata=str(info) if info else None,
                download_duration_seconds=download_duration,
                success=True,
            )
            db.commit()

            logger.info(f"Download completed for task {task_id}: {downloaded_file}")
            return True

    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        logger.error(f"Download failed for task {task_id}: {error_msg}")

        if not task:
            print(
                f"No task found for task_id {task_id} during unexpected error handling."
            )
            db.close()
            return False
        # Update task status
        download_repo.update_task_status(
            db,
            task.task_id,
            status="failed",
            error_message=error_msg[:500],  # Limit error message length
        )

        # Increment retry count
        task = download_repo.get_task_by_task_id(db, task.task_id)
        if task:
            task.retry_count += 1

        db.commit()

        # Create failed history record
        end_time = datetime.now()
        download_duration = int((end_time - start_time).total_seconds())

        if not task:
            print(
                f"No task found for task_id {task_id} during unexpected error handling."
            )
            return False
        download_repo.create_history_record(
            db,
            channel_id=task.channel_id,
            video_id=task.video_id,
            video_title="Unknown",
            video_url=task.video_url,
            task_id=task.task_id,
            download_duration_seconds=download_duration,
            success=False,
            error_code="DOWNLOAD_ERROR",
        )
        db.commit()

        # Re-raise to trigger Huey retry
        raise

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(f"Unexpected error for task {task_id}: {error_msg}")

        try:
            if not task:
                print(
                    f"No task found for task_id {task_id} during unexpected error handling."
                )
                return False
            download_repo.update_task_status(
                db, task.task_id, status="failed", error_message=error_msg[:500]
            )

            # Increment retry count
            task = download_repo.get_task_by_task_id(db, task.task_id)
            if task:
                task.retry_count += 1

            db.commit()

            # Create failed history record
            end_time = datetime.now()
            download_duration = int((end_time - start_time).total_seconds())

            if not task:
                print(
                    f"No task found for task_id {task_id} during unexpected error handling."
                )
                return False

            download_repo.create_history_record(
                db,
                channel_id=task.channel_id,
                video_id=task.video_id,
                video_title="Unknown",
                video_url=task.video_url,
                task_id=task.task_id,
                download_duration_seconds=download_duration,
                success=False,
                error_code="UNEXPECTED_ERROR",
            )
            db.commit()
        except Exception as commit_error:
            logger.error(f"Failed to update task status: {commit_error}")

        return False

    finally:
        db.close()
