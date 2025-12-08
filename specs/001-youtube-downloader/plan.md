# Implementation Plan: YouTube Downloader Full-Stack Application

**Branch**: `001-youtube-downloader` | **Date**: 2025-12-08 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-youtube-downloader/spec.md`

## Summary

Build a full-stack YouTube downloader application with FastAPI backend and React frontend. Users manage YouTube channels, request video downloads that run asynchronously via Huey task queue using yt-dlp, monitor download status in real-time, and browse download history. The system prevents duplicate downloads, handles failures with retries, and ensures non-blocking I/O throughout. Frontend builds to a portable dist/ folder that runs on any HTTP server.

## Technical Context

**Language/Version**: Python 3.10+, TypeScript 5.x  
**Primary Dependencies**: FastAPI, SQLAlchemy, Huey, yt-dlp, React 18+, Vite, Shadcn  
**Storage**: SQLite (channels, videos, download_history, task_queue)  
**Testing**: pytest (backend), Vitest or Jest (frontend - NEEDS CLARIFICATION)  
**Target Platform**: Web application - backend server (Linux/Windows/macOS), frontend browser (Chrome, Firefox, Edge)  
**Project Type**: Web (backend + frontend)  
**Performance Goals**: API <200ms p95 (read ops), database queries <50ms, 10+ concurrent downloads, search 1000+ records <1s  
**Constraints**: Non-blocking I/O mandatory, SQLite size limits (<100GB), single-server deployment, native fetch API only  
**Scale/Scope**: Single-user MVP, ~2000 LOC backend, ~1500 LOC frontend, 4 main pages, 15-20 API endpoints

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

### Principle I: Clean Architecture ✅

**Status**: COMPLIANT

- Backend follows `/models`, `/repository`, `/services`, `/routers` structure per constitution
- Each layer has single responsibility: data, persistence, business logic, API
- Spec explicitly requires Clean Architecture in FR-010

### Principle II: Non-Blocking I/O ✅

**Status**: COMPLIANT

- All download operations via Huey task queue (FR-004, FR-007)
- Database check before enqueueing (FR-005)
- Immediate API responses with task status (FR-008)
- yt-dlp runs asynchronously, never blocks API thread

### Principle III: Minimal Dependencies ✅

**Status**: COMPLIANT

- Backend: FastAPI, SQLAlchemy, Huey, yt-dlp (all essential)
- Frontend: React, TypeScript, Vite, Shadcn, native fetch (constitution-mandated)
- No unnecessary libraries, each dependency solves critical problem
- Native fetch preferred over axios per constitution v1.0.1

### Principle IV: Performance-First ✅

**Status**: COMPLIANT

- API <200ms for read operations (FR-011, constitution requirement)
- Database queries with proper indexing (FR-013)
- Task failures handled gracefully with retry logic (FR-009)
- Frontend renders without blocking UI thread (FR-023)
- Specific performance metrics in success criteria (SC-002, SC-007, SC-009)

### Principle V: Static Build Distribution ✅

**Status**: COMPLIANT

- Vite produces standalone dist/ folder (FR-017)
- Runs on any HTTP server without Node.js (FR-024)
- No runtime dependencies on build tools
- Constitution requirement explicitly met

### Gate Result: ✅ PASS

All 5 constitutional principles satisfied. No violations requiring justification. Proceed to Phase 0 research.

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
├── models/
│   ├── __init__.py
│   ├── database.py          # SQLAlchemy setup, session management
│   ├── channel.py           # Channel SQLAlchemy model
│   ├── video.py             # Video SQLAlchemy model
│   ├── download_task.py     # DownloadTask SQLAlchemy model
│   └── schemas.py           # Pydantic request/response schemas
├── repository/
│   ├── __init__.py
│   ├── channel_repo.py      # Channel CRUD operations
│   ├── video_repo.py        # Video CRUD operations
│   └── download_repo.py     # Download task/history CRUD
├── services/
│   ├── __init__.py
│   ├── channel_service.py   # Channel management business logic
│   ├── download_service.py  # Download orchestration, duplicate checking
│   ├── queue_service.py     # Huey task queue interaction
│   └── youtube_service.py   # YouTube metadata extraction (yt-dlp)
├── routers/
│   ├── __init__.py
│   ├── channels.py          # Channel CRUD endpoints
│   ├── downloads.py         # Download initiation endpoints
│   ├── queue.py             # Queue status endpoints
│   └── history.py           # Download history endpoints
├── tasks/
│   ├── __init__.py
│   └── download_tasks.py    # Huey task definitions for yt-dlp execution
├── utils/
│   ├── __init__.py
│   ├── logger.py            # Logging configuration
│   ├── validators.py        # URL/path sanitization
│   └── config.py            # Configuration management
├── main.py                  # FastAPI app, Huey integration, CORS setup
└── requirements.txt         # Python dependencies

web/
├── src/
│   ├── components/
│   │   ├── ChannelCard.tsx       # Channel display card
│   │   ├── ChannelList.tsx       # Channel list component
│   │   ├── VideoCard.tsx         # Video item display
│   │   ├── QueueItem.tsx         # Queue task display
│   │   ├── HistoryItem.tsx       # History record display
│   │   └── ui/                   # Shadcn components
│   ├── pages/
│   │   ├── Channels.tsx          # Channel management page
│   │   ├── Downloads.tsx         # Video download page
│   │   ├── Queue.tsx             # Queue status monitoring
│   │   └── History.tsx           # Download history & search
│   ├── services/
│   │   ├── api.ts                # Base fetch wrapper, error handling
│   │   ├── channelApi.ts         # Channel API calls
│   │   ├── downloadApi.ts        # Download API calls
│   │   ├── queueApi.ts           # Queue status API calls
│   │   └── historyApi.ts         # History API calls
│   ├── types/
│   │   ├── channel.ts            # Channel type definitions
│   │   ├── video.ts              # Video type definitions
│   │   ├── download.ts           # Download task types
│   │   └── api.ts                # API response types
│   ├── utils/
│   │   ├── formatters.ts         # Date, size, duration formatters
│   │   └── validators.ts         # URL validation
│   ├── App.tsx                   # Main app component, routing
│   ├── main.tsx                  # React entry point
│   └── index.css                 # Global styles
├── public/                       # Static assets
├── dist/                         # Build output (generated)
├── package.json
├── tsconfig.json
├── vite.config.ts
└── pnpm-lock.yaml

downloads/                        # Video storage directory (created at runtime)
data/                            # SQLite database file location (created at runtime)
└── app.db
```

