# Tasks: Channel and Global Download Settings

**Input**: Design documents from `/specs/002-channel-settings/`  
**Prerequisites**: plan.md ✅, spec.md ✅

**Tests**: Not explicitly requested in specification - focus on implementation and manual testing

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and database migration setup

- [ ] T001 Enable SQLite WAL mode in backend/src/models/database.py for row-level locking support
- [ ] T002 [P] Create migration file backend/migrations/002_add_global_settings_table.py for GlobalSettings
- [ ] T003 [P] Create migration file backend/migrations/003_extend_channel_model.py for Channel updates
- [ ] T004 Document migration execution order in backend/migrations/README.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core database and utility infrastructure that MUST be complete before ANY user story

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Create GlobalSettings model in backend/src/models/global_settings.py with id (PK=1), default_download_path, default_subtitle_language, default_video_quality
- [ ] T006 Update Channel model in backend/src/models/channel.py: rename name→title, add name (unique), subtitle_language, video_quality, last_video_index (default 0)
- [ ] T007 Update DownloadHistory model in backend/src/models/download_history.py: add index_number, has_subtitles fields
- [ ] T008 Run database migrations to create/update tables with unique constraints
- [ ] T009 Create settings repository in backend/src/repository/settings_repo.py with get_settings(), update_settings(), ensure_default_row()
- [ ] T010 [P] Create filename sanitization utility in backend/src/utils/filename_sanitizer.py with sanitize_filename() function (replace unsafe chars: `:→-`, `/→-`, `\→-`, `|→_`, `?→`, `*→`, `<→`, `>→`, `"→'`)
- [ ] T011 [P] Create language code validator in backend/src/utils/validators.py with validate_language_code() for ISO 639-1 codes (en, ja, vi, ko, etc.)
- [ ] T012 [P] Create video quality validator in backend/src/utils/validators.py with validate_video_quality() for formats (best, worst, 1080p, 720p, 480p, 360p)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 2 - Add Custom Channel Name and Enhanced Channel Properties (Priority: P1) 🎯 MVP

**Goal**: Enable users to organize channels with custom names and specific download settings

**Independent Test**: Add a channel with custom name "Tech Reviews" for YouTube channel "TechTips Official", verify both names stored, downloads go to correct path

### Implementation for User Story 2

- [ ] T013 [P] [US2] Create ChannelCreateRequest schema in backend/src/models/schemas.py with name (required, unique), url, download_path (optional), subtitle_language (optional), video_quality (optional)
- [ ] T014 [P] [US2] Create ChannelUpdateRequest schema in backend/src/models/schemas.py with name (optional), download_path, subtitle_language, video_quality
- [ ] T015 [P] [US2] Create ChannelResponse schema in backend/src/models/schemas.py including title, name, url, download_path, subtitle_language, video_quality, last_video_index, date_added, last_updated
- [ ] T016 [US2] Update channel_repo.py add_channel() in backend/src/repository/channel_repo.py to handle name uniqueness check, populate title from YouTube API
- [ ] T017 [US2] Update channel_repo.py update_channel() in backend/src/repository/channel_repo.py to validate unique name on update
- [ ] T018 [US2] Update channel_service.py in backend/src/services/channel_service.py: add create_channel() with YouTube API call to fetch title, handle unique name violations with clear error
- [ ] T019 [US2] Update channel_service.py in backend/src/services/channel_service.py: add update_channel() to validate and update channel properties
- [ ] T020 [US2] Update POST /api/channels endpoint in backend/src/routers/channels.py to accept new ChannelCreateRequest schema
- [ ] T021 [US2] Update PUT /api/channels/{id} endpoint in backend/src/routers/channels.py to accept ChannelUpdateRequest schema
- [ ] T022 [US2] Update GET /api/channels endpoint in backend/src/routers/channels.py to return ChannelResponse with all new fields
- [ ] T023 [US2] Update ChannelCard component in web/src/components/ChannelCard.tsx to display custom name prominently, show title as secondary
- [ ] T024 [US2] Create ChannelForm component in web/src/components/ChannelForm.tsx with inputs for name (required), subtitle_language (dropdown), video_quality (dropdown), download_path (text)
- [ ] T025 [US2] Update Channels page in web/src/pages/Channels.tsx to use new ChannelForm for add/edit operations
- [ ] T026 [US2] Update channel type definitions in web/src/types/channel.ts with title, name, subtitle_language, video_quality, last_video_index
- [ ] T027 [US2] Update channelApi.ts in web/src/services/channelApi.ts to send/receive new channel fields
- [ ] T028 [US2] Add error handling for duplicate name errors in web/src/components/ChannelForm.tsx with user-friendly message

