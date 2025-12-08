# Data Model: YouTube Downloader Full-Stack Application

**Feature**: [001-youtube-downloader](spec.md)  
**Date**: 2025-12-08  
**Purpose**: Define database schema and entity relationships

## Entity-Relationship Overview

```
Channel (1) ──────< (N) Video (1) ──────< (N) DownloadTask
                                   │
                                   └──────< (N) DownloadHistory
```

## Entities

### 1. Channel

Represents a YouTube channel tracked by the user.

**Attributes**:

- `id` (INTEGER, PK, AUTO INCREMENT): Internal database ID
- `channel_id` (VARCHAR(255), UNIQUE, NOT NULL, INDEXED): YouTube's channel ID (e.g., "UCx...")
- `name` (VARCHAR(500), NOT NULL): Display name of the channel
- `url` (VARCHAR(1000), NOT NULL): Full YouTube channel URL
- `date_added` (DATETIME, NOT NULL, DEFAULT=CURRENT_TIMESTAMP): When user added this channel
- `last_updated` (DATETIME, NULL): Last time channel metadata was refreshed

**Indexes**:

- PRIMARY KEY on `id`
- UNIQUE INDEX on `channel_id`
- INDEX on `date_added` (for recent channels query)

**Constraints**:

- `channel_id` must match pattern: `^UC[a-zA-Z0-9_-]{22}$` or `@[a-zA-Z0-9_-]+$`
- `url` must start with `https://www.youtube.com/`

**Business Rules**:

- Cannot have duplicate `channel_id` (same channel added twice)
- Soft delete not required (hard delete on user request)
- `name` can be updated if YouTube changes channel name

---

### 2. Video

Represents a YouTube video from a tracked channel.

**Attributes**:

- `id` (INTEGER, PK, AUTO INCREMENT): Internal database ID
- `video_id` (VARCHAR(11), UNIQUE, NOT NULL, INDEXED): YouTube's video ID (e.g., "dQw4w9WgXcQ")
- `channel_id` (INTEGER, FK → Channel.id, NOT NULL, INDEXED): Parent channel
- `title` (VARCHAR(500), NOT NULL): Video title
- `url` (VARCHAR(1000), NOT NULL): Full YouTube video URL
- `upload_date` (DATE, NULL): When video was uploaded to YouTube
- `duration` (INTEGER, NULL): Video duration in seconds
- `file_path` (VARCHAR(2000), NULL): Local filesystem path (NULL if not downloaded)
- `file_size` (BIGINT, NULL): File size in bytes (NULL if not downloaded)
- `metadata` (JSON/TEXT, NULL): Additional metadata (resolution, format, etc.)
- `date_added` (DATETIME, NOT NULL, DEFAULT=CURRENT_TIMESTAMP): When video was discovered

**Indexes**:

- PRIMARY KEY on `id`
- UNIQUE INDEX on `video_id`
- INDEX on `channel_id` (FK lookup)
- INDEX on `date_added` (for recent videos)

**Foreign Keys**:

- `channel_id` REFERENCES Channel(id) ON DELETE CASCADE

**Constraints**:

- `video_id` must match pattern: `^[a-zA-Z0-9_-]{11}$`
- `duration` >= 0
- `file_size` >= 0
- `file_path` must be absolute path starting with `/var/downloads/` or `downloads/`

**Business Rules**:

- `file_path` and `file_size` are NULL until download completes
- If channel is deleted, all associated videos are deleted (CASCADE)
- `metadata` stored as JSON string: `{"resolution": "1080p", "format": "mp4"}`

---

### 3. DownloadTask

Represents a queued or active download operation (Huey task tracking).

**Attributes**:

- `id` (INTEGER, PK, AUTO INCREMENT): Internal database ID
- `task_id` (VARCHAR(36), UNIQUE, NOT NULL, INDEXED): Huey task UUID
- `video_id` (INTEGER, FK → Video.id, NOT NULL, INDEXED): Video being downloaded
- `status` (ENUM/VARCHAR(20), NOT NULL, INDEXED): Task status
  - Values: `pending`, `downloading`, `completed`, `failed`
