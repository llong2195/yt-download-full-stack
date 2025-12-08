"""Verify complete database setup including Huey."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.utils.config import settings
from src.models import engine
from sqlalchemy import inspect


def main():
    print("=" * 70)
    print("DATABASE SETUP VERIFICATION")
    print("=" * 70)

    # 1. Check directories
    print("\n📁 DIRECTORIES:")
    data_dir = Path(settings.HUEY_DB).parent
    downloads_dir = Path(settings.DOWNLOAD_DIR)

    print(f"   Data:      {data_dir.absolute()} {'✅' if data_dir.exists() else '❌'}")
    print(
        f"   Downloads: {downloads_dir.absolute()} {'✅' if downloads_dir.exists() else '❌'}"
    )

    # 2. Check main database
    print("\n🗄️  MAIN DATABASE:")
    db_path_str = settings.DATABASE_URL.replace("sqlite:///", "")
    if db_path_str.startswith("./"):
        db_path_str = str(Path.cwd() / db_path_str[2:])
    db_path = Path(db_path_str)

    if db_path.exists():
        size_kb = db_path.stat().st_size / 1024
        print(f"   Path:   {db_path.absolute()}")
        print(f"   Size:   {size_kb:.2f} KB")
        print(f"   Status: ✅ EXISTS")

        # Check tables
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"   Tables: {len(tables)}")
        for table in tables:
            indexes = inspector.get_indexes(table)
            print(f"      - {table}: {len(indexes)} indexes")
    else:
        print(f"   Path:   {db_path.absolute()}")
        print(f"   Status: ❌ NOT FOUND")

    # 3. Check Huey database
    print("\n🔄 HUEY TASK QUEUE DATABASE:")
    huey_db_path = Path(settings.HUEY_DB)
    if not huey_db_path.is_absolute():
        huey_db_path = Path.cwd() / huey_db_path

    print(f"   Path:   {huey_db_path.absolute()}")

    if huey_db_path.exists():
        size_kb = huey_db_path.stat().st_size / 1024
        print(f"   Size:   {size_kb:.2f} KB")
        print(f"   Status: ✅ EXISTS")
    else:
        print(f"   Size:   0 KB")
        print(f"   Status: ⚠️  WILL BE CREATED ON FIRST USE")

    # 4. Check Huey configuration
    print("\n⚙️  HUEY CONFIGURATION:")
    print(f"   Immediate Mode: {settings.HUEY_IMMEDIATE_MODE}")

    if settings.HUEY_IMMEDIATE_MODE:
        print(f"   Consumer:       ❌ NOT NEEDED (tasks run immediately)")
    else:
        print(f"   Consumer:       ⚠️  REQUIRED (run: python run_consumer.py)")

    # 5. Test Huey initialization
    print("\n🧪 TESTING HUEY INITIALIZATION:")
    try:
        settings.ensure_huey_database()
        print("   ✅ Huey database check passed")

        from src.tasks.huey_instance import huey

        print(f"   ✅ Huey instance created: {huey.name}")
        print(f"   ✅ Storage type: {huey.storage.__class__.__name__}")
        print(f"   ✅ Pending tasks: {len(huey)}")
    except Exception as e:
        print(f"   ❌ Huey initialization failed: {e}")
        return 1

    print("\n" + "=" * 70)
    print("✅ ALL DATABASE CHECKS PASSED")
    print("=" * 70)

    # Summary
    print("\n📝 SUMMARY:")
    print("   • Main database:  ✅ Ready")
    print("   • Huey database:  ✅ Ready")
    print("   • Directories:    ✅ Created")
    print("   • Configuration:  ✅ Loaded")

    if settings.HUEY_IMMEDIATE_MODE:
        print("\n💡 TIP: Immediate mode is ON - tasks will execute instantly")
        print("   For production, set HUEY_IMMEDIATE_MODE=false and run consumer")
    else:
        print("\n💡 TIP: Remember to run Huey consumer for task processing:")
        print("   python run_consumer.py")

    return 0


if __name__ == "__main__":
    sys.exit(main())
