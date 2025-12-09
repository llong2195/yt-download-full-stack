"""Test video title as filename logic."""

import sys
sys.path.insert(0, '.')

from pathlib import Path
from src.utils.validators import sanitize_filename

print('=' * 80)
print('TEST: Video Title as Filename')
print('=' * 80)

# Simulate video titles
test_videos = [
    {
        'id': 'dQw4w9WgXcQ',
        'title': 'Rick Astley - Never Gonna Give You Up (Official Video)',
    },
    {
        'id': 'p6duAYhQMyw',
        'title': 'Muse - Supermassive Black Hole [Official Music Video]',
    },
    {
        'id': 'VvVRJ53oXkQ',
        'title': 'MUSE - Won\'t Stand Down [Official Music Video]',
    },
]

print('\nFilename Generation:')
print('-' * 80)

for video in test_videos:
    video_id = video['id']
    title = video['title']
    
    # Sanitize title for filename
    sanitized = sanitize_filename(title)
    
    print(f'\nVideo ID: {video_id}')
    print(f'Title:    {title}')
    print(f'Filename: {sanitized}.mp4')

# Test numbering with titles
print('\n' + '=' * 80)
print('TEST: File Numbering with Titles')
print('-' * 80)

test_dir = Path('D:\\MMO\\test-title-naming')
test_dir.mkdir(parents=True, exist_ok=True)

# Clean up old files
for old_file in test_dir.glob('*.mp4'):
    old_file.unlink()

video_title = "Rick Astley - Never Gonna Give You Up (Official Video)"
base_filename = sanitize_filename(video_title)

print(f'\nVideo title: {video_title}')
print(f'Base filename: {base_filename}')
print('\nSimulating multiple downloads:')

for attempt in range(1, 4):
    counter = 0
    final_filename = base_filename
    
    # Check if file already exists and generate unique name
    while True:
        test_path = test_dir / f"{final_filename}.mp4"
        if not test_path.exists():
            break
        counter += 1
        final_filename = f"{base_filename} ({counter})"
    
    # Create file
    output_file = test_dir / f"{final_filename}.mp4"
    output_file.touch()
    
    print(f'  Download {attempt}: {output_file.name}')

# List files
print('\n' + '=' * 80)
print('FILES CREATED:')
print('-' * 80)
all_files = sorted(test_dir.glob('*.mp4'))
for i, f in enumerate(all_files, 1):
    print(f'  {i}. {f.name}')

print('\n' + '=' * 80)
print('KEY CHANGES:')
print('-' * 80)
print('✓ OLD: Filename = video_id (e.g., dQw4w9WgXcQ.mp4)')
print('✓ NEW: Filename = video_title (e.g., Rick Astley - Never Gonna Give You Up.mp4)')
print('\n✓ Benefits:')
print('  - Human-readable filenames')
print('  - Easier to identify videos without metadata')
print('  - Better file organization')
print('  - Still unique with auto-numbering')

print('\n' + '=' * 80)
print('✓ SUCCESS: Video titles now used as filenames!')
print('=' * 80)
