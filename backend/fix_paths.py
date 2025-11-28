"""Fix existing videos to use URL paths"""
import sqlite3
from pathlib import Path

db_path = Path("visionpulse.db")

if db_path.exists():
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Get all videos with file system paths
    cursor.execute("SELECT id, video_path, audio_path, image_paths FROM videos WHERE status = 'completed'")
    videos = cursor.fetchall()
    
    for video_id, video_path, audio_path, image_paths in videos:
        # Update video_path to URL format
        if video_path and not video_path.startswith('/'):
            new_video_path = f"/videos/{video_id}.mp4"
            cursor.execute("UPDATE videos SET video_path = ? WHERE id = ?", (new_video_path, video_id))
            print(f"✓ Updated video {video_id}: {video_path} -> {new_video_path}")
        
        # Update audio_path to URL format
        if audio_path and not audio_path.startswith('/'):
            new_audio_path = f"/audio/{video_id}/narration.mp3"
            cursor.execute("UPDATE videos SET audio_path = ? WHERE id = ?", (new_audio_path, video_id))
            print(f"✓ Updated audio {video_id}: {audio_path} -> {new_audio_path}")
    
    conn.commit()
    conn.close()
    print("\n✓ All videos updated to use URL paths!")
else:
    print("Database doesn't exist yet.")
