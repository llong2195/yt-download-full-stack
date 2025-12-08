<!--
SYNC IMPACT REPORT
==================
Version Change: 0.0.0 → 1.0.0
Rationale: Initial constitution establishing core architectural principles and governance

Principles Defined:
- I. Clean Architecture (NEW)
- II. Non-Blocking I/O (NEW)
- III. Minimal Dependencies (NEW)
- IV. Performance-First (NEW)
- V. Static Build Distribution (NEW)

Sections Added:
- Technology Stack (Backend/Frontend requirements)
- Code Organization Standards (directory structure rules)
- Development Standards (code quality expectations)
- Governance (amendment and compliance procedures)

Templates Status:
✅ plan-template.md - Aligned (supports backend/frontend web app structure)
✅ spec-template.md - Aligned (supports functional requirements and user stories)
✅ tasks-template.md - Aligned (supports web app structure with backend/frontend phases)

Follow-up Items:
- None

Generated: 2025-12-08
-->

# YouTube Download Full-Stack Constitution

## Core Principles

### I. Clean Architecture

Backend MUST follow layered architecture with clear separation of concerns:

- `/models` - Data models and database schemas only
- `/repository` - Database access layer, no business logic
- `/services` - Business logic, orchestrates repositories and external services
- `/routers` - API endpoints, thin controllers delegating to services

**Rationale**: Maintains code clarity, testability, and scalability. Each layer has a single responsibility and can be tested independently.

### II. Non-Blocking I/O

Heavy operations MUST NOT block the main API thread:

- All download operations MUST use Huey task queue
- Check database for existing downloads BEFORE enqueueing tasks
- yt-dlp execution MUST run asynchronously via Huey
- API endpoints MUST return immediately with task status

**Rationale**: Ensures API responsiveness and enables horizontal scaling. Users get instant feedback while operations complete in the background.

### III. Minimal Dependencies

Code MUST prioritize simplicity and minimal external dependencies:

- Only use libraries that solve critical problems
- Prefer standard library solutions when performance is acceptable
- Document justification for each non-trivial dependency
- Frontend MUST use only: React, TypeScript, Vite, Shadcn, native fetch API

**Rationale**: Reduces maintenance burden, security surface area, and build complexity. Easier to understand and debug.

### IV. Performance-First

System MUST prioritize performance and stability:

- Database queries MUST be indexed appropriately
- API responses MUST be under 200ms for read operations (excluding downloads)
- Memory usage MUST remain predictable under load
- Task queue MUST handle failures gracefully with retries
- Frontend MUST render smoothly without blocking UI thread

**Rationale**: User experience depends on responsiveness. Performance issues are harder to fix later than to prevent early.

### V. Static Build Distribution

Frontend build MUST be fully self-contained:

- Vite MUST produce `dist/` folder with all assets bundled
- Built application MUST run on any HTTP server without node_modules
- No runtime dependencies on Node.js or build tools
- Configuration MUST be injectable at runtime (environment variables or config file)

**Rationale**: Enables simple deployment, portability across servers, and easy distribution. Separates build-time from runtime concerns.

## Technology Stack

### Backend Requirements

- **Framework**: FastAPI for REST API
- **Database**: SQLite for channels, download history, and task status
- **Task Queue**: Huey with SQLite backend (integrated, no separate process)
- **Download Tool**: yt-dlp for YouTube video downloads
- **Python Version**: 3.10 or higher

### Frontend Requirements

- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite for fast builds and HMR
- **UI Library**: Shadcn components
- **HTTP Client**: Native fetch API (preferred) or Axios when necessary
- **Package Manager**: pnpm (as evidenced by pnpm-lock.yaml)

## Code Organization Standards

### Backend Structure

```
backend/
├── models/          # SQLAlchemy models, Pydantic schemas
├── repository/      # Database access layer (CRUD operations)
├── services/        # Business logic (download orchestration, channel management)
├── routers/         # FastAPI route handlers
├── tasks/           # Huey task definitions
├── utils/           # Helper functions, constants
└── main.py          # Application entry point, Huey integration
```

### Frontend Structure

```
web/
├── src/
│   ├── components/  # Reusable UI components
│   ├── pages/       # Page-level components (channel list, history, queue status)
│   ├── services/    # API client functions (axios wrappers)
│   ├── types/       # TypeScript type definitions
│   └── utils/       # Helper functions
├── public/          # Static assets
└── dist/            # Build output (generated)
```

## Development Standards

### Code Quality

- Code MUST be self-documenting with clear naming
- Complex logic MUST include explanatory comments
- API endpoints MUST have Pydantic request/response models
- TypeScript MUST have strict mode enabled
- No `any` types except when absolutely necessary with justification

### Error Handling

- All exceptions MUST be caught and logged
- API errors MUST return appropriate HTTP status codes
- Task failures MUST be logged with full context
- User-facing errors MUST be clear and actionable

### Security

- API MUST validate all inputs
- Database queries MUST use parameterized statements (SQLAlchemy ORM)
- File paths MUST be sanitized
- CORS MUST be configured appropriately for Chrome extension integration

## Governance

This constitution supersedes all other development practices and preferences.

**Amendment Process**:

1. Proposed changes MUST be documented with rationale
2. Impact on existing code MUST be assessed
3. Migration plan MUST be created if breaking changes
4. Version MUST be bumped according to semantic versioning

**Compliance**:

- All code reviews MUST verify constitutional compliance
- Architectural deviations MUST be explicitly justified in PR description
- Template files (plan, spec, tasks) MUST align with constitution

**Versioning**:

- MAJOR: Principle removed/redefined, breaking governance changes
- MINOR: New principle added, section expanded
- PATCH: Clarifications, wording improvements, non-semantic changes

**Version**: 1.0.1 | **Ratified**: 2025-12-08 | **Last Amended**: 2025-12-08
