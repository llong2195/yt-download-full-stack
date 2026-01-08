# Structure Verification: Channel and Global Download Settings

**Date**: December 9, 2025  
**Status**: ✅ VERIFIED

## Purpose

This document verifies that all file paths referenced in the feature documentation match the actual project structure. It also documents cross-platform considerations for scripts and commands.

---

## Backend Structure ✅ VERIFIED

### Existing Files (Will be MODIFIED)

| File Path | Status | Changes Required |
|-----------|--------|------------------|
| `backend/src/models/channel.py` | ✅ EXISTS | Add fields: `title`, `subtitle_language`, `video_quality`, make `name` unique |
| `backend/src/models/schemas.py` | ✅ EXISTS | Extend Channel schemas, add GlobalSettings schemas |
| `backend/src/repository/channel_repo.py` | ✅ EXISTS | Add support for unique name constraint, new fields |
| `backend/src/services/channel_service.py` | ✅ EXISTS | Add settings inheritance logic |
| `backend/src/services/download_service.py` | ✅ EXISTS | Implement fallback chain for quality/language |
| `backend/src/services/youtube_service.py` | ✅ EXISTS | Pass settings to yt-dlp |
| `backend/src/routers/channels.py` | ✅ EXISTS | Extend endpoints to handle new fields |
| `backend/src/utils/validators.py` | ✅ EXISTS | Add quality/language validation |
| `backend/src/tasks/download_tasks.py` | ✅ EXISTS | Error handling for settings |
| `backend/main.py` | ✅ EXISTS | Register settings router |
| `backend/init_db.py` | ✅ EXISTS | Add GlobalSettings singleton creation |

### New Files (Will be CREATED)

| File Path | Status | Purpose |
|-----------|--------|---------|
| `backend/src/models/global_settings.py` | 🆕 NEW | GlobalSettings SQLAlchemy model |
| `backend/src/repository/settings_repo.py` | 🆕 NEW | GlobalSettings CRUD operations |
| `backend/src/services/settings_service.py` | 🆕 NEW | Settings business logic |
| `backend/src/routers/settings.py` | 🆕 NEW | `/api/settings` endpoints |

### Import Patterns ✅ VERIFIED

All backend code uses consistent import pattern:
```python
from src.models.channel import Channel
from src.models.database import get_db, SessionLocal
from src.models.schemas import ChannelCreate, ChannelResponse
from src.repository import channel_repo
from src.services.channel_service import ChannelService
```

**Note**: Imports are relative to `backend/` directory (added to `sys.path` in `main.py`)

---

## Frontend Structure ✅ VERIFIED

### Existing Files (Will be MODIFIED)

| File Path | Status | Changes Required |
|-----------|--------|------------------|
| `web/src/types/channel.ts` | ✅ EXISTS | Add fields: `title`, `name`, `subtitle_language`, `video_quality` |
| `web/src/services/channelApi.ts` | ✅ EXISTS | Extend add/update functions |
| `web/src/components/ChannelCard.tsx` | ✅ EXISTS | Display custom name prominently |
| `web/src/pages/Channels.tsx` | ✅ EXISTS | Add form fields for new properties |
| `web/src/pages/History.tsx` | ✅ EXISTS | Show quality/language used |
| `web/src/pages/Queue.tsx` | ✅ EXISTS | Show quality/language indicators |
| `web/src/App.tsx` | ✅ EXISTS | Add Settings navigation link |

### New Files (Will be CREATED)

| File Path | Status | Purpose |
|-----------|--------|---------|
| `web/src/types/settings.ts` | 🆕 NEW | GlobalSettings TypeScript types |
| `web/src/services/settingsApi.ts` | 🆕 NEW | Settings API client |
| `web/src/pages/Settings.tsx` | 🆕 NEW | Settings management page |

### Import Patterns ✅ VERIFIED

All frontend code uses path aliases:
```typescript
import type { Channel } from "@/types/channel";
import { fetchApi } from "@/services/api";
import { Button } from "@/components/ui/button";
```

**Note**: `@/` is aliased to `web/src/` in `vite.config.ts`

---

## Database Management ⚠️ IMPORTANT

### Current Approach (NOT Alembic)

This project **DOES NOT use Alembic migrations**. Database schema is managed via:

1. **SQLAlchemy Models**: Define schema in model classes
2. **`Base.metadata.create_all()`**: Creates tables automatically
3. **`init_db.py`**: Script that runs `create_all()` and initializes data

**Evidence**:
- ✅ `backend/migrations/` folder is **EMPTY**
- ✅ No `alembic.ini` file exists
- ✅ No imports of `alembic` in any Python file
- ✅ `init_db.py` uses `Base.metadata.create_all(bind=engine)`
- ✅ `main.py` also calls `Base.metadata.create_all(bind=engine)` on startup

### Schema Update Workflow

**For this feature**:

1. Create/update model classes in `src/models/`
2. Update `init_db.py` to create GlobalSettings singleton row
3. Backup existing database: `cp backend/data/ytdownloader.db backend/data/ytdownloader.db.backup`
4. Run: `python backend/init_db.py`
5. SQLAlchemy will add new tables/columns automatically
6. Write one-time data migration script if needed (e.g., copy `name` → `title`)

**Migration Safety**:
- New columns should use `nullable=True` or `server_default` values
- Test on database copy first
- Existing data will NOT be lost (only new columns added)

---

## Scripts and Cross-Platform Compatibility

### Available Scripts ✅ VERIFIED

Location: `.specify/scripts/bash/`

| Script | Format | Purpose |
|--------|--------|---------|
| `create-new-feature.sh` | Bash only | Initialize new feature branch |
| `setup-plan.sh` | Bash only | Generate plan documents |
| `check-prerequisites.sh` | Bash only | Verify docs exist |
| `update-agent-context.sh` | Bash only | Update Copilot context |
| `common.sh` | Bash only | Shared utilities |

**⚠️ Windows Users**:
- These scripts require **Bash** (Git Bash, WSL, or Cygwin)
- PowerShell scripts do **NOT** exist in this project
- Alternative: Manually run Python/Node commands shown in quickstart.md

### Common Commands - Cross-Platform

#### Database Operations

**Backup database**:
```bash
# Bash (Linux/Mac/Git Bash)
cp backend/data/ytdownloader.db backend/data/ytdownloader.db.backup

# PowerShell
Copy-Item backend\data\ytdownloader.db backend\data\ytdownloader.db.backup
```

**Initialize database**:
```bash
# All platforms (Python is cross-platform)
python backend/init_db.py
```

**Query database** (requires sqlite3 CLI):
```bash
# All platforms (if sqlite3 is installed)
sqlite3 backend/data/ytdownloader.db
.schema channels
.quit
```

#### Development Server

**Backend**:
```bash
# All platforms
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend**:
```bash
# All platforms (npm/pnpm are cross-platform)
cd web
pnpm dev
```

---

## File System Paths

### Path Separators

| Platform | Separator | Example |
|----------|-----------|---------|
| Linux/Mac | `/` | `backend/src/models/channel.py` |
| Windows | `\` or `/` | `backend\src\models\channel.py` (both work in Python) |

**Python Note**: Python's `pathlib.Path()` handles separators automatically across platforms.

### Download Paths in Settings

**Default**: `./download` (relative to backend directory)

**Platform-specific examples**:
```python
# Linux/Mac
download_path = "/home/user/Videos/YouTube"

# Windows
download_path = "D:/Videos/YouTube"  # Forward slashes work in Python
download_path = "D:\\Videos\\YouTube"  # Or escaped backslashes
```

**Recommendation**: Always use forward slashes `/` in configuration (works everywhere).

---

## Validation Checklist

Before starting implementation, verify:

- [x] All existing backend files are present and importable
- [x] All existing frontend files are present
- [x] Python path includes `backend/` directory (checked in `main.py`)
- [x] Vite path alias `@/` points to `web/src/` (checked in `vite.config.ts`)
- [x] Database schema approach is SQLAlchemy create_all (NOT Alembic)
- [x] Scripts are bash-only (Windows users need Git Bash/WSL)
- [x] Import patterns match existing codebase conventions
- [x] No references to non-existent migrations folder
- [x] All file paths use forward slashes in documentation

---

## Summary

✅ **Project structure verified**  
✅ **All paths validated against actual codebase**  
✅ **Database approach confirmed (SQLAlchemy, not Alembic)**  
✅ **Cross-platform considerations documented**  
✅ **Import patterns match existing conventions**

**Ready for implementation**: All prerequisites met. Tasks.md provides correct file paths and approach.