**Structure Decision**: Web application structure (Option 2) selected. This is a full-stack web application with:

- **Backend**: Python backend at repository root `/backend` following constitutional clean architecture
- **Frontend**: React frontend at repository root `/web` with Vite build system
- **Separation**: Backend and frontend are clearly separated, can be deployed independently
- **Constitution Alignment**: Matches exact structure defined in constitution Code Organization Standards

## Complexity Tracking

No constitutional violations detected. All architectural decisions align with constitution v1.0.1 principles.

---

## Phase 0 Output: Research

**File**: [research.md](research.md)

**Completed**: 2025-12-08

**Summary**: Resolved all technical unknowns:

- Frontend testing framework: Vitest (native Vite integration)
- Huey integration: Consumer thread in FastAPI lifespan event
- yt-dlp usage: Python library with progress hooks (not CLI)
- SQLite concurrency: WAL mode + connection pooling
- Real-time updates: HTTP polling (2.5s interval)
- CORS: Allow chrome-extension:// origins
- File storage: UUID-based subdirectories for security
- Error handling: Structured responses with user/developer messages

All NEEDS CLARIFICATION items from Technical Context resolved.

---

## Phase 1 Output: Design Artifacts

### Data Model

**File**: [data-model.md](data-model.md)

**Completed**: 2025-12-08

**Entities Designed**:

- **Channel**: YouTube channel tracking (4 attributes, 2 indexes)
- **Video**: Downloadable videos (10 attributes, 3 indexes, 1 FK)
- **DownloadTask**: Queue task tracking (10 attributes, 4 indexes, 1 FK)
- **DownloadHistory**: Audit log (7 attributes, 4 indexes, 1 FK)

**Relationships**:

- Channel (1) → Video (N) - CASCADE delete
- Video (1) → DownloadTask (N) - CASCADE delete
- Video (1) → DownloadHistory (N) - CASCADE delete

**Database Schema**: Full SQLite SQL + SQLAlchemy models + TypeScript interfaces provided

### API Contracts

