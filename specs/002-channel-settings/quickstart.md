# Quickstart: Channel and Global Download Settings

**Feature**: Channel and Global Download Settings  
**Date**: December 9, 2025  
**Target Audience**: Developers implementing this feature

## Overview

This quickstart provides a step-by-step guide to implement global download settings and enhanced channel properties. Follow the phases in order for a systematic implementation.

## Prerequisites

- Existing YouTube downloader application running
- Python 3.10+ with FastAPI, SQLAlchemy (no Alembic - project uses `Base.metadata.create_all()`)
- React 18+ frontend with TypeScript, Vite, Shadcn UI
- Familiarity with the existing codebase structure
- **Note**: `.specify/scripts/` contains bash scripts only. On Windows, use Git Bash, WSL, or manually translate commands to PowerShell

## Implementation Phases

### Phase 0: Database Schema

**⚠️ IMPORTANT**: This project uses SQLAlchemy's `Base.metadata.create_all()` pattern (not Alembic migrations). Schema changes require updating model classes and running `init_db.py`.

#### Step 1: Backup Existing Database

**Bash (Linux/Mac/Git Bash on Windows)**:
```bash
cp backend/data/ytdownloader.db backend/data/ytdownloader.db.backup
```

**PowerShell (Windows)**:
```powershell
Copy-Item backend\data\ytdownloader.db backend\data\ytdownloader.db.backup
```

#### Step 2: Create GlobalSettings Model

Create `backend/src/models/global_settings.py`:

```python
"""Global settings model for application-wide defaults."""

from datetime import datetime
from sqlalchemy import CheckConstraint, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from .database import Base


class GlobalSettings(Base):
    """System-wide default configuration (singleton pattern)."""

    __tablename__ = "global_settings"
    __table_args__ = (
        CheckConstraint("id = 1", name="singleton_check"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    default_download_path: Mapped[str] = mapped_column(
        String(2000), nullable=False, server_default="./download"
    )
    default_subtitle_language: Mapped[str | None] = mapped_column(
        String(10), nullable=True
    )
    default_video_quality: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    def __repr__(self):
        return f"<GlobalSettings(id={self.id}, path={self.default_download_path})>"
```

#### Step 3: Extend Channel Model

Update `backend/src/models/channel.py`:

```python
# Add these new fields to the Channel class:

title: Mapped[str] = mapped_column(String(500), nullable=False)
# Note: Existing 'name' field becomes user's custom name
# You may need to rename or handle this during migration
subtitle_language: Mapped[str | None] = mapped_column(String(10), nullable=True)
video_quality: Mapped[str | None] = mapped_column(String(50), nullable=True)

# Add unique constraint on name (if not already unique)
# Update the 'name' column definition:
name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
```

#### Step 4: Update init_db.py

Add GlobalSettings initialization after `Base.metadata.create_all()`:

```python
# In backend/init_db.py, after Base.metadata.create_all(bind=engine):

from src.models.global_settings import GlobalSettings
from sqlalchemy.orm import Session

# Create GlobalSettings singleton row if doesn't exist
with Session(engine) as session:
    settings = session.query(GlobalSettings).filter_by(id=1).first()
    if not settings:
        settings = GlobalSettings(
            id=1,
            default_download_path="./download"
        )
        session.add(settings)
        session.commit()
        print("   ✅ GlobalSettings singleton created")
    else:
        print("   ✅ GlobalSettings already exists")
```

#### Step 5: Run Database Initialization

**All platforms**:
```bash
python backend/init_db.py
```

**Verification** (requires sqlite3 CLI installed):
```bash
sqlite3 backend/data/ytdownloader.db
.schema global_settings
.schema channels
SELECT * FROM global_settings;
.quit
```

You should see:
- `global_settings` table with singleton row (id=1)
- `channels` table with new columns: `title`, `subtitle_language`, `video_quality`

---

