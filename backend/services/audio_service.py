from pathlib import Path
from openai import AsyncOpenAI

from config.settings import settings
from config.presets import NARRATION_VOICES

class AudioService:
    """Service for generating narration audio using OpenAI TTS"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.audio_dir = settings.AUDIO_DIR
    
    async def generate_narration(self, text: str, voice: str, video_id: str) -> str:
        """
        Generate narration audio from text
        
        Args:
            text: Script text to narrate
            voice: Voice ID to use
            video_id: Unique identifier for the video
            
        Returns:
            File path to generated audio
        """
        try:
            # Get voice ID from presets
            voice_config = NARRATION_VOICES.get(voice, NARRATION_VOICES["alloy"])
            voice_id = voice_config["voice_id"]
            
            print(f"  Generating narration with voice: {voice_config['name']}...")
            
            # Generate audio with OpenAI TTS
            response = await self.client.audio.speech.create(
                model=settings.OPENAI_TTS_MODEL,
                voice=voice_id,
                input=text,
                response_format="mp3"
            )
            
            # Save audio file
            audio_path = self._get_audio_path(video_id)
            audio_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Stream to file
            await response.astream_to_file(str(audio_path))
            
            print(f"  ✓ Audio saved: {audio_path}")
            
            # Return URL path instead of file system path
            return f"/audio/{video_id}/narration.mp3"
            
        except Exception as e:
            print(f"  ✗ Failed to generate audio: {str(e)}")
            raise
    
    def _get_audio_path(self, video_id: str) -> Path:
        """Get the path for the audio file"""
        return self.audio_dir / video_id / "narration.mp3"
