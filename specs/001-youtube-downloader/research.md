# Research: YouTube Downloader Full-Stack Application

**Feature**: [001-youtube-downloader](spec.md)  
**Date**: 2025-12-08  
**Purpose**: Resolve technical unknowns and document architectural decisions

## Research Items

### 1. Frontend Testing Framework Selection

**Question**: Testing framework for React frontend - Vitest vs Jest?

**Decision**: **Vitest**

**Rationale**:

- Native Vite integration (already using Vite for build)
- Faster execution than Jest (ESM-first, no transpilation)
- Same API as Jest (easy migration if needed)
- Better TypeScript support out of the box
- Recommended by Vite ecosystem

**Alternatives Considered**:

- **Jest**: More mature, larger community, but requires additional configuration for Vite + TypeScript + ESM
- **React Testing Library**: Still used with Vitest for component testing (not mutually exclusive)

**Implementation Notes**:

- Install: `pnpm add -D vitest @testing-library/react @testing-library/jest-dom jsdom`
- Configure in `vite.config.ts` with jsdom environment
- Use React Testing Library for component tests

---

### 2. Huey Configuration with FastAPI

**Question**: How to integrate Huey task queue within FastAPI process (no separate consumer)?

**Decision**: **Use immediate mode or embedded consumer thread**

**Rationale**:

- Constitution requires Huey runs "within backend, no separate script"
- Two approaches:
  1. **Immediate mode** (`immediate=True` for development) - tasks run synchronously
  2. **Consumer thread** - Start Huey consumer in FastAPI lifespan startup event

**Recommended Approach**: Consumer thread in production, immediate mode in dev

```python
# main.py example structure
from huey import SqliteHuey
from contextlib import asynccontextmanager

huey = SqliteHuey(filename='data/huey.db')

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start Huey consumer in background thread
    consumer_thread = Thread(target=huey.start, daemon=True)
    consumer_thread.start()
    yield
    # Cleanup on shutdown
    huey.stop()

app = FastAPI(lifespan=lifespan)
```

**Alternatives Considered**:

- **Separate process**: Violates constitution requirement
- **Celery**: Overkill, requires Redis/RabbitMQ, violates minimal dependencies

**Implementation Notes**:

- Use SQLite storage for Huey: `SqliteHuey(filename='data/huey.db')`
- Configure retries: `@huey.task(retries=3, retry_delay=60)`
- Exponential backoff via custom retry logic in task

---

### 3. yt-dlp Integration Best Practices

**Question**: How to properly invoke yt-dlp from Python with error handling and progress tracking?

**Decision**: **Use yt-dlp Python library (not CLI), with custom progress hooks**

**Rationale**:

- Python library provides better error handling than subprocess CLI
- Progress hooks enable real-time status updates
- Returns structured metadata (title, duration, file size)
- Exception handling for rate limiting, geo-blocking, etc.

**Implementation Pattern**:

```python
import yt_dlp

def download_video(video_url: str, output_dir: str):
    ydl_opts = {
        'format': 'best',
        'outtmpl': f'{output_dir}/%(id)s-%(title)s.%(ext)s',
        'progress_hooks': [progress_callback],
        'quiet': False,
        'no_warnings': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            return {
                'title': info['title'],
                'duration': info['duration'],
                'file_size': info.get('filesize') or info.get('filesize_approx'),
                'file_path': ydl.prepare_filename(info)
            }
    except yt_dlp.utils.DownloadError as e:
        # Handle rate limiting, geo-block, unavailable video
        raise
```

**Edge Cases to Handle**:

- Rate limiting (HTTP 429) → retry with exponential backoff
- Geo-restricted videos → log and mark as failed with clear message
- Age-restricted videos → may require authentication (out of scope for MVP)
- Video removed/unavailable → mark as failed, don't retry
- Disk space exhaustion → catch OSError, clear task queue, alert user

**Implementation Notes**:

- Install: `pip install yt-dlp`
- Update yt-dlp regularly: `yt-dlp -U` (YouTube changes frequently)
- Progress hooks update database with download percentage

---

### 4. SQLite Concurrency & Locking Strategy

**Question**: How to handle concurrent access to SQLite from FastAPI (multiple requests) and Huey tasks?

**Decision**: **WAL mode + connection pooling + row-level locking**

**Rationale**:

- SQLite default mode blocks readers during writes
- WAL (Write-Ahead Logging) enables concurrent reads during writes
- Connection pooling prevents "database is locked" errors
- Row-level locking for download status updates

**Configuration**:

```python
# models/database.py
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

engine = create_engine(
    'sqlite:///data/app.db',
    connect_args={
        'check_same_thread': False,  # Allow multi-threading
        'timeout': 10,  # Wait 10s for lock before failing
    },
    poolclass=StaticPool,  # Single connection for SQLite
    echo=False
)

# Enable WAL mode
with engine.connect() as conn:
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=10000")
```

**Best Practices**:

- Short transactions - commit quickly
- Avoid long-running queries in transactions
- Use `with_for_update()` for row-level locking when updating download status
- Separate read-only queries (no transaction needed)

**Alternatives Considered**:

- **PostgreSQL**: Overkill for single-user MVP, violates simplicity
- **File locking**: Manual locking is error-prone, SQLite handles this

**Implementation Notes**:

- Add indexes on: `video.video_id`, `channel.channel_id`, `download_task.status`
- Vacuum database periodically to reclaim space

---

### 5. Real-Time Queue Status Updates

**Question**: How to implement real-time updates (polling vs WebSocket)?

**Decision**: **HTTP Polling (2-3 second interval)**

