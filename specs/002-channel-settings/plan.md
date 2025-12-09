# Implementation Plan: Channel and Global Download Settings

**Branch**: `002-channel-settings` | **Date**: December 9, 2025 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/002-channel-settings/spec.md`

## Summary

Add global default settings and enhanced channel properties to improve download organization. Users can set system-wide defaults (download path, subtitle language, video quality) that apply to all channels, and customize each channel with a user-defined name, specific settings, and sequential video numbering (0001, 0002, etc.) for easy sorting in Windows File Explorer.

**Technical Approach**: Extend existing database models to add GlobalSettings table (single row) and expand Channel model with new fields (name, title, subtitle_language, video_quality, last_video_index). Update download service to use row-level locking for concurrent index assignment. Add Settings page to UI for global configuration. Implement filename sanitization and sequential numbering in download tasks.

## Technical Context

**Language/Version**: Python 3.10+ (Backend), TypeScript/React 18+ (Frontend)  
**Primary Dependencies**: FastAPI, SQLAlchemy, yt-dlp, Huey (Backend); React, Vite, Shadcn, fetch API (Frontend)  
**Storage**: SQLite for GlobalSettings, Channel, and DownloadedVideo models  
**Testing**: pytest (Backend), Vitest (Frontend)  
**Target Platform**: Linux/Windows server (Backend), Chrome browser (Frontend)  
**Project Type**: Web application (backend + frontend)  
**Performance Goals**: <200ms API responses for read operations, concurrent downloads without index conflicts  
**Constraints**: Row-level locking for index assignment, unique constraint on channel names, no filename truncation  
**Scale/Scope**: ~100 channels, ~10k videos per channel, 3 new database tables/migrations

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Clean Architecture ✅
- ✅ New GlobalSettings model in `/models`
- ✅ Settings repository in `/repository`
- ✅ Settings service in `/services` for business logic
- ✅ New settings router in `/routers`
- ✅ No cross-layer violations

### Non-Blocking I/O ✅
- ✅ Download operations already use Huey task queue
- ✅ Index assignment happens in task (non-blocking)
- ✅ Settings CRUD operations are fast database reads/writes

### Minimal Dependencies ✅
- ✅ No new external dependencies required
- ✅ Uses existing SQLAlchemy, FastAPI, Shadcn stack
- ✅ Standard library for filename sanitization

### Performance-First ✅
- ✅ Database indexes: GlobalSettings.id (PK), Channel.name (unique)
- ✅ Row-level locks prevent concurrent index conflicts
- ✅ Settings read operations <50ms (single table query)

### Static Build Distribution ✅
- ✅ New Settings page uses existing Vite build pipeline
- ✅ No runtime dependencies added

**Gates Passed**: All constitutional principles satisfied. No violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/002-channel-settings/
├── plan.md              # This file
├── spec.md              # Feature specification
├── checklists/
│   └── requirements.md  # Quality checklist
├── research.md          # Phase 0: Research findings (TO BE CREATED)
├── data-model.md        # Phase 1: Database schema (TO BE CREATED)
├── quickstart.md        # Phase 1: User guide (TO BE CREATED)
└── contracts/           # Phase 1: API contracts (TO BE CREATED)
    └── api-spec.md
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── global_settings.py        # NEW: GlobalSettings model
│   │   ├── channel.py                # MODIFY: Add name, title, subtitle_language, video_quality, last_video_index
│   │   └── download_history.py       # MODIFY: Add index_number, has_subtitles fields
│   ├── repository/
│   │   ├── settings_repo.py          # NEW: GlobalSettings CRUD operations
│   │   └── channel_repo.py           # MODIFY: Add unique name validation, lock operations
│   ├── services/
│   │   ├── settings_service.py       # NEW: Settings business logic, inheritance resolution
│   │   ├── channel_service.py        # MODIFY: Add name/title management, settings inheritance
│   │   └── download_service.py       # MODIFY: Sequential naming, filename sanitization, index locking
│   ├── routers/
│   │   ├── settings.py               # NEW: GET/PUT /api/settings endpoints
│   │   └── channels.py               # MODIFY: Update POST/PUT to handle new fields
│   ├── tasks/
│   │   └── download_tasks.py         # MODIFY: Add index assignment with locking, filename formatting
│   └── utils/
│       └── filename_sanitizer.py     # NEW: Sanitize video titles for filesystem
├── migrations/
│   ├── 00X_add_global_settings.py    # NEW: Create GlobalSettings table
│   └── 00Y_extend_channel_model.py   # NEW: Add new Channel fields, unique constraint
└── tests/
    ├── test_settings_service.py      # NEW: Test settings inheritance logic
    ├── test_sequential_naming.py     # NEW: Test index assignment and concurrency
    └── test_filename_sanitization.py # NEW: Test special character handling

frontend/
├── src/
│   ├── components/
│   │   ├── ChannelCard.tsx           # MODIFY: Display custom name prominently
│   │   └── ChannelForm.tsx           # NEW: Form with name, subtitle_language, video_quality inputs
│   ├── pages/
│   │   ├── Settings.tsx              # NEW: Global settings configuration page
│   │   └── Channels.tsx              # MODIFY: Show custom names, add/edit with new fields
│   ├── services/
│   │   ├── settingsApi.ts            # NEW: API calls for global settings
│   │   └── channelApi.ts             # MODIFY: Update channel endpoints with new fields
│   └── types/
│       ├── settings.ts               # NEW: GlobalSettings type definition
│       └── channel.ts                # MODIFY: Add new channel fields
└── tests/
    └── Settings.test.tsx             # NEW: Test Settings page rendering and submission
```

