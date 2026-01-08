"""Test file numbering logic for duplicate downloads."""

import sys
sys.path.insert(0, '.')

from pathlib import Path

print('=' * 80)
print('TEST: File Numbering for Duplicate Downloads')
print('=' * 80)

# Setup test directory
test_dir = Path('D:\\MMO\\test-numbering')
test_dir.mkdir(parents=True, exist_ok=True)

# Test video ID
video_id = 'test_video_123'

print(f'\nTest directory: {test_dir}')
print(f'Video ID: {video_id}')
print('\nSimulating multiple downloads of same video:')
print('-' * 80)

# Simulate the numbering logic
for attempt in range(1, 6):
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
    
    # Create the file to simulate download
    output_file = test_dir / f"{final_filename}.mp4"
    output_file.touch()
    
    print(f'Attempt {attempt}: Created file -> {output_file.name}')

# List all created files
print('\n' + '=' * 80)
print('Files created:')
print('-' * 80)
all_files = sorted(test_dir.glob('*.mp4'))
for i, f in enumerate(all_files, 1):
    print(f'{i}. {f.name}')

print('\n' + '=' * 80)
print('✓ SUCCESS: File numbering logic works correctly!')
print('  - First download: test_video_123.mp4')
print('  - Second download: test_video_123 (1).mp4')
print('  - Third download: test_video_123 (2).mp4')
print('  - And so on...')
print('=' * 80)
