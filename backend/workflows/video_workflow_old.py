from typing import TypedDict, List, Optional
import json
import asyncio

from config.settings import settings
from config.presets import VISUAL_STYLES
from services.sora_service import SoraService
from services.image_service import ImageService
from services.audio_service import AudioService

# Try to import langchain, but work without it if not available
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage
    USE_LANGCHAIN = True
except ImportError:
    USE_LANGCHAIN = False
    print("Warning: LangChain not available, using direct OpenAI API")

class VideoGenerationState(TypedDict):
    """State for the video generation workflow"""
    video_id: str
    script: str
    style: str
    voice: str
    keywords: List[str]
    negative_keywords: List[str]
    prompts: List[str]
    image_paths: List[str]
    audio_path: str
    video_path: str
    duration: Optional[int]
    narration_text: Optional[str]
    error: Optional[str]
    current_step: str

class VideoGenerationWorkflow:
    """
    Video Generation Workflow using OpenAI Sora API with DALL-E reference images
    
    Steps:
    1. Generate prompts from script
    2. Generate reference images with DALL-E
    3. Generate audio narration with selected voice
    4. Generate video using Sora with image reference
    """
    
    def __init__(self):
        # Use LangChain if available, otherwise would need direct API
        if USE_LANGCHAIN:
            self.llm = ChatOpenAI(
                model=settings.OPENAI_MODEL,
                api_key=settings.OPENAI_API_KEY,
                temperature=0.7
            )
        else:
            self.llm = None
            
        self.sora_service = SoraService()
        self.image_service = ImageService()
        self.audio_service = AudioService()
    
    
    async def run(self, initial_state: VideoGenerationState) -> VideoGenerationState:
        """Execute the video generation workflow using Sora"""
        print(f"[{initial_state['video_id']}] Starting Sora video generation workflow...")
        
        try:
            # Generate video prompt from script
            script = initial_state["script"]
            style = initial_state["style"]
            duration = initial_state.get("duration", 8)  # Default 8 seconds
            video_id = initial_state["video_id"]
            
            style_info = VISUAL_STYLES.get(style, VISUAL_STYLES["realistic"])
            
            # Create a concise video prompt
            video_prompt = f"{script}\n\nStyle: {style_info['description']}, {style_info['prompt_suffix']}"
            
            # Determine which Sora model to use
            use_pro = getattr(settings, 'SORA_MODEL', 'sora-2-pro') == 'sora-2-pro'
            
            # Generate video with Sora
            initial_state["current_step"] = "sora_generating"
            print(f"[{video_id}] 🎬 Generating video with Sora {'Pro' if use_pro else ''}...")
            
            result = await self.sora_service.generate_video(
                prompt=video_prompt,
                duration=duration,
                video_id=video_id,
                style=style,
                use_pro=use_pro
            )
            
            initial_state["video_path"] = result["video_path"]
            initial_state["duration"] = result["duration"]
            initial_state["current_step"] = "completed"
            
            print(f"[{video_id}] ✅ Video generation completed successfully!")
            return initial_state
            
        except Exception as e:
            error_msg = str(e)
            print(f"[{initial_state['video_id']}] ❌ Workflow error: {error_msg}")
            initial_state["error"] = error_msg
            initial_state["current_step"] = "failed"
            return initial_state