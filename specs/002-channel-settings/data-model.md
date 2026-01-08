# Data Model: Channel and Global Download Settings

**Date**: December 9, 2025  
**Feature**: Channel and Global Download Settings  
**Status**: Complete

## Overview

This document defines the data entities, relationships, and state transitions for the channel settings feature. Two main entities are introduced/modified: GlobalSettings (new) and Channel (extended).

## Entity Definitions

### 1. GlobalSettings

Stores system-wide default configuration values that apply to all channels unless overridden.

**Purpose**: Provide default values for download path, subtitle language, and video quality to avoid repetitive channel configuration.

**Storage**: SQLite database table with single row (id=1)

**Fields**:

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| id | Integer | PRIMARY KEY | 1 | Always 1 (singleton pattern) |
| default_download_path | String(2000) | NOT NULL | "./download" | Base directory for video downloads |
| default_subtitle_language | String(10) | NULLABLE | NULL | ISO 639-1 language code (e.g., "en", "ja") |
| default_video_quality | String(50) | NULLABLE | NULL | Quality setting (e.g., "1080p", "best") |
| created_at | DateTime | NOT NULL | now() | Timestamp of creation |
| updated_at | DateTime | NULLABLE | NULL | Timestamp of last update |

**Validation Rules**:
- `default_download_path`: Must be valid directory path, no invalid filesystem characters
- `default_subtitle_language`: Must be valid ISO 639-1 code (2 lowercase letters) if provided
- `default_video_quality`: Must be in whitelist (`best`, `worst`, `2160p`, `1440p`, `1080p`, `720p`, `480p`, `360p`, `240p`, `144p`) if provided

**Indexes**:
- Primary key on `id`

**Relationships**:
- None (standalone configuration entity)

---

### 2. Channel (Extended)

Represents a YouTube channel tracked by the user, with custom naming and per-channel download settings.

**Purpose**: Store channel metadata and user-specific configuration for organizing downloads.

**Storage**: SQLite database table

**Fields** (⚠️ = Modified, ✨ = New):

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| id | Integer | PRIMARY KEY | auto | Unique identifier |
| channel_id | String(255) | UNIQUE, NOT NULL, INDEXED | - | YouTube channel ID |
| ⚠️ title | String(500) | NOT NULL | - | YouTube channel name (from API) |
| ⚠️ name | String(255) | UNIQUE, NOT NULL | - | Custom user-defined name |
| url | String(1000) | NOT NULL | - | YouTube channel URL |
| download_path | String(2000) | NOT NULL | - | Download directory for this channel |
| ✨ subtitle_language | String(10) | NULLABLE | NULL | Preferred subtitle language (ISO 639-1) |
| ✨ video_quality | String(50) | NULLABLE | NULL | Preferred video quality |
| date_added | DateTime | NOT NULL, INDEXED | now() | Timestamp when channel added |
| last_updated | DateTime | NULLABLE | NULL | Timestamp of last modification |

**Changes from Existing Schema**:
- **Renamed**: `name` → `title` (conceptually; migration copies old `name` to new `title`)
- **Modified**: `name` now stores user-provided custom name (was YouTube channel title)
- **Added**: `subtitle_language` - Per-channel subtitle preference
- **Added**: `video_quality` - Per-channel quality preference

**Validation Rules**:
- `title`: Required, populated from YouTube API, updated periodically
- `name`: Required, unique, 1-255 characters, user-defined
- `download_path`: Valid directory path, defaults to `{global_download_path}/{name}` if not specified
- `subtitle_language`: ISO 639-1 code if provided, inherits from global if NULL
- `video_quality`: Whitelisted value if provided, inherits from global if NULL

**Indexes**:
- Primary key on `id`
- Unique index on `channel_id`
- **NEW**: Unique index on `name`
- Index on `date_added` (existing)

**Relationships**:
- Has many `DownloadTask` (existing relationship)
- Has many `DownloadHistory` (existing relationship)

---

### 3. DownloadTask (No Changes)

Existing entity. No modifications required for this feature.

---

### 4. DownloadHistory (No Changes)

Existing entity. No modifications required for this feature.

## Entity Relationships

```
┌─────────────────┐
│ GlobalSettings  │
│  (singleton)    │
└─────────────────┘
         │
         │ (provides defaults to)
         ↓
┌─────────────────┐
│    Channel      │
│  (many)         │
└─────────────────┘
         │
         │ 1:N
         ↓
┌─────────────────┐
│  DownloadTask   │
│  (many)         │
└─────────────────┘

┌─────────────────┐
│    Channel      │
│  (many)         │
└─────────────────┘
         │
         │ 1:N
         ↓
┌─────────────────┐
│DownloadHistory  │
│  (many)         │
└─────────────────┘
```

## Settings Inheritance Logic

The system uses a three-tier fallback chain to determine effective settings values:

```
Channel-specific value (highest priority)
        ↓ (if NULL)
Global default value
        ↓ (if NULL)
Hardcoded application default (lowest priority)
```

