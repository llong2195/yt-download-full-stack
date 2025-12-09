# Feature Specification: Channel and Global Download Settings

**Feature Branch**: `2-channel-settings`  
**Created**: December 9, 2025  
**Status**: Draft  
**Input**: User description: "setting chung - nơi download mặc định nếu channel không có setting ( ./download ) - ngôn ngữ mặc định nếu channel không có setting -- Channel ( Kênh ) - thay thế trường name -> title ( tên của kênh ) - thêm trường name: tên do mình điền vào - mỗi channel có một download_path: (mặc định : setting_download_path + name) - Khi tải video file_name: {index}_{title_video}.{định dạng} ( index theo định dạng 0001 -> tăng dần 0002 ) để windown dễ sắp xếp - mỗi channel chọn một ngôn ngữ để đi kèm khi download: ja, vn, ... - cho chọn chất lượng tải xuống khi thêm/sửa channel"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Configure Global Download Defaults (Priority: P2)

An administrator wants to set system-wide default settings for all new channels so they don't have to configure the same settings repeatedly for each channel.

**Why this priority**: Provides convenience and consistency across channels, but channels can still function without global settings (using hardcoded defaults).

**Independent Test**: Can be fully tested by configuring global settings and verifying that new channels inherit these defaults. Existing functionality remains unaffected if global settings are not configured.

**Acceptance Scenarios**:

1. **Given** no global settings exist, **When** the system needs to download a video for a channel without specific settings, **Then** system uses hardcoded defaults (download path: ./download, language: none)
2. **Given** administrator configures global default download path to "D:/Videos", **When** a new channel is added without specifying a download path, **Then** the channel's download path defaults to "D:/Videos/{channel-name}"
3. **Given** administrator configures global default subtitle language to "en", **When** a new channel is added without specifying a language, **Then** downloads for that channel include English subtitles by default

---

### User Story 2 - Add Custom Channel Name and Enhanced Channel Properties (Priority: P1)

A user wants to organize their YouTube channel subscriptions with custom names and specific download settings, so they can easily identify channels and have downloads organized their preferred way.

**Why this priority**: Core functionality that directly impacts how users manage and organize their channels. The distinction between channel title (from YouTube) and custom name (user-defined) is fundamental to the feature.

**Independent Test**: Can be tested by adding a channel with custom name and settings, then verifying downloads are organized correctly. This is the MVP that delivers immediate value.

**Acceptance Scenarios**:

1. **Given** a user adds a YouTube channel "TechTips Official", **When** they provide custom name "Tech Reviews", **Then** the system stores both the channel title "TechTips Official" (from YouTube) and custom name "Tech Reviews" (user-provided)
2. **Given** a channel named "Tech Reviews" with custom download path "D:/YouTube/Tech", **When** a video is downloaded, **Then** it is saved to "D:/YouTube/Tech"
3. **Given** global download path is "./download", **When** a new channel "Music" is added without custom download path, **Then** the channel's download path defaults to "./download/Music"
4. **Given** a channel exists with custom name "Japanese Lessons", **When** viewing the channel list, **Then** the custom name "Japanese Lessons" is displayed prominently with the original channel title shown as secondary information

---

### User Story 3 - Sequential Video Naming for Organized Downloads (Priority: P1)

A user wants downloaded videos to be automatically numbered in sequence so Windows File Explorer displays them in chronological download order, making it easier to track and watch videos in the order they were saved.

**Why this priority**: Critical for user experience on Windows systems where alphabetical file sorting is default. Without sequential numbering, videos would be sorted unpredictably by title.

**Independent Test**: Can be tested by downloading multiple videos from a channel and verifying they are named with sequential indices that sort correctly in File Explorer.

**Acceptance Scenarios**:

1. **Given** a channel has no videos downloaded yet, **When** the first video "Amazing Tutorial" is downloaded as MP4, **Then** the file is saved as "0001_Amazing Tutorial.mp4"
2. **Given** a channel already has videos with highest index 0023, **When** a new video "Latest Content" is downloaded, **Then** the file is saved as "0024_Latest Content.mp4"
3. **Given** multiple videos are downloaded in sequence, **When** viewed in Windows File Explorer sorted by name, **Then** videos appear in download order (0001, 0002, 0003, etc.)
4. **Given** a channel's last downloaded video has index 9999, **When** the next video is downloaded, **Then** the system uses index 10000 (5 digits)
5. **Given** video title contains special characters like ":", "/", or "\", **When** the file is saved, **Then** these characters are replaced with safe alternatives (e.g., "-", "_") while maintaining readability

---

### User Story 4 - Channel-Specific Subtitle Language Selection (Priority: P2)

A user wants to specify preferred subtitle languages for different channels so educational or foreign language content automatically includes the subtitles they need without manual configuration per video.

**Why this priority**: Enhances user experience for specific use cases (language learning, accessibility) but not critical for basic download functionality.