**Structure Decision**: Web application structure (backend + frontend) as defined in constitution. Follows existing layered architecture with models, repository, services, routers. Frontend maintains component-based structure with pages, services, and types.

## Phase 0: Research & Discovery

**Objective**: Resolve all "NEEDS CLARIFICATION" items and establish technical approach.

### Research Tasks

1. **Database Migration Strategy**
   - Document SQLAlchemy Alembic migration approach for adding GlobalSettings table
   - Plan migration for adding fields to existing Channel table without data loss
   - Verify unique constraint behavior in SQLite for Channel.name
   - Determine default values for existing channels (null subtitle_language, null video_quality, 0 last_video_index)

2. **Row-Level Locking in SQLite**
   - Research SQLAlchemy session locking mechanisms (SELECT FOR UPDATE)
   - Verify SQLite support for row-level locks in WAL mode
   - Document transaction isolation level requirements
   - Create proof-of-concept for atomic index increment

3. **Filename Sanitization Best Practices**
   - Identify all filesystem-unsafe characters for Windows/Linux: `< > : " / \ | ? *`
   - Determine safe replacement characters (e.g., `-` for `:`, `_` for `|`)
   - Handle Unicode characters in video titles (preserve UTF-8)
   - Research Python libraries: `pathlib.Path`, `unicodedata.normalize`

4. **ISO 639-1 Language Code Validation**
   - Compile list of supported yt-dlp subtitle language codes
   - Create validation enum or list for API input validation
   - Document fallback behavior when language not available

5. **Video Quality Format Validation**
   - Document yt-dlp quality format strings: "best", "worst", "1080p", "720p", etc.
   - Create validation pattern for quality input
   - Determine fallback quality selection algorithm

### Deliverable: `research.md`

Document all findings with code examples, chosen approaches, and rationale. Format:

```markdown
# Research: Channel and Global Download Settings

## Database Migrations
[Approach, code examples, migration commands]

## Row-Level Locking
[Implementation approach, transaction patterns, code examples]

## Filename Sanitization
[Character mapping table, implementation approach, edge cases]

## Language & Quality Validation
[Supported values, validation implementation]
```

## Phase 1: Design & Contracts

**Objective**: Design database schema, API contracts, and user workflows.

### Design Tasks

1. **Database Schema Design** → `data-model.md`
   
   ```sql
   -- GlobalSettings Table
   CREATE TABLE global_settings (
       id INTEGER PRIMARY KEY CHECK (id = 1),
       default_download_path TEXT NOT NULL DEFAULT './download',
       default_subtitle_language TEXT,
       default_video_quality TEXT
   );
   
   -- Channel Table Updates
   ALTER TABLE channels ADD COLUMN title TEXT;  -- Renamed from name
   ALTER TABLE channels ADD COLUMN name TEXT NOT NULL UNIQUE;  -- NEW: User custom name
   ALTER TABLE channels ADD COLUMN subtitle_language TEXT;
   ALTER TABLE channels ADD COLUMN video_quality TEXT;
   ALTER TABLE channels ADD COLUMN last_video_index INTEGER NOT NULL DEFAULT 0;
   
   -- DownloadedVideo Table Updates (if tracking)
   ALTER TABLE download_history ADD COLUMN index_number INTEGER;
   ALTER TABLE download_history ADD COLUMN has_subtitles BOOLEAN;
   ```

2. **API Contract Definition** → `contracts/api-spec.md`
   
   **New Endpoints**:
   - `GET /api/settings` - Retrieve global settings
   - `PUT /api/settings` - Update global settings
   
   **Modified Endpoints**:
   - `POST /api/channels` - Add `name`, `title`, `subtitle_language`, `video_quality`
   - `PUT /api/channels/{id}` - Update including new fields
   - `GET /api/channels` - Response includes all new fields

3. **User Workflow Documentation** → `quickstart.md`
   
   Cover:
   - How to configure global defaults in Settings page
   - How to add a channel with custom name and settings
   - How to edit channel settings
   - How sequential video naming works
   - How settings inheritance works (global → channel)

### Constitution Re-Check

After design phase, verify:
- ✅ Clean architecture maintained (no business logic in routers)
- ✅ Database schema follows existing patterns
- ✅ API design consistent with existing endpoints
- ✅ No new dependencies introduced

### Deliverables

- `data-model.md` - Complete database schema with constraints, indexes, relationships
- `contracts/api-spec.md` - OpenAPI-style endpoint documentation
- `quickstart.md` - User-facing guide with examples

## Phase 2: Implementation Planning

**Objective**: Break down implementation into concrete tasks (done via `/speckit.tasks` command - NOT in this plan).

