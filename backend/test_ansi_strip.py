"""Test ANSI code stripping for progress parsing."""

import re


def strip_ansi_codes(text: str) -> str:
    """Remove ANSI escape sequences from text."""
    ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
    return ansi_escape.sub("", text)


def parse_progress(percent_str: str) -> int:
    """Parse progress percentage from yt-dlp output."""
    # Remove ANSI color codes
    percent_str = strip_ansi_codes(str(percent_str))

    # Clean up
    percent_str = percent_str.strip().replace("%", "").replace(" ", "")

    # Parse to float then int
    progress = int(float(percent_str))

    # Clamp between 0-100
    return max(0, min(100, progress))


# Test cases
test_cases = [
    ("\x1b[0;94m  7.6\x1b[0m", 7),
    ("\x1b[0;91m 15.2\x1b[0m%", 15),
    ("  50.5%", 50),
    ("\x1b[1;32m100.0\x1b[0m%", 100),
    ("0%", 0),
    ("99.9%", 99),
    ("\x1b[0m  45.67  \x1b[0m", 45),
]

print("Testing ANSI code stripping and progress parsing:")
print("=" * 70)

passed = 0
failed = 0

for test_input, expected in test_cases:
    try:
        result = parse_progress(test_input)
        if result == expected:
            print(f"✅ PASS: {repr(test_input):50s} → {result:3d}%")
            passed += 1
        else:
            print(
                f"❌ FAIL: {repr(test_input):50s} → {result:3d}% (expected {expected}%)"
            )
            failed += 1
    except Exception as e:
        print(f"❌ ERROR: {repr(test_input):50s} → {e}")
        failed += 1

print("=" * 70)
print(f"Results: {passed} passed, {failed} failed")

if failed == 0:
    print("✅ All tests passed!")
else:
    print(f"❌ {failed} tests failed")
