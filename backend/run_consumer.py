"""Run Huey consumer to process background tasks."""

from huey.consumer import Consumer
from huey.consumer_options import ConsumerConfig
from src.tasks.huey_instance import huey

if __name__ == "__main__":
    print("🚀 Starting Huey consumer...")
    print(f"📦 Huey instance: {huey.name}")
    print(f"💾 Storage: {huey.storage}")
    print(f"📊 Pending tasks: {len(huey)}")
    print("")

    # Configure consumer
    config = ConsumerConfig(
        workers=2,  # 2 worker threads
        worker_type="thread",  # Thread-based workers
        check_worker_health=True,
        health_check_interval=10,
        flush_locks=True,
        verbose=True,
    )

    # Create and run consumer
    consumer = Consumer(huey, **config.values)
    consumer.run()
