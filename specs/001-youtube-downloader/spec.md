# Feature Specification: YouTube Downloader Full-Stack Application

**Feature Branch**: `001-youtube-downloader`  
**Created**: 2025-12-08  
**Status**: Draft  
**Input**: User description: "Ứng dụng YouTube downloader full-stack với backend FastAPI + SQLite + Huey và frontend React + TypeScript + Vite để quản lý channels, download videos, và theo dõi trạng thái queue"

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Channel Management (Priority: P1)

Users can add, view, and manage YouTube channels they want to track for video downloads. The system stores channel information and provides a clean interface to manage the channel list.

**Why this priority**: Foundation feature - must exist before any downloads can be tracked or managed. Provides immediate value by organizing channels.

**Independent Test**: Can be fully tested by adding a channel via web UI, viewing the channel list, and verifying persistence across page refreshes without any video downloads.

**Acceptance Scenarios**:

1. **Given** user is on the web interface, **When** user enters a valid YouTube channel URL and clicks "Add Channel", **Then** the channel appears in the channel list with basic info (name, URL, date added)
2. **Given** channel list has multiple channels, **When** user views the list, **Then** all channels are displayed with their metadata and last update timestamp
3. **Given** user selects a channel, **When** user clicks "Remove Channel", **Then** the channel is deleted from the list and database
4. **Given** user closes and reopens the web application, **When** page loads, **Then** all previously added channels are still visible

---

### User Story 2 - Video Download Initiation (Priority: P2)

Users can request video downloads from tracked channels. The system checks if videos are already downloaded, enqueues new downloads to Huey task queue, and provides immediate feedback without blocking.

**Why this priority**: Core functionality that delivers the primary value proposition. Depends on channel management (P1) but provides the main use case.

**Independent Test**: Can be tested by adding a channel (US1), requesting a video download, verifying the task is queued (not downloaded yet), and checking that API responds immediately.

**Acceptance Scenarios**:

1. **Given** user has added a channel with videos, **When** user clicks "Download Video" for a specific video, **Then** system checks database and either starts download or shows "already downloaded" message
2. **Given** video is not yet downloaded, **When** download is requested, **Then** task is added to Huey queue and API returns immediately with task ID and "queued" status
3. **Given** video is already downloaded, **When** download is requested again, **Then** system returns "already exists" without creating duplicate task
4. **Given** multiple videos are selected, **When** user clicks "Download All", **Then** all videos not yet downloaded are enqueued as separate tasks

---

### User Story 3 - Download Status Monitoring (Priority: P3)

Users can view real-time status of download queue, including pending tasks, actively downloading videos, completed downloads, and failed tasks with error messages.

**Why this priority**: Enhances user experience by providing visibility into background operations. System works without this (downloads still happen), but users can't monitor progress.

**Independent Test**: Can be tested by queuing downloads (US2) and viewing the queue status page, which shows tasks transitioning from pending → downloading → complete.

**Acceptance Scenarios**:

1. **Given** downloads are queued, **When** user views queue status page, **Then** system displays list of all tasks with status (pending, downloading, completed, failed)
2. **Given** a video is currently downloading, **When** user refreshes status, **Then** progress percentage and download speed are shown
3. **Given** a download fails, **When** user views queue status, **Then** error message is displayed with retry option
4. **Given** user is on queue status page, **When** download completes, **Then** status updates automatically without manual refresh (polling or websocket)

---

### User Story 4 - Download History & Search (Priority: P4)

Users can browse complete download history with search and filter capabilities. History persists across sessions and provides metadata about each downloaded video.

**Why this priority**: Quality-of-life feature for managing large collections. MVP can function without this, but becomes essential as download count grows.

**Independent Test**: Can be tested by completing several downloads (US2+US3), then searching/filtering history by channel, date, or video title.

**Acceptance Scenarios**:

1. **Given** multiple videos have been downloaded, **When** user views history page, **Then** all completed downloads are listed with video title, channel, download date, and file size
2. **Given** user enters search term, **When** search is submitted, **Then** only matching videos are displayed based on title, channel, or metadata
3. **Given** user selects date range filter, **When** filter is applied, **Then** only downloads within that date range are shown
4. **Given** user clicks on a history item, **When** video details page opens, **Then** full metadata is displayed including download path, duration, resolution, and file size

---

### Edge Cases

- What happens when YouTube channel URL is invalid or inaccessible?
- How does system handle network interruptions during download?
- What if yt-dlp fails with rate limiting or authentication errors?
- How does system handle disk space exhaustion?
- What happens when same video is requested simultaneously by multiple processes?
- How does system handle YouTube API changes or blocked IPs?
- What if database becomes corrupted or locked?
- How does system handle extremely long channel names or special characters in video titles?

## Requirements _(mandatory)_

### Functional Requirements

#### Backend Requirements

