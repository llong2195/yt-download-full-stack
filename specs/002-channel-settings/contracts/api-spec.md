# API Specification: Channel and Global Download Settings

**Version**: 1.0  
**Date**: December 9, 2025  
**Base URL**: `http://localhost:8000/api`

## Overview

This document defines the REST API contract for managing global download settings and channel configurations. All endpoints follow RESTful conventions and return JSON responses.

## Authentication

**Current**: No authentication required (single-user application)  
**Future**: Bearer token authentication when multi-user support added

## Common Response Formats

### Success Response

```json
{
  "status": "success",
  "data": { ... }
}
```

### Error Response

```json
{
  "status": "error",
  "message": "Human-readable error message",
  "detail": {
    "field": "error details"
  }
}
```

### Common HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PUT |
| 201 | Created | Successful POST |
| 400 | Bad Request | Validation error |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate resource (e.g., channel name) |
| 500 | Internal Server Error | Unexpected server error |

---

## Global Settings Endpoints

### GET /api/settings

Retrieve global default settings.

**Method**: `GET`  
**Auth**: None  
**Query Parameters**: None

**Response** (200 OK):

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "default_download_path": "./download",
    "default_subtitle_language": "en",
    "default_video_quality": "1080p",
    "created_at": "2025-12-09T10:00:00Z",
    "updated_at": "2025-12-09T12:30:00Z"
  }
}
```

**Field Descriptions**:
- `id`: Always 1 (singleton)
- `default_download_path`: Base directory for downloads
- `default_subtitle_language`: ISO 639-1 code or `null`
- `default_video_quality`: Quality setting or `null`
- `created_at`: Timestamp of creation
- `updated_at`: Timestamp of last modification or `null`

**Error Responses**: None (settings always exist)

---

### PUT /api/settings

Update global default settings.

**Method**: `PUT`  
**Auth**: None  
**Content-Type**: `application/json`

**Request Body**:

```json
{
  "default_download_path": "D:/Videos",
  "default_subtitle_language": "ja",
  "default_video_quality": "1080p"
}
```

**Field Constraints**:
- `default_download_path`: Required, valid directory path
- `default_subtitle_language`: Optional, ISO 639-1 code (2 lowercase letters)
- `default_video_quality`: Optional, one of: `best`, `worst`, `2160p`, `1440p`, `1080p`, `720p`, `480p`, `360p`, `240p`, `144p`

**Response** (200 OK):

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "default_download_path": "D:/Videos",
    "default_subtitle_language": "ja",
    "default_video_quality": "1080p",
    "created_at": "2025-12-09T10:00:00Z",
    "updated_at": "2025-12-09T14:15:00Z"
  }
}
```

**Error Responses**:

**400 Bad Request** (Validation Error):
```json
{
  "status": "error",
  "message": "Validation error",
  "detail": {
    "default_subtitle_language": "Invalid language code. Must be 2-letter ISO 639-1 code (e.g., 'en', 'ja')"
  }
}
```

**Example Validation Errors**:
- Invalid download path: `"default_download_path": "Path contains invalid characters: <>?*"`
- Invalid language: `"default_subtitle_language": "Invalid language code 'english'. Use 'en' instead."`
- Invalid quality: `"default_video_quality": "Invalid quality 'HD'. Allowed: best, worst, 1080p, 720p, etc."`

---

## Channel Endpoints (Extended)

### GET /api/channels

List all channels with extended information.

**Method**: `GET`  
**Auth**: None  
**Query Parameters**: None

**Response** (200 OK):

```json
{
  "status": "success",
  "data": {
    "channels": [
      {
        "id": 1,
        "channel_id": "UC1234567890",
        "title": "TechTips Official",
        "name": "Tech Reviews",
        "url": "https://www.youtube.com/@techtips",
        "download_path": "D:/Videos/Tech Reviews",
        "subtitle_language": "en",
        "video_quality": "1080p",
        "date_added": "2025-12-01T10:00:00Z",
        "last_updated": "2025-12-09T12:00:00Z"
      },
      {
        "id": 2,
        "channel_id": "UC0987654321",
        "title": "日本語学習チャンネル",
        "name": "Japanese Lessons",
        "url": "https://www.youtube.com/@japanese-learning",
        "download_path": "./download/Japanese Lessons",
        "subtitle_language": "ja",
        "video_quality": null,
        "date_added": "2025-12-05T15:30:00Z",
        "last_updated": null
      }
    ]
  }
}
```