**Checkpoint**: Users can add/edit channels with custom names and settings. This is the MVP.

---

## Phase 4: User Story 3 - Sequential Video Naming for Organized Downloads (Priority: P1)

**Goal**: Automatically number videos in sequence (0001, 0002, ...) for chronological sorting in File Explorer

**Independent Test**: Download 3 videos from a channel, verify files named 0001_Title.mp4, 0002_Title.mp4, 0003_Title.mp4

### Implementation for User Story 3

- [ ] T029 [P] [US3] Create get_next_index() function in backend/src/repository/channel_repo.py using SELECT FOR UPDATE row lock, increment last_video_index atomically
- [ ] T030 [P] [US3] Create format_filename() function in backend/src/services/download_service.py that takes index, title, extension and returns {index}_{sanitized_title}.{ext} with 4-digit padding (0001-9999) or 5-digit (10000+)
- [ ] T031 [US3] Update download_video task in backend/src/tasks/download_tasks.py to call get_next_index() within transaction before download
- [ ] T032 [US3] Update download_video task in backend/src/tasks/download_tasks.py to use format_filename() for video output path
- [ ] T033 [US3] Update download_video task in backend/src/tasks/download_tasks.py to save index_number to download_history table
- [ ] T034 [US3] Add error handling in backend/src/tasks/download_tasks.py for path length exceeding OS limits (Windows 260 chars) with message suggesting shorter channel name/path
- [ ] T035 [US3] Update HistoryItem component in web/src/components/HistoryItem.tsx to display sequential index in UI

**Checkpoint**: Videos download with sequential numbering that sorts correctly in File Explorer

---

## Phase 5: User Story 1 - Configure Global Download Defaults (Priority: P2)

**Goal**: Set system-wide defaults for download path, subtitle language, and video quality

**Independent Test**: Configure global defaults in Settings page, add new channel without specifying settings, verify it inherits global defaults

### Implementation for User Story 1

- [ ] T036 [P] [US1] Create GlobalSettingsResponse schema in backend/src/models/schemas.py with default_download_path, default_subtitle_language, default_video_quality
- [ ] T037 [P] [US1] Create GlobalSettingsUpdateRequest schema in backend/src/models/schemas.py with optional fields for all settings
- [ ] T038 [US1] Create settings service in backend/src/services/settings_service.py with get_or_create_settings(), update_settings()
- [ ] T039 [US1] Create settings inheritance functions in backend/src/services/settings_service.py: resolve_download_path(channel, global_settings), resolve_subtitle_language(channel, global_settings), resolve_video_quality(channel, global_settings)
- [ ] T040 [US1] Create settings router in backend/src/routers/settings.py with GET /api/settings and PUT /api/settings endpoints
- [ ] T041 [US1] Update channel_service.py create_channel() in backend/src/services/channel_service.py to use resolve_download_path() when download_path not provided
- [ ] T042 [US1] Update download_service.py in backend/src/services/download_service.py to use resolve_subtitle_language() and resolve_video_quality() for downloads
- [ ] T043 [US1] Create Settings page in web/src/pages/Settings.tsx with form for global defaults (download_path, subtitle_language, video_quality)
- [ ] T044 [US1] Create settings API client in web/src/services/settingsApi.ts with getSettings() and updateSettings()
- [ ] T045 [US1] Create GlobalSettings type in web/src/types/settings.ts
- [ ] T046 [US1] Add Settings link to navigation in web/src/App.tsx or main navigation component
- [ ] T047 [US1] Add input validation in Settings page for download_path (valid directory), subtitle_language (ISO 639-1), video_quality (supported formats)

