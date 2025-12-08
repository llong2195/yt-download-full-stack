#!/usr/bin/env python
"""Initialize the database - create all tables and indexes."""

import sys
from pathlib import Path

from sqlalchemy import inspect

# Add backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.models import Base, engine
from src.utils.config import settings


def main():
    """Initialize database tables and verify indexes."""
    print("🔧 Initializing YouTube Downloader database...")

    # Ensure directories exist
    print("📁 Creating directories...")
    settings.ensure_directories()
    print(f"   ✅ Data directory: {Path(settings.HUEY_DB).parent}")
    print(f"   ✅ Downloads directory: {settings.DOWNLOAD_DIR}")

    # Create all tables
    print("\n🗄️  Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print(f"   ✅ Database created at: {settings.DATABASE_URL}")

    # List all tables and indexes
    print("\n📊 Database schema verification:")

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    if not tables:
        print("   ❌ No tables found in database!")
        return 1

    for table in tables:
        indexes = inspector.get_indexes(table)
        columns = inspector.get_columns(table)
        print(f"   ✅ {table}: {len(columns)} columns, {len(indexes)} indexes")
        for idx in indexes:
            print(f"      - {idx['name']}")

    # Check database file
    db_path_str = settings.DATABASE_URL.replace("sqlite:///", "")
    db_path = Path(db_path_str)

    if db_path.exists():
        size_kb = db_path.stat().st_size / 1024
        print(f"\n✅ Database file exists: {db_path.absolute()}")
        print(f"   Size: {size_kb:.2f} KB")
    else:
        print(f"\n❌ Database file not found: {db_path.absolute()}")
        return 1

    print("\n🎉 Database initialization complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
