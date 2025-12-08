# Progress Parsing Fix - ANSI Color Codes

## 🐛 Issue

**Error**: `Failed to parse progress: could not convert string to float: '\x1b[0;94m  7.6\x1b[0m'`

**Cause**: yt-dlp outputs progress with ANSI escape sequences (color codes) which cannot be parsed as float.

## ✅ Solution

Added ANSI escape sequence stripping before parsing progress percentage.

### Changes Made

1. **New Function**: `strip_ansi_codes(text: str) -> str`
   - Removes ANSI escape sequences using regex: `\x1b\[[0-9;]*m`
   - Cleans color codes from yt-dlp output

2. **Enhanced Progress Parsing**:
   - Strip ANSI codes before parsing
   - Better error handling with detailed logging
   - Clamp progress between 0-100%
   - Show both raw and cleaned values in error logs

### Code Example

```python
# Before (fails with ANSI codes)
percent_str = d.get("_percent_str", "0%").strip().replace("%", "")
progress = int(float(percent_str))  # ❌ Fails on '\x1b[0;94m  7.6\x1b[0m'

# After (handles ANSI codes)
percent_str = d.get("_percent_str", "0%")
percent_str = strip_ansi_codes(str(percent_str))  # Remove color codes
percent_str = percent_str.strip().replace("%", "").replace(" ", "")
progress = int(float(percent_str))  # ✅ Works!
progress = max(0, min(100, progress))  # Clamp 0-100
```

## 🧪 Testing

### Test Cases
```python
# All these now parse correctly:
'\x1b[0;94m  7.6\x1b[0m'      →  7%
'\x1b[0;91m 15.2\x1b[0m%'     → 15%
'  50.5%'                      → 50%
'\x1b[1;32m100.0\x1b[0m%'     → 100%
```

### Test Scripts
- `test_ansi_strip.py` - Test ANSI stripping function
- `test_progress_hook.py` - Test full progress hook with mock data

## 📊 Impact

- ✅ Progress updates now work with colored yt-dlp output
- ✅ No more parsing errors in logs
- ✅ Real-time download progress visible in UI
- ✅ Better error logging with raw/cleaned values

## 🔍 Technical Details

### ANSI Escape Sequences
Common yt-dlp color codes:
- `\x1b[0;94m` - Blue color
- `\x1b[0;91m` - Red color  
- `\x1b[1;32m` - Green bold
- `\x1b[0m` - Reset color

### Regex Pattern
```python
ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
```
- `\x1b` - ESC character
- `\[` - Open bracket
- `[0-9;]*` - Zero or more digits/semicolons
- `m` - End marker

## 📝 Files Modified

- `src/tasks/download_tasks.py`
  - Added `strip_ansi_codes()` function
  - Enhanced `DownloadProgress.__call__()` method
  - Improved error logging

## ⚠️ Error Logging

New error format includes debugging info:
```python
logger.warning(
    f"Failed to parse progress: {e} "
    f"(raw: {repr(raw_percent)}, cleaned: {repr(percent_str)})"
)
```

This helps diagnose any future parsing issues.

## 🚀 Deployment

No configuration changes needed. The fix is automatic and backward compatible.

### Verification
```bash
# Test the fix
cd backend
python test_ansi_strip.py
python test_progress_hook.py

# All tests should pass
✅ All tests passed!
```

## 💡 Future Improvements

Potential enhancements:
1. Alternative: Use yt-dlp's `progress_template` to disable colors
2. Cache compiled regex for performance
3. Add unit tests to test suite
4. Monitor for other ANSI sequences

## 📚 References

- ANSI Escape Codes: https://en.wikipedia.org/wiki/ANSI_escape_code
- yt-dlp Progress Hooks: https://github.com/yt-dlp/yt-dlp#progress-hooks
- Python Regex: https://docs.python.org/3/library/re.html

---

**Status**: ✅ **FIXED** - Progress parsing now handles ANSI color codes correctly!