**Checkpoint**: Users can configure global defaults that apply to all new channels

---

## Phase 6: User Story 4 - Channel-Specific Subtitle Language Selection (Priority: P2)

**Goal**: Specify preferred subtitle languages per channel for automatic subtitle downloads

**Independent Test**: Configure channel with "ja" subtitle language, download video, verify Japanese subtitles downloaded (if available)

### Implementation for User Story 4

- [ ] T048 [US4] Update download_video task in backend/src/tasks/download_tasks.py to pass subtitle language to yt-dlp via --write-subs --sub-langs parameter
- [ ] T049 [US4] Update download_video task in backend/src/tasks/download_tasks.py to detect if subtitles were downloaded and set has_subtitles field in download_history
- [ ] T050 [US4] Update download_video task in backend/src/tasks/download_tasks.py to log warning when requested subtitle language not available
- [ ] T051 [US4] Update download_history response schema in backend/src/models/schemas.py to include has_subtitles, subtitle_language fields
- [ ] T052 [US4] Update HistoryItem component in web/src/components/HistoryItem.tsx to show subtitle indicator/badge when has_subtitles=true

**Checkpoint**: Channels download with specified subtitle languages automatically

---

## Phase 7: User Story 5 - Channel-Specific Video Quality Selection (Priority: P2)

**Goal**: Set preferred video quality per channel to control resolution and disk space

**Independent Test**: Configure channel with "720p" quality, download video, verify 720p quality selected (or closest available)

### Implementation for User Story 5

- [ ] T053 [US5] Update download_video task in backend/src/tasks/download_tasks.py to pass quality setting to yt-dlp via -f/--format parameter
- [ ] T054 [US5] Update download_video task in backend/src/tasks/download_tasks.py to implement fallback quality logic when exact quality not available (select closest lower quality)
- [ ] T055 [US5] Update download_video task in backend/src/tasks/download_tasks.py to log warning when requested quality not available and fallback used
- [ ] T056 [US5] Update download_history response schema in backend/src/models/schemas.py to include actual quality field
- [ ] T057 [US5] Update HistoryItem component in web/src/components/HistoryItem.tsx to display actual video quality downloaded

**Checkpoint**: Channels download with specified quality settings

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T058 [P] Add API error handling middleware in backend/src/routers/ for unique constraint violations (IntegrityError) returning 409 Conflict with clear message
- [ ] T059 [P] Add logging for all settings operations in backend/src/services/settings_service.py and channel_service.py
- [ ] T060 [P] Add logging for index assignment and filename generation in backend/src/tasks/download_tasks.py
- [ ] T061 [P] Update README.md with new features: global settings, custom channel names, sequential numbering
- [ ] T062 [P] Create migration script in backend/migrations/ to populate existing channels with default values (title from name, last_video_index=0)
- [ ] T063 Validate all edge cases: duplicate names, long paths, invalid language codes, invalid quality formats, concurrent downloads
- [ ] T064 Performance test concurrent downloads (5+ simultaneous) to verify no index conflicts
- [ ] T065 Manual test Settings page UI flow: configure, save, verify inheritance
- [ ] T066 Manual test channel management UI: add, edit, display custom names
- [ ] T067 [P] Code cleanup and refactoring: extract common validation logic, improve error messages
- [ ] T068 Update API documentation (if exists) with new endpoints and request/response schemas

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) completion - BLOCKS all user stories
- **User Story 2 - Custom Names (Phase 3, P1)**: Depends on Foundational - Can start immediately after Phase 2
- **User Story 3 - Sequential Naming (Phase 4, P1)**: Depends on Foundational - Can start in parallel with Phase 3
- **User Story 1 - Global Settings (Phase 5, P2)**: Depends on Foundational and Phase 3 (needs channel_service updates) - Start after Phase 3
- **User Story 4 - Subtitles (Phase 6, P2)**: Depends on Foundational and Phase 4 (needs download task) - Can start after Phase 4
- **User Story 5 - Quality (Phase 7, P2)**: Depends on Foundational and Phase 4 (needs download task) - Can start in parallel with Phase 6
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

