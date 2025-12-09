"""Huey background tasks for video downloads."""

import os
import re
import time
from datetime import datetime
from pathlib import Path

import yt_dlp
import yt_dlp.utils
from sqlalchemy.orm import Session
from src.models.database import SessionLocal
from src.models.download_task import DownloadTask
from src.repository import channel_repo, download_repo, settings_repo
from src.utils.logger import get_logger
from src.utils.validators import sanitize_filename

from .huey_instance import huey

logger = get_logger(__name__)


def strip_ansi_codes(text: str) -> str:
    """Remove ANSI escape sequences from text.

    Args:
        text: String potentially containing ANSI codes

    Returns:
        Clean string without ANSI codes
    """
    ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
    return ansi_escape.sub("", text)


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
                    # Get progress percentage from yt-dlp
                    percent_str = d.get("_percent_str", "0%")

                    # Remove ANSI color codes (e.g., \x1b[0;94m)
                    percent_str = strip_ansi_codes(str(percent_str))

                    # Clean up: remove %, spaces, and other non-numeric chars except decimal point
                    percent_str = percent_str.strip().replace("%", "").replace(" ", "")

                    # Parse to float then int
                    progress = int(float(percent_str))

                    # Clamp between 0-100
                    progress = max(0, min(100, progress))

                    download_repo.update_task_status(
                        self.db,
                        self.task_id,
                        status="downloading",
                        progress_percent=progress,
                    )
                    self.db.commit()
                    self.last_update = current_time

                except (ValueError, TypeError, KeyError) as e:
                    # Log with the actual problematic string for debugging
                    raw_percent = d.get("_percent_str", "N/A")
                    logger.warning(
                        f"Failed to parse progress: {e} "
                        f"(raw: {repr(raw_percent)}, cleaned: {repr(percent_str if 'percent_str' in locals() else 'N/A')})"
                    )

        elif d["status"] == "finished":
            logger.info(f"Download finished for task {self.task_id}")


@huey.task(retries=3, retry_delay=20)
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

        # Get channel info for download path and settings
        channel = channel_repo.get_channel_by_id(db, task.channel_id)
        if not channel:
            logger.error(f"Channel {task.channel_id} not found for task {task_id}")
            download_repo.update_task_status(
                db, task.task_id, status="failed", error_message="Channel not found"
            )
            db.commit()
            return False

        # Get global settings for fallback chain
        global_settings = settings_repo.get_settings(db)

        # Determine effective subtitle language (channel → global → None)
        subtitle_language = None
        if channel.subtitle_language:
            subtitle_language = channel.subtitle_language
        elif global_settings and global_settings.default_subtitle_language:
            subtitle_language = global_settings.default_subtitle_language

        # Determine effective video quality (channel → global → "best")
        video_quality = "best"
        if channel.video_quality:
            video_quality = channel.video_quality
        elif global_settings and global_settings.default_video_quality:
            video_quality = global_settings.default_video_quality

        logger.info(
            f"Download settings for task {task_id}: "
            f"quality={video_quality}, subtitles={subtitle_language or 'none'}"
        )

        # Update status to downloading (started_at is set automatically in update_task_status)
        download_repo.update_task_status(db, task.task_id, status="downloading")
        db.commit()

        logger.info(f"Starting download for task {task_id}: {task.video_url}")

        # Ensure download directory exists
        download_path = Path(channel.download_path)
        download_path.mkdir(parents=True, exist_ok=True)

        # Use video title as filename (sanitized)
        video_title = task.video_title
        base_filename = sanitize_filename(video_title)
        
        # Prepare output filename with numbering if file exists
        counter = 0
        final_filename = base_filename
        
        # Check if file already exists and generate unique name
        while True:
            test_path = download_path / f"{final_filename}.mp4"
            if not test_path.exists():
                break
            counter += 1
            final_filename = f"{base_filename} ({counter})"
            logger.info(f"File exists, trying with number: {final_filename}")
        
        output_template = str(download_path / f"{final_filename}.%(ext)s")
        logger.info(f"Output filename: {final_filename}.mp4")

        # Build format string based on video quality setting
        format_string = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
        if video_quality and video_quality != "best":
            # Map quality settings to yt-dlp format selectors
            if video_quality.endswith("p"):
                # Resolution-based (e.g., "1080p")
                height = video_quality[:-1]
                format_string = (
                    f"bestvideo[height<={height}][ext=mp4]+"
                    f"bestaudio[ext=m4a]/"
                    f"best[height<={height}][ext=mp4]/"
                    f"best[height<={height}]"
                )
            elif video_quality == "worst":
                format_string = "worstvideo[ext=mp4]+worstaudio[ext=m4a]/worst[ext=mp4]/worst"

        # Configure yt-dlp options
        ydl_opts: yt_dlp._Params = {
            "format": format_string,
            "outtmpl": output_template,
            "progress_hooks": [DownloadProgress(task_id, db)],
            "quiet": False,
            "no_warnings": False,
            "extract_flat": False,
            "writethumbnail": False,
            "writesubtitles": bool(subtitle_language),
            "writeautomaticsub": False,
            "subtitleslangs": [subtitle_language] if subtitle_language else [],
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

        if subtitle_language:
            logger.info(f"Requesting subtitles in language: {subtitle_language}")

        # Download video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(task.video_url, download=True)
                
                # Log if subtitles were available
                if subtitle_language:
                    available_subs = info.get("subtitles", {})
                    if subtitle_language not in available_subs:
                        logger.warning(
                            f"Requested subtitles ({subtitle_language}) not available "
                            f"for video {task.video_id}"
                        )
            except Exception as e:
                # Check if it's a quality/format error
                if "requested format not available" in str(e).lower():
                    logger.warning(
                        f"Requested quality ({video_quality}) not available, "
                        f"falling back to best available"
                    )
                    # Retry with best quality
                    ydl_opts["format"] = "best"
                    info = ydl.extract_info(task.video_url, download=True)
                else:
                    raise

            # Get actual downloaded file path
            downloaded_file = ydl.prepare_filename(info)
            if not os.path.exists(downloaded_file):
                # Try with the numbered filename we created
                downloaded_file = str(download_path / f"{final_filename}.mp4")

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
                    # Convert to datetime object (not string!)
                    # SQLite DateTime column requires Python datetime/date object
                    upload_date = datetime.strptime(
                        info.get("upload_date", None), "%Y%m%d"
                    )
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