**File**: [contracts/api-spec.md](contracts/api-spec.md)

**Completed**: 2025-12-08

**Endpoints Designed**: 19 total

- **Channels**: GET /channels, POST /channels, DELETE /channels/{id}
- **Videos**: GET /channels/{id}/videos, POST /videos/fetch
- **Downloads**: POST /downloads, POST /downloads/batch
- **Queue**: GET /queue/status, GET /queue/tasks/{id}, POST /queue/tasks/{id}/retry
- **History**: GET /history, GET /history/stats
- **Health**: GET /health

**Error Codes**: 13 defined (INVALID_URL, ALREADY_DOWNLOADED, RATE_LIMIT, etc.)

**Request/Response Schemas**: All endpoints have Pydantic-compatible JSON schemas

### Quickstart Guide

**File**: [quickstart.md](quickstart.md)

**Completed**: 2025-12-08

**Sections**:

- Prerequisites & installation
- Quick setup (5 minutes)
- Detailed configuration
- Running the application (dev & production)
- Testing guide
- Troubleshooting
- Deployment checklist

### Agent Context Update

**File**: `.github/agents/copilot-instructions.md`

**Completed**: 2025-12-08

Added to agent context:

- Languages: Python 3.10+, TypeScript 5.x
- Frameworks: FastAPI, SQLAlchemy, Huey, yt-dlp, React 18+, Vite, Shadcn
- Database: SQLite (channels, videos, download_history, task_queue)
- Project type: Web (backend + frontend)

---

## Post-Design Constitution Re-Check ✅

**Status**: ALL PRINCIPLES COMPLIANT

### Verification Against Design Artifacts

**Principle I: Clean Architecture** ✅

- Data model separates concerns: models, repository layer implied, services layer implied
- API contracts show thin controller pattern (routers)
- No business logic in models or routers
- Clear layer boundaries maintained in design

**Principle II: Non-Blocking I/O** ✅

- API contracts show 202 Accepted for downloads (async)
- DownloadTask entity tracks async operations
- Queue status endpoint enables monitoring without blocking
- Research documents consumer thread pattern

**Principle III: Minimal Dependencies** ✅

- Only essential dependencies in design
- No unnecessary libraries introduced
- Native fetch API maintained in quickstart
- Shadcn used as specified in constitution

**Principle IV: Performance-First** ✅

- Database indexes designed for common queries
- API contracts specify appropriate status codes (no unnecessary processing)
- Polling interval (2.5s) balances responsiveness with load
- SQLite WAL mode enables concurrent access
- Success criteria include performance metrics

**Principle V: Static Build Distribution** ✅

- Quickstart documents Vite build process
- dist/ folder deployment clearly described
- No runtime dependencies on Node.js in production
- Multiple HTTP server options documented

### Design Quality Gates

- [x] Data model has proper indexes and constraints
- [x] API contracts define clear error codes and messages
- [x] All entities have validation rules
- [x] Relationships use CASCADE deletes appropriately
- [x] No N+1 query patterns in design
- [x] Quickstart is executable (step-by-step, no gaps)
- [x] Research resolves all technical unknowns
- [x] Agent context updated with project technologies

### Final Gate: ✅ PASS

Design phase complete. All constitutional principles maintained. Ready for Phase 2: Task breakdown (`/speckit.tasks` command).

---

## Next Steps

1. **Run `/speckit.tasks`** to generate implementation task list organized by user story
2. **Begin implementation** starting with Phase 1 (Setup) and Phase 2 (Foundation) from tasks.md
3. **Implement user stories** in priority order (P1 → P2 → P3 → P4)
4. **Validate each story independently** before moving to next priority

---

## Artifacts Checklist

- [x] plan.md - This file (implementation plan with technical context, structure, constitution checks)
- [x] research.md - Technical research resolving unknowns (8 research items documented)
- [x] data-model.md - Database schema, entities, relationships, SQLAlchemy models, TypeScript interfaces
- [x] contracts/api-spec.md - REST API specification with 19 endpoints, error codes, schemas
- [x] quickstart.md - Setup and deployment guide with prerequisites, configuration, troubleshooting
- [x] .github/agents/copilot-instructions.md - Agent context file updated with project stack
- [ ] tasks.md - Implementation task list (Phase 2 - NOT created by /speckit.plan, use /speckit.tasks)