**Field Descriptions**:
- `title`: YouTube channel name (from API)
- `name`: User-defined custom name (unique)
- `subtitle_language`: Per-channel preference or `null` (inherits from global)
- `video_quality`: Per-channel preference or `null` (inherits from global)

---

### GET /api/channels/{id}

Get details for a specific channel.

**Method**: `GET`  
**Auth**: None  
**Path Parameters**:
- `id` (integer): Channel ID

**Response** (200 OK):

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "channel_id": "UC1234567890",
    "title": "TechTips Official",
    "name": "Tech Reviews",
    "url": "https://www.youtube.com/@techtips",
    "download_path": "D:/Videos/Tech Reviews",
    "subtitle_language": "en",
    "video_quality": "1080p",
    "date_added": "2025-12-01T10:00:00Z",
    "last_updated": "2025-12-09T12:00:00Z"
  }
}
```

**Error Responses**:

**404 Not Found**:
```json
{
  "status": "error",
  "message": "Channel not found",
  "detail": {
    "id": 999
  }
}
```

---

### POST /api/channels

Add a new channel with custom configuration.

**Method**: `POST`  
**Auth**: None  
**Content-Type**: `application/json`

**Request Body**:

```json
{
  "url": "https://www.youtube.com/@techtips",
  "name": "Tech Reviews",
  "download_path": "D:/Videos/Tech Reviews",
  "subtitle_language": "en",
  "video_quality": "1080p"
}
```

**Field Constraints**:
- `url`: Required, valid YouTube channel URL
- `name`: Required, unique, 1-255 characters
- `download_path`: Optional, defaults to `{global_download_path}/{name}`
- `subtitle_language`: Optional, ISO 639-1 code or `null` (inherits from global)
- `video_quality`: Optional, whitelisted value or `null` (inherits from global)

**Response** (201 Created):

```json
{
  "status": "success",
  "data": {
    "id": 3,
    "channel_id": "UC1234567890",
    "title": "TechTips Official",
    "name": "Tech Reviews",
    "url": "https://www.youtube.com/@techtips",
    "download_path": "D:/Videos/Tech Reviews",
    "subtitle_language": "en",
    "video_quality": "1080p",
    "date_added": "2025-12-09T15:00:00Z",
    "last_updated": null
  }
}
```

**Notes**:
- `channel_id` extracted from YouTube URL
- `title` fetched from YouTube API
- `download_path` defaults to `{global_download_path}/{name}` if not provided

**Error Responses**:

**400 Bad Request** (Validation Error):
```json
{
  "status": "error",
  "message": "Validation error",
  "detail": {
    "url": "Invalid YouTube channel URL"
  }
}
```

**409 Conflict** (Duplicate Name):
```json
{
  "status": "error",
  "message": "Channel with this name already exists",
  "detail": {
    "name": "Tech Reviews",
    "existing_channel_id": 1
  }
}
```

**Example Validation Errors**:
- Empty name: `"name": "Custom name is required"`
- Invalid language: `"subtitle_language": "Invalid language code 'english'. Use 'en' instead."`
- Invalid quality: `"video_quality": "Invalid quality 'HD'. Allowed: best, worst, 1080p, 720p, etc."`
- Invalid URL: `"url": "Not a valid YouTube channel URL"`

---

### PUT /api/channels/{id}

Update channel configuration.

**Method**: `PUT`  
**Auth**: None  
**Path Parameters**:
- `id` (integer): Channel ID

**Content-Type**: `application/json`

**Request Body** (all fields optional, only include fields to update):

```json
{
  "name": "Tech Reviews Renamed",
  "download_path": "D:/NewPath/Tech Reviews",
  "subtitle_language": "ja",
  "video_quality": "720p"
}
```

**Field Constraints**:
- `name`: Optional, unique, 1-255 characters
- `download_path`: Optional, valid directory path
- `subtitle_language`: Optional, ISO 639-1 code or `null`
- `video_quality`: Optional, whitelisted value or `null`

**Notes**:
- Cannot update `url`, `channel_id`, `title` (read-only)
- `title` updated automatically by periodic sync with YouTube API
- `last_updated` timestamp set automatically

**Response** (200 OK):

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "channel_id": "UC1234567890",
    "title": "TechTips Official",
    "name": "Tech Reviews Renamed",
    "url": "https://www.youtube.com/@techtips",
    "download_path": "D:/NewPath/Tech Reviews",
    "subtitle_language": "ja",
    "video_quality": "720p",
    "date_added": "2025-12-01T10:00:00Z",
    "last_updated": "2025-12-09T16:00:00Z"
  }
}
```

