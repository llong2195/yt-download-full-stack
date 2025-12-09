# Tasks: Channel and Global Download Settings

**Feature Branch**: `002-channel-settings`  
**Input**: Design documents from `/specs/002-channel-settings/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api-spec.md, quickstart.md

**Tests**: Not explicitly requested in specification - TDD approach not required for this feature.

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Task Format: `- [ ] [ID] [P?] [Story?] Description with file path`

- **[P]**: Parallelizable task (different files, no dependencies on incomplete tasks)
- **[Story]**: User story label (US1, US2, US3, US4) - only for user story phases
- File paths are absolute from repository root

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Database schema setup for settings feature

**⚠️ NOTE**: This project uses SQLAlchemy's `Base.metadata.create_all()` (not Alembic migrations). Schema changes require updating model classes and running `init_db.py`.

- [ ] T001 Create GlobalSettings SQLAlchemy model class in backend/src/models/global_settings.py
- [ ] T002 Extend Channel model with new fields (title, subtitle_language, video_quality) in backend/src/models/channel.py
- [ ] T003 Update database initialization to create GlobalSettings singleton row in backend/init_db.py
- [ ] T004 Run `python backend/init_db.py` to apply schema changes and verify tables created
- [ ] T005 Verify GlobalSettings singleton row exists with default values in database using SQLite CLI

**Checkpoint**: Database schema ready for implementation

**Migration Strategy**: Since existing Channel table has data:
1. Backup existing database before schema changes
2. For new columns on Channel: Add with nullable=True or provide default values
3. Existing `name` field becomes `title`, add new `name` field
4. Write a one-time data migration script if needed to populate new fields

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core schemas, validators, and repository layer required by all user stories

**⚠️ CRITICAL**: Complete this phase before starting any user story. Phase 1 (models + schema) must be complete.

- [ ] T006 [P] Add GlobalSettings Pydantic schemas (GlobalSettingsSchema, GlobalSettingsUpdateSchema) in backend/src/models/schemas.py
- [ ] T007 [P] Extend Channel Pydantic schemas (ChannelCreateSchema, ChannelUpdateSchema, ChannelResponseSchema) in backend/src/models/schemas.py
- [ ] T008 [P] Add video quality validation constants and function in backend/src/utils/validators.py
- [ ] T009 [P] Add subtitle language validation constants and function in backend/src/utils/validators.py
- [ ] T010 [P] Add download path validation function in backend/src/utils/validators.py
- [ ] T011 Create SettingsRepository with get_settings and update_settings methods in backend/src/repository/settings_repo.py
- [ ] T012 Extend ChannelRepository to handle unique name constraint and new fields in backend/src/repository/channel_repo.py

**Checkpoint**: Foundation complete - user stories can now be implemented in parallel

---

## Phase 3: User Story 2 - Custom Channel Name and Properties (Priority: P1) 🎯 MVP

**Goal**: Enable users to add channels with custom names and per-channel settings. Channel list displays custom names prominently.

**Independent Test**: Add channel with custom name → verify stored with both title and name → verify custom name shown in UI → verify duplicate name rejected.

### Backend Implementation for US2

- [ ] T013 [P] [US2] Create SettingsService with get_settings and update_settings methods in backend/src/services/settings_service.py
- [ ] T014 [P] [US2] Extend ChannelService with settings inheritance logic (get_effective_settings method) in backend/src/services/channel_service.py
- [ ] T015 [US2] Update ChannelService create_channel to apply default download path from global settings in backend/src/services/channel_service.py
- [ ] T016 [US2] Update ChannelService create_channel to validate custom name uniqueness with proper error handling in backend/src/services/channel_service.py
- [ ] T017 [US2] Update ChannelService update_channel to handle custom name changes with validation in backend/src/services/channel_service.py
- [ ] T018 [P] [US2] Extend POST /api/channels endpoint to accept new fields (name, subtitle_language, video_quality) in backend/src/routers/channels.py
- [ ] T019 [P] [US2] Extend PUT /api/channels/{id} endpoint to update custom name and settings in backend/src/routers/channels.py
- [ ] T020 [P] [US2] Extend GET /api/channels endpoints to return new fields (title, name, subtitle_language, video_quality) in backend/src/routers/channels.py
- [ ] T021 [US2] Add error handling for 409 Conflict when duplicate channel name in channels router in backend/src/routers/channels.py

### Frontend Implementation for US2

- [ ] T022 [P] [US2] Extend Channel TypeScript interface with title, name, subtitle_language, video_quality fields in web/src/types/channel.ts
- [ ] T023 [P] [US2] Extend ChannelCreate and ChannelUpdate interfaces in web/src/types/channel.ts
- [ ] T024 [P] [US2] Add VALID_LANGUAGES constant array in web/src/types/channel.ts
- [ ] T025 [P] [US2] Add VALID_QUALITIES constant array in web/src/types/channel.ts
- [ ] T026 [US2] Update channelApi.ts addChannel function to send new fields in web/src/services/channelApi.ts
- [ ] T027 [US2] Update channelApi.ts updateChannel function to support new fields in web/src/services/channelApi.ts
- [ ] T028 [US2] Update ChannelCard component to display custom name prominently and title as secondary in web/src/components/ChannelCard.tsx
- [ ] T029 [US2] Add custom name input field to channel add form in web/src/pages/Channels.tsx
- [ ] T030 [US2] Add optional download path input to channel add form in web/src/pages/Channels.tsx
- [ ] T031 [US2] Add optional subtitle language select dropdown to channel add form in web/src/pages/Channels.tsx
- [ ] T032 [US2] Add optional video quality select dropdown to channel add form in web/src/pages/Channels.tsx
- [ ] T033 [US2] Add error handling for duplicate name (409) with user-friendly message in web/src/pages/Channels.tsx
- [ ] T034 [US2] Implement channel edit dialog with all editable fields in web/src/pages/Channels.tsx

**Checkpoint**: User Story 2 complete - channels can be managed with custom names and settings

---

## Phase 4: User Story 1 - Global Download Defaults (Priority: P2)

**Goal**: Provide system-wide default settings accessible via Settings page. New channels inherit these defaults.

**Independent Test**: Configure global defaults → add new channel without specifying settings → verify channel inherits global defaults.

### Backend Implementation for US1

- [ ] T035 [P] [US1] Create settings router with GET /api/settings endpoint in backend/src/routers/settings.py
- [ ] T036 [P] [US1] Create settings router with PUT /api/settings endpoint in backend/src/routers/settings.py
- [ ] T037 [US1] Register settings router in FastAPI app in backend/main.py
- [ ] T038 [US1] Add validation error handling in SettingsService for invalid paths/languages/qualities in backend/src/services/settings_service.py

### Frontend Implementation for US1

- [ ] T039 [P] [US1] Create GlobalSettings TypeScript interface in web/src/types/settings.ts
- [ ] T040 [P] [US1] Create GlobalSettingsUpdate TypeScript interface in web/src/types/settings.ts
- [ ] T041 [P] [US1] Export VALID_LANGUAGES constant from settings types in web/src/types/settings.ts
- [ ] T042 [P] [US1] Export VALID_QUALITIES constant from settings types in web/src/types/settings.ts
- [ ] T043 [P] [US1] Create fetchSettings API function in web/src/services/settingsApi.ts
- [ ] T044 [P] [US1] Create updateSettings API function in web/src/services/settingsApi.ts
- [ ] T045 [US1] Create Settings page component with global settings form in web/src/pages/Settings.tsx
- [ ] T046 [US1] Add default download path input to Settings page in web/src/pages/Settings.tsx
- [ ] T047 [US1] Add default subtitle language select to Settings page in web/src/pages/Settings.tsx
- [ ] T048 [US1] Add default video quality select to Settings page in web/src/pages/Settings.tsx
- [ ] T049 [US1] Add Save button with loading state to Settings page in web/src/pages/Settings.tsx
- [ ] T050 [US1] Add settings navigation link to app menu/navigation in web/src/App.tsx
- [ ] T051 [US1] Add error handling and success feedback for settings save in web/src/pages/Settings.tsx

**Checkpoint**: User Story 1 complete - global defaults can be configured and are inherited by new channels

---

## Phase 5: User Story 3 - Channel-Specific Subtitle Language (Priority: P2)

**Goal**: Allow per-channel subtitle language configuration with inheritance from global defaults. Download service uses channel/global/hardcoded fallback.

**Independent Test**: Set channel subtitle language → download video → verify correct subtitles downloaded. Set only global default → verify inherited. Set neither → verify fallback to none.

### Backend Implementation for US3

- [ ] T052 [US3] Extend download_service.py to retrieve channel settings before download in backend/src/services/download_service.py
- [ ] T053 [US3] Implement subtitle language fallback chain (channel → global → null) in download service in backend/src/services/download_service.py
- [ ] T054 [US3] Pass subtitle language to yt-dlp download command in backend/src/services/youtube_service.py
- [ ] T055 [US3] Add logging when subtitle language not available for video in backend/src/services/youtube_service.py
- [ ] T056 [US3] Handle yt-dlp subtitle download errors gracefully in backend/src/tasks/download_tasks.py

### Frontend Implementation for US3

- [ ] T057 [US3] Update download history display to show subtitle language used in web/src/pages/History.tsx
- [ ] T058 [US3] Add subtitle language indicator in queue items in web/src/pages/Queue.tsx

**Checkpoint**: User Story 3 complete - subtitle language settings work end-to-end in download flow

---

## Phase 6: User Story 4 - Channel-Specific Video Quality (Priority: P2)

**Goal**: Allow per-channel video quality configuration with inheritance from global defaults. Download service uses channel/global/hardcoded fallback.

**Independent Test**: Set channel quality → download video → verify correct quality downloaded. Set only global default → verify inherited. Set neither → verify fallback to "best".

### Backend Implementation for US4

- [ ] T059 [US4] Implement video quality fallback chain (channel → global → "best") in download service in backend/src/services/download_service.py
- [ ] T060 [US4] Pass video quality to yt-dlp format selection in backend/src/services/youtube_service.py
- [ ] T061 [US4] Add logging when requested quality not available (fallback used) in backend/src/services/youtube_service.py
- [ ] T062 [US4] Handle yt-dlp quality selection errors gracefully in backend/src/tasks/download_tasks.py

### Frontend Implementation for US4

- [ ] T063 [US4] Update download history display to show actual quality downloaded in web/src/pages/History.tsx
- [ ] T064 [US4] Add quality indicator in queue items in web/src/pages/Queue.tsx

**Checkpoint**: User Story 4 complete - video quality settings work end-to-end in download flow

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final integration, testing, and quality improvements

- [ ] T065 [P] Add comprehensive error handling for all validation errors across all endpoints in backend/src/routers/
- [ ] T066 [P] Ensure all API responses follow consistent format (status, data, message) in backend/src/routers/
- [ ] T067 [P] Add logging for all settings changes (audit trail) in backend/src/services/settings_service.py
- [ ] T068 [P] Add logging for channel CRUD operations in backend/src/services/channel_service.py
- [ ] T069 [P] Verify all database indexes are created correctly (check with .schema command)
- [ ] T070 [P] Test unique constraint enforcement on Channel.name (attempt duplicate)
- [ ] T071 [P] Test GlobalSettings singleton constraint (attempt second row)
- [ ] T072 [P] Add loading states to all async operations in frontend components
- [ ] T073 [P] Add proper error messages for all validation failures in frontend forms
- [ ] T074 [P] Ensure responsive design works on all Settings and Channels UI in web/src/
- [ ] T075 Test complete workflow: configure global settings → add channel with partial config → verify inheritance → download video → verify settings applied
- [ ] T076 Test edge case: duplicate channel name → verify 409 error with clear message
- [ ] T077 Test edge case: invalid quality/language code → verify validation error
- [ ] T078 Test edge case: change channel custom name → verify update works and old downloads unaffected
- [ ] T079 Test settings persistence: restart backend → verify settings loaded correctly
- [ ] T080 Update README or documentation with new Settings page and channel configuration features

**Checkpoint**: Feature complete, polished, and production-ready

---

## Implementation Strategy

### MVP Scope (Phase 3 - User Story 2)

User Story 2 is the MVP as it's P1 priority and delivers the core value: custom channel names and per-channel settings. This can be delivered first for immediate user benefit.

**MVP Deliverables**:
- Custom channel naming (title vs name distinction)
- Per-channel download path, subtitle language, video quality
- Unique name constraint enforcement
- Enhanced channel list UI showing custom names

### Subsequent Increments

1. **Increment 2**: User Story 1 (Global Defaults) - Adds convenience layer
2. **Increment 3**: User Story 3 (Subtitle Language) - Completes download flow integration
3. **Increment 4**: User Story 4 (Video Quality) - Completes download flow integration
4. **Final**: Polish phase - Error handling, logging, testing

### Parallel Execution Opportunities

**Within User Story 2**:
- Backend tasks T013, T014 can run in parallel
- Backend tasks T018, T019, T020 can run in parallel (different endpoints)
- Frontend tasks T022-T025 can run in parallel (type definitions)
- Frontend tasks T028-T034 can run together after T022-T027 complete

**Across User Stories** (after foundation complete):
- User Story 1 backend (T035-T038) can run in parallel with User Story 2 backend
- User Story 1 frontend (T039-T051) can run after User Story 2 frontend (depends on types)
- User Story 3 and 4 can run in parallel (different aspects of download flow)

**Polish Phase**:
- All tasks T065-T074 are parallelizable (different files/concerns)
- Integration tests T075-T080 run sequentially

---

## Dependencies

### User Story Dependencies

```
Phase 1 (Setup) 
    ↓
