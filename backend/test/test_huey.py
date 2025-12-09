"""Test Huey immediate mode."""

from src.tasks.huey_instance import huey
from src.tasks.download_tasks import download_video

print("=" * 60)
print("HUEY CONFIGURATION TEST")
print("=" * 60)
print(f"Huey instance: {huey.name}")
print(f"Immediate mode: {huey.immediate}")
print(f"Storage: {huey.storage.__class__.__name__}")
print(f"Pending tasks: {len(huey)}")
print("=" * 60)

if huey.immediate:
    print("✅ IMMEDIATE MODE ENABLED")
    print("   Tasks will execute immediately (no consumer needed)")
else:
    print("⚠️  IMMEDIATE MODE DISABLED")
    print("   You must run consumer: python run_consumer.py")
    print("   Or set HUEY_IMMEDIATE_MODE=true in .env")

print("=" * 60)