### Phase 1: Backend Schemas and Validation
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    default_download_path: Mapped[str] = mapped_column(
        String(2000), nullable=False, default="./download"
    )
    default_subtitle_language: Mapped[str | None] = mapped_column(
        String(10), nullable=True
    )
    default_video_quality: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    
    def __repr__(self):
        return f"<GlobalSettings(id={self.id}, download_path={self.default_download_path})>"
```

#### Step 2: Extend Channel Model

Edit `backend/src/models/channel.py`:

```python
# Add new fields
title: Mapped[str] = mapped_column(String(500), nullable=False)  # NEW
subtitle_language: Mapped[str | None] = mapped_column(String(10), nullable=True)  # NEW
video_quality: Mapped[str | None] = mapped_column(String(50), nullable=True)  # NEW

# Note: 'name' field already exists, now has unique constraint
```

#### Step 3: Update Schemas

Edit `backend/src/models/schemas.py`:

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Global Settings Schemas
class GlobalSettingsSchema(BaseModel):
    id: int
    default_download_path: str
    default_subtitle_language: Optional[str] = None
    default_video_quality: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class GlobalSettingsUpdateSchema(BaseModel):
    default_download_path: str = Field(..., min_length=1, max_length=2000)
    default_subtitle_language: Optional[str] = Field(None, min_length=2, max_length=2)
    default_video_quality: Optional[str] = Field(None, max_length=50)

# Channel Schemas (extend existing)
class ChannelCreateSchema(BaseModel):
    url: str
    name: str = Field(..., min_length=1, max_length=255)
    download_path: Optional[str] = Field(None, max_length=2000)
    subtitle_language: Optional[str] = Field(None, min_length=2, max_length=2)
    video_quality: Optional[str] = Field(None, max_length=50)

class ChannelUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    download_path: Optional[str] = Field(None, max_length=2000)
    subtitle_language: Optional[str] = Field(None, min_length=2, max_length=2)
    video_quality: Optional[str] = Field(None, max_length=50)

class ChannelResponseSchema(BaseModel):
    id: int
    channel_id: str
    title: str  # NEW
    name: str
    url: str
    download_path: str
    subtitle_language: Optional[str] = None  # NEW
    video_quality: Optional[str] = None  # NEW
    date_added: datetime
    last_updated: Optional[datetime] = None
    
    class Config:
        from_attributes = True
```

---

### Phase 2: Backend Validation

#### Step 1: Add Validators

Edit `backend/src/utils/validators.py`:

```python
# Add these constants and functions

VALID_QUALITY_KEYWORDS = ["best", "worst", "bestaudio", "bestvideo"]
VALID_RESOLUTIONS = ["2160p", "1440p", "1080p", "720p", "480p", "360p", "240p", "144p"]
VALID_LANGUAGES = ["en", "ja", "ko", "zh", "vi", "es", "fr", "de", "ru", "ar", "pt", "it", "th", "pl", "nl"]

def validate_video_quality(quality: str | None) -> bool:
    """Validate video quality setting."""
    if quality is None:
        return True
    return quality in VALID_QUALITY_KEYWORDS or quality in VALID_RESOLUTIONS

def validate_subtitle_language(language: str | None) -> bool:
    """Validate subtitle language code (ISO 639-1)."""
    if language is None:
        return True
    return len(language) == 2 and language.lower() in VALID_LANGUAGES

def validate_download_path(path: str) -> bool:
    """Validate download path format."""
    if not path:
        return False
    
    # Check for invalid filesystem characters
    invalid_chars = '<>:"|?*'
    if any(char in path for char in invalid_chars):
        return False
    
    # Check length
    if len(path) > 2000:
        return False
    
    return True
```

---

### Phase 3: Backend Repository

#### Step 1: Create Settings Repository

Create `backend/src/repository/settings_repo.py`:

