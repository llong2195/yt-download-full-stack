# Implementation Plan: Channel and Global Download Settings

                                                                     **Branch**: `002-channel-settings` | **Date**: December 9, 2025 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-channel-settings/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This feature adds system-wide default settings (download path, subtitle language, video quality) and enhances channel management with custom naming. The Channel model will be extended to include both YouTube's channel title and user-defined custom names, along with per-channel download settings that inherit from global defaults. A new GlobalSettings table will store system-wide defaults, and the download service will use a fallback chain: channel-specific → global → hardcoded defaults.

## Technical Context

**Language/Version**: Python 3.10+, TypeScript 5.x  
**Primary Dependencies**: FastAPI, SQLAlchemy, React 18, Vite, Shadcn UI, yt-dlp  
**Storage**: SQLite database (schema managed via SQLAlchemy `Base.metadata.create_all()`)  
**Testing**: pytest (backend), Vitest (frontend)  
**Target Platform**: Web application (Windows/Linux/Mac server, modern browsers)  
**Project Type**: Web application (full-stack)  
**Performance Goals**: <200ms API response for read operations, <50ms database queries  
**Constraints**: Non-blocking I/O for all downloads, clean architecture with layered separation  
**Scale/Scope**: ~100 channels per user, 4 new database models/tables, 8 new API endpoints, 2 new UI pages

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Clean Architecture ✅ PASS
- Models: New `GlobalSettings` model, extended `Channel` model with additional fields
- Repository: New `SettingsRepository` for global settings CRUD, extend `ChannelRepository`
- Services: Extend `ChannelService` with settings inheritance logic
- Routers: New `/api/settings` endpoints, extend `/api/channels` endpoints

**Rationale**: Maintains existing layered architecture pattern. No violations.

### II. Non-Blocking I/O ✅ PASS
- No blocking operations introduced
- Settings are lightweight configuration data (read from database)
- Download operations continue to use existing Huey task queue
- API endpoints return immediately

**Rationale**: Settings management is CRUD operations only. No long-running tasks.

### III. Minimal Dependencies ✅ PASS
- No new external dependencies required
- Uses existing SQLAlchemy for database operations
- Schema changes handled by updating models and running init_db.py (no Alembic)
- Frontend uses existing Shadcn UI components

**Rationale**: Feature built entirely on existing stack. Project uses direct SQLAlchemy schema creation rather than migration framework.

### IV. Performance-First ✅ PASS
- Database queries indexed appropriately (channel.name unique index)
- GlobalSettings accessed once per download (cacheable)
- No N+1 query patterns introduced
- Settings inheritance logic is O(1) lookup

**Rationale**: Simple database lookups with proper indexing. No performance concerns.

### V. Static Build Distribution ✅ PASS
- No changes to build process
- Frontend changes are component additions only
- No runtime dependencies added

**Rationale**: Standard React components, no impact on build/distribution.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── global_settings.py        # NEW: GlobalSettings model
│   │   ├── channel.py                 # MODIFIED: Add title, subtitle_language, video_quality fields
│   │   └── schemas.py                 # MODIFIED: Add request/response schemas
│   ├── repository/
│   │   ├── settings_repo.py          # NEW: CRUD for global settings
│   │   └── channel_repo.py            # MODIFIED: Support new channel fields
│   ├── services/
│   │   ├── settings_service.py       # NEW: Settings business logic
│   │   ├── channel_service.py         # MODIFIED: Settings inheritance logic
│   │   └── download_service.py        # MODIFIED: Use channel/global settings
│   ├── routers/
│   │   ├── settings.py               # NEW: /api/settings endpoints
│   │   └── channels.py                # MODIFIED: Extended channel endpoints
│   └── utils/
│       └── validators.py              # MODIFIED: Add language/quality validators
├── init_db.py                         # MODIFIED: Add GlobalSettings singleton creation
└── tests/
    ├── test_settings_service.py      # NEW: Settings tests
    └── test_channel_service.py        # MODIFIED: Test settings inheritance

web/
├── src/
│   ├── components/
│   │   ├── SettingsForm.tsx          # NEW: Global settings form
│   │   └── ChannelCard.tsx            # MODIFIED: Show custom name prominently
│   ├── pages/
│   │   ├── Settings.tsx               # NEW: Settings management page
│   │   └── Channels.tsx               # MODIFIED: Add custom name field
│   ├── services/
│   │   ├── settingsApi.ts            # NEW: Settings API client
│   │   └── channelApi.ts              # MODIFIED: Extended channel API
│   └── types/
│       ├── settings.ts               # NEW: Settings types
│       └── channel.ts                 # MODIFIED: Add new channel fields
```

**Structure Decision**: Web application (backend + frontend). Follows existing clean architecture with models/repository/services/routers separation on backend, and components/pages/services separation on frontend.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitutional violations. All checks passed. This section is not needed.

---

## Phase 1 Re-evaluation of Constitution Check

*Re-checked after completing data model and API contracts design.*

### I. Clean Architecture ✅ PASS (Confirmed)
- Data model clearly separates concerns (GlobalSettings, Channel entities)
- API contracts follow RESTful conventions
- No business logic in models or routes
- Clear separation of validation (validators), data access (repository), and business logic (services)

### II. Non-Blocking I/O ✅ PASS (Confirmed)
- All operations are simple CRUD (database reads/writes)
- No long-running processes introduced
- Settings inheritance is in-memory calculation
- Download operations remain async via Huey

### III. Minimal Dependencies ✅ PASS (Confirmed)
- No new dependencies required in research phase
- Quickstart confirms implementation uses only existing stack
- Pydantic for validation, SQLAlchemy for ORM, Shadcn for UI

### IV. Performance-First ✅ PASS (Confirmed)
- Data model includes appropriate indexes
- Settings queries cacheable (GlobalSettings is singleton)
- No complex joins or N+1 queries
- API response time estimates under 200ms for read operations

### V. Static Build Distribution ✅ PASS (Confirmed)
- No impact on frontend build process
- No new runtime dependencies
- Vite build produces standard static assets

**Final Assessment**: All constitutional principles upheld. Design approved for implementation.
