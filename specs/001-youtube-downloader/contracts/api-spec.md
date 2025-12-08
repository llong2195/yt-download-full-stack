# API Contracts: YouTube Downloader Full-Stack Application

**Feature**: [001-youtube-downloader](../spec.md)  
**Date**: 2025-12-08  
**Purpose**: Define REST API endpoints, request/response schemas, and error codes

## Base Configuration

- **Base URL**: `http://localhost:8000` (development), `https://api.yourdomain.com` (production)
- **API Prefix**: `/api`
- **Content-Type**: `application/json`
- **Authentication**: None (MVP), future: Bearer token
- **CORS**: Enabled for `http://localhost:5173` and `chrome-extension://*`

---

## Endpoints

### 1. Channels API

#### `GET /api/channels`

Get all tracked channels.

**Request**:

```
GET /api/channels
```

**Response** (200 OK):

```json
{
  "channels": [
    {
      "id": 1,
      "channel_id": "UC1234567890abcdefghijk",
      "name": "Example Channel",
      "url": "https://www.youtube.com/@examplechannel",
      "date_added": "2025-12-08T10:30:00Z",
      "last_updated": "2025-12-08T12:00:00Z",
      "video_count": 42
    }
  ],
  "total": 1
}
```

---

#### `POST /api/channels`

Add a new channel.

**Request**:

```json
{
  "url": "https://www.youtube.com/@examplechannel"
}
```

**Validation**:

- `url` required, must be valid YouTube channel URL
- `url` patterns: `https://www.youtube.com/@channelname` or `https://www.youtube.com/channel/UC...`

**Response** (201 Created):

```json
{
  "id": 1,
  "channel_id": "UC1234567890abcdefghijk",
  "name": "Example Channel",
  "url": "https://www.youtube.com/@examplechannel",
  "date_added": "2025-12-08T10:30:00Z",
  "last_updated": null,
  "video_count": 0
}
```

**Errors**:

- `400 Bad Request`: Invalid URL format
  ```json
  {
    "error_code": "INVALID_URL",
    "user_message": "Please enter a valid YouTube channel URL",
    "technical_details": "URL must match pattern: https://www.youtube.com/@... or /channel/UC..."
  }
  ```
- `409 Conflict`: Channel already exists
  ```json
  {
    "error_code": "CHANNEL_EXISTS",
    "user_message": "This channel is already in your list",
    "technical_details": "channel_id UC1234... already exists in database"
  }
  ```
- `422 Unprocessable Entity`: Channel not found on YouTube
  ```json
  {
    "error_code": "CHANNEL_NOT_FOUND",
    "user_message": "Could not find this YouTube channel. Please check the URL.",
    "technical_details": "yt-dlp returned: Channel does not exist"
  }
  ```

---

#### `DELETE /api/channels/{channel_id}`

Remove a channel and all associated data.

**Request**:

```
DELETE /api/channels/1
```

**Response** (204 No Content): Empty body

**Errors**:

- `404 Not Found`: Channel doesn't exist
  ```json
  {
    "error_code": "CHANNEL_NOT_FOUND",
    "user_message": "Channel not found",
    "technical_details": "No channel with id=1"
  }
  ```

---

### 2. Videos API

#### `GET /api/channels/{channel_id}/videos`

Get all videos for a specific channel.

**Request**:

```
GET /api/channels/1/videos?limit=50&offset=0
```

**Query Parameters**:

- `limit` (optional, default=50): Number of results
- `offset` (optional, default=0): Pagination offset

**Response** (200 OK):

```json
{
  "videos": [
    {
      "id": 1,
      "video_id": "dQw4w9WgXcQ",
      "channel_id": 1,
      "title": "Example Video Title",
      "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
      "upload_date": "2025-12-01",
      "duration": 212,
      "file_path": "/var/downloads/dQ/dQw4w9WgXcQ-example-video.mp4",
      "file_size": 52428800,
      "metadata": {
        "resolution": "1080p",
        "format": "mp4"
      },
      "date_added": "2025-12-08T10:30:00Z",
      "is_downloaded": true
    }
  ],
  "total": 100,
  "limit": 50,
  "offset": 0
}
```

**Errors**:

- `404 Not Found`: Channel doesn't exist

---

#### `POST /api/videos/fetch`

Fetch latest videos from a channel (without downloading).

**Request**:

```json
{
  "channel_id": 1,
  "max_results": 10
}
```

**Validation**:

- `channel_id` required, must exist
- `max_results` optional, default=10, max=50

**Response** (200 OK):

```json
{
  "videos_found": 10,
  "new_videos": 5,
  "videos": [
    {
      "id": 2,
      "video_id": "abc123xyz",
      "title": "New Video",
      "url": "https://www.youtube.com/watch?v=abc123xyz",
      "upload_date": "2025-12-07",
      "duration": 360,
      "date_added": "2025-12-08T14:00:00Z",
      "is_downloaded": false
    }
  ]
}
```