- `progress_percent` (INTEGER, DEFAULT=0): Download progress (0-100)
- `error_message` (TEXT, NULL): Error details if status=failed
- `retry_count` (INTEGER, DEFAULT=0): Number of retry attempts
- `created_at` (DATETIME, NOT NULL, DEFAULT=CURRENT_TIMESTAMP): Task creation time
- `started_at` (DATETIME, NULL): When download actually started
- `completed_at` (DATETIME, NULL): When download finished (success or failure)

**Indexes**:

- PRIMARY KEY on `id`
- UNIQUE INDEX on `task_id`
- INDEX on `video_id` (FK lookup)
- INDEX on `status` (for queue filtering)
- COMPOSITE INDEX on (`status`, `created_at`) for queue dashboard

**Foreign Keys**:

- `video_id` REFERENCES Video(id) ON DELETE CASCADE

**Constraints**:

- `status` IN ('pending', 'downloading', 'completed', 'failed')
- `progress_percent` BETWEEN 0 AND 100
- `retry_count` >= 0 AND <= 3 (max retries)
- `completed_at` >= `started_at` (if both NOT NULL)
- `started_at` >= `created_at`

**Business Rules**:

- Only one active task per video (check before enqueueing)
- Tasks older than 24 hours with status=pending may be stale (cleanup job)
- `error_message` populated only if status=failed
- Task marked `completed` when status=completed AND Video.file_path IS NOT NULL

---

### 4. DownloadHistory

Persistent record of all download attempts (audit log).

**Attributes**:

- `id` (INTEGER, PK, AUTO INCREMENT): Internal database ID
- `video_id` (INTEGER, FK → Video.id, NOT NULL, INDEXED): Downloaded video
- `task_id` (VARCHAR(36), NULL, INDEXED): Reference to DownloadTask.task_id (may be cleaned up)
- `download_date` (DATETIME, NOT NULL, DEFAULT=CURRENT_TIMESTAMP): When download completed
- `file_size` (BIGINT, NOT NULL): Final file size in bytes
- `download_duration_seconds` (INTEGER, NOT NULL): Time taken to download
- `success` (BOOLEAN, NOT NULL): True if completed successfully, False if failed
- `error_code` (VARCHAR(50), NULL): Error code if failed (e.g., "RATE_LIMIT", "VIDEO_UNAVAILABLE")

**Indexes**:

- PRIMARY KEY on `id`
- INDEX on `video_id` (FK lookup, for history page)
- INDEX on `download_date` DESC (recent downloads first)
- INDEX on `success` (filter by success/failure)
- COMPOSITE INDEX on (`video_id`, `download_date`) for video-specific history

**Foreign Keys**:

- `video_id` REFERENCES Video(id) ON DELETE CASCADE

**Constraints**:

- `file_size` >= 0
- `download_duration_seconds` > 0
- `error_code` must be NOT NULL if success=False

**Business Rules**:

- New record created for each download attempt (even retries)
- Used for analytics: success rate, average download time, etc.
- Never deleted (audit log) unless video is deleted
- `task_id` may be NULL if DownloadTask is cleaned up (old tasks purged)

---

## Relationships

### Channel → Video (One-to-Many)

- One channel has many videos
- Deleting a channel cascades to delete all its videos
- Access pattern: "Show all videos for channel X"

### Video → DownloadTask (One-to-Many)

- One video can have multiple tasks (retries, re-downloads)
- Deleting a video cascades to delete associated tasks
- Business constraint: Only ONE task in 'pending' or 'downloading' status per video at a time
- Access pattern: "Get active download for video Y"

### Video → DownloadHistory (One-to-Many)

- One video can have multiple history records (audit trail)
- Deleting a video cascades to delete history
- Access pattern: "Show download history for video Z", "Show all downloads from date range"

---

## Database Initialization

### SQLite Schema (SQL)