**Rationale**:

- Simpler than WebSocket (no additional connection management)
- Matches constitution's simplicity principle
- Acceptable latency for download monitoring (not millisecond-critical)
- Works with any HTTP server (static deployment requirement)
- No additional dependencies

**Implementation**:

```typescript
// Frontend polling
useEffect(() => {
  const interval = setInterval(async () => {
    const status = await fetchQueueStatus();
    setQueueData(status);
  }, 2500); // 2.5 seconds

  return () => clearInterval(interval);
}, []);
```

**Alternatives Considered**:

- **WebSocket**: More complex, requires persistent connection, harder to deploy
- **Server-Sent Events (SSE)**: One-way only, still requires persistent connection
- **Long polling**: More complex than simple polling, marginal benefit

**Implementation Notes**:

- Backend endpoint: `GET /api/queue/status` returns all active tasks
- Stop polling when user leaves page (cleanup in useEffect)
- Show "last updated" timestamp to user

---

### 6. CORS Configuration for Chrome Extension

**Question**: What CORS settings needed for Chrome extension integration?

**Decision**: **Allow specific origin with credentials support**

**Rationale**:

- Chrome extensions run from `chrome-extension://` protocol
- Need explicit CORS headers for cross-origin requests
- Allow all methods (GET, POST, PUT, DELETE) for REST API

**Configuration**:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "chrome-extension://*",   # Chrome extension (wildcard)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Security Notes**:

- For MVP: Allow all chrome-extension origins (no auth yet)
- Future: Add authentication token, restrict to specific extension ID
- Production: Replace localhost with actual domain

**Implementation Notes**:

- Extension manifest needs `host_permissions` for API domain
- Handle preflight OPTIONS requests automatically via FastAPI middleware

---

### 7. File Storage & Path Sanitization

**Question**: How to safely store downloaded videos and prevent path traversal attacks?

**Decision**: **Dedicated downloads directory with UUID-based subdirectories**

**Rationale**:

- Never trust user input (video titles may contain `../`, special chars)
- UUID ensures unique storage, prevents collisions
- Store original filename in database, not filesystem

**Implementation Pattern**:

```python
import uuid
from pathlib import Path

def safe_download_path(video_id: str, title: str) -> Path:
    # Base directory (outside web root)
    base_dir = Path('/var/downloads') or Path('downloads/')

    # Create subdirectory using first 2 chars of video_id for sharding
    shard = video_id[:2]
    video_dir = base_dir / shard / video_id
    video_dir.mkdir(parents=True, exist_ok=True)

    # Sanitize filename but use UUID as primary identifier
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_'))
    safe_title = safe_title[:100]  # Limit length

    return video_dir / f"{video_id}-{safe_title}.mp4"
```

**Security Measures**:

- Never use raw video title as filename
- Check file size before saving (reject >5GB as likely error)
- Verify disk space before starting download
- Store absolute paths in database, never relative

**Implementation Notes**:

- Add disk space check in download service before enqueueing task
- Log full paths for debugging but never expose to frontend
- Frontend shows video title, not filesystem path

---

### 8. Error Handling & User Feedback Strategy

**Question**: How to provide clear, actionable error messages to users?

**Decision**: **Structured error responses with user-friendly messages + technical details**

**Rationale**:

- Users need actionable feedback (e.g., "Video is private" not "HTTP 403")
- Developers need technical details for debugging
- Separate user-facing messages from logs

**Error Response Format**:

```typescript
interface APIError {
  error_code: string; // Machine-readable: "VIDEO_UNAVAILABLE"
  user_message: string; // User-friendly: "This video is unavailable"
  technical_details?: string; // Optional: for developers
  retry_possible: boolean; // Can user retry?
}
```

**Implementation**:

```python
class DownloadException(Exception):
    def __init__(self, error_code: str, user_message: str,
                 technical_details: str = None, retry_possible: bool = False):
        self.error_code = error_code
        self.user_message = user_message
        self.technical_details = technical_details
        self.retry_possible = retry_possible
```

**Common Error Scenarios**:

- **Rate limiting**: "Too many requests. Try again in 15 minutes." (retry_possible=True)
- **Invalid URL**: "Please enter a valid YouTube video URL." (retry_possible=False)
- **Disk full**: "Not enough storage space. Free up space and retry." (retry_possible=True)
- **Video unavailable**: "Video is private, deleted, or region-locked." (retry_possible=False)

**Implementation Notes**:

- Log technical details to file with full stack trace
- Return user_message in API response (400/500 status codes)
- Show retry button in UI only if retry_possible=True

---

## Summary of Decisions

| Research Area      | Decision                                    | Key Rationale                               |
| ------------------ | ------------------------------------------- | ------------------------------------------- |
| Frontend Testing   | Vitest                                      | Native Vite integration, faster than Jest   |
| Huey Integration   | Consumer thread in FastAPI lifespan         | Meets "no separate process" requirement     |
| yt-dlp Usage       | Python library with progress hooks          | Better error handling than CLI              |
| SQLite Concurrency | WAL mode + connection pooling               | Prevents locking, enables concurrent reads  |
| Real-time Updates  | HTTP polling (2.5s interval)                | Simpler than WebSocket, meets requirements  |
| CORS               | Allow chrome-extension:// origins           | Enables extension integration               |
| File Storage       | UUID-based subdirectories                   | Prevents path traversal, ensures uniqueness |
| Error Handling     | Structured responses with user/dev messages | Clear feedback + debuggability              |

## Next Steps

All NEEDS CLARIFICATION items resolved. Ready for Phase 1: Data Model & Contracts design.
