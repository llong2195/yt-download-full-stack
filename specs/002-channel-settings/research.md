# Research: Channel and Global Download Settings

**Date**: December 9, 2025  
**Feature**: Channel and Global Download Settings  
**Status**: Complete

## Overview

This document consolidates research findings for implementing global settings and enhanced channel properties in the YouTube downloader application. No technical unknowns existed; research focused on best practices for settings management, database migrations, and settings inheritance patterns.

## Research Areas

### 1. Global Settings Storage Strategy

**Decision**: Single-row table pattern with id=1

**Rationale**:
- Simplest approach for application-wide configuration
- Easy to query and update (no need to check existence)
- Supports future expansion by adding columns
- Standard pattern for single-tenant applications
- SQLAlchemy ORM handles it naturally

**Alternatives Considered**:
- **Environment variables**: Rejected because settings need to be user-configurable at runtime through UI
- **JSON config file**: Rejected because it requires file I/O permissions and doesn't leverage existing database infrastructure
- **Key-value table**: More complex querying, unnecessary overhead for small number of settings

**Implementation Notes**:
- Create table with default row in migration
- Repository layer ensures row exists before any operation
- Use `get_or_create()` pattern in repository for safety

### 2. Database Schema Migration Strategy

**Decision**: Update SQLAlchemy models and use `Base.metadata.create_all()` with manual data migration script if needed

**Rationale**:
- Project does not use Alembic migrations (migrations/ folder is empty)
- Existing pattern: Update model classes → run `python backend/init_db.py`
- SQLAlchemy detects schema changes and creates missing columns automatically
- Simpler for small-scale projects without complex migration history

**Implementation Order**:
1. Create `GlobalSettings` model class in `backend/src/models/global_settings.py`
2. Extend `Channel` model with new fields in `backend/src/models/channel.py`
3. Update `init_db.py` to create GlobalSettings singleton row after table creation
4. Run `python backend/init_db.py` to apply schema changes
5. Write one-time data migration script if needed to populate new fields on existing channels

**Alternatives Considered**:
- **Alembic migrations**: More robust for production, but project doesn't currently use it. Adding Alembic mid-project requires setup and historical migration files
- **Manual SQL scripts**: Error-prone and doesn't leverage ORM benefits

**Implementation Notes**:
- For new columns on Channel: Add with `nullable=True` or provide `server_default` values
- Existing `name` field becomes `title`, add new `name` field with default value
- Backup database before schema changes: `cp backend/data/ytdownloader.db backend/data/ytdownloader.db.backup`
- Test schema changes on copy of production database first

### 3. Settings Inheritance Pattern

**Decision**: Three-tier fallback chain (channel → global → hardcoded)

**Rationale**:
- Provides maximum flexibility without complexity
- Clear priority: most specific wins
- System always works even without configuration
- Easy to understand for users

**Implementation**:
```python
def get_effective_setting(channel, global_settings, setting_name, hardcoded_default):
    """
    Retrieves effective value for a setting using fallback chain.
    
    Priority: channel-specific > global default > hardcoded default
    """
    channel_value = getattr(channel, setting_name, None)
    if channel_value is not None:
        return channel_value
    
    global_value = getattr(global_settings, f"default_{setting_name}", None)
    if global_value is not None:
        return global_value
    
    return hardcoded_default
```

**Alternatives Considered**:
- **Only global settings**: Less flexible, doesn't support per-channel customization
- **Only channel settings**: Requires repeating configuration for every channel
- **Complex inheritance with overrides**: Too complex for user understanding

### 4. Channel Name Uniqueness Enforcement

**Decision**: Database unique constraint + application-level validation

**Rationale**:
- Database constraint prevents race conditions
- Application validation provides user-friendly error messages
- Dual layer ensures data integrity

**Implementation Notes**:
- Add unique index on `Channel.name` in migration
- Catch SQLAlchemy IntegrityError in repository layer
- Convert to domain exception in service layer
- Return appropriate HTTP 409 Conflict with clear message

**Alternatives Considered**:
- **Application-level only**: Race condition risk with concurrent requests
- **Database-level only**: Generic error messages, poor UX

### 5. Video Quality and Subtitle Language Validation

**Decision**: Whitelist validation with yt-dlp integration check

**Rationale**:
- yt-dlp supports specific quality formats
- ISO 639-1 codes are standard for languages
- Early validation prevents runtime errors
- Clear error messages guide users

**Supported Quality Formats**:
- Keywords: `best`, `worst`, `bestaudio`, `bestvideo`
- Resolutions: `2160p`, `1440p`, `1080p`, `720p`, `480p`, `360p`, `240p`, `144p`
- Format codes: validated against yt-dlp's available formats