**Error Responses**:

**404 Not Found**:
```json
{
  "status": "error",
  "message": "Channel not found",
  "detail": {
    "id": 999
  }
}
```

**409 Conflict** (Duplicate Name):
```json
{
  "status": "error",
  "message": "Channel with this name already exists",
  "detail": {
    "name": "Tech Reviews Renamed",
    "existing_channel_id": 2
  }
}
```

**400 Bad Request** (Validation Error):
```json
{
  "status": "error",
  "message": "Validation error",
  "detail": {
    "subtitle_language": "Invalid language code 'english'. Use 'en' instead."
  }
}
```

---

### DELETE /api/channels/{id}

Delete a channel.

**Method**: `DELETE`  
**Auth**: None  
**Path Parameters**:
- `id` (integer): Channel ID

**Response** (200 OK):

```json
{
  "status": "success",
  "message": "Channel deleted successfully",
  "data": {
    "id": 1
  }
}
```

**Error Responses**:

**404 Not Found**:
```json
{
  "status": "error",
  "message": "Channel not found",
  "detail": {
    "id": 999
  }
}
```

**Notes**:
- Downloaded files remain on disk (not deleted automatically)
- Download history may persist (implementation dependent)

---

## Data Types

### ISO 639-1 Language Codes

Supported language codes (2 lowercase letters):

| Code | Language |
|------|----------|
| en   | English  |
| ja   | Japanese |
| ko   | Korean   |
| zh   | Chinese  |
| vi   | Vietnamese |
| es   | Spanish  |
| fr   | French   |
| de   | German   |
| ru   | Russian  |
| ar   | Arabic   |
| pt   | Portuguese |
| it   | Italian  |
| th   | Thai     |
| pl   | Polish   |
| nl   | Dutch    |

### Video Quality Options

Supported quality values:

**Keywords**:
- `best` - Highest available quality
- `worst` - Lowest available quality
- `bestaudio` - Best audio-only
- `bestvideo` - Best video-only

**Resolutions**:
- `2160p` - 4K
- `1440p` - 2K/QHD
- `1080p` - Full HD
- `720p` - HD
- `480p` - SD
- `360p` - Low
- `240p` - Very Low
- `144p` - Mobile

---

## Example Workflows

### Workflow 1: Configure Global Settings

```bash
# Get current settings
GET /api/settings

# Update settings
PUT /api/settings
{
  "default_download_path": "D:/Videos",
  "default_subtitle_language": "en",
  "default_video_quality": "1080p"
}
```

### Workflow 2: Add Channel with Custom Settings

```bash
# Add channel with all settings specified
POST /api/channels
{
  "url": "https://www.youtube.com/@techtips",
  "name": "Tech Reviews",
  "download_path": "D:/Videos/Tech",
  "subtitle_language": "en",
  "video_quality": "1080p"
}
```

### Workflow 3: Add Channel with Inherited Settings