**Example - Determining Download Path**:
1. If `Channel.download_path` is set → use it
2. Else if `GlobalSettings.default_download_path` is set → use `{global_path}/{channel.name}`
3. Else use `./download/{channel.name}`

**Example - Determining Subtitle Language**:
1. If `Channel.subtitle_language` is set → use it
2. Else if `GlobalSettings.default_subtitle_language` is set → use it
3. Else use `None` (no subtitles)

**Example - Determining Video Quality**:
1. If `Channel.video_quality` is set → use it
2. Else if `GlobalSettings.default_video_quality` is set → use it
3. Else use `"best"` (highest available quality)

## State Transitions

### GlobalSettings State Machine

```
┌─────────────┐
│   Created   │ (on first app startup or migration)
│  (default)  │
└──────┬──────┘
       │
       │ User updates settings
       ↓
┌─────────────┐
│   Updated   │ ←──┐
│             │    │ User updates settings
└─────────────┘ ───┘
```

**States**:
- **Created**: Initial state with default values
- **Updated**: Modified by user through settings UI

**Transitions**:
- Created → Updated: User saves settings via PUT /api/settings
- Updated → Updated: Subsequent updates

**No deletion**: GlobalSettings row persists for application lifetime.

---

### Channel State Machine

```
┌─────────────┐
│   Added     │ (user adds channel via UI)
│             │
└──────┬──────┘
       │
       │ User edits channel settings
       ↓
┌─────────────┐
│   Updated   │ ←──┐
│             │    │ User edits settings
└──────┬──────┘ ───┘
       │
       │ User deletes channel
       ↓
┌─────────────┐
│   Deleted   │ (soft or hard delete)
│             │
└─────────────┘
```

**States**:
- **Added**: Channel exists with initial configuration
- **Updated**: Channel configuration modified
- **Deleted**: Channel removed from system

**Transitions**:
- Added → Updated: User modifies channel via PUT /api/channels/{id}
- Updated → Updated: Subsequent modifications
- Added/Updated → Deleted: User removes channel via DELETE /api/channels/{id}

**State Implications**:
- **Added**: New channels inherit from global settings if optional fields not specified
- **Updated**: `last_updated` timestamp updated
- **Deleted**: Associated download history may persist (implementation dependent)

## Data Validation Rules

### Field-Level Validation

**Download Paths** (both global and channel-specific):
- No invalid filesystem characters: `< > : " | ? *`
- No Windows reserved names: `CON`, `PRN`, `AUX`, `NUL`, `COM1-9`, `LPT1-9`
- Maximum length: 2000 characters
- Can be relative or absolute
- Must be valid path format (validated using `pathlib.Path`)

**Subtitle Language Codes**:
- Must be exactly 2 lowercase letters (ISO 639-1)
- Allowed values: `en`, `ja`, `ko`, `zh`, `vi`, `es`, `fr`, `de`, `ru`, `ar`, `pt`, `it`, `th`, `pl`, `nl`, etc.
- Validated against whitelist in `validators.py`

**Video Quality Settings**:
- Allowed keywords: `best`, `worst`, `bestaudio`, `bestvideo`
- Allowed resolutions: `2160p`, `1440p`, `1080p`, `720p`, `480p`, `360p`, `240p`, `144p`
- Validated against whitelist in `validators.py`

**Custom Channel Names**:
- Required field (cannot be empty)
- Must be unique across all channels
- Length: 1-255 characters
- Allows Unicode characters (international names)
- No leading/trailing whitespace (trimmed automatically)

### Entity-Level Validation

**GlobalSettings**:
- `default_download_path` is required (cannot be NULL)
- Must have exactly one row in database (id=1)

**Channel**:
- `name` must be unique (enforced by database constraint)
- `title` populated from YouTube API (cannot be user-set)
- If `download_path` not specified, defaults to `{global_download_path}/{name}`
- `channel_id` must be unique (existing constraint)

### Cross-Entity Validation

**Settings Inheritance**:
- No validation needed (NULL values trigger fallback to global/default)

**Download Path Creation**:
- Directory must be creatable before first download
- Validated at download time, not at configuration time (allows network paths)

## Database Schema (SQL)

### GlobalSettings Table

```sql
CREATE TABLE global_settings (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    default_download_path VARCHAR(2000) NOT NULL DEFAULT './download',
    default_subtitle_language VARCHAR(10) NULL,
    default_video_quality VARCHAR(50) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL
);

-- Insert default row
INSERT INTO global_settings (id, default_download_path) 
VALUES (1, './download');
```

### Channels Table (Modified)

```sql
-- Migration: Add new columns
ALTER TABLE channels ADD COLUMN title VARCHAR(500);
ALTER TABLE channels ADD COLUMN subtitle_language VARCHAR(10) NULL;
ALTER TABLE channels ADD COLUMN video_quality VARCHAR(50) NULL;

-- Migration: Copy existing name to title
UPDATE channels SET title = name;

-- Migration: Set title to NOT NULL after population
ALTER TABLE channels ALTER COLUMN title SET NOT NULL;

-- Migration: Add unique constraint on name
CREATE UNIQUE INDEX idx_channels_name_unique ON channels(name);
```