---

### 3. Downloads API

#### `POST /api/downloads`

Request a video download (enqueues task).

**Request**:

```json
{
  "video_id": "dQw4w9WgXcQ"
}
```

**Validation**:

- `video_id` required, must be valid YouTube video ID (11 chars)

**Response** (202 Accepted):

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "video_id": "dQw4w9WgXcQ",
  "status": "pending",
  "message": "Download queued successfully"
}
```

**Errors**:

- `400 Bad Request`: Invalid video ID
- `409 Conflict`: Download already exists
  ```json
  {
    "error_code": "ALREADY_DOWNLOADED",
    "user_message": "This video has already been downloaded",
    "technical_details": "file_path exists: /var/downloads/...",
    "retry_possible": false
  }
  ```
- `409 Conflict`: Download already in progress
  ```json
  {
    "error_code": "DOWNLOAD_IN_PROGRESS",
    "user_message": "This video is already being downloaded",
    "technical_details": "task_id 550e8400... status=downloading",
    "retry_possible": false
  }
  ```

---

#### `POST /api/downloads/batch`

Request multiple video downloads at once.

**Request**:

```json
{
  "video_ids": ["dQw4w9WgXcQ", "abc123xyz", "def456uvw"]
}
```

**Validation**:

- `video_ids` required, array of 1-50 video IDs
- Each video_id must be valid format

**Response** (202 Accepted):

```json
{
  "total_requested": 3,
  "queued": 2,
  "skipped": 1,
  "tasks": [
    {
      "video_id": "dQw4w9WgXcQ",
      "task_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "pending"
    },
    {
      "video_id": "abc123xyz",
      "task_id": "660e8400-e29b-41d4-a716-446655440001",
      "status": "pending"
    }
  ],
  "skipped_videos": [
    {
      "video_id": "def456uvw",
      "reason": "Already downloaded"
    }
  ]
}
```

---

### 4. Queue API

#### `GET /api/queue/status`

Get current queue status (all active and pending tasks).

**Request**:

```
GET /api/queue/status
```

**Response** (200 OK):

```json
{
  "queue_summary": {
    "pending": 5,
    "downloading": 2,
    "completed_today": 10,
    "failed_today": 1
  },
  "active_tasks": [
    {
      "id": 1,
      "task_id": "550e8400-e29b-41d4-a716-446655440000",
      "video_id": "dQw4w9WgXcQ",
      "video_title": "Example Video",
      "status": "downloading",
      "progress_percent": 45,
      "created_at": "2025-12-08T14:00:00Z",
      "started_at": "2025-12-08T14:00:05Z",
      "estimated_completion": "2025-12-08T14:05:00Z"
    },
    {
      "id": 2,
      "task_id": "660e8400-e29b-41d4-a716-446655440001",
      "video_id": "abc123xyz",
      "video_title": "Another Video",
      "status": "pending",
      "progress_percent": 0,
      "created_at": "2025-12-08T14:01:00Z",
      "started_at": null,
      "estimated_completion": null
    }
  ]
}
```

---

#### `GET /api/queue/tasks/{task_id}`

Get status of a specific task.

**Request**:

```
GET /api/queue/tasks/550e8400-e29b-41d4-a716-446655440000
```

**Response** (200 OK):

```json
{
  "id": 1,
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "video_id": "dQw4w9WgXcQ",
  "video_title": "Example Video",
  "status": "downloading",
  "progress_percent": 45,
  "error_message": null,
  "retry_count": 0,
  "created_at": "2025-12-08T14:00:00Z",
  "started_at": "2025-12-08T14:00:05Z",
  "completed_at": null
}
```

**Errors**:

- `404 Not Found`: Task doesn't exist

---

#### `POST /api/queue/tasks/{task_id}/retry`

Retry a failed download task.

**Request**:

```
POST /api/queue/tasks/550e8400-e29b-41d4-a716-446655440000/retry
```

**Response** (200 OK):

```json
{
  "task_id": "770e8400-e29b-41d4-a716-446655440002",
  "video_id": "dQw4w9WgXcQ",
  "status": "pending",
  "message": "Task re-queued for retry"
}
```

**Errors**:

- `400 Bad Request`: Task is not in failed status
  ```json
  {
    "error_code": "CANNOT_RETRY",
    "user_message": "Can only retry failed tasks",
    "technical_details": "Current status: completed",
    "retry_possible": false
  }
  ```
- `429 Too Many Requests`: Max retries exceeded
  ```json
  {
    "error_code": "MAX_RETRIES_EXCEEDED",
    "user_message": "This download has failed too many times",
    "technical_details": "retry_count=3, max=3",
    "retry_possible": false
  }
  ```

---

### 5. History API

#### `GET /api/history`

Get download history with search and filters.

**Request**:

```
GET /api/history?search=tutorial&date_from=2025-12-01&date_to=2025-12-08&success=true&limit=50&offset=0
```

**Query Parameters**:

- `search` (optional): Search in video title
- `date_from` (optional): ISO date, filter by download date >= this
- `date_to` (optional): ISO date, filter by download date <= this
- `success` (optional, boolean): Filter by success status
- `limit` (optional, default=50): Number of results
- `offset` (optional, default=0): Pagination offset

**Response** (200 OK):

```json
{
  "history": [
    {
      "id": 1,
      "video_id": "dQw4w9WgXcQ",
      "video_title": "Example Tutorial",
      "channel_name": "Example Channel",
      "task_id": "550e8400-e29b-41d4-a716-446655440000",
      "download_date": "2025-12-08T14:05:00Z",
      "file_size": 52428800,
      "download_duration_seconds": 120,
      "success": true,
      "error_code": null
    }
  ],
  "total": 100,
  "limit": 50,
  "offset": 0,
  "filters_applied": {
    "search": "tutorial",
    "date_from": "2025-12-01",
    "date_to": "2025-12-08",
    "success": true
  }
}
```

---

#### `GET /api/history/stats`

Get download statistics.

**Request**:

```
GET /api/history/stats?period=30d
```

**Query Parameters**:

- `period` (optional, default=30d): Time period (7d, 30d, 90d, all)

**Response** (200 OK):

```json
{
  "period": "30d",
  "total_downloads": 150,
  "successful_downloads": 145,
  "failed_downloads": 5,
  "success_rate": 96.67,
  "total_size_bytes": 7864320000,
  "total_size_gb": 7.33,
  "average_download_time_seconds": 95,
  "most_downloaded_channel": {
    "channel_id": 1,
    "channel_name": "Example Channel",
    "download_count": 42
  }
}
```

---

### 6. Health Check API

#### `GET /api/health`

Check API and dependencies health.

**Request**:

```
GET /api/health
```

**Response** (200 OK):

```json
{
  "status": "healthy",
  "timestamp": "2025-12-08T14:00:00Z",
  "version": "1.0.0",
  "dependencies": {
    "database": "healthy",
    "huey_queue": "healthy",
    "yt_dlp": "available"
  },
  "queue_stats": {
    "pending_tasks": 5,
    "active_tasks": 2
  }
}
```

**Response** (503 Service Unavailable):

```json
{
  "status": "unhealthy",
  "timestamp": "2025-12-08T14:00:00Z",
  "version": "1.0.0",
  "dependencies": {
    "database": "unhealthy",
    "huey_queue": "healthy",
    "yt_dlp": "available"
  },
  "errors": ["Database connection failed: unable to connect"]
}
```

---

## Error Response Format

All error responses follow this structure:

```json
{
  "error_code": "MACHINE_READABLE_CODE",
  "user_message": "Human-friendly message for display",
  "technical_details": "Developer-facing details for debugging",
  "retry_possible": true,
  "timestamp": "2025-12-08T14:00:00Z"
}
```

**Error Codes**:

- `INVALID_URL`: Malformed URL
- `CHANNEL_EXISTS`: Duplicate channel
- `CHANNEL_NOT_FOUND`: Channel doesn't exist in DB or YouTube
- `VIDEO_NOT_FOUND`: Video doesn't exist
- `ALREADY_DOWNLOADED`: Video already has file_path
- `DOWNLOAD_IN_PROGRESS`: Active task exists for video
- `CANNOT_RETRY`: Task not in failed status
- `MAX_RETRIES_EXCEEDED`: Reached retry limit (3)
- `RATE_LIMIT`: YouTube rate limiting active
- `VIDEO_UNAVAILABLE`: Video is private/deleted/geo-blocked
- `DISK_FULL`: Insufficient storage space
- `INTERNAL_ERROR`: Unexpected server error

---

## HTTP Status Codes

- `200 OK`: Successful GET/DELETE/PATCH
- `201 Created`: Successful POST (created resource)
- `202 Accepted`: Accepted for async processing (downloads)
- `204 No Content`: Successful DELETE
- `400 Bad Request`: Invalid request (validation error)
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict (duplicate, already in progress)
- `422 Unprocessable Entity`: Valid request but semantic error (channel not on YouTube)
- `429 Too Many Requests`: Rate limiting
- `500 Internal Server Error`: Unexpected error
- `503 Service Unavailable`: Service temporarily down

---

## Rate Limiting

**Not implemented in MVP**, but future considerations:

- `X-RateLimit-Limit`: Max requests per window
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Timestamp when limit resets

---

## Pagination

All list endpoints support pagination:

- Query params: `limit` (default 50, max 100), `offset` (default 0)
- Response includes: `total`, `limit`, `offset`
- Use `offset = offset + limit` for next page

---

## OpenAPI / Swagger

FastAPI auto-generates OpenAPI spec:

- Docs UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

---

## WebSocket (Future Enhancement)

For real-time queue updates instead of polling:

- Endpoint: `ws://localhost:8000/ws/queue`
- Messages: JSON with task updates
- Not included in MVP (use polling for now)
