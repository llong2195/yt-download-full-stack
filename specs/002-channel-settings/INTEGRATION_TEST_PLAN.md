# Integration Test Plan for Channel Settings Feature

**Date**: December 9, 2025  
**Feature**: 002-channel-settings  
**Status**: Test Plan Documented

## Test Environment Setup

### Prerequisites
1. Backend server running: `uvicorn main:app --reload`
2. Huey consumer running: `python run_consumer.py`
3. Frontend dev server running: `npm run dev` (or production build served)
4. Fresh database with GlobalSettings initialized

## T075: Complete Workflow Test

**Test**: Configure global settings → add channel with partial config → verify inheritance → download video → verify settings applied

### Steps:

1. **Configure Global Settings**
   - Navigate to Settings page (`/settings`)
   - Set default_download_path: `./downloads/test`
   - Set default_subtitle_language: `en`
   - Set default_video_quality: `720p`
   - Click Save
   - Verify success message

2. **Add Channel with Partial Config**
   - Navigate to Channels page (`/`)
   - Enter channel URL: `https://www.youtube.com/@kurzgesagt`
   - Enter custom name: `Kurzgesagt Test`
   - Leave download path empty (should inherit global)
   - Set subtitle language: `de` (override global)
   - Leave video quality empty (should inherit global 720p)
   - Click Add Channel
   - Verify channel appears in list

3. **Verify Inheritance**
   - Check channel card shows:
     - Custom name: "Kurzgesagt Test"
     - Title: "Kurzgesagt – In a Nutshell" (from YouTube)
   - Edit the channel
   - Verify download path shows inherited value or is empty
   - Verify subtitle language shows `de`
   - Verify video quality is empty (inheriting 720p)

4. **Download Video**
   - Navigate to Downloads page
   - Paste a video URL from the channel
   - Click Download
   - Navigate to Queue page
   - Verify task appears with:
     - Subtitle indicator showing `DE`
     - Quality indicator showing `720p`

5. **Verify Settings Applied**
   - Wait for download to complete
   - Navigate to History page
   - Verify history item shows:
     - Subtitle language badge: `DE`
     - Quality badge: `720p`
   - Check file system:
     - Video should be in `./downloads/test/kurzgesagt-test/` or similar
     - Subtitle file should exist (`.de.vtt` or `.de.srt`)
   - Check video properties (right-click → Properties → Details):
     - Resolution should be 720p or best available ≤720p

### Expected Results:
- ✅ Global settings save successfully
- ✅ Channel inherits global download path
- ✅ Channel overrides subtitle language (de instead of en)
- ✅ Channel inherits video quality (720p)
- ✅ Download uses correct settings
- ✅ German subtitles downloaded
- ✅ Video is 720p quality

---

## T076: Duplicate Channel Name Test

**Test**: Duplicate channel name → verify 409 error with clear message

### Steps:

1. Navigate to Channels page
2. Add a channel with custom name: `Test Channel`
3. Try to add another channel with same name: `Test Channel`
4. Verify error message appears
5. Verify error is clear and user-friendly

### Expected Results:
- ✅ Second channel rejected
- ✅ HTTP 409 Conflict status
- ✅ Error message: "A channel with this name already exists" or similar
- ✅ Form remains populated (user can edit name)

---

## T077: Invalid Quality/Language Code Test

**Test**: Invalid quality/language code → verify validation error

### Steps:

1. **Test Invalid Quality** (requires API call, not exposed in UI)
   ```bash
   curl -X POST http://localhost:8000/api/channels \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://youtube.com/@test",
       "name": "Test Invalid Quality",
       "video_quality": "9999p"
     }'
   ```
   - Expected: HTTP 400 with validation error

2. **Test Invalid Subtitle Language** (requires API call)
   ```bash
   curl -X POST http://localhost:8000/api/channels \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://youtube.com/@test",
       "name": "Test Invalid Lang",
       "subtitle_language": "xyz"
     }'
   ```
   - Expected: HTTP 400 with validation error

3. **Test Invalid Global Settings**
   ```bash
   curl -X PUT http://localhost:8000/api/settings \
     -H "Content-Type: application/json" \
     -d '{
       "default_video_quality": "invalid",
       "default_subtitle_language": "toolong"
     }'
   ```
   - Expected: HTTP 400 with validation error

### Expected Results:
- ✅ Invalid quality rejected (not in whitelist)
- ✅ Invalid language code rejected (not ISO 639-1)
- ✅ HTTP 400 Bad Request
- ✅ Clear validation error messages

---

## T078: Change Channel Custom Name Test

**Test**: Change channel custom name → verify update works and old downloads unaffected

### Steps:

1. Add channel with name: `Original Name`
2. Download a video from this channel
3. Wait for download to complete
4. Edit channel and change name to: `Updated Name`
5. Verify channel list shows new name
6. Navigate to History page
7. Verify old download still shows original channel name or new name (both acceptable)
8. Verify download file path unchanged
9. Download another video
10. Verify new download uses new channel name in path (if path includes channel name)

### Expected Results:
- ✅ Channel name updates successfully
- ✅ Old download history preserved
- ✅ Old file paths unchanged
- ✅ New downloads may use new name in path (implementation dependent)
- ✅ No data corruption or loss

---

## T079: Settings Persistence Test

**Test**: Settings persistence → restart backend → verify settings loaded correctly

### Steps:

1. Configure global settings:
   - Path: `./downloads/persist-test`
   - Language: `fr`
   - Quality: `1080p`
2. Save settings
3. Add a channel with custom settings
4. Stop backend server (Ctrl+C)
5. Restart backend server
6. Navigate to Settings page
7. Verify all settings match what was saved
8. Navigate to Channels page
9. Verify channel settings preserved
10. Edit channel
11. Verify settings still show correctly

### Expected Results:
- ✅ Global settings persist across restarts
- ✅ Channel settings persist across restarts
- ✅ No data loss
- ✅ Application loads successfully
- ✅ GlobalSettings singleton correctly loaded

---

## Test Execution Notes

**Manual Testing**: These tests require manual execution as they involve:
- UI interaction
- Multiple services (backend, frontend, Huey consumer)
- File system verification
- Time-based operations (download completion)

**Automation Potential**: Could be automated with:
- Selenium/Playwright for UI testing
- pytest-bdd for backend API testing
- File system assertions in pytest

**Test Data Cleanup**: After testing, clean up:
- Test channels created
- Test downloads in file system
- Test entries in download history

## Test Results Log

| Test | Date | Result | Notes |
|------|------|--------|-------|
| T075 | Pending | ⏳ | Complete workflow test |
| T076 | Pending | ⏳ | Duplicate name rejection |
| T077 | Pending | ⏳ | Validation error handling |
| T078 | Pending | ⏳ | Channel name change |
| T079 | Pending | ⏳ | Settings persistence |

---

## Automated Test Coverage

The following aspects ARE tested automatically in `test_constraints.py`:
- ✅ T070: Channel.name unique constraint (database level)
- ✅ T071: GlobalSettings singleton constraint (database level)

The following aspects COULD be tested with pytest:
- Settings service business logic
- Inheritance fallback chains
- Validator functions
- API endpoint responses (with TestClient)

**Recommendation**: Add pytest test suite for business logic, keep E2E tests manual or add later with Playwright.