- **FR-001**: System MUST provide REST API using FastAPI framework
- **FR-002**: System MUST store channel data in SQLite database with fields: channel_id, name, url, date_added, last_updated
- **FR-003**: System MUST store download history in SQLite with fields: video_id, channel_id, title, url, status, file_path, download_date, file_size, metadata
- **FR-004**: System MUST integrate Huey task queue using SQLite backend within the same process as FastAPI
- **FR-005**: System MUST check database for existing downloads BEFORE enqueuing new tasks
- **FR-006**: System MUST enqueue download tasks to Huey when video is not already downloaded
- **FR-007**: System MUST execute yt-dlp asynchronously via Huey tasks without blocking API responses
- **FR-008**: System MUST return task status immediately (queued/downloading/complete/failed) to API clients
- **FR-009**: System MUST handle task failures gracefully with retry logic (max 3 retries with exponential backoff)
- **FR-010**: Backend MUST follow Clean Architecture with layers: `/models`, `/repository`, `/services`, `/routers`
- **FR-011**: API endpoints MUST respond within 200ms for read operations (excluding actual downloads)
- **FR-012**: All API inputs MUST be validated using Pydantic models
- **FR-013**: All database queries MUST use SQLAlchemy ORM with proper indexing
- **FR-014**: System MUST log all errors with full context (task_id, video_id, error message, stack trace)
- **FR-015**: System MUST sanitize all file paths before saving to prevent directory traversal attacks

#### Frontend Requirements

- **FR-016**: Frontend MUST be built with React 18+ and TypeScript in strict mode
- **FR-017**: Frontend MUST use Vite as build tool to produce standalone `dist/` folder
- **FR-018**: Frontend MUST communicate with backend using native fetch API
- **FR-019**: Frontend MUST display channel list with add/remove capabilities
- **FR-020**: Frontend MUST provide interface to trigger video downloads per channel
- **FR-021**: Frontend MUST show download queue status with real-time updates (polling every 2-3 seconds)
- **FR-022**: Frontend MUST display download history with search/filter functionality
- **FR-023**: Frontend MUST render smoothly without blocking UI thread during API calls
- **FR-024**: Built frontend MUST run on any HTTP server without Node.js or build tools
- **FR-025**: Frontend MUST use Shadcn components for consistent UI design

#### Integration Requirements

- **FR-026**: Frontend and backend MUST communicate via RESTful JSON API
- **FR-027**: API MUST support CORS for Chrome extension integration
- **FR-028**: System MUST maintain referential integrity between channels and download history
- **FR-029**: API MUST provide endpoints for: channel CRUD, download initiation, queue status, history retrieval

### Key Entities

- **Channel**: Represents a YouTube channel to track. Attributes: unique channel_id, display name, YouTube URL, date added, last sync timestamp. Related to multiple Video entities.

- **Video**: Represents a downloadable/downloaded YouTube video. Attributes: unique video_id, title, YouTube URL, file path (when downloaded), file size, upload date, metadata (resolution, duration, format). Belongs to one Channel.

- **DownloadTask**: Represents a queued or completed download operation. Attributes: task_id (Huey generated), video_id reference, status (queued/downloading/complete/failed), created_at, started_at, completed_at, error_message, retry_count. Links to one Video.

- **DownloadHistory**: Persistent record of completed downloads. Attributes: history_id, video_id reference, download_date, file_size, download_duration, success status. Links to one Video.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: Users can add a new YouTube channel and see it in the list within 2 seconds
- **SC-002**: Download requests respond within 200ms and immediately return task status
- **SC-003**: System successfully downloads videos in background without blocking web UI
- **SC-004**: Frontend build process produces deployable folder that runs on any static HTTP server without errors
- **SC-005**: Download queue status updates within 3 seconds of task status change
- **SC-006**: System handles at least 10 concurrent download tasks without degradation
- **SC-007**: Database queries for checking existing downloads complete within 50ms
- **SC-008**: Failed downloads retry automatically up to 3 times before marking as failed
- **SC-009**: Users can search through 1000+ download history records and see results within 1 second
- **SC-010**: System prevents duplicate downloads - requesting same video twice only downloads once

## Assumptions

- YouTube channel URLs follow standard format: `https://www.youtube.com/@channelname` or `https://www.youtube.com/channel/CHANNEL_ID`
- yt-dlp is pre-installed and available in system PATH or backend environment
- Downloaded videos are stored on local filesystem accessible to backend
- SQLite database file has sufficient disk space (no enterprise-scale multi-GB databases)
- Chrome extension integration requires CORS but not authentication (auth can be added later)
- Users have stable internet connection for downloads (system handles temporary interruptions with retries)
- System runs on single server (no distributed deployment in MVP)
- Default video format/quality settings are acceptable (customization can be added later)

## Out of Scope (for MVP)

- User authentication and multi-user support
- Video playback within the web interface
- Automatic channel monitoring and scheduled downloads
- Video format/quality selection UI (uses yt-dlp defaults)
- Cloud storage integration (S3, Google Drive, etc.)
- Mobile app (iOS/Android)
- Video metadata editing or tagging
- Playlist management
- Video thumbnails display
- Bandwidth throttling or download scheduling