```python
from sqlalchemy.orm import Session
from ..models.global_settings import GlobalSettings

class SettingsRepository:
    """Repository for global settings operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_settings(self) -> GlobalSettings:
        """Get global settings (always returns singleton)."""
        settings = self.db.query(GlobalSettings).filter(GlobalSettings.id == 1).first()
        if not settings:
            # Create default settings if not exist
            settings = GlobalSettings(
                id=1,
                default_download_path="./download"
            )
            self.db.add(settings)
            self.db.commit()
            self.db.refresh(settings)
        return settings
    
    def update_settings(self, update_data: dict) -> GlobalSettings:
        """Update global settings."""
        settings = self.get_settings()
        
        for key, value in update_data.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
        
        from datetime import datetime
        settings.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(settings)
        return settings
```

#### Step 2: Extend Channel Repository

Edit `backend/src/repository/channel_repo.py`:

```python
# Add to create_channel method
def create_channel(self, channel_data: dict) -> Channel:
    """Create new channel with settings."""
    channel = Channel(**channel_data)
    self.db.add(channel)
    try:
        self.db.commit()
        self.db.refresh(channel)
        return channel
    except IntegrityError as e:
        self.db.rollback()
        if "name" in str(e):
            raise ValueError(f"Channel with name '{channel_data.get('name')}' already exists")
        raise

# Add to update_channel method - handle unique constraint
```

---

### Phase 4: Backend Service Layer

#### Step 1: Create Settings Service

Create `backend/src/services/settings_service.py`:

```python
from sqlalchemy.orm import Session
from ..repository.settings_repo import SettingsRepository
from ..models.schemas import GlobalSettingsUpdateSchema
from ..utils.validators import validate_download_path, validate_video_quality, validate_subtitle_language

class SettingsService:
    """Business logic for global settings."""
    
    def __init__(self, db: Session):
        self.repo = SettingsRepository(db)
    
    def get_settings(self):
        """Get global settings."""
        return self.repo.get_settings()
    
    def update_settings(self, update_schema: GlobalSettingsUpdateSchema):
        """Update global settings with validation."""
        # Validate download path
        if not validate_download_path(update_schema.default_download_path):
            raise ValueError("Invalid download path")
        
        # Validate language
        if not validate_subtitle_language(update_schema.default_subtitle_language):
            raise ValueError("Invalid language code")
        
        # Validate quality
        if not validate_video_quality(update_schema.default_video_quality):
            raise ValueError("Invalid video quality")
        
        return self.repo.update_settings(update_schema.model_dump())
```

#### Step 2: Extend Channel Service

Edit `backend/src/services/channel_service.py`:

```python
# Add settings inheritance logic
def create_channel(self, channel_data: dict) -> Channel:
    """Create channel with settings inheritance."""
    # Get global settings for defaults
    global_settings = SettingsRepository(self.db).get_settings()
    
    # Apply defaults if not provided
    if not channel_data.get('download_path'):
        channel_data['download_path'] = f"{global_settings.default_download_path}/{channel_data['name']}"
    
    # Validate
    if not validate_download_path(channel_data.get('download_path', '')):
        raise ValueError("Invalid download path")
    
    if not validate_subtitle_language(channel_data.get('subtitle_language')):
        raise ValueError("Invalid subtitle language")
    
    if not validate_video_quality(channel_data.get('video_quality')):
        raise ValueError("Invalid video quality")
    
    return self.repo.create_channel(channel_data)

def get_effective_settings(self, channel_id: int) -> dict:
    """Get effective settings for channel (with inheritance)."""
    channel = self.repo.get_channel_by_id(channel_id)
    global_settings = SettingsRepository(self.db).get_settings()
    
    return {
        'download_path': channel.download_path,
        'subtitle_language': channel.subtitle_language or global_settings.default_subtitle_language,
        'video_quality': channel.video_quality or global_settings.default_video_quality or 'best'
    }
```

---

### Phase 5: Backend API Routes

#### Step 1: Create Settings Router

