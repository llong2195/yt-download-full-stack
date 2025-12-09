#!/usr/bin/env python
"""Data migration script for channel settings feature.

This script migrates existing Channel records to the new schema:
- Copies existing `name` to new `title` field  
- Sets `name` to a sanitized version (or prompts user)
- Ensures unique names
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from src.models import engine
from src.models.channel import Channel
from src.utils.validators import sanitize_filename


def migrate_channels():
    """Migrate existing channels to new schema."""
    print("🔄 Migrating channels to new schema...")
    
    with Session(engine) as session:
        channels = session.query(Channel).all()
        
        if not channels:
            print("   ℹ️  No existing channels to migrate")
            return
        
        print(f"   Found {len(channels)} channel(s) to migrate")
        
        # Track used names to ensure uniqueness
        used_names = set()
        
        for channel in channels:
            # If title doesn't exist, it means we're using old schema
            if not hasattr(channel, 'title') or channel.title is None:
                print(f"\n   Migrating: {channel.name}")
                
                # Copy old name to title
                original_name = channel.name
                
                # For backward compatibility, try to parse if the name
                # was actually a title
                # Set title to original name
                # And generate a sanitized name
                channel.title = original_name
                
                # Generate unique custom name
                base_name = sanitize_filename(original_name)
                custom_name = base_name
                counter = 1
                
                while custom_name in used_names:
                    custom_name = f"{base_name}_{counter}"
                    counter += 1
                
                channel.name = custom_name
                used_names.add(custom_name)
                
                print(f"      Title: {channel.title}")
                print(f"      Name:  {channel.name}")
        
        # Commit all changes
        session.commit()
        print(f"\n   ✅ Migrated {len(channels)} channel(s) successfully")


if __name__ == "__main__":
    try:
        migrate_channels()
        print("\n🎉 Migration complete!")
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