## Migration Strategy

### Existing Data Transformation

**Problem**: Existing channels have `name` field storing YouTube channel title. New schema requires:
- `title` field for YouTube name
- `name` field for custom user name (must be unique)

**Solution**:

1. **Add new columns** (`title`, `subtitle_language`, `video_quality`) as nullable
2. **Copy data**: `name` → `title` for all existing channels
3. **Handle uniqueness**: Keep `name` as-is for existing channels (they become custom names)
   - If duplicate names exist: append `_1`, `_2`, `_3` suffix to ensure uniqueness
4. **Apply constraints**: Set `title` to NOT NULL, add unique index on `name`
5. **Set defaults**: `subtitle_language` and `video_quality` remain NULL (inherit from global)

**Implementation Notes** (SQLAlchemy create_all approach):

Since this project uses `Base.metadata.create_all()` instead of Alembic:

1. Update the `Channel` model class with new fields:
   ```python
   title: Mapped[str] = mapped_column(String(500), nullable=True)  # Temporarily nullable
   subtitle_language: Mapped[str | None] = mapped_column(String(10), nullable=True)
   video_quality: Mapped[str | None] = mapped_column(String(50), nullable=True)
   ```

2. Run `python backend/init_db.py` to create new columns

3. Write a one-time data migration script:
   ```python
   # migrate_channel_names.py
   from sqlalchemy.orm import Session
   from src.models import engine, Channel
   
   with Session(engine) as session:
       # Copy name to title for all existing channels
       channels = session.query(Channel).all()
       for channel in channels:
           if not channel.title:
               channel.title = channel.name
       session.commit()
       print(f"Migrated {len(channels)} channels")
   ```

4. Update model to make `title` non-nullable after migration
    
    # Handle duplicate names (if any)
    # ... Python logic to find duplicates and append suffixes ...
    
    # Add unique constraint on name
    op.create_index('idx_channels_name_unique', 'channels', ['name'], unique=True)

def downgrade():
    op.drop_index('idx_channels_name_unique', 'channels')
    op.drop_column('channels', 'video_quality')
    op.drop_column('channels', 'subtitle_language')
    op.drop_column('channels', 'title')
```

## Performance Considerations

### Query Patterns

**Read-Heavy Patterns**:
- Global settings: Read once per download operation (highly cacheable)
- Channel settings: Read once per download operation (indexed by ID or name)

**Write-Infrequent Patterns**:
- Global settings: Updated rarely (user-initiated)
- Channel settings: Updated occasionally (user-initiated)

### Indexing Strategy

**Existing Indexes** (keep):
- `channels.id` (primary key)
- `channels.channel_id` (unique)
- `channels.date_added` (for sorting)

**New Indexes**:
- `channels.name` (unique) - Required for duplicate checking and lookup by custom name

### Caching Opportunities

**GlobalSettings**:
- Can be cached in application memory
- Invalidate on PUT /api/settings
- TTL: Infinite (or refresh on update notification)

**Channel Settings**:
- Cache individual channel configs by ID
- Invalidate on PUT /api/channels/{id}
- TTL: 5-10 minutes or infinite (small dataset)

## Testing Scenarios

### Data Integrity Tests

1. **GlobalSettings Singleton**: Attempt to insert second row → should fail
2. **Channel Name Uniqueness**: Add channel with duplicate name → should fail with constraint error
3. **Migration Idempotency**: Run migration twice → should not corrupt data

### Validation Tests

1. **Invalid Download Path**: Submit path with `<>?*` → should reject
2. **Invalid Language Code**: Submit "english" instead of "en" → should reject
3. **Invalid Quality**: Submit "HD" instead of "1080p" → should reject
4. **Empty Custom Name**: Submit empty string → should reject

### Settings Inheritance Tests

1. **Channel overrides global**: Channel quality=720p, Global=1080p → use 720p
2. **Channel inherits global**: Channel quality=NULL, Global=1080p → use 1080p
3. **Hardcoded fallback**: Both NULL → use "best"

### State Transition Tests

1. **Create global settings**: First app start → default row created
2. **Update global settings**: Change download path → updated_at timestamp set
3. **Add channel with partial settings**: Only name provided → inherits globals
4. **Update channel name**: Change to unique name → succeeds
5. **Update channel name**: Change to existing name → fails with 409 Conflict

## Summary

This data model extends the existing schema with minimal changes:
- **1 new table**: GlobalSettings (singleton)
- **3 new columns**: Channel.title, Channel.subtitle_language, Channel.video_quality
- **1 renamed field**: Channel.name (conceptually changed from YouTube title to custom name)
- **1 new index**: Unique index on Channel.name

All changes backward-compatible through SQLAlchemy schema updates and one-time data migration script. Clear validation rules and state transitions defined. Settings inheritance logic provides flexibility without complexity.