**Priority 1 (MVP):**
- **US2 - Custom Names**: Foundational only → Can start after Phase 2
- **US3 - Sequential Naming**: Foundational only → Can start in parallel with US2 after Phase 2

**Priority 2 (Enhancements):**
- **US1 - Global Settings**: Requires US2 (channel_service) → Start after Phase 3
- **US4 - Subtitles**: Requires US3 (download task updates) → Start after Phase 4
- **US5 - Quality**: Requires US3 (download task updates) → Start in parallel with US4 after Phase 4

### Within Each User Story

- Models and schemas before repositories
- Repositories before services
- Services before routers (backend) or API clients (frontend)
- Backend before frontend (API must exist for UI to call)
- Core functionality before UI polish

### Parallel Opportunities

**Phase 1 (Setup):**
- T002 and T003 can run in parallel (different migration files)

**Phase 2 (Foundational):**
- T005, T006, T007 can run in parallel (different model files)
- T010, T011, T012 can run in parallel (different utility files)

**Phase 3 (US2):**
- T013, T014, T015 can run in parallel (different schemas)

**Phase 4 (US3):**
- T029, T030 can run in parallel (different files)

**Phase 5 (US1):**
- T036, T037 can run in parallel (different schemas)

**Phase 6 & 7:**
- Phases 6 and 7 can run completely in parallel (different features)

**Phase 8 (Polish):**
- T058, T059, T060, T061, T062, T067 can all run in parallel

---

## Parallel Execution Examples

### After Phase 2 Completes:

**Option A - Sequential by Priority:**
```bash
# Implement P1 stories first
Phase 3 (US2) → Phase 4 (US3) → Phase 5 (US1) → Phases 6+7 (US4, US5) → Phase 8
```

**Option B - Parallel P1 Stories (2 developers):**
```bash
Dev 1: Phase 3 (US2 - Custom Names)
Dev 2: Phase 4 (US3 - Sequential Naming)
# Then merge and continue with P2 stories
```

**Option C - Full Parallel (5+ developers):**
```bash
Dev 1: Phase 3 (US2) → Phase 5 (US1) → Phase 8
Dev 2: Phase 4 (US3) → Phase 6 (US4) → Phase 8
Dev 3: Phase 4 (US3) → Phase 7 (US5) → Phase 8
# All developers work independently, merge incrementally
```

### Minimum MVP Path:
```bash
Phase 1 → Phase 2 → Phase 3 (US2) → Phase 4 (US3) → Phase 8 (minimal polish)
# Delivers: Custom channel names + Sequential numbering
# Time estimate: ~3-5 days for experienced developer
```

### Full Feature Path:
```bash
Phase 1 → Phase 2 → Phases 3+4 (parallel) → Phase 5 → Phases 6+7 (parallel) → Phase 8
# Delivers: All 5 user stories
# Time estimate: ~1-2 weeks for experienced developer
```

---

## Task Completion Checklist

For each task, verify:
- [ ] Code follows clean architecture (correct layer)
- [ ] Database operations use transactions where needed
- [ ] Input validation added for user-facing inputs
- [ ] Error handling with clear user messages
- [ ] Logging added for debugging
- [ ] No hardcoded values (use constants/config)
- [ ] File paths use OS-independent path joining
- [ ] API responses follow consistent schema format
- [ ] Frontend components handle loading/error states
- [ ] Code committed with descriptive message

## Implementation Strategy

**Recommended Approach**: MVP First (P1 stories), then enhance (P2 stories)

1. **Week 1**: Complete Phase 1, 2, 3, 4
   - Result: Users can add channels with custom names and videos download with sequential numbering
   - Deliverable: Fully functional MVP

2. **Week 2**: Complete Phase 5, 6, 7, 8
   - Result: Global settings, subtitle language, video quality features added
   - Deliverable: Full feature set with polish

**Testing Focus**:
- Manual test each user story independently after phase completion
- Integration test concurrent downloads for index conflicts
- Edge case testing for duplicate names, invalid inputs, long paths
- Load test with realistic data (50 channels, 100 videos each)

**Rollback Plan**:
- Keep database migrations reversible
- Feature flag Settings page if needed
- Maintain backward compatibility (existing channels work without new fields)