```sql
-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- Enable WAL mode for concurrency
PRAGMA journal_mode = WAL;
PRAGMA busy_timeout = 10000;

CREATE TABLE channels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(500) NOT NULL,
    url VARCHAR(1000) NOT NULL,
    date_added DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_updated DATETIME
);

CREATE INDEX idx_channels_channel_id ON channels(channel_id);
CREATE INDEX idx_channels_date_added ON channels(date_added);

CREATE TABLE videos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id VARCHAR(11) UNIQUE NOT NULL,
    channel_id INTEGER NOT NULL,
    title VARCHAR(500) NOT NULL,
    url VARCHAR(1000) NOT NULL,
    upload_date DATE,
    duration INTEGER,
    file_path VARCHAR(2000),
    file_size BIGINT,
    metadata TEXT,
    date_added DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (channel_id) REFERENCES channels(id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX idx_videos_video_id ON videos(video_id);
CREATE INDEX idx_videos_channel_id ON videos(channel_id);
CREATE INDEX idx_videos_date_added ON videos(date_added);

CREATE TABLE download_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id VARCHAR(36) UNIQUE NOT NULL,
    video_id INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL CHECK(status IN ('pending', 'downloading', 'completed', 'failed')),
    progress_percent INTEGER DEFAULT 0 CHECK(progress_percent BETWEEN 0 AND 100),
    error_message TEXT,
    retry_count INTEGER DEFAULT 0 CHECK(retry_count BETWEEN 0 AND 3),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at DATETIME,
    completed_at DATETIME,
    FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE CASCADE,
    CHECK (completed_at IS NULL OR started_at IS NOT NULL),
    CHECK (started_at IS NULL OR started_at >= created_at)
);

CREATE UNIQUE INDEX idx_tasks_task_id ON download_tasks(task_id);
CREATE INDEX idx_tasks_video_id ON download_tasks(video_id);
CREATE INDEX idx_tasks_status ON download_tasks(status);
CREATE INDEX idx_tasks_status_created ON download_tasks(status, created_at);

CREATE TABLE download_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id INTEGER NOT NULL,
    task_id VARCHAR(36),
    download_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    file_size BIGINT NOT NULL CHECK(file_size >= 0),
    download_duration_seconds INTEGER NOT NULL CHECK(download_duration_seconds > 0),
    success BOOLEAN NOT NULL,
    error_code VARCHAR(50),
    FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE CASCADE,
    CHECK ((success = 1 AND error_code IS NULL) OR (success = 0 AND error_code IS NOT NULL))
);

CREATE INDEX idx_history_video_id ON download_history(video_id);
CREATE INDEX idx_history_download_date ON download_history(download_date DESC);
CREATE INDEX idx_history_success ON download_history(success);
CREATE INDEX idx_history_video_date ON download_history(video_id, download_date);
```

---

## SQLAlchemy Models (Python)

```python
# backend/models/database.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, BigInteger, Text, ForeignKey, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

Base = declarative_base()
engine = create_engine('sqlite:///data/app.db', echo=False)
SessionLocal = sessionmaker(bind=engine)

# backend/models/channel.py
class Channel(Base):
    __tablename__ = 'channels'

    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=False)
    date_added = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_updated = Column(DateTime, nullable=True)

    videos = relationship("Video", back_populates="channel", cascade="all, delete-orphan")

# backend/models/video.py
class Video(Base):
    __tablename__ = 'videos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(String(11), unique=True, nullable=False, index=True)
    channel_id = Column(Integer, ForeignKey('channels.id', ondelete='CASCADE'), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=False)
    upload_date = Column(DateTime, nullable=True)
    duration = Column(Integer, nullable=True)
    file_path = Column(String(2000), nullable=True)
    file_size = Column(BigInteger, nullable=True)
    metadata = Column(Text, nullable=True)  # JSON string
    date_added = Column(DateTime, nullable=False, default=datetime.utcnow)

    channel = relationship("Channel", back_populates="videos")
    download_tasks = relationship("DownloadTask", back_populates="video", cascade="all, delete-orphan")
    download_history = relationship("DownloadHistory", back_populates="video", cascade="all, delete-orphan")

# backend/models/download_task.py
class DownloadTask(Base):
    __tablename__ = 'download_tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(36), unique=True, nullable=False, index=True)
    video_id = Column(Integer, ForeignKey('videos.id', ondelete='CASCADE'), nullable=False, index=True)
    status = Column(String(20), nullable=False, index=True)
    progress_percent = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    video = relationship("Video", back_populates="download_tasks")

    __table_args__ = (
        CheckConstraint("status IN ('pending', 'downloading', 'completed', 'failed')", name='check_status'),
        CheckConstraint('progress_percent BETWEEN 0 AND 100', name='check_progress'),
        CheckConstraint('retry_count BETWEEN 0 AND 3', name='check_retry'),
    )

# backend/models/download_history.py
class DownloadHistory(Base):
    __tablename__ = 'download_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(Integer, ForeignKey('videos.id', ondelete='CASCADE'), nullable=False, index=True)
    task_id = Column(String(36), nullable=True, index=True)
    download_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    file_size = Column(BigInteger, nullable=False)
    download_duration_seconds = Column(Integer, nullable=False)
    success = Column(Boolean, nullable=False)
    error_code = Column(String(50), nullable=True)

    video = relationship("Video", back_populates="download_history")
```

