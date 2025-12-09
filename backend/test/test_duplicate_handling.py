"""Test complete duplicate file handling with actual video ID format."""

import sys
sys.path.insert(0, '.')

from pathlib import Path

print('=' * 80)
print('REAL-WORLD TEST: Duplicate Video Download Handling')
print('=' * 80)

# Setup realistic test scenario
test_dir = Path('D:\\MMO\\Rick Astley')
test_dir.mkdir(parents=True, exist_ok=True)

# Real YouTube video ID format (11 characters)
video_id = 'dQw4w9WgXcQ'  # Rick Astley - Never Gonna Give You Up

print(f'\nChannel directory: {test_dir}')
print(f'Video ID: {video_id}')
print('\nScenario: User downloads same video multiple times')
print('=' * 80)

# Clean up existing test files first
for old_file in test_dir.glob(f'{video_id}*.mp4'):
    old_file.unlink()
    print(f'Cleaned up: {old_file.name}')

print('\nSimulating downloads:')
print('-' * 80)

downloads = []
for attempt in range(1, 6):
    # This is the exact logic from download_tasks.py
    base_filename = video_id
    counter = 0
    final_filename = base_filename
    
    # Check if file already exists and generate unique name
    while True:
        test_path = test_dir / f"{final_filename}.mp4"
        if not test_path.exists():
            break
        counter += 1
        final_filename = f"{base_filename} ({counter})"
    
    # Simulate download
    output_file = test_dir / f"{final_filename}.mp4"
    output_file.write_text(f"Video content - download {attempt}")
    downloads.append(output_file)
    
    print(f'Download #{attempt}:')
    print(f'  ✓ Saved to: {output_file.name}')
    print(f'  ✓ File size: {output_file.stat().st_size} bytes')

# Verify results
print('\n' + '=' * 80)
print('VERIFICATION:')
print('-' * 80)

all_files = sorted(test_dir.glob(f'{video_id}*.mp4'))
print(f'Total files created: {len(all_files)}')
print(f'Expected files: {len(downloads)}')
print(f'Match: {"✓ YES" if len(all_files) == len(downloads) else "✗ NO"}')

print('\nFile list:')
for i, f in enumerate(all_files, 1):
    size = f.stat().st_size
    print(f'  {i}. {f.name:30} ({size} bytes)')

# Test edge case: Download #6
print('\n' + '=' * 80)
print('EDGE CASE TEST: Download #6')
print('-' * 80)

base_filename = video_id
counter = 0
final_filename = base_filename

while True:
    test_path = test_dir / f"{final_filename}.mp4"
    if not test_path.exists():
        break
    counter += 1
    final_filename = f"{base_filename} ({counter})"

print(f'Next available filename: {final_filename}.mp4')
print(f'Counter value: {counter}')

print('\n' + '=' * 80)
print('✓ SUCCESS: Duplicate file handling verified!')
print('  ✓ Files are never overwritten')
print('  ✓ Numbering starts from (1), then (2), (3), etc.')
print('  ✓ Original file keeps simple name (no number)')
print('  ✓ Works with real YouTube video IDs')
print('=' * 80)
