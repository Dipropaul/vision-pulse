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
    size: str  # Video resolution (e.g., "1280x720")
    keywords: List[str]
    negative_keywords: List[str]
    prompts: List[str]
    best_prompt: str  # Auto-selected best prompt
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
    
    async def generate_prompts(self, state: VideoGenerationState) -> VideoGenerationState:
        """Step 1: Generate 5-6 image prompts from script"""
        print(f"[{state['video_id']}] Step 1: Generating 5-6 prompts...")
        
        try:
            script = state["script"]
            style = state["style"]
            keywords = state.get("keywords", [])
            negative_keywords = state.get("negative_keywords", [])
            
            style_info = VISUAL_STYLES.get(style, VISUAL_STYLES["realistic"])
            style_suffix = style_info["prompt_suffix"]
            
            keywords_text = ", ".join(keywords) if keywords else ""
            negative_text = ", ".join(negative_keywords) if negative_keywords else ""
            
            prompt = f"""Create 5-6 detailed image prompts that will serve as reference images for video generation.

Script:
{script}

Visual Style: {style_info['name']}
Style Description: {style_info['description']}
Additional Keywords: {keywords_text}
Avoid: {negative_text}

Requirements:
1. Create 5-6 key scene prompts (these will be reference images for Sora)
2. Each prompt should capture a different critical visual moment
3. Include lighting, mood, composition, and camera angle details
4. Make prompts suitable for DALL-E 3
5. Keep prompts family-friendly and diverse

Return ONLY a JSON array of strings:
["prompt 1", "prompt 2", "prompt 3", "prompt 4", "prompt 5", "prompt 6"]"""

            if USE_LANGCHAIN and self.llm:
                response = await self.llm.ainvoke([HumanMessage(content=prompt)])
                content = response.content.strip()
            else:
                raise Exception("LangChain required for prompt generation")
            
            # Parse response
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            prompts = json.loads(content.strip())
            prompts = [f"{p}, {style_suffix}" for p in prompts]
            
            state["prompts"] = prompts
            state["current_step"] = "prompts_generated"
            print(f"[{state['video_id']}] Generated {len(prompts)} prompts")
            
        except Exception as e:
            state["error"] = f"Prompt generation failed: {str(e)}"
            print(f"[{state['video_id']}] Error: {state['error']}")
        
        return state
    
    async def select_best_prompt(self, state: VideoGenerationState) -> VideoGenerationState:
        """Step 1.5: Auto-select the best prompt for video generation"""
        print(f"[{state['video_id']}] Step 1.5: Selecting best prompt...")
        
        if state.get("error"):
            return state
        
        try:
            prompts = state["prompts"]
            script = state["script"]
            
            selection_prompt = f"""Given these {len(prompts)} image prompts, select the ONE that would work best as the primary reference for video generation.

Original Script:
{script}

Image Prompts:
{chr(10).join(f"{i+1}. {p}" for i, p in enumerate(prompts))}

Which prompt (#1-{len(prompts)}) best captures the essence and would be the strongest visual reference for the video? 
Consider: visual impact, clarity, alignment with script, and video potential.

Respond with ONLY the number (1-{len(prompts)})."""

            if USE_LANGCHAIN and self.llm:
                response = await self.llm.ainvoke([HumanMessage(content=selection_prompt)])
                choice = response.content.strip()
                # Extract number
                import re
                match = re.search(r'\d+', choice)
                if match:
                    index = int(match.group()) - 1
                    if 0 <= index < len(prompts):
                        state["best_prompt"] = prompts[index]
                        print(f"[{state['video_id']}] Selected prompt #{index+1} as best")
                    else:
                        state["best_prompt"] = prompts[0]
                else:
                    state["best_prompt"] = prompts[0]
            else:
                state["best_prompt"] = prompts[0]
            
        except Exception as e:
            print(f"[{state['video_id']}] Best prompt selection failed: {e}, using first prompt")
            state["best_prompt"] = state["prompts"][0] if state["prompts"] else ""
        
        return state
    
    async def generate_images(self, state: VideoGenerationState) -> VideoGenerationState:
        """Step 2: Generate reference images with DALL-E"""
        print(f"[{state['video_id']}] Step 2: Generating reference images...")
        
        if state.get("error"):
            return state
        
        try:
            prompts = state["prompts"]
            video_id = state["video_id"]
            
            image_paths = await self.image_service.generate_images(
                prompts=prompts,
                video_id=video_id
            )
            
            state["image_paths"] = image_paths
            state["current_step"] = "images_generated"
            print(f"[{state['video_id']}] Generated {len(image_paths)} reference images")
            
        except Exception as e:
            state["error"] = f"Image generation failed: {str(e)}"
            print(f"[{state['video_id']}] Error: {state['error']}")
        
        return state
    
    async def extract_narration(self, state: VideoGenerationState) -> VideoGenerationState:
        """Extract narration text from script"""
        script = state["script"]
        
        if "narration:" in script.lower() or "—" in script or ":" in script:
            extraction_prompt = f"""Extract ONLY the narration/voiceover text from this script.
            
Script:
{script}

Rules:
1. Extract only text that should be spoken aloud
2. Look for text after "narration:" markers or — dashes
3. Ignore technical instructions
4. Combine all narration into one flowing script
5. Return ONLY the narration text"""
            
            try:
                if USE_LANGCHAIN and self.llm:
                    response = await self.llm.ainvoke([HumanMessage(content=extraction_prompt)])
                    narration_text = response.content.strip().strip('"')
                    state["narration_text"] = narration_text
                else:
                    state["narration_text"] = script
            except Exception as e:
                print(f"[{state['video_id']}] Narration extraction failed: {e}")
                state["narration_text"] = script
        else:
            state["narration_text"] = script
        
        return state
    
    async def generate_audio(self, state: VideoGenerationState) -> VideoGenerationState:
        """Step 3: Generate audio narration with selected voice"""
        print(f"[{state['video_id']}] Step 3: Generating audio narration...")
        
        if state.get("error"):
            return state
        
        try:
            narration_text = state.get("narration_text", state["script"])
            voice = state["voice"]
            video_id = state["video_id"]
            
            audio_path = await self.audio_service.generate_narration(
                text=narration_text,
                voice=voice,
                video_id=video_id
            )
            
            state["audio_path"] = audio_path
            state["current_step"] = "audio_generated"
            print(f"[{state['video_id']}] Generated audio with voice '{voice}': {audio_path}")
            
        except Exception as e:
            state["error"] = f"Audio generation failed: {str(e)}"
            print(f"[{state['video_id']}] Error: {state['error']}")
        
        return state
    
    async def generate_video_with_sora(self, state: VideoGenerationState) -> VideoGenerationState:
        """Step 4: Generate video using Sora with first 2 images as reference"""
        print(f"[{state['video_id']}] Step 4: Generating video with Sora...")
        
        if state.get("error"):
            return state
        
        try:
            best_prompt = state.get("best_prompt", state["script"])
            style = state["style"]
            size = state.get("size", "1280x720")  # Get size from state
            duration = state.get("duration", 8)
            video_id = state["video_id"]
            image_paths = state.get("image_paths", [])
            
            style_info = VISUAL_STYLES.get(style, VISUAL_STYLES["realistic"])
            
            # Create video prompt using the best selected prompt
            video_prompt = f"{best_prompt}\n\nStyle: {style_info['description']}"
            
            # Use first 2 images as reference if available
            reference_images = []
            if image_paths:
                from pathlib import Path
                # Take first 2 images
                for img_url in image_paths[:2]:
                    if img_url.startswith('/images/'):
                        filename = Path(img_url).name
                        img_path = str(settings.IMAGES_DIR / video_id / filename)
                        reference_images.append(img_path)
                
                if reference_images:
                    print(f"[{video_id}] Using {len(reference_images)} reference images")
            
            # Determine model
            use_pro = getattr(settings, 'SORA_MODEL', 'sora-2-pro') == 'sora-2-pro'
            
            # Generate video with custom size from frontend
            result = await self.sora_service.generate_video(
                prompt=video_prompt,
                duration=duration,
                video_id=video_id,
                size=size,  # Pass custom size
                use_pro=use_pro,
                reference_images=reference_images  # Pass multiple images
            )
            
            state["video_path"] = result["video_path"]
            state["duration"] = result["duration"]
            state["current_step"] = "completed"
            print(f"[{video_id}] ✅ Video completed: {result['video_path']}")
            
        except Exception as e:
            state["error"] = f"Sora video generation failed: {str(e)}"
            print(f"[{state['video_id']}] Error: {state['error']}")
        
        return state
    
    async def run(self, initial_state: VideoGenerationState) -> VideoGenerationState:
        """Execute the complete workflow"""
        print(f"[{initial_state['video_id']}] Starting enhanced Sora workflow...")
        
        try:
            # Step 1: Generate 5-6 prompts
            state = await self.generate_prompts(initial_state)
            if state.get("error"):
                return state
            
            # Step 1.5: Auto-select best prompt
            state = await self.select_best_prompt(state)
            
            # Step 2: Generate reference images
            state = await self.generate_images(state)
            if state.get("error"):
                return state
            
            # Step 2.5: Extract narration
            state = await self.extract_narration(state)
            
            # Step 3: Generate audio narration with selected voice
            state = await self.generate_audio(state)
            if state.get("error"):
                return state
            
            # Step 4: Generate video with Sora (using first 2 images + custom size)
            state = await self.generate_video_with_sora(state)
            
            if state.get("error"):
                print(f"[{initial_state['video_id']}] Workflow failed: {state['error']}")
            else:
                print(f"[{initial_state['video_id']}] ✅ Complete workflow finished!")
            
            return state
            
        except Exception as e:
            error_msg = str(e)
            print(f"[{initial_state['video_id']}] ❌ Workflow error: {error_msg}")
            initial_state["error"] = error_msg
            initial_state["current_step"] = "failed"
            return initial_state
