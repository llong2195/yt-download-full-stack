"""Test the check_downloads API endpoint."""

import sys
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base
from src.models.channel import Channel
from src.models.download_history import DownloadHistory
from src.repository import download_repo

# Add backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_check_downloads():
    """Test checking if videos are downloaded."""
    # Create in-memory database
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # Create a test channel
        channel = Channel(
            channel_id="UC_test_channel",
            title="Test Channel",
            name="Test Channel",
            url="https://youtube.com/@testchannel",
            download_path="./downloads",
        )
        db.add(channel)
        db.commit()
        db.refresh(channel)

        # Create some download history records
        history1 = DownloadHistory(
            channel_id=channel.id,
            video_id="dQw4w9WgXcQ",
            video_title="Test Video 1",
            video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            task_id="task-1",
            download_date=datetime.now(),
            download_duration_seconds=120,
            success=True,
            file_path="./downloads/test_video_1.mp4",
            file_size=1024000,
        )

        history2 = DownloadHistory(
            channel_id=channel.id,
            video_id="jNQXAC9IVRw",
            video_title="Test Video 2",
            video_url="https://www.youtube.com/watch?v=jNQXAC9IVRw",
            task_id="task-2",
            download_date=datetime.now(),
            download_duration_seconds=150,
            success=True,
            file_path="./downloads/test_video_2.mp4",
            file_size=2048000,
        )

        db.add(history1)
        db.add(history2)
        db.commit()

        # Test the repository function
        video_ids = ["dQw4w9WgXcQ", "jNQXAC9IVRw", "notdownloaded"]
        results = download_repo.check_videos_downloaded_by_ids(db, video_ids)

        print("\n=== Test Results ===")
        print(f"Checked {len(video_ids)} videos")
        print(f"\nResults:")

        for video_id in video_ids:
            record = results.get(video_id)
            if record:
                print(f"  ✓ {video_id}: Downloaded")
                print(f"    - Title: {record.video_title}")
                print(f"    - Path: {record.file_path}")
                print(f"    - Date: {record.download_date}")
            else:
                print(f"  ✗ {video_id}: Not downloaded")

        # Assertions
        assert results["dQw4w9WgXcQ"] is not None
        assert results["dQw4w9WgXcQ"].video_title == "Test Video 1"
        assert results["jNQXAC9IVRw"] is not None
        assert results["jNQXAC9IVRw"].video_title == "Test Video 2"
        assert results["notdownloaded"] is None

        print("\n✓ All tests passed!")

    finally:
        db.close()


if __name__ == "__main__":
    test_check_downloads()
