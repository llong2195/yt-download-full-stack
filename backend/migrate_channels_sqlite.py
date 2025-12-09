#!/usr/bin/env python
"""SQLite-safe data migration for channel settings feature.

SQLite has limited ALTER TABLE support, so we:
1. Create new table with new schema
2. Copy data with transformations  
3. Drop old table
4. Rename new table
"""

import sys
import sqlite3
from pathlib import Path

# Path to database
DB_PATH = Path(__file__).parent / "data" / "ytdownloader.db"


def migrate_database():
    """Perform SQLite-safe schema migration."""
    print(f"🔄 Migrating database: {DB_PATH}")
    
    if not DB_PATH.exists():
        print("   ℹ️  Database doesn't exist yet - no migration needed")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if migration already done
        cursor.execute("PRAGMA table_info(channels)")
        columns = {row[1] for row in cursor.fetchall()}
        
        if 'title' in columns:
            print("   ℹ️  Migration already completed - title column exists")
            conn.close()
            return
        
        print("   📋 Backing up existing channels...")
        cursor.execute("SELECT id, channel_id, name, url, download_path, date_added, last_updated FROM channels")
        existing_channels = cursor.fetchall()
        print(f"      Found {len(existing_channels)} channel(s)")
        
        # Create new table with updated schema
        print("   🏗️  Creating new channels table...")
        cursor.execute("""
            CREATE TABLE channels_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id VARCHAR(255) UNIQUE NOT NULL,
                title VARCHAR(500) NOT NULL,
                name VARCHAR(255) UNIQUE NOT NULL,
                url VARCHAR(1000) NOT NULL,
                download_path VARCHAR(2000) NOT NULL,
                subtitle_language VARCHAR(10),
                video_quality VARCHAR(50),
                date_added DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_updated DATETIME
            )
        """)
        
        # Create indexes on new table
        cursor.execute("CREATE UNIQUE INDEX ix_channels_new_channel_id ON channels_new (channel_id)")
        cursor.execute("CREATE INDEX ix_channels_new_date_added ON channels_new (date_added)")
        cursor.execute("CREATE UNIQUE INDEX ix_channels_new_name ON channels_new (name)")
        
        # Migrate data
        print("   📦 Migrating channel data...")
        used_names = set()
        
        for row in existing_channels:
            id, channel_id, old_name, url, download_path, date_added, last_updated = row
            
            # Copy name to title, generate sanitized unique custom name
            title = old_name
            
            # Generate unique custom name
            import re
            base_name = re.sub(r'[<>:"/\\|?*]', '_', old_name)
            custom_name = base_name
            counter = 1
            
            while custom_name in used_names:
                custom_name = f"{base_name}_{counter}"
                counter += 1
            
            used_names.add(custom_name)
            
            cursor.execute("""
                INSERT INTO channels_new 
                (id, channel_id, title, name, url, download_path, subtitle_language, video_quality, date_added, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, NULL, NULL, ?, ?)
            """, (id, channel_id, title, custom_name, url, download_path, date_added, last_updated))
            
            print(f"      ✓ Migrated: {title} → {custom_name}")
        
        # Drop old table and rename new one
        print("   🔄 Replacing old table...")
        cursor.execute("DROP TABLE channels")
        cursor.execute("ALTER TABLE channels_new RENAME TO channels")
        
        # Commit transaction
        conn.commit()
        print(f"\n   ✅ Successfully migrated {len(existing_channels)} channel(s)")
        
    except Exception as e:
        conn.rollback()
        print(f"\n   ❌ Migration failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    try:
        migrate_database()
        print("\n🎉 Migration complete!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