**Supported Language Codes** (ISO 639-1):
- Common: `en`, `ja`, `ko`, `zh`, `vi`, `es`, `fr`, `de`, `ru`, `ar`, `pt`, `it`
- All ISO 639-1 two-letter codes supported
- Validation uses pycountry or hardcoded list

**Implementation Notes**:
```python
VALID_QUALITY_KEYWORDS = ["best", "worst", "bestaudio", "bestvideo"]
VALID_RESOLUTIONS = ["2160p", "1440p", "1080p", "720p", "480p", "360p", "240p", "144p"]
VALID_LANGUAGES = ["en", "ja", "ko", "zh", "vi", "es", "fr", "de", "ru", "ar", "pt", "it", "th", "pl", "nl"]

def validate_quality(quality: str) -> bool:
    return quality in VALID_QUALITY_KEYWORDS or quality in VALID_RESOLUTIONS

def validate_language(lang: str) -> bool:
    return len(lang) == 2 and lang.lower() in VALID_LANGUAGES
```

### 6. Download Path Validation

**Decision**: Validate on save, create on use

**Rationale**:
- Catch obvious errors early (invalid characters, absolute path)
- Allow network paths that might not be available at config time
- Create directory only when actually needed (prevents unnecessary filesystem changes)

**Validation Rules**:
- No invalid filesystem characters: `< > : " | ? *`
- Windows: No reserved names (CON, PRN, AUX, NUL, COM1-9, LPT1-9)
- Path length reasonable (< 250 characters to leave room for filenames)
- Can be relative or absolute

**Implementation Notes**:
- Use `pathlib.Path` for cross-platform compatibility
- Validate in service layer before saving
- Create directories in download service right before download
- Log warnings if path doesn't exist but is valid format

### 7. Frontend Settings Management UI Pattern

**Decision**: Dedicated Settings page with form sections

**Rationale**:
- Separates settings from channel list (avoid clutter)
- Standard pattern familiar to users
- Can expand with more setting categories later
- Follows existing page structure (Channels, Downloads, History, Queue)

**UI Structure**:
```
Settings Page
├── Global Defaults Section
│   ├── Default Download Path
│   ├── Default Subtitle Language (dropdown)
│   └── Default Video Quality (dropdown)
└── Save/Reset Buttons
```

**Channel Form Updates**:
```
Add/Edit Channel Dialog
├── YouTube URL (existing)
├── Custom Name (new, required)
├── Channel Title (read-only, from YouTube)
├── Download Path (optional, shows default if empty)
├── Subtitle Language (optional dropdown, shows default if empty)
└── Video Quality (optional dropdown, shows default if empty)
```

**Alternatives Considered**:
- **Inline settings on channel list**: Too cluttered, hard to overview global settings
- **Modal dialog**: Overkill for simple form, harder to navigate

### 8. API Design Patterns

**Decision**: RESTful endpoints following existing conventions

**Backend Endpoints**:
```
GET    /api/settings                  # Get global settings
PUT    /api/settings                  # Update global settings
POST   /api/channels                  # Create channel (extended schema)
PUT    /api/channels/{id}             # Update channel (extended schema)
GET    /api/channels                  # List channels (extended response)
GET    /api/channels/{id}             # Get channel details (extended response)
```

**Request/Response Schema**:
```python
# Global Settings
class GlobalSettingsSchema(BaseModel):
    default_download_path: str = "./download"
    default_subtitle_language: Optional[str] = None
    default_video_quality: Optional[str] = None

# Channel
class ChannelCreateSchema(BaseModel):
    url: str
    name: str  # Custom name (required)
    download_path: Optional[str] = None
    subtitle_language: Optional[str] = None
    video_quality: Optional[str] = None

class ChannelResponseSchema(BaseModel):
    id: int
    channel_id: str
    title: str  # From YouTube
    name: str   # Custom name
    url: str
    download_path: str
    subtitle_language: Optional[str]
    video_quality: Optional[str]
    date_added: datetime
    last_updated: Optional[datetime]
```

## Technology Decisions

### Backend Dependencies

**No new dependencies required.** All functionality built with existing stack:
- SQLAlchemy for ORM and database operations
- Alembic for migrations
- Pydantic for schema validation
- FastAPI for API endpoints

### Frontend Dependencies

**No new dependencies required.** All functionality built with existing stack:
- React 18 for UI components
- TypeScript for type safety
- Shadcn UI for form components (Input, Select, Button, Card)
- Native fetch API for HTTP requests

## Performance Considerations

### Database Performance

**Indexes**:
- `Channel.name` - Unique index (for duplicate checking)
- `Channel.channel_id` - Already indexed
- `GlobalSettings.id` - Primary key (always 1)

**Query Patterns**:
- Global settings: Single row query, highly cacheable
- Channel lookup: By ID (primary key) or name (indexed)
- Settings inheritance: In-memory logic, no additional queries

