# Data Model: YouTube Downloader Full-Stack Application

**Feature**: [001-youtube-downloader](spec.md)  
**Date**: 2025-12-08  
**Purpose**: Define database schema and entity relationships

## Entity-Relationship Overview

```
Channel (1) ──────< (N) DownloadTask
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
- `download_path` (VARCHAR(2000), NOT NULL): Local filesystem path for this channel's videos (e.g., "downloads/UCx123...")
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
- `download_path` is created using channel_id: `downloads/{channel_id}/`
- Each channel has its own directory for organizing downloaded videos

---

### 2. DownloadTask

Represents a queued or active download operation (Huey task tracking).

**Attributes**:

- `id` (INTEGER, PK, AUTO INCREMENT): Internal database ID
- `task_id` (VARCHAR(36), UNIQUE, NOT NULL, INDEXED): Huey task UUID
- `channel_id` (INTEGER, FK → Channel.id, NOT NULL, INDEXED): Channel owning this video
- `video_id` (VARCHAR(11), NOT NULL, INDEXED): YouTube video ID (e.g., "dQw4w9WgXcQ")
- `video_url` (VARCHAR(1000), NOT NULL): Full YouTube video URL
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
- INDEX on `channel_id` (FK lookup)
- INDEX on `video_id` (for duplicate check)
- INDEX on `status` (for queue filtering)
- COMPOSITE INDEX on (`status`, `created_at`) for queue dashboard
- COMPOSITE INDEX on (`channel_id`, `video_id`) for duplicate detection

**Foreign Keys**:

- `channel_id` REFERENCES Channel(id) ON DELETE CASCADE

**Constraints**:

- `status` IN ('pending', 'downloading', 'completed', 'failed')
- `progress_percent` BETWEEN 0 AND 100
- `retry_count` >= 0 AND <= 3 (max retries)
- `completed_at` >= `started_at` (if both NOT NULL)
- `started_at` >= `created_at`
- `video_id` must match pattern: `^[a-zA-Z0-9_-]{11}$`

**Business Rules**:

- Only one active task per video_id (check before enqueueing)
- Tasks older than 24 hours with status=pending may be stale (cleanup job)
- `error_message` populated only if status=failed
- Video stored in channel's download_path directory
- Duplicate check: search for existing completed task with same video_id

---

### 3. DownloadHistory

Persistent record of all download attempts (audit log) with complete video information.

**Attributes**:

- `id` (INTEGER, PK, AUTO INCREMENT): Internal database ID
- `channel_id` (INTEGER, FK → Channel.id, NOT NULL, INDEXED): Channel owning this video
- `video_id` (VARCHAR(11), NOT NULL, INDEXED): YouTube video ID
- `video_title` (VARCHAR(500), NOT NULL): Video title at time of download
- `video_url` (VARCHAR(1000), NOT NULL): Full YouTube video URL
- `task_id` (VARCHAR(36), NULL, INDEXED): Reference to DownloadTask.task_id (may be cleaned up)
- `download_date` (DATETIME, NOT NULL, DEFAULT=CURRENT_TIMESTAMP): When download completed
- `upload_date` (DATE, NULL): When video was uploaded to YouTube
- `duration` (INTEGER, NULL): Video duration in seconds
- `file_path` (VARCHAR(2000), NULL): Local filesystem path (NULL if failed)
- `file_size` (BIGINT, NULL): Final file size in bytes (NULL if failed)
- `metadata` (JSON/TEXT, NULL): Additional metadata (resolution, format, codec, etc.)
- `download_duration_seconds` (INTEGER, NOT NULL): Time taken to download
- `success` (BOOLEAN, NOT NULL): True if completed successfully, False if failed
- `error_code` (VARCHAR(50), NULL): Error code if failed (e.g., "RATE_LIMIT", "VIDEO_UNAVAILABLE")

**Indexes**:

- PRIMARY KEY on `id`
- INDEX on `channel_id` (FK lookup)
- INDEX on `video_id` (for search and duplicate detection)
- INDEX on `download_date` DESC (recent downloads first)
- INDEX on `success` (filter by success/failure)
- COMPOSITE INDEX on (`channel_id`, `video_id`) for channel-specific video lookup
- COMPOSITE INDEX on (`video_id`, `download_date`) for video-specific history

**Foreign Keys**:

- `channel_id` REFERENCES Channel(id) ON DELETE CASCADE

**Constraints**:

- `file_size` >= 0 (if success=True)
- `download_duration_seconds` > 0
- `error_code` must be NOT NULL if success=False
- `file_path` must be NOT NULL if success=True
- `video_id` must match pattern: `^[a-zA-Z0-9_-]{11}$`
- `duration` >= 0 (if not NULL)

**Business Rules**:

- New record created for each download attempt (even retries)
- Used for analytics: success rate, average download time, etc.
- Never deleted (audit log) unless channel is deleted
- `task_id` may be NULL if DownloadTask is cleaned up (old tasks purged)
- Contains complete video information snapshot at download time
- `file_path` stored relative to channel's download_path
- Search by video title for finding downloaded videos

---

## Relationships

### Channel → DownloadTask (One-to-Many)

- One channel has many download tasks
- Deleting a channel cascades to delete all its tasks
- Business constraint: Only ONE task in 'pending' or 'downloading' status per video_id at a time
- Access pattern: "Show all active downloads for channel X"

### Channel → DownloadHistory (One-to-Many)

- One channel has many history records (audit trail)
- Deleting a channel cascades to delete all its download history
- Access pattern: "Show all downloaded videos for channel X", "Show download history with filters"

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
    download_path VARCHAR(2000) NOT NULL,
    date_added DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_updated DATETIME
);

CREATE INDEX idx_channels_channel_id ON channels(channel_id);
CREATE INDEX idx_channels_date_added ON channels(date_added);

CREATE TABLE download_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id VARCHAR(36) UNIQUE NOT NULL,
    channel_id INTEGER NOT NULL,
    video_id VARCHAR(11) NOT NULL,
    video_url VARCHAR(1000) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK(status IN ('pending', 'downloading', 'completed', 'failed')),
    progress_percent INTEGER DEFAULT 0 CHECK(progress_percent BETWEEN 0 AND 100),
    error_message TEXT,
    retry_count INTEGER DEFAULT 0 CHECK(retry_count BETWEEN 0 AND 3),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at DATETIME,
    completed_at DATETIME,
    FOREIGN KEY (channel_id) REFERENCES channels(id) ON DELETE CASCADE,
    CHECK (completed_at IS NULL OR started_at IS NOT NULL),
    CHECK (started_at IS NULL OR started_at >= created_at)
);

CREATE UNIQUE INDEX idx_tasks_task_id ON download_tasks(task_id);
CREATE INDEX idx_tasks_channel_id ON download_tasks(channel_id);
CREATE INDEX idx_tasks_video_id ON download_tasks(video_id);
CREATE INDEX idx_tasks_status ON download_tasks(status);
CREATE INDEX idx_tasks_status_created ON download_tasks(status, created_at);
CREATE INDEX idx_tasks_channel_video ON download_tasks(channel_id, video_id);

CREATE TABLE download_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_id INTEGER NOT NULL,
    video_id VARCHAR(11) NOT NULL,
    video_title VARCHAR(500) NOT NULL,
    video_url VARCHAR(1000) NOT NULL,
    task_id VARCHAR(36),
    download_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    upload_date DATE,
    duration INTEGER CHECK(duration >= 0),
    file_path VARCHAR(2000),
    file_size BIGINT CHECK(file_size >= 0),
    metadata TEXT,
    download_duration_seconds INTEGER NOT NULL CHECK(download_duration_seconds > 0),
    success BOOLEAN NOT NULL,
    error_code VARCHAR(50),
    FOREIGN KEY (channel_id) REFERENCES channels(id) ON DELETE CASCADE,
    CHECK ((success = 1 AND error_code IS NULL AND file_path IS NOT NULL) OR (success = 0 AND error_code IS NOT NULL))
);

CREATE INDEX idx_history_channel_id ON download_history(channel_id);
CREATE INDEX idx_history_video_id ON download_history(video_id);
CREATE INDEX idx_history_download_date ON download_history(download_date DESC);
CREATE INDEX idx_history_success ON download_history(success);
CREATE INDEX idx_history_channel_video ON download_history(channel_id, video_id);
CREATE INDEX idx_history_video_date ON download_history(video_id, download_date);
```