---

## TypeScript Interfaces (Frontend)

```typescript
// web/src/types/channel.ts
export interface Channel {
  id: number;
  channel_id: string;
  name: string;
  url: string;
  date_added: string; // ISO 8601 date string
  last_updated: string | null;
}

// web/src/types/video.ts
export interface Video {
  id: number;
  video_id: string;
  channel_id: number;
  title: string;
  url: string;
  upload_date: string | null;
  duration: number | null;
  file_path: string | null;
  file_size: number | null;
  metadata: VideoMetadata | null;
  date_added: string;
}

export interface VideoMetadata {
  resolution?: string;
  format?: string;
  codec?: string;
}

// web/src/types/download.ts
export interface DownloadTask {
  id: number;
  task_id: string;
  video_id: number;
  status: "pending" | "downloading" | "completed" | "failed";
  progress_percent: number;
  error_message: string | null;
  retry_count: number;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
}

export interface DownloadHistory {
  id: number;
  video_id: number;
  task_id: string | null;
  download_date: string;
  file_size: number;
  download_duration_seconds: number;
  success: boolean;
  error_code: string | null;
}
```

---

## Validation Rules

### Channel

- `channel_id`: Regex `/^(UC[a-zA-Z0-9_-]{22}|@[a-zA-Z0-9_-]+)$/`
- `url`: Must start with `https://www.youtube.com/`
- `name`: Max 500 characters

### Video

- `video_id`: Regex `/^[a-zA-Z0-9_-]{11}$/`
- `url`: Must start with `https://www.youtube.com/watch?v=` or `https://youtu.be/`
- `title`: Max 500 characters
- `file_path`: Must be absolute, start with approved download directory
- `duration`: >= 0 seconds

### DownloadTask

- `task_id`: Valid UUID v4
- `status`: One of enum values
- `progress_percent`: 0-100
- `retry_count`: 0-3

### DownloadHistory

- `file_size`: > 0 (actual download occurred)
- `download_duration_seconds`: > 0
- `error_code`: Required if success=false

---

## Migration Strategy

**Initial Setup**: Run `Base.metadata.create_all(engine)` in `backend/models/database.py`

**Future Migrations**: Use Alembic for schema changes

- Add alembic.ini configuration
- Generate migrations: `alembic revision --autogenerate -m "description"`
- Apply migrations: `alembic upgrade head`

---

## Query Patterns

### Common Queries

**Get all channels with video count**:

```python
session.query(Channel, func.count(Video.id)).join(Video).group_by(Channel.id)
```

**Check if video already downloaded**:

```python
session.query(Video).filter(Video.video_id == 'abc123', Video.file_path.isnot(None)).first()
```

**Get active downloads**:

```python
session.query(DownloadTask).filter(DownloadTask.status.in_(['pending', 'downloading'])).all()
```

**Search history**:

```python
session.query(DownloadHistory).join(Video).filter(Video.title.like(f'%{search_term}%')).all()
```

---

## Performance Considerations

- **Indexes**: All foreign keys indexed, common query fields indexed
- **Pagination**: Use LIMIT/OFFSET for history queries (1000+ records)
- **Caching**: Consider caching channel list (changes infrequently)
- **Cleanup**: Periodic job to delete old completed tasks (>30 days)
- **WAL Mode**: Enables concurrent reads during writes
- **Connection Pooling**: StaticPool for SQLite prevents "database locked" errors

---

## Data Integrity

- Foreign key constraints enforced
- Check constraints on enums and ranges
- Unique constraints prevent duplicates
- Cascade deletes maintain referential integrity
- Transactions ensure atomic operations