**Expected Load**:
- Settings reads: ~1 per download operation (cacheable)
- Settings writes: Rare (user-initiated configuration changes)
- No performance concerns

### Frontend Performance

**Bundle Size Impact**: 
- New components: ~5KB gzipped
- No new third-party libraries
- Negligible impact on load time

**Runtime Performance**:
- Form validation: Client-side, instant
- Settings updates: Single API call, <100ms
- No complex state management needed

## Security Considerations

### Input Validation

**Download Paths**:
- Sanitize for path traversal attempts (`../`, absolute paths outside allowed directories)
- Reject paths containing environment variables or shell expansions
- Validate on both client and server

**Language/Quality Codes**:
- Whitelist validation (reject anything not in approved list)
- Case-insensitive comparison
- No SQL injection risk (ORM parameterized queries)

**Custom Names**:
- Validate length (max 255 characters)
- Allow Unicode for international names
- Reject control characters and excessive whitespace

### Authorization

**Current Scope**: Single-user application, no authentication
**Future Consideration**: If multi-user support added, settings must be user-scoped

## Testing Strategy

### Unit Tests

**Repository Layer**:
- CRUD operations for GlobalSettings
- Unique constraint enforcement for Channel.name
- Migration rollback/forward

**Service Layer**:
- Settings inheritance logic (all fallback combinations)
- Validation rules for language/quality/paths
- Error handling for duplicate names

**Frontend**:
- Form validation logic
- Settings inheritance display
- Error message display

### Integration Tests

**API Endpoints**:
- GET/PUT /api/settings
- POST/PUT /api/channels with new fields
- Error responses for validation failures

**Database**:
- Migrations run cleanly
- Constraints enforced
- Default values applied

### Manual Testing Scenarios

1. Configure global settings → verify new channels inherit
2. Override channel settings → verify channel-specific values used
3. Attempt duplicate channel name → verify rejection
4. Invalid quality/language → verify validation error
5. Download with settings → verify correct paths/quality/subtitles

## Migration Plan for Existing Data

### Existing Channel Records

**Current Schema**:
```python
- id
- channel_id
- name  # Currently stores YouTube channel title
- url
- download_path
- date_added
- last_updated
```

**New Schema**:
```python
- id
- channel_id
- title  # YouTube channel title (new)
- name   # Custom user name (modified - must be unique)
- url
- download_path
- subtitle_language  # New
- video_quality      # New
- date_added
- last_updated
```

**Migration Strategy**:
1. Add new columns: `title`, `subtitle_language`, `video_quality` (all nullable)
2. Copy existing `name` → `title` for all records
3. Generate unique custom names: keep `name` as-is if unique, append `_1`, `_2` etc. if duplicates exist
4. Apply unique constraint on `name`
5. Set `subtitle_language` and `video_quality` to NULL (inherit from global)

**Migration SQL**:
```sql
-- Add new columns
ALTER TABLE channels ADD COLUMN title VARCHAR(500);
ALTER TABLE channels ADD COLUMN subtitle_language VARCHAR(10);
ALTER TABLE channels ADD COLUMN video_quality VARCHAR(50);

-- Copy existing name to title
UPDATE channels SET title = name;

-- For duplicate names, append suffix
-- (Handled in Alembic Python script, not raw SQL)

-- Add unique constraint
CREATE UNIQUE INDEX idx_channels_name_unique ON channels(name);
```

## Open Questions & Future Considerations

### Resolved
All questions resolved in clarifications. No open items.

### Future Enhancements (Out of Scope)
- Automatic file migration when channel name/path changes
- Bulk settings operations across multiple channels
- Settings profiles (e.g., "High Quality", "Save Space")
- Settings export/import for backup
- Per-video overrides (user selects different quality for specific video)

## References

- [SQLAlchemy Documentation - ORM Relationships](https://docs.sqlalchemy.org/en/14/orm/relationships.html)
- [SQLAlchemy Documentation - Creating and Dropping Tables](https://docs.sqlalchemy.org/en/20/core/metadata.html#creating-and-dropping-database-tables)
- [yt-dlp Format Selection](https://github.com/yt-dlp/yt-dlp#format-selection)
- [ISO 639-1 Language Codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- [React Form Patterns](https://react.dev/reference/react-dom/components/input)

## Summary

All technical decisions made. No dependencies on external research. Implementation can proceed directly to Phase 1 (data model and contracts).

**Key Takeaways**:
1. Use single-row GlobalSettings table with id=1
2. Three-tier fallback: channel → global → hardcoded
3. Unique constraint + application validation for channel names
4. Whitelist validation for quality and language codes
5. SQLAlchemy model updates with init_db.py (no Alembic migrations)
6. No new dependencies required
7. Dedicated Settings page in UI
8. Migration path for existing channel data defined