Create `backend/src/routers/settings.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models.database import get_db
from ..models.schemas import GlobalSettingsSchema, GlobalSettingsUpdateSchema
from ..services.settings_service import SettingsService

router = APIRouter(prefix="/api/settings", tags=["settings"])

@router.get("", response_model=GlobalSettingsSchema)
def get_settings(db: Session = Depends(get_db)):
    """Get global settings."""
    service = SettingsService(db)
    return service.get_settings()

@router.put("", response_model=GlobalSettingsSchema)
def update_settings(
    update_data: GlobalSettingsUpdateSchema,
    db: Session = Depends(get_db)
):
    """Update global settings."""
    service = SettingsService(db)
    try:
        return service.update_settings(update_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

#### Step 2: Update Channels Router

Edit `backend/src/routers/channels.py`:

```python
# Update response models to include new fields
# Add validation error handling for 409 Conflict

@router.post("", response_model=ChannelResponseSchema, status_code=201)
def create_channel(
    channel_data: ChannelCreateSchema,
    db: Session = Depends(get_db)
):
    """Create new channel."""
    service = ChannelService(db)
    try:
        return service.create_channel(channel_data.model_dump())
    except ValueError as e:
        if "already exists" in str(e):
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
```

#### Step 3: Register Settings Router

Edit `backend/main.py`:

```python
from .routers import channels, downloads, history, queue, settings  # Add settings

# Register router
app.include_router(settings.router)
```

---

### Phase 6: Frontend Types

#### Step 1: Create Settings Types

Create `web/src/types/settings.ts`:

```typescript
export interface GlobalSettings {
  id: number;
  default_download_path: string;
  default_subtitle_language: string | null;
  default_video_quality: string | null;
  created_at: string;
  updated_at: string | null;
}

export interface GlobalSettingsUpdate {
  default_download_path: string;
  default_subtitle_language?: string | null;
  default_video_quality?: string | null;
}

export const VALID_LANGUAGES = [
  { code: 'en', name: 'English' },
  { code: 'ja', name: 'Japanese' },
  { code: 'ko', name: 'Korean' },
  { code: 'zh', name: 'Chinese' },
  { code: 'vi', name: 'Vietnamese' },
  { code: 'es', name: 'Spanish' },
  { code: 'fr', name: 'French' },
  { code: 'de', name: 'German' },
  // ... more
];

export const VALID_QUALITIES = [
  { value: 'best', label: 'Best Quality' },
  { value: '2160p', label: '4K (2160p)' },
  { value: '1440p', label: '2K (1440p)' },
  { value: '1080p', label: 'Full HD (1080p)' },
  { value: '720p', label: 'HD (720p)' },
  { value: '480p', label: 'SD (480p)' },
  // ... more
];
```

#### Step 2: Update Channel Types

Edit `web/src/types/channel.ts`:

```typescript
export interface Channel {
  id: number;
  channel_id: string;
  title: string;  // NEW: YouTube channel name
  name: string;   // CHANGED: Now custom user name
  url: string;
  download_path: string;
  subtitle_language: string | null;  // NEW
  video_quality: string | null;      // NEW
  date_added: string;
  last_updated: string | null;
}

export interface ChannelCreate {
  url: string;
  name: string;
  download_path?: string;
  subtitle_language?: string | null;
  video_quality?: string | null;
}

export interface ChannelUpdate {
  name?: string;
  download_path?: string;
  subtitle_language?: string | null;
  video_quality?: string | null;
}
```

---

### Phase 7: Frontend API Client

#### Step 1: Create Settings API

Create `web/src/services/settingsApi.ts`:

```typescript
import { api } from './api';
import type { GlobalSettings, GlobalSettingsUpdate } from '@/types/settings';

export async function fetchSettings(): Promise<GlobalSettings> {
  const response = await api<{ data: GlobalSettings }>('/settings');
  return response.data;
}

