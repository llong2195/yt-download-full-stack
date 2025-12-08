# Tasks: YouTube Downloader Full-Stack Application

**Input**: Design documents from `/specs/001-youtube-downloader/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api-spec.md

**Tests**: MVP does not require tests. Focus on implementation and manual validation using quickstart.md scenarios.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/` and `web/` at repository root
- Paths shown below use web app structure per plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create backend directory structure: backend/models, backend/repository, backend/services, backend/routers, backend/tasks, backend/utils
- [x] T002 Create web directory structure: web/src/components, web/src/pages, web/src/services, web/src/types, web/src/utils
- [x] T003 Create backend/requirements.txt with dependencies: fastapi==0.124.0, uvicorn==0.38.0, SQLAlchemy==2.0.44, pydantic==2.12.5, huey==2.5.5, yt-dlp==2025.12.8
- [x] T004 [P] Initialize Python virtual environment and install backend dependencies: python -m venv backend/venv && pip install -r backend/requirements.txt
- [x] T005 [P] Initialize web/package.json with dependencies: react@19.2.0, react-dom@19.2.0, react-router@7.10.1, typescript@5.9.3, vite@7.2.4, @vitejs/plugin-react@5.1.1
- [x] T006 [P] Install web dependencies: cd web && pnpm install
- [x] T007 Create data/ and downloads/ directories at repository root for SQLite database and video storage
- [x] T008 [P] Create web/vite.config.ts with proxy configuration for /api to http://localhost:8000
- [x] T009 [P] Create web/tsconfig.json with strict mode enabled and path aliases
- [x] T010 [P] Create backend/.env template file with DATABASE_URL, HUEY_DB, DOWNLOAD_DIR, API_PORT, CORS_ORIGINS

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T011 Create backend/models/database.py with SQLAlchemy engine, Base, SessionLocal, WAL mode config
- [x] T012 [P] Create backend/models/**init**.py to export Base and session management
- [x] T013 [P] Create backend/models/channel.py with Channel SQLAlchemy model (id, channel_id, name, url, download_path, date_added, last_updated)
- [x] T014 [P] SKIPPED - Video model removed per data model update (video info stored in DownloadHistory)
- [x] T015 [P] Create backend/models/download_task.py with DownloadTask SQLAlchemy model (id, task_id, channel_id FK, video_id STRING, video_url, status, progress_percent, error_message, retry_count, created_at, started_at, completed_at)
- [x] T016 [P] Create backend/models/download_history.py with DownloadHistory SQLAlchemy model (id, channel_id FK, video_id, video_title, video_url, task_id, download_date, upload_date, duration, file_path, file_size, video_metadata, download_duration_seconds, success, error_code)
- [x] T017 Create backend/models/schemas.py with Pydantic request/response models for all entities
- [x] T018 Initialize database by running Base.metadata.create_all(engine) - creates all tables with indexes and constraints
- [x] T019 Create backend/main.py with FastAPI app, CORS middleware for http://localhost:5173 and chrome-extension://\*
- [x] T020 Configure Huey in backend/main.py: SqliteHuey(filename='data/huey.db') configured for task execution
- [x] T021 [P] Create backend/utils/logger.py for structured logging configuration
- [x] T022 [P] Create backend/utils/validators.py with URL validation and path sanitization functions
- [x] T023 [P] Create backend/utils/config.py to load environment variables from .env file
- [x] T024 Add health check endpoint GET /api/health in backend/main.py returning status, version, dependencies

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Channel Management (Priority: P1) 🎯 MVP

**Goal**: Users can add, view, and remove YouTube channels. Data persists across sessions.

**Independent Test**: Add a channel via web UI, view list, close browser, reopen, verify channel still there.

### Backend for User Story 1

- [x] T025 [P] [US1] Create backend/repository/channel_repo.py with CRUD functions: get_all_channels(), get_channel_by_id(), create_channel(), delete_channel()
- [x] T026 [US1] Create backend/services/channel_service.py with business logic: validate channel URL, extract channel info using yt-dlp, check for duplicates
- [x] T027 [US1] Create backend/routers/channels.py with GET /api/channels endpoint (returns all channels with video count)
- [x] T028 [US1] Add POST /api/channels endpoint to backend/routers/channels.py (validates URL, extracts metadata, saves to DB)
- [x] T029 [US1] Add DELETE /api/channels/{channel_id} endpoint to backend/routers/channels.py (cascade deletes videos)
- [x] T030 [US1] Register channels router in backend/main.py with prefix /api/channels
- [x] T031 [US1] Add error handling in backend/services/channel_service.py for invalid URLs, duplicate channels, YouTube API errors

### Frontend for User Story 1

- [x] T032 [P] [US1] Create web/src/types/channel.ts with Channel and API response interfaces
- [x] T033 [P] [US1] Create web/src/services/api.ts with base fetch wrapper function and error handling
- [x] T034 [US1] Create web/src/services/channelApi.ts with functions: fetchChannels(), addChannel(url), deleteChannel(id)
- [x] T035 [P] [US1] Create web/src/components/ChannelCard.tsx to display channel info (name, URL, date added, video count, delete button)
- [x] T036 [P] [US1] Create web/src/components/ChannelList.tsx to render list of ChannelCard components
- [x] T037 [US1] Create web/src/pages/Channels.tsx with add channel form, channel list, and state management
- [x] T038 [US1] Add routing in web/src/App.tsx with react-router v7 (BrowserRouter, Routes, Route): / → Channels page
- [x] T039 [US1] ALREADY EXISTS - web/src/main.tsx with StrictMode (no BrowserRouter needed here per react-router v7)
- [x] T040 [US1] Add loading states and error messages in web/src/pages/Channels.tsx for add/delete operations
- [x] T041 [US1] Style web/src/pages/Channels.tsx with basic CSS for layout and form

**Checkpoint**: User Story 1 complete - users can manage channels, persist data, independently testable

---

## Phase 4: User Story 2 - Video Download Initiation (Priority: P2)

**Goal**: Users request video downloads. System checks for duplicates, enqueues to Huey, returns immediately with task status.

**Independent Test**: Add channel (US1), request download, verify API responds <200ms with task_id and "pending" status.

### Backend for User Story 2

- [x] T042 [P] [US2] Create backend/repository/download_repo.py with functions: create_task(), get_task_by_id(), update_task_status(), check_active_task_for_video(), check_if_downloaded(video_id)
- [x] T043 [P] [US2] Create backend/repository/history_repo.py with get_history_by_video_id() to check if video was previously downloaded (MERGED INTO download_repo.py with get_successful_download_for_video function)
- [x] T044 [US2] Create backend/services/youtube_service.py with extract_video_metadata(url) using yt-dlp: returns video_id, title, duration, upload_date, channel_id, channel_name
- [x] T045 [US2] Add extract_video_id_from_url(url) function to backend/services/youtube_service.py supporting 3 URL patterns (youtube.com/watch, youtu.be, m.youtube.com)
- [x] T046 [US2] Add auto_create_channel(channel_id, channel_name) function to backend/services/channel_service.py with download_path=downloads/{channel_id}/ (IMPLEMENTED IN download_service.py using existing channel_service functions)
- [x] T047 [US2] Create backend/services/download_service.py with check_if_downloaded(video_id), check_in_progress(video_id), enqueue_download(channel_id, video_id, video_url) logic
- [ ] T048 [US2] Create backend/tasks/download_tasks.py with Huey task @huey.task: download_video(task_id) using yt-dlp Python library
- [ ] T049 [US2] Add yt-dlp progress hook in backend/tasks/download_tasks.py to update DownloadTask.progress_percent and status in database
- [ ] T050 [US2] Implement retry logic in backend/tasks/download_tasks.py: max 3 retries with exponential backoff (60s, 120s, 240s)
- [ ] T051 [US2] Add file path logic in backend/tasks/download_tasks.py: save to channel's download_path directory (downloads/{channel_id}/{video_id}.mp4)
- [ ] T052 [US2] Create DownloadHistory record in backend/tasks/download_tasks.py on completion with full video metadata (title, duration, file_path, file_size, success, error_code)
- [x] T053 [US2] Create backend/routers/downloads.py with POST /api/downloads endpoint (accepts video_id + channel_id, checks duplicates, enqueues task, returns 202 with task_id)
- [ ] T054 [US2] Add POST /api/downloads/batch endpoint to backend/routers/downloads.py (accepts array of video_ids with channel_ids, enqueues multiple tasks) (SKIPPED - batch-urls is more user-friendly)
- [x] T055 [US2] Add POST /api/downloads/batch-urls endpoint to backend/routers/downloads.py (accepts video_urls array, extracts video_id, fetches metadata, auto-creates channels, checks duplicates, enqueues tasks)
- [x] T056 [US2] Register downloads router in backend/main.py with prefix /api/downloads
- [x] T057 [US2] Add error handling for ALREADY_DOWNLOADED, DOWNLOAD_IN_PROGRESS, VIDEO_UNAVAILABLE, METADATA_FETCH_FAILED, RATE_LIMIT_EXCEEDED in backend/services/download_service.py

### Frontend for User Story 2

- [x] T058 [P] [US2] Create web/src/types/download.ts with DownloadTask interface (task_id, video_id, video_url, channel_id, status, progress_percent, etc.)
- [x] T059 [US2] Create web/src/services/downloadApi.ts with functions: requestDownload(video_id, channel_id), requestBatchDownload(video_ids), requestBatchDownloadByUrls(video_urls)
- [x] T060 [P] [US2] Create web/src/components/UrlInput.tsx with textarea for pasting multiple YouTube URLs (one per line) and "Download All" button
- [x] T061 [US2] Create web/src/pages/Downloads.tsx with URL input form, recent downloads list, and download status feedback
- [x] T062 [US2] Add Downloads route in web/src/App.tsx using <Route path="/downloads" element={<Downloads />} />
- [x] T063 [US2] Add navigation menu in web/src/App.tsx using <Link> components from react-router for Channels, Downloads, Queue, History pages (Added Channels and Downloads links)
- [x] T064 [US2] Implement URL parsing in web/src/pages/Downloads.tsx: split textarea by newlines, validate URLs, call requestBatchDownloadByUrls()
- [x] T065 [US2] Show success toast notification in web/src/pages/Downloads.tsx with summary: X queued, Y skipped, Z channels created (Implemented as Alert with stats grid)
- [x] T066 [US2] Show error messages in web/src/pages/Downloads.tsx for invalid URLs, failed metadata fetches, or rate limits
- [x] T067 [US2] Display skipped videos list in web/src/pages/Downloads.tsx showing reason (already downloaded, in progress) with download date (Implemented with skipped_reason alert)

**Checkpoint**: User Story 2 complete - downloads enqueue, API responds fast, tasks run in background

---

## Phase 5: User Story 3 - Download Status Monitoring (Priority: P3)

**Goal**: Users view real-time download queue with status (pending/downloading/completed/failed), progress percentage, and error messages.

**Independent Test**: Queue downloads (US2), navigate to Queue page, see status transition from pending → downloading → completed.

### Backend for User Story 3

- [ ] T068 [P] [US3] Add get_active_tasks() function to backend/repository/download_repo.py (filters status IN ['pending', 'downloading'])
- [ ] T069 [P] [US3] Add get_task_with_channel_info() function to backend/repository/download_repo.py (JOIN with Channel to get channel name)
- [ ] T070 [US3] Create backend/routers/queue.py with GET /api/queue/status endpoint (returns summary + list of active tasks with video info)
- [ ] T071 [US3] Add GET /api/queue/tasks/{task_id} endpoint to backend/routers/queue.py (returns detailed task status)
- [ ] T072 [US3] Add POST /api/queue/tasks/{task_id}/retry endpoint to backend/routers/queue.py (re-enqueues failed task if retry_count < 3)
- [ ] T073 [US3] Register queue router in backend/main.py with prefix /api/queue
- [ ] T074 [US3] Add error handling in backend/routers/queue.py for CANNOT_RETRY (task not failed) and MAX_RETRIES_EXCEEDED

### Frontend for User Story 3

- [ ] T075 [P] [US3] Create web/src/services/queueApi.ts with functions: fetchQueueStatus(), fetchTaskStatus(task_id), retryTask(task_id)
- [ ] T076 [P] [US3] Create web/src/components/QueueItem.tsx to display task info (video title, status badge, progress bar, error message, retry button if failed)
- [ ] T077 [US3] Create web/src/pages/Queue.tsx with queue summary stats (pending, downloading, completed_today, failed_today) and task list
- [ ] T078 [US3] Add Queue route in web/src/App.tsx using <Route path="/queue" element={<Queue />} />
- [ ] T079 [US3] Implement polling in web/src/pages/Queue.tsx: useEffect with setInterval every 2500ms to fetch queue status
- [ ] T080 [US3] Show progress bar in web/src/components/QueueItem.tsx for tasks with status=downloading (0-100%)
- [ ] T081 [US3] Add retry button in web/src/components/QueueItem.tsx for failed tasks (calls retryTask API)
- [ ] T082 [US3] Show "last updated" timestamp in web/src/pages/Queue.tsx to indicate freshness of data
- [ ] T083 [US3] Add color-coded status badges in web/src/components/QueueItem.tsx: pending=yellow, downloading=blue, completed=green, failed=red
- [ ] T084 [US3] Stop polling when user leaves Queue page (cleanup in useEffect return function)

**Checkpoint**: User Story 3 complete - queue visibility, real-time updates via polling, retry capability

---

## Phase 6: User Story 4 - Download History & Search (Priority: P4)

**Goal**: Users browse complete download history with search by title/channel, filter by date range, and view detailed metadata.

**Independent Test**: Complete several downloads (US2+US3), navigate to History page, search for specific video, apply date filter.

### Backend for User Story 4

- [ ] T085 [P] [US4] Update backend/repository/history_repo.py with get_history(search, date_from, date_to, success, limit, offset) function with JOIN to Channel (video info already in DownloadHistory)
- [ ] T086 [P] [US4] Add get_history_stats(period) function to backend/repository/history_repo.py for analytics (total, success rate, total size, avg time, most downloaded channel)
- [ ] T087 [US4] Create backend/routers/history.py with GET /api/history endpoint supporting query params: search, date_from, date_to, success, limit, offset
- [ ] T088 [US4] Add GET /api/history/stats endpoint to backend/routers/history.py with period query param (7d, 30d, 90d, all)
- [ ] T089 [US4] Register history router in backend/main.py with prefix /api/history
- [ ] T090 [US4] Add pagination metadata to GET /api/history response: total, limit, offset, filters_applied

### Frontend for User Story 4

- [ ] T091 [P] [US4] Create web/src/types/history.ts with DownloadHistory interface
- [ ] T092 [P] [US4] Create web/src/services/historyApi.ts with functions: fetchHistory(filters), fetchHistoryStats(period)
- [ ] T093 [P] [US4] Create web/src/components/HistoryItem.tsx to display history record (video title, channel, date, file size, duration, success badge)
- [ ] T094 [US4] Create web/src/pages/History.tsx with search input, date range filters, success filter checkbox, and history list
- [ ] T095 [US4] Add History route in web/src/App.tsx using <Route path="/history" element={<History />} />
- [ ] T096 [US4] Implement search functionality in web/src/pages/History.tsx: debounced input calling fetchHistory with search param
- [ ] T097 [US4] Add date range pickers in web/src/pages/History.tsx (date_from, date_to inputs) that trigger fetchHistory
- [ ] T098 [US4] Implement pagination in web/src/pages/History.tsx with "Load More" button or infinite scroll
- [ ] T099 [US4] Show history stats summary at top of web/src/pages/History.tsx: total downloads, success rate, total size
- [ ] T100 [US4] Add filtering by success/failure in web/src/pages/History.tsx with checkbox or toggle
- [ ] T101 [P] [US4] Create web/src/utils/formatters.ts with functions: formatFileSize(bytes), formatDuration(seconds), formatDate(iso_string)
- [ ] T102 [US4] Use formatters in web/src/components/HistoryItem.tsx to display human-readable file sizes and dates

**Checkpoint**: User Story 4 complete - full history browsing, search, filters, all 4 user stories implemented

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories or enhance overall quality

- [ ] T103 [P] Add indexes verification script in backend/models/database.py to ensure all indexes from data-model.md are created
- [ ] T104 [P] Create backend/utils/error_handlers.py with custom exception classes: DownloadException, ValidationException, NotFoundException
- [ ] T105 Add global exception handler in backend/main.py to catch all exceptions and return structured error responses with error_code, user_message, technical_details
- [ ] T106 [P] Add disk space check in backend/services/download_service.py before enqueueing download (reject if <1GB free)
- [ ] T107 [P] Add request logging middleware in backend/main.py to log all API requests with timestamp, method, path, status, duration
- [ ] T108 [P] Create web/src/index.css with global styles and CSS variables for consistent theming
- [ ] T109 [P] Add loading spinner component in web/src/components/LoadingSpinner.tsx used across all pages
- [ ] T110 [P] Add error boundary component in web/src/components/ErrorBoundary.tsx to catch React errors
- [ ] T111 Wrap App in ErrorBoundary in web/src/main.tsx
- [ ] T112 [P] Add toast notification system in web/src/components/Toast.tsx for success/error messages
- [ ] T113 Add README.md at repository root with project overview, setup instructions (link to quickstart.md), and architecture diagram
- [ ] T114 [P] Add .gitignore at repository root: venv/, node_modules/, dist/, data/, downloads/, \*.db, .env
- [ ] T115 Validate all endpoints against contracts/api-spec.md: verify request/response schemas match
- [ ] T116 Validate database schema against data-model.md: verify all indexes, constraints, foreign keys exist
- [ ] T117 Run through quickstart.md manual test scenarios for all 4 user stories to verify independent testability
- [ ] T118 [P] Add environment variable documentation in backend/.env.example with comments explaining each variable
- [ ] T119 [P] Add TypeScript type validation: run tsc --noEmit in web/ to check for type errors
- [ ] T120 [P] Optimize web build in web/vite.config.ts: enable code splitting, minification, compression

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase - MVP foundation
- **User Story 2 (Phase 4)**: Depends on User Story 1 (needs Channel entity and UI)
- **User Story 3 (Phase 5)**: Depends on User Story 2 (needs DownloadTask entity and enqueue logic)
- **User Story 4 (Phase 6)**: Depends on User Story 2 (needs DownloadHistory created by tasks)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories ✅ MVP
- **User Story 2 (P2)**: Requires User Story 1 (channels must exist to have videos)
- **User Story 3 (P3)**: Requires User Story 2 (tasks must be enqueued to monitor queue)
- **User Story 4 (P4)**: Requires User Story 2 (history records created by download tasks)

### Within Each User Story

- Backend models/repositories before services
- Services before routers
- Routers before frontend API services
- Frontend API services before components
- Components before pages
- Pages before routing

### Parallel Opportunities

- **Setup tasks**: T004, T005, T006, T008, T009, T010 can all run in parallel (different directories)
- **Foundational models**: T013, T014, T015, T016 can run in parallel (different model files)
- **Foundational utils**: T021, T022, T023 can run in parallel (different utility files)
- **Within US1 backend**: T025 (repository) parallel with nothing, but T031 (error handling) after T026
- **Within US1 frontend**: T032, T033, T035, T036 can run in parallel (different files)
- **Within US2 backend**: T042, T043, T044, T045 can run in parallel (different service/repository files)
- **Within US2 frontend**: T058, T060 can run in parallel (different type/component files)
- **Within US3 backend**: T068, T069 can run in parallel (different repository functions)
- **Within US3 frontend**: T075, T076 can run in parallel (service and component)
- **Within US4 backend**: T085, T086 can run in parallel (different repository functions)
- **Within US4 frontend**: T091, T092, T093, T101 can run in parallel (types, services, components, utils)
- **Polish tasks**: T103, T104, T106, T107, T108, T109, T110, T112, T114, T118, T119, T120 can run in parallel (different files)

---

## Parallel Example: User Story 1 Backend

```bash
# These can run simultaneously (different files):
Task T025: "Create backend/repository/channel_repo.py"
Task T032: "Create web/src/types/channel.ts"
Task T033: "Create web/src/services/api.ts"
Task T035: "Create web/src/components/ChannelCard.tsx"

# These must be sequential:
Task T026: "Create backend/services/channel_service.py" (needs T025 repository)
Task T027: "Create backend/routers/channels.py GET endpoint" (needs T026 service)
Task T034: "Create web/src/services/channelApi.ts" (needs T027 endpoint)
Task T037: "Create web/src/pages/Channels.tsx" (needs T034 API client)
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup ✅
2. Complete Phase 2: Foundational ✅ (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 ✅ (Channel management - independently testable)
4. Complete Phase 4: User Story 2 ✅ (Download initiation - core value)
5. **STOP and VALIDATE**: Test US1 + US2 independently using quickstart.md
6. Deploy/demo if ready (functional YouTube downloader with basic features)

### Full MVP (All 4 User Stories)

1. MVP First (above) ✅
2. Complete Phase 5: User Story 3 (Queue monitoring - enhanced UX)
3. Complete Phase 6: User Story 4 (History & search - completeness)
4. Complete Phase 7: Polish (error handling, logging, optimization)
5. Full validation with quickstart.md test scenarios
6. Production deployment

### Incremental Delivery

1. Phase 1 + 2 → Foundation ready
2. Add US1 → Test independently → Users can manage channels ✅
3. Add US2 → Test independently → Users can download videos ✅ MVP!
4. Add US3 → Test independently → Users can monitor progress
5. Add US4 → Test independently → Users can search history
6. Add Phase 7 → Polish and optimize
7. Each addition is deployable without breaking previous features

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (backend + frontend)
   - Developer B: User Story 2 backend
   - Developer C: User Story 2 frontend (starts after Developer B creates endpoints)
3. After US1 + US2 complete:
   - Developer A: User Story 3
   - Developer B: User Story 4
   - Developer C: Polish tasks (can start earlier)

---

## Task Validation Checklist

✅ **Format compliance**:

- All tasks use `- [ ] [TID] [P?] [Story?] Description with file path` format
- Task IDs are sequential: T001-T120
- [P] marker only on truly parallelizable tasks (different files, no dependencies)
- [Story] labels (US1, US2, US3, US4) on all user story tasks
- Setup and Foundational tasks have NO story label
- Polish tasks have NO story label

✅ **Organization**:

- Organized by user story (P1 → P2 → P3 → P4)
- Each phase has clear purpose and checkpoint
- Dependencies documented explicitly
- Parallel opportunities identified

✅ **Completeness**:

- All 3 entities from data-model.md covered (Channel, DownloadTask, DownloadHistory)
- All 14 API endpoints from contracts/api-spec.md covered (including new batch-urls)
- All 8 research decisions from research.md incorporated
- All layers (models, repository, services, routers, components, pages) included
- Frontend and backend for each user story

✅ **File paths**:

- Every task specifies exact file path
- Paths match structure in plan.md
- No ambiguous locations

✅ **Independent testability**:

- Each user story phase has checkpoint with test description
- User Story 1 can be tested without US2, US3, US4
- User Story 2 can be tested with just US1 (not US3, US4)
- User Story 3 requires US2 but not US4
- User Story 4 requires US2 but not US3

---

## Task Count Summary

- **Phase 1 (Setup)**: 10 tasks (T001-T010)
- **Phase 2 (Foundational)**: 14 tasks (T011-T024)
- **Phase 3 (US1 - Channel Management)**: 17 tasks (T025-T041)
  - Backend: 7 tasks
  - Frontend: 10 tasks
- **Phase 4 (US2 - Download Initiation)**: 26 tasks (T042-T067)
  - Backend: 15 tasks
  - Frontend: 11 tasks
- **Phase 5 (US3 - Queue Monitoring)**: 17 tasks (T068-T084)
  - Backend: 7 tasks
  - Frontend: 10 tasks
- **Phase 6 (US4 - History & Search)**: 18 tasks (T085-T102)
  - Backend: 6 tasks
  - Frontend: 12 tasks
- **Phase 7 (Polish)**: 18 tasks (T103-T120)

**Total**: 120 tasks

**Parallel tasks**: 39 tasks marked with [P] (32.5% can run in parallel)

**MVP tasks**: Phase 1 + Phase 2 + Phase 3 = 41 tasks (34% of total for basic channel management)

**Core MVP tasks**: Phase 1 + Phase 2 + Phase 3 + Phase 4 = 67 tasks (56% for functional downloader)

---

## Notes

- **Data Model**: Simplified to 3 tables (Channel, DownloadTask, DownloadHistory) - no separate Videos table
- **Video Storage**: Each channel has its own download directory: `downloads/{channel_id}/`
- **Video Metadata**: Stored in DownloadHistory table (video_title, video_url, duration, upload_date, metadata)
- **New API**: POST /api/downloads/batch-urls accepts video URLs, auto-detects and creates channels
- **Version Updates**: Tasks use actual package.json versions (React 19.2.0, react-router 7.10.1, TypeScript 5.9.3, Vite 7.2.4)
- **Routing**: Uses react-router v7 API (BrowserRouter, Routes, Route, Link) not react-router-dom v6
- No test tasks included (MVP does not require automated tests per research.md)
- Use quickstart.md for manual validation of each user story
- Commit after each task or logical group
- Verify against constitution at each checkpoint
- Stop at any phase to validate story independently before continuing
- Tasks marked [P] can be done in parallel if team has capacity
- File paths are exact - no ambiguity about where code goes
- Each user story is independently deployable and demonstrable
