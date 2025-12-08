#!/bin/bash
# Run Huey consumer to process background tasks

echo "🚀 Starting Huey consumer..."
echo "📁 Working directory: $(pwd)"
echo "🔄 Processing tasks from: data/huey.db"
echo ""

# Run Huey consumer with verbose logging
python -m huey.consumer main.huey -v -w 2 -k thread

# Options:
# -v: verbose mode (shows task execution details)
# -w 2: 2 worker threads (can process 2 tasks concurrently)
# -k thread: use thread-based workers (faster for I/O-bound tasks like downloads)