**Independent Test**: Can be tested by configuring a channel with a specific subtitle language and verifying downloads include those subtitles.

**Acceptance Scenarios**:

1. **Given** a channel is configured with subtitle language "ja" (Japanese), **When** a video is downloaded from that channel, **Then** Japanese subtitles are downloaded if available
2. **Given** a channel has no subtitle language configured and global default is "vi" (Vietnamese), **When** a video is downloaded, **Then** Vietnamese subtitles are downloaded if available
3. **Given** a channel is configured with subtitle language "en", **When** a video is downloaded but English subtitles are not available, **Then** the download proceeds without subtitles and logs a warning
4. **Given** user edits a channel's subtitle language from "ja" to "ko" (Korean), **When** future videos are downloaded, **Then** Korean subtitles are downloaded instead of Japanese

---

### User Story 5 - Channel-Specific Video Quality Selection (Priority: P2)

A user wants to set preferred video quality for each channel so high-quality content channels download in high resolution while casual content downloads in lower quality to save disk space.

**Why this priority**: Provides control over storage and bandwidth usage, but system can function with default quality settings.

**Independent Test**: Can be tested by configuring channels with different quality settings and verifying downloads match the specified quality.

**Acceptance Scenarios**:

1. **Given** a channel is configured with quality "best" (highest available), **When** a video is downloaded, **Then** the highest quality version is selected
2. **Given** a channel is configured with quality "720p", **When** a video is downloaded, **Then** 720p quality is selected if available, or the closest lower quality if 720p is not available
3. **Given** a channel has no quality configured and global default is "1080p", **When** a video is downloaded, **Then** 1080p quality is used
4. **Given** user edits a channel's quality setting from "480p" to "1080p", **When** future videos are downloaded, **Then** they download in 1080p quality
5. **Given** a channel is configured with quality "1080p" but video only available in 720p, **When** download occurs, **Then** system downloads 720p and logs that requested quality was not available

---

### Edge Cases

- What happens when a custom channel name conflicts with an existing channel's custom name? System should either prevent duplicates or allow duplicates with a warning.
- What happens when the download path specified in settings doesn't exist or is not writable? System should create the directory if possible, or fail gracefully with a clear error message.
- What happens when calculating the next index for video numbering and multiple downloads happen simultaneously? System must ensure unique sequential numbers without conflicts.
- What happens when a video title is extremely long (e.g., 300 characters)? System should truncate the title in the filename to avoid filesystem path length limits while preserving the index.
- What happens when changing a channel's custom name after videos have already been downloaded to a path containing the old name? Existing videos remain in the old path; new downloads use the new path (or optionally, system could offer to migrate).
- What happens when a channel is deleted but videos have been downloaded to its custom path? Videos remain on disk but are no longer associated with the channel in the system.
- What happens when subtitle language code is invalid or not recognized by the download system? System should validate language codes on input and reject invalid ones.
- What happens when quality setting format is invalid (e.g., "ultra-HD" instead of "1080p")? System should validate quality settings and provide a list of acceptable values.

## Requirements *(mandatory)*

### Functional Requirements

#### Global Settings

- **FR-001**: System MUST maintain global default settings that include default download path and default subtitle language
- **FR-002**: System MUST use "./download" as the hardcoded fallback download path when no global or channel-specific path is configured
- **FR-003**: System MUST use no subtitle language (null/empty) as the hardcoded fallback when no global or channel-specific language is configured
- **FR-004**: System MUST allow administrators to view and modify global default settings
- **FR-005**: Global settings MUST be persisted and loaded on system restart

#### Channel Properties

- **FR-006**: System MUST store both "title" (original YouTube channel name) and "name" (user-provided custom name) for each channel
- **FR-007**: The "title" field MUST be automatically populated from YouTube channel metadata and updated periodically
- **FR-008**: The "name" field MUST be provided by the user when adding a channel and be editable at any time
- **FR-009**: Each channel MUST have a configurable download_path that defaults to {global_download_path}/{channel_custom_name} if not explicitly set
- **FR-010**: Each channel MUST have a configurable subtitle language preference (optional, inherits from global default if not set)
- **FR-011**: Each channel MUST have a configurable video quality preference (optional, inherits from global default if not set)

#### Video File Naming

