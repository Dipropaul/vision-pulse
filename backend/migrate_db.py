"""Add duration column to existing database"""
import sqlite3
from pathlib import Path

# Database path
db_path = Path("visionpulse.db")

if db_path.exists():
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Check if duration column exists
    cursor.execute("PRAGMA table_info(videos)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'duration' not in columns:
        print("Adding duration column to videos table...")
        cursor.execute("ALTER TABLE videos ADD COLUMN duration INTEGER")
        conn.commit()
        print("✓ Migration completed successfully!")
    else:
        print("Duration column already exists, no migration needed.")
    
    conn.close()
else:
    print("Database doesn't exist yet. It will be created with the new schema.")