export async function updateSettings(
  settings: GlobalSettingsUpdate
): Promise<GlobalSettings> {
  const response = await api<{ data: GlobalSettings }>('/settings', {
    method: 'PUT',
    body: JSON.stringify(settings),
  });
  return response.data;
}
```

#### Step 2: Update Channel API

Edit `web/src/services/channelApi.ts`:

```typescript
// Update types to match new schema
// Add subtitle_language and video_quality to requests
```

---

### Phase 8: Frontend UI

#### Step 1: Create Settings Page

Create `web/src/pages/Settings.tsx`:

```typescript
import { useState, useEffect } from 'react';
import { fetchSettings, updateSettings } from '@/services/settingsApi';
import type { GlobalSettings, GlobalSettingsUpdate } from '@/types/settings';
import { VALID_LANGUAGES, VALID_QUALITIES } from '@/types/settings';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function Settings() {
  const [settings, setSettings] = useState<GlobalSettings | null>(null);
  const [formData, setFormData] = useState<GlobalSettingsUpdate>({
    default_download_path: '',
    default_subtitle_language: null,
    default_video_quality: null,
  });
  const [saving, setSaving] = useState(false);
  
  useEffect(() => {
    loadSettings();
  }, []);
  
  const loadSettings = async () => {
    const data = await fetchSettings();
    setSettings(data);
    setFormData({
      default_download_path: data.default_download_path,
      default_subtitle_language: data.default_subtitle_language,
      default_video_quality: data.default_video_quality,
    });
  };
  
  const handleSave = async () => {
    setSaving(true);
    try {
      await updateSettings(formData);
      await loadSettings();
    } catch (error) {
      console.error('Failed to save settings', error);
    } finally {
      setSaving(false);
    }
  };
  
  return (
    <div className="container mx-auto p-4">
      <Card>
        <CardHeader>
          <CardTitle>Global Settings</CardTitle>
          <CardDescription>
            Configure default settings for all channels
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label>Default Download Path</label>
            <Input
              value={formData.default_download_path}
              onChange={(e) => setFormData({ ...formData, default_download_path: e.target.value })}
            />
          </div>
          
          <div>
            <label>Default Subtitle Language</label>
            <Select
              value={formData.default_subtitle_language || 'none'}
              onValueChange={(value) => 
                setFormData({ ...formData, default_subtitle_language: value === 'none' ? null : value })
              }
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">None</SelectItem>
                {VALID_LANGUAGES.map((lang) => (
                  <SelectItem key={lang.code} value={lang.code}>
                    {lang.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          <div>
            <label>Default Video Quality</label>
            <Select
              value={formData.default_video_quality || 'best'}
              onValueChange={(value) => 
                setFormData({ ...formData, default_video_quality: value })
              }
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {VALID_QUALITIES.map((quality) => (
                  <SelectItem key={quality.value} value={quality.value}>
                    {quality.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          <Button onClick={handleSave} disabled={saving}>
            {saving ? 'Saving...' : 'Save Settings'}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
```

#### Step 2: Update Channel Components

Edit channel-related components to show custom name prominently and add new fields to the add/edit forms.

---

## Testing

### Backend Tests

```bash
cd backend
pytest tests/test_settings_service.py -v
pytest tests/test_channel_service.py -v
```

### Frontend Tests

```bash
cd web
npm run test
```

### Manual Testing

1. Start backend: `cd backend && uvicorn main:app --reload`
2. Start frontend: `cd web && npm run dev`
3. Open http://localhost:5173
4. Test global settings configuration
5. Test channel creation with custom name
6. Test settings inheritance

---

## Deployment Checklist

- [ ] Database migrations run successfully
- [ ] All tests passing
- [ ] API endpoints returning correct data
- [ ] Frontend UI rendering correctly
- [ ] Settings inheritance working as expected
- [ ] Validation errors displayed properly
- [ ] Duplicate channel name prevention working

## Troubleshooting

**Migration fails on SQLite**: Use batch operations for ALTER TABLE
**Unique constraint violation**: Check for existing duplicate channel names
**Frontend not showing new fields**: Clear browser cache and rebuild

## Next Steps

After completing this feature, proceed to `/speckit.tasks` to generate detailed implementation tasks.