### Task Categories (Preview)

1. **Database Layer** (Backend)
   - Create migrations for GlobalSettings and Channel updates
   - Implement GlobalSettings model and repository
   - Update Channel model with new fields and unique constraint
   - Add indexes for performance

2. **Business Logic** (Backend)
   - Implement settings service with inheritance logic
   - Update channel service with name/title management
   - Modify download service for sequential naming and locking
   - Create filename sanitization utility

3. **API Layer** (Backend)
   - Create settings router with GET/PUT endpoints
   - Update channels router for new fields
   - Add validation for language codes and quality formats

4. **Task Queue** (Backend)
   - Modify download tasks to use row-level locks
   - Implement sequential index assignment
   - Add filename formatting with sanitization

5. **UI Components** (Frontend)
   - Create Settings page with global defaults form
   - Update ChannelCard to display custom names
   - Create/update ChannelForm with new fields
   - Add validation and error handling

6. **API Integration** (Frontend)
   - Implement settings API client
   - Update channel API client with new fields
   - Add type definitions for new structures

7. **Testing**
   - Unit tests for settings inheritance logic
   - Integration tests for concurrent index assignment
   - E2E tests for Settings page and channel management
   - Edge case tests (duplicate names, path length, etc.)

**Note**: Detailed task breakdown with acceptance criteria, test cases, and implementation order will be created by `/speckit.tasks` command in Phase 2.

## Key Implementation Considerations

### 1. Database Migration Order

**Critical**: Migrations must be applied in correct order to avoid data loss:

1. Add new columns to `channels` table (nullable initially)
2. Migrate existing `channels.name` → `channels.title`
3. Populate `channels.name` with sanitized version of title
4. Add unique constraint on `channels.name`
5. Create `global_settings` table with default row

### 2. Row-Level Locking Pattern

```python
# Pseudocode for atomic index assignment
with db.session.begin():
    channel = db.session.query(Channel)\
        .filter(Channel.id == channel_id)\
        .with_for_update()\
        .first()
    
    next_index = channel.last_video_index + 1
    channel.last_video_index = next_index
    db.session.commit()
    
    return next_index
```

### 3. Settings Inheritance Logic

```python
def resolve_download_path(channel, global_settings):
    if channel.download_path:
        return channel.download_path
    base_path = global_settings.default_download_path or "./download"
    return f"{base_path}/{channel.name}"

def resolve_subtitle_language(channel, global_settings):
    return channel.subtitle_language or global_settings.default_subtitle_language

def resolve_video_quality(channel, global_settings):
    return channel.video_quality or global_settings.default_video_quality or "best"
```

### 4. Filename Sanitization

```python
UNSAFE_CHARS = {
    ':': '-',
    '/': '-',
    '\\': '-',
    '|': '_',
    '?': '',
    '*': '',
    '<': '',
    '>': '',
    '"': "'"
}

def sanitize_filename(title: str) -> str:
    for unsafe, safe in UNSAFE_CHARS.items():
        title = title.replace(unsafe, safe)
    return title.strip()
```

### 5. Sequential Filename Format

```python
def format_video_filename(index: int, title: str, extension: str) -> str:
    sanitized_title = sanitize_filename(title)
    # Determine padding based on index magnitude
    if index < 10000:
        index_str = f"{index:04d}"  # 0001-9999
    else:
        index_str = f"{index:05d}"  # 10000+
    
    return f"{index_str}_{sanitized_title}.{extension}"
```

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Migration breaks existing channels | HIGH | Test migrations on copy of production DB, add rollback scripts |
| Row-level locking not supported in SQLite | HIGH | Enable WAL mode, verify with integration tests, document SQLite version requirement |
| Long paths exceed OS limits | MEDIUM | Provide clear error messages, document path length constraints in UI |
| Duplicate name conflicts during migration | MEDIUM | Pre-migration script to detect and resolve duplicates |
| UI breaks for existing users | LOW | Feature flag for Settings page, graceful fallbacks for missing global settings |

## Success Metrics

**Implementation Complete When**:
- ✅ All 38 functional requirements (FR-001 to FR-030, including sub-requirements) implemented and tested
- ✅ 5 user stories have passing acceptance tests
- ✅ 8 edge cases handled with appropriate error messages
- ✅ Database migrations tested with existing data
- ✅ Concurrent downloads assign unique sequential indices 100% of time
- ✅ Settings page accessible and functional
- ✅ Channel management UI displays custom names and allows editing all new fields

**Verification**:
- Run integration test suite with concurrent download scenarios
- Manual testing of settings inheritance (global → channel)
- Path length edge case testing with extremely long titles
- Load test with 100 channels and 1000 videos per channel

## Next Steps

1. ✅ **Phase 0 Complete**: Run `/speckit.plan` to generate `research.md`
2. ⏳ **Phase 1 Pending**: Complete research, then generate `data-model.md`, `contracts/api-spec.md`, `quickstart.md`
3. ⏳ **Phase 2 Pending**: Run `/speckit.tasks` to generate `tasks.md` with detailed implementation tasks

**Current Status**: Phase 0 (Research) - Ready to begin research tasks