---

## SQLAlchemy Models (Python)

```python
# backend/models/database.py
from sqlalchemy import create_engine, Integer, String, DateTime, Boolean, BigInteger, Text, ForeignKey, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

Base = declarative_base()
engine = create_engine('sqlite:///data/app.db', echo=False)
SessionLocal = sessionmaker(bind=engine)

# backend/models/channel.py
class Channel(Base):
    __tablename__ = 'channels'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    channel_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    download_path: Mapped[str] = mapped_column(String(2000), nullable=False)
    date_added: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    last_updated: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    download_tasks = relationship("DownloadTask", back_populates="channel", cascade="all, delete-orphan")
    download_history = relationship("DownloadHistory", back_populates="channel", cascade="all, delete-orphan")

# backend/models/download_task.py
class DownloadTask(Base):
    __tablename__ = 'download_tasks'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, index=True)
    channel_id: Mapped[int] = mapped_column(Integer, ForeignKey('channels.id', ondelete='CASCADE'), nullable=False, index=True)
    video_id: Mapped[str] = mapped_column(String(11), nullable=False, index=True)
    video_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    progress_percent: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    channel = relationship("Channel", back_populates="download_tasks")

    __table_args__ = (
        CheckConstraint("status IN ('pending', 'downloading', 'completed', 'failed')", name='check_status'),
        CheckConstraint('progress_percent BETWEEN 0 AND 100', name='check_progress'),
        CheckConstraint('retry_count BETWEEN 0 AND 3', name='check_retry'),
    )

# backend/models/download_history.py
class DownloadHistory(Base):
    __tablename__ = 'download_history'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    channel_id: Mapped[int] = mapped_column(Integer, ForeignKey('channels.id', ondelete='CASCADE'), nullable=False, index=True)
    video_id: Mapped[str] = mapped_column(String(11), nullable=False, index=True)
    video_title: Mapped[str] = mapped_column(String(500), nullable=False)
    video_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    task_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    download_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    upload_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    duration: Mapped[int] = mapped_column(Integer, nullable=True)
    file_path: Mapped[str] = mapped_column(String(2000), nullable=True)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=True)
    metadata: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string
    download_duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    error_code: Mapped[str] = mapped_column(String(50), nullable=True)

    channel = relationship("Channel", back_populates="download_history")
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
  download_path: string;
  date_added: string; // ISO 8601 date string
  last_updated: string | null;
}

// web/src/types/download.ts
export interface DownloadTask {
  id: number;
  task_id: string;
  channel_id: number;
  video_id: string;
  video_url: string;
  status: "pending" | "downloading" | "completed" | "failed";
  progress_percent: number;
  error_message: string | null;
  retry_count: number;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
}

export interface VideoMetadata {
  resolution?: string;
  format?: string;
  codec?: string;
}

export interface DownloadHistory {
  id: number;
  channel_id: number;
  video_id: string;
  video_title: string;
  video_url: string;
  task_id: string | null;
  download_date: string;
  upload_date: string | null;
  duration: number | null;
  file_path: string | null;
  file_size: number | null;
  metadata: VideoMetadata | null;
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
- `download_path`: Must be relative path starting with `downloads/`

### DownloadTask

- `task_id`: Valid UUID v4
- `status`: One of enum values
- `progress_percent`: 0-100
- `retry_count`: 0-3

### DownloadHistory

- `video_id`: Regex `/^[a-zA-Z0-9_-]{11}$/`
- `video_title`: Max 500 characters
- `file_path`: Must be relative path within channel's download_path
- `file_size`: >= 0 (if success=true)
- `duration`: >= 0 seconds (if not NULL)
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

**Get all channels with download count**:

```python
session.query(Channel, func.count(DownloadHistory.id))\
    .outerjoin(DownloadHistory)\
    .filter(DownloadHistory.success == True)\
    .group_by(Channel.id)
```

**Check if video already downloaded**:

```python
session.query(DownloadHistory)\
    .filter(DownloadHistory.video_id == 'abc123', DownloadHistory.success == True)\
    .first()
```

**Get active downloads**:

```python
session.query(DownloadTask)\
    .filter(DownloadTask.status.in_(['pending', 'downloading']))\
    .all()
```

**Search history by video title**:

```python
session.query(DownloadHistory)\
    .filter(DownloadHistory.video_title.like(f'%{search_term}%'))\
    .order_by(DownloadHistory.download_date.desc())\
    .all()
```

**Get downloaded videos for a channel**:

```python
session.query(DownloadHistory)\
    .filter(DownloadHistory.channel_id == channel_id, DownloadHistory.success == True)\
    .order_by(DownloadHistory.download_date.desc())\
    .all()
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
