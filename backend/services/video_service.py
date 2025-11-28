from pathlib import Path
from typing import List
try:
    # Try moviepy 2.x
    from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
except ImportError:
    # Fall back to moviepy 1.x
    from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from PIL import Image
import asyncio

from backend.config.settings import settings

class VideoService:
    """Service for assembling videos from images and audio"""
    
    def __init__(self):
        self.videos_dir = settings.VIDEOS_DIR
        self.images_dir = settings.IMAGES_DIR
        self.audio_dir = settings.AUDIO_DIR
        self.fps = settings.DEFAULT_VIDEO_FPS
    
    def _url_to_filepath(self, url_path: str, video_id: str, media_type: str) -> str:
        """Convert URL path to filesystem path"""
        if url_path.startswith('/'):
            # Extract filename from URL path
            filename = Path(url_path).name
            if media_type == 'images':
                return str(self.images_dir / video_id / filename)
            elif media_type == 'audio':
                return str(self.audio_dir / video_id / filename)
        return url_path  # Already a filesystem path
    
    async def create_video(
        self, 
        image_paths: List[str], 
        audio_path: str, 
        video_id: str
    ) -> dict:
        """
        Create video from images and audio
        
        Args:
            image_paths: List of image file paths
            audio_path: Path to audio file
            video_id: Unique identifier for the video
            
        Returns:
            Dictionary with video_path and duration
        """
        try:
            print(f"  Assembling video from {len(image_paths)} images...")
            
            # Convert URL paths to filesystem paths
            fs_image_paths = [self._url_to_filepath(path, video_id, 'images') for path in image_paths]
            fs_audio_path = self._url_to_filepath(audio_path, video_id, 'audio')
            
            # Run video creation in thread pool to avoid blocking
            result = await asyncio.to_thread(
                self._create_video_sync,
                fs_image_paths,
                fs_audio_path,
                video_id
            )
            
            print(f"  ✓ Video saved: {result['video_path']} (duration: {result['duration']}s)")
            
            return result
            
        except Exception as e:
            print(f"  ✗ Failed to create video: {str(e)}")
            raise
    
    def _create_video_sync(
        self, 
        image_paths: List[str], 
        audio_path: str, 
        video_id: str
    ) -> dict:
        """Synchronous video creation (runs in thread pool)"""
        
        # Load audio to get duration
        audio = AudioFileClip(audio_path)
        audio_duration = audio.duration
        
        # Calculate duration per image
        num_images = len(image_paths)
        duration_per_image = audio_duration / num_images
        
        print(f"  Audio duration: {audio_duration:.2f}s")
        print(f"  Duration per image: {duration_per_image:.2f}s")
        
        # Create video clips from images with simple resize (motion effects disabled for compatibility)
        clips = []
        for i, image_path in enumerate(image_paths):
            print(f"  Processing image {i + 1}/{num_images}...")
            
            # Ensure consistent image size
            img = Image.open(image_path)
            img = img.convert('RGB')
            
            # Resize to Full HD
            target_size = (1920, 1080)
            img = self._resize_image(img, target_size)
            
            # Save processed image temporarily
            temp_path = Path(image_path).with_suffix('.temp.jpg')
            img.save(temp_path, 'JPEG', quality=95)
            
            # Create simple clip (motion effects can be added later when MoviePy compatibility improves)
            clip = ImageClip(str(temp_path), duration=duration_per_image)
            clips.append(clip)
            
            # Clean up temp file
            temp_path.unlink()
        
        # Concatenate all clips
        print("  Concatenating clips...")
        video = concatenate_videoclips(clips, method="compose")
        
        # Add audio (MoviePy 2.x uses with_audio instead of set_audio)
        print("  Adding audio...")
        try:
            video = video.with_audio(audio)
        except AttributeError:
            # Fallback for MoviePy 1.x
            video = video.set_audio(audio)
        
        # Write final video
        video_path = self._get_video_path(video_id)
        video_path.parent.mkdir(parents=True, exist_ok=True)
        
        print("  Rendering final video...")
        try:
            # MoviePy 2.x
            video.write_videofile(
                str(video_path),
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                logger=None  # Suppress moviepy logs
            )
        except TypeError:
            # MoviePy 1.x fallback
            video.write_videofile(
                str(video_path),
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                logger=None
            )
        
        # Clean up
        video.close()
        audio.close()
        for clip in clips:
            clip.close()
        
        # Return URL path and duration
        return {
            "video_path": f"/videos/{video_id}.mp4",
            "duration": int(audio_duration)  # Duration in seconds
        }
    
    def _resize_image(self, img: Image.Image, target_size: tuple) -> Image.Image:
        """Resize image to target size while maintaining aspect ratio"""
        # Calculate aspect ratios
        target_ratio = target_size[0] / target_size[1]
        img_ratio = img.width / img.height
        
        if img_ratio > target_ratio:
            # Image is wider, fit to width
            new_height = int(target_size[0] / img_ratio)
            resized = img.resize((target_size[0], new_height), Image.Resampling.LANCZOS)
            # Pad height
            result = Image.new('RGB', target_size, (0, 0, 0))
            y_offset = (target_size[1] - new_height) // 2
            result.paste(resized, (0, y_offset))
        else:
            # Image is taller, fit to height
            new_width = int(target_size[1] * img_ratio)
            resized = img.resize((new_width, target_size[1]), Image.Resampling.LANCZOS)
            # Pad width
            result = Image.new('RGB', target_size, (0, 0, 0))
            x_offset = (target_size[0] - new_width) // 2
            result.paste(resized, (x_offset, 0))
        
        return result
    
    def _get_video_path(self, video_id: str) -> Path:
        """Get the path for the video file"""
        return self.videos_dir / f"{video_id}.mp4"