Phase 2 (Foundational)
    ↓
    ├─→ Phase 3 (User Story 2 - P1) 🎯 MVP
    │       ↓
    ├─→ Phase 4 (User Story 1 - P2) ← depends on US2 types/infra
    │
    ├─→ Phase 5 (User Story 3 - P2) ← depends on US2 channel settings
    │
    └─→ Phase 6 (User Story 4 - P2) ← depends on US2 channel settings
            ↓
    Phase 7 (Polish) ← depends on all user stories
```

### Task Dependencies Within Phases

**Phase 1**: Sequential (T001-T002 create models, T003 updates init_db.py, T004 runs init script, T005 verifies)

**Phase 2**: 
- T006-T010 parallelizable (different files)
- T011 depends on T001 (uses GlobalSettings model)
- T012 depends on T002 (uses extended Channel model)

**Phase 3 (US2)**:
- Backend: T013-T014 parallel, then T015-T017 sequential (same file), then T018-T021 parallel
- Frontend: T022-T025 parallel, T026-T027 after T022-T023, T028-T034 after T026-T027

**Phase 4 (US1)**:
- Backend: T035-T036 parallel, T037 after T035-T036, T038 anytime
- Frontend: T039-T044 parallel, T045-T051 after T039-T044

**Phase 5 (US3)**: Sequential within backend (T052-T056), frontend (T057-T058) parallel

**Phase 6 (US4)**: Sequential within backend (T059-T062), frontend (T063-T064) parallel

**Phase 7**: Most tasks parallelizable except integration tests (T075-T079) are sequential

---

## Validation Checklist

Before marking feature complete, verify:

- [ ] All 4 user stories pass their independent tests
- [ ] Settings inheritance works correctly (channel → global → hardcoded)
- [ ] Unique constraint on channel name enforced (database + API)
- [ ] All validation errors return clear user-friendly messages
- [ ] Downloads use correct quality and subtitle language from settings
- [ ] Settings page accessible and functional
- [ ] Channel list displays custom names prominently
- [ ] No data loss or corruption during migrations
- [ ] All acceptance scenarios from spec.md pass
- [ ] Constitution compliance maintained (clean architecture, non-blocking I/O)

---

## Total Task Count: 80 tasks

**Breakdown by Phase**:
- Phase 1 (Setup): 5 tasks
- Phase 2 (Foundational): 7 tasks
- Phase 3 (US2 - P1 MVP): 22 tasks
- Phase 4 (US1 - P2): 17 tasks
- Phase 5 (US3 - P2): 7 tasks
- Phase 6 (US4 - P2): 6 tasks
- Phase 7 (Polish): 16 tasks

**Parallel Opportunities**: 31 tasks marked with [P] can be executed in parallel when dependencies met.

**User Story Distribution**:
- User Story 1 (Global Defaults): 17 tasks
- User Story 2 (Custom Names): 22 tasks
- User Story 3 (Subtitle Language): 7 tasks
- User Story 4 (Video Quality): 6 tasks
- Shared/Setup: 28 tasks
