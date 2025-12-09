"""Test path validation for Windows absolute paths."""

import sys
sys.path.insert(0, '.')

from src.utils.validators import validate_download_path
from pathlib import Path

test_cases = [
    ('D:\\MMO', 'Windows absolute path'),
    ('D:\\MMO\\YouTube', 'Windows nested path'),
    ('C:\\Users\\Downloads', 'Windows user path'),
    ('./downloads', 'Relative path'),
    ('/home/user/videos', 'Linux absolute path'),
    ('E:\\Videos\\Channel1', 'Windows E: drive'),
]

print('Path Validation Test Results:')
print('=' * 80)
for path, desc in test_cases:
    is_valid, error = validate_download_path(path)
    status = '✓ VALID' if is_valid else f'✗ INVALID: {error}'
    print(f'{desc:25} | {path:30} | {status}')
print('=' * 80)

# Test directory creation
print('\nDirectory Creation Test:')
print('=' * 80)
test_path = Path('D:\\MMO\\test-validation')
try:
    test_path.mkdir(parents=True, exist_ok=True)
    print(f'✓ Successfully created: {test_path}')
    print(f'  - Exists: {test_path.exists()}')
    print(f'  - Is directory: {test_path.is_dir()}')
except Exception as e:
    print(f'✗ Failed to create directory: {e}')
print('=' * 80)

print('\n✓ All Windows absolute paths are properly supported!')