```bash
# Add channel with minimal config (inherits from global)
POST /api/channels
{
  "url": "https://www.youtube.com/@japanese-learning",
  "name": "Japanese Lessons"
}

# Result: download_path = D:/Videos/Japanese Lessons (from global + name)
#         subtitle_language = en (from global)
#         video_quality = 1080p (from global)
```

### Workflow 4: Update Channel Name

```bash
# Change custom name
PUT /api/channels/1
{
  "name": "New Custom Name"
}
```

### Workflow 5: Override Channel Setting

```bash
# Change channel-specific quality (overrides global)
PUT /api/channels/1
{
  "video_quality": "720p"
}
```

### Workflow 6: Reset to Global Default

```bash
# Remove channel-specific quality (inherit from global)
PUT /api/channels/1
{
  "video_quality": null
}
```

---

## Error Handling

### Validation Error Format

All validation errors follow consistent format:

```json
{
  "status": "error",
  "message": "Validation error",
  "detail": {
    "field_name": "Specific error message for this field",
    "another_field": "Another error message"
  }
}
```

### Common Validation Errors

**Download Path**:
- `"Path contains invalid characters: <>?*"`
- `"Path exceeds maximum length of 2000 characters"`
- `"Path cannot contain Windows reserved names (CON, PRN, etc.)"`

**Subtitle Language**:
- `"Invalid language code 'english'. Use 'en' instead."`
- `"Language code must be exactly 2 lowercase letters"`

**Video Quality**:
- `"Invalid quality 'HD'. Allowed: best, worst, 1080p, 720p, etc."`

**Channel Name**:
- `"Custom name is required"`
- `"Channel name must be between 1 and 255 characters"`
- `"Channel with this name already exists"`

**YouTube URL**:
- `"Not a valid YouTube channel URL"`
- `"Unable to extract channel ID from URL"`

---

## Pydantic Schemas (Backend Reference)

### GlobalSettingsSchema

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class GlobalSettingsSchema(BaseModel):
    id: int = 1
    default_download_path: str = Field(..., min_length=1, max_length=2000)
    default_subtitle_language: Optional[str] = Field(None, min_length=2, max_length=2)
    default_video_quality: Optional[str] = Field(None, max_length=50)
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
```

### GlobalSettingsUpdateSchema

```python
class GlobalSettingsUpdateSchema(BaseModel):
    default_download_path: str = Field(..., min_length=1, max_length=2000)
    default_subtitle_language: Optional[str] = Field(None, min_length=2, max_length=2)
    default_video_quality: Optional[str] = Field(None, max_length=50)
```

### ChannelCreateSchema

```python
class ChannelCreateSchema(BaseModel):
    url: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=255)
    download_path: Optional[str] = Field(None, max_length=2000)
    subtitle_language: Optional[str] = Field(None, min_length=2, max_length=2)
    video_quality: Optional[str] = Field(None, max_length=50)
```

### ChannelUpdateSchema

```python
class ChannelUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    download_path: Optional[str] = Field(None, max_length=2000)
    subtitle_language: Optional[str] = Field(None, min_length=2, max_length=2)
    video_quality: Optional[str] = Field(None, max_length=50)
```

### ChannelResponseSchema

```python
class ChannelResponseSchema(BaseModel):
    id: int
    channel_id: str
    title: str
    name: str
    url: str
    download_path: str
    subtitle_language: Optional[str] = None
    video_quality: Optional[str] = None
    date_added: datetime
    last_updated: Optional[datetime] = None

    class Config:
        from_attributes = True
```

---

## TypeScript Types (Frontend Reference)

### GlobalSettings

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
```

### Channel

```typescript
export interface Channel {
  id: number;
  channel_id: string;
  title: string;  // YouTube channel name
  name: string;   // Custom user name
  url: string;
  download_path: string;
  subtitle_language: string | null;
  video_quality: string | null;
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

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-09 | Initial API specification |

## Notes

- All timestamps in ISO 8601 format (UTC)
- All endpoints return `application/json`
- Request bodies must be `application/json`
- CORS configured for `http://localhost:5173` (frontend dev server)