- **FR-012**: System MUST name downloaded video files using the format: {index}_{video_title}.{extension}
- **FR-013**: The index MUST be a zero-padded 4-digit number starting from 0001 (e.g., 0001, 0002, ..., 0009, 0010, ..., 0099, 0100, ..., 9999)
- **FR-014**: The index MUST auto-increment based on the highest existing index in the channel's download directory
- **FR-015**: When index exceeds 9999, system MUST expand to 5 digits (10000, 10001, etc.) to maintain sort order
- **FR-016**: The video_title component MUST be sanitized to remove or replace filesystem-unsafe characters (e.g., : / \ * ? " < > |)
- **FR-017**: System MUST track the highest index used for each channel to ensure sequential numbering
- **FR-018**: If video title length would cause the full path to exceed filesystem limits (typically 255 characters for filename), system MUST truncate the title while preserving the index and extension

#### Channel Management UI

- **FR-019**: Users MUST be able to add a new channel by providing a YouTube channel URL and custom name
- **FR-020**: Users MUST be able to edit a channel's custom name, download path, subtitle language, and quality settings
- **FR-021**: When adding a channel, system MUST allow optional configuration of download path, subtitle language, and quality (using defaults if not provided)
- **FR-022**: Channel list MUST display the custom name prominently with the channel title as secondary information
- **FR-023**: System MUST validate that download paths are valid directory paths before saving channel settings
- **FR-024**: System MUST validate that subtitle language codes are supported (e.g., ISO 639-1 codes like "en", "ja", "vi", "ko")
- **FR-025**: System MUST validate that quality settings use recognized formats (e.g., "best", "worst", "1080p", "720p", "480p", "360p")

#### Download Behavior

- **FR-026**: When downloading a video, system MUST use channel-specific settings if configured; otherwise fall back to global defaults
- **FR-027**: System MUST create the download directory if it doesn't exist before attempting to download
- **FR-028**: System MUST log warnings when requested subtitle language is not available for a video
- **FR-029**: System MUST log warnings when requested quality is not available and a fallback quality is used
- **FR-030**: System MUST prevent index conflicts by checking for existing files with the same index before finalizing the filename

### Key Entities

- **GlobalSettings**: Represents system-wide default configuration
  - default_download_path: Base directory for downloads (defaults to "./download")
  - default_subtitle_language: Default language code for subtitles (optional)
  - default_video_quality: Default quality setting for downloads (optional)

- **Channel**: Represents a YouTube channel tracked by the user
  - channel_id: Unique YouTube channel identifier
  - title: Original YouTube channel name (from YouTube API)
  - name: User-provided custom name for organization
  - url: YouTube channel URL
  - download_path: Custom download directory (defaults to {global_path}/{name})
  - subtitle_language: Preferred subtitle language (optional, inherits from global)
  - video_quality: Preferred video quality (optional, inherits from global)
  - last_video_index: Highest index used for video files (for sequential numbering)
  - date_added: Timestamp when channel was added
  - last_updated: Timestamp of last update

- **DownloadedVideo**: Represents a video that has been downloaded
  - channel_id: Reference to the channel
  - video_id: Unique YouTube video identifier
  - video_title: Title of the video
  - file_name: Full filename including index and extension
  - file_path: Complete path where video is stored
  - index_number: The sequential index assigned to this video
  - quality: Actual quality downloaded
  - has_subtitles: Whether subtitles were downloaded
  - subtitle_language: Language of downloaded subtitles (if any)
  - download_date: Timestamp of download

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can add and configure a new channel with custom name and settings in under 30 seconds
- **SC-002**: Downloaded videos from the same channel appear in correct chronological order (by index) when sorted by name in File Explorer 100% of the time
- **SC-003**: Users can successfully set global defaults that apply to all new channels without per-channel configuration
- **SC-004**: System correctly inherits settings (global → channel) with zero configuration errors or conflicts
- **SC-005**: Custom channel names make it possible for users to identify channels 50% faster than using YouTube channel titles alone (especially for channels with generic or long titles)
- **SC-006**: Video file naming prevents sorting confusion, reducing user time spent manually organizing files by 80%
- **SC-007**: Subtitle language preferences result in 95% of downloaded videos having the correct subtitles when available
- **SC-008**: Quality settings are respected in 100% of downloads where the specified quality exists

## Assumptions *(mandatory)*

- The system already has a working YouTube channel and video download implementation
- Users primarily use Windows File Explorer for browsing downloaded videos (hence focus on sequential naming for Windows sorting)
- The existing download system supports quality selection and subtitle downloading capabilities
- Users manage a moderate number of channels (up to 100) where custom naming provides significant organizational value
- Video downloads are not expected to exceed 9999 per channel under normal usage
- Language codes follow ISO 639-1 standard (2-letter codes like "en", "ja", "vi")
- Quality settings follow common video resolution naming (e.g., "720p", "1080p") or keywords ("best", "worst")
- System has write permissions to create directories and files in specified download paths
- Users understand that changing a channel's name or download path doesn't automatically move existing files

## Out of Scope *(mandatory)*

- Automatic migration of existing downloaded files when channel settings change
- Bulk editing of settings across multiple channels simultaneously
- Cloud storage integration for download paths
- Advanced filename templates beyond the {index}_{title}.{ext} format
- Automatic subtitle translation or generation
- Video transcoding or quality conversion after download
- Duplicate video detection across different channels
- Automatic cleanup of old videos based on age or disk space
- Sharing settings configurations between different system installations
- Integration with external media library managers (Plex, Jellyfin, etc.)
