"""Start both FastAPI server and Huey consumer in parallel."""

import subprocess
import sys
import time
import signal
from pathlib import Path

# Track subprocesses
processes = []


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print("\n🛑 Shutting down...")
    for proc in processes:
        proc.terminate()
    sys.exit(0)


def main():
    """Start FastAPI and Huey consumer in parallel."""
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)

    print("=" * 60)
    print("🚀 Starting YouTube Downloader Full Stack")
    print("=" * 60)
    print()

    # Start FastAPI server
    print("📡 Starting FastAPI server on http://0.0.0.0:8000")
    fastapi_proc = subprocess.Popen(
        [sys.executable, "main.py"],
        cwd=Path(__file__).parent,
    )
    processes.append(fastapi_proc)

    # Give FastAPI a moment to start
    time.sleep(2)

    # Start Huey consumer
    print("⚙️  Starting Huey consumer...")
    huey_proc = subprocess.Popen(
        [sys.executable, "run_consumer.py"],
        cwd=Path(__file__).parent,
    )
    processes.append(huey_proc)

    print()
    print("=" * 60)
    print("✅ All services started successfully!")
    print("=" * 60)
    print()
    print("📡 FastAPI: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("⚙️  Huey Consumer: Running in background")
    print()
    print("Press Ctrl+C to stop all services")
    print("=" * 60)
    print()

    # Wait for processes
    try:
        # Monitor processes
        while True:
            # Check if any process died
            for proc in processes:
                if proc.poll() is not None:
                    print(f"⚠️  Process {proc.pid} terminated unexpectedly")
                    # Kill all processes
                    for p in processes:
                        if p.poll() is None:
                            p.terminate()
                    sys.exit(1)
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)


if __name__ == "__main__":
    main()
