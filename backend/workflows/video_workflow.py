from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI, OpenAI
from langchain_core.messages import HumanMessage
import json
import asyncio

from backend.config.settings import settings
from backend.config.presets import VISUAL_STYLES
from backend.services.image_service import ImageService
from backend.services.audio_service import AudioService
from backend.services.video_service import VideoService

class VideoGenerationState(TypedDict):
    """State for the video generation workflow"""
    video_id: str
    script: str
    style: str
    voice: str
    keywords: List[str]
    negative_keywords: List[str]
    prompts: List[str]
    image_urls: List[str]
    image_paths: List[str]
    audio_path: str
    video_path: str
    error: Optional[str]
    current_step: str

class VideoGenerationWorkflow:
    """
    LangGraph Sequential Workflow for Video Generation
    
    Steps:
    1. Generate prompts from script
    2. Generate images from prompts
    3. Generate narration audio
    4. Assemble video
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.7
        )
        self.image_service = ImageService()
        self.audio_service = AudioService()
        self.video_service = VideoService()
        
        # Build the graph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph sequential workflow"""
        workflow = StateGraph(VideoGenerationState)
        
        # Add nodes
        workflow.add_node("generate_prompts", self.generate_prompts)
        workflow.add_node("generate_images", self.generate_images)
        workflow.add_node("generate_audio", self.generate_audio)
        workflow.add_node("assemble_video", self.assemble_video)
        
        # Define the sequential flow
        workflow.set_entry_point("generate_prompts")
        workflow.add_edge("generate_prompts", "generate_images")
        workflow.add_edge("generate_images", "generate_audio")
        workflow.add_edge("generate_audio", "assemble_video")
        workflow.add_edge("assemble_video", END)
        
        return workflow.compile()
    
    async def generate_prompts(self, state: VideoGenerationState) -> VideoGenerationState:
        """Step 1: Generate 6-7 image prompts from the script"""
        print(f"[{state['video_id']}] Step 1: Generating prompts...")
        
        try:
            script = state["script"]
            style = state["style"]
            keywords = state.get("keywords", [])
            negative_keywords = state.get("negative_keywords", [])
            
            style_info = VISUAL_STYLES.get(style, VISUAL_STYLES["realistic"])
            style_suffix = style_info["prompt_suffix"]
            
            keywords_text = ", ".join(keywords) if keywords else ""
            negative_text = ", ".join(negative_keywords) if negative_keywords else ""
            
            prompt = f"""You are an expert at breaking down video scripts into visual scenes.

Given the following script, generate exactly 6-7 detailed image prompts that will be used to create visuals for the video.

Script:
{script}

Visual Style: {style_info['name']}
Style Description: {style_info['description']}
Additional Keywords: {keywords_text}
Avoid: {negative_text}

IMPORTANT SAFETY GUIDELINES:
- Keep all prompts family-friendly and appropriate
- Avoid any violent, disturbing, or controversial content
- Focus on positive, educational, or entertaining visuals
- Do not include real people, copyrighted characters, or brands
- Keep prompts abstract and artistic

Requirements:
1. Create 6-7 prompts (one per scene)
2. Each prompt should be highly detailed and vivid
3. Include the visual style in each prompt
4. Make prompts flow sequentially to tell the story
5. Each prompt should be suitable for DALL-E 3 image generation
6. Ensure all prompts follow OpenAI's content policy

Return ONLY a JSON array of strings, like this:
["prompt 1 here", "prompt 2 here", "prompt 3 here", ...]

Do not include any other text or explanation."""

            response = await self.llm.ainvoke(
                [HumanMessage(content=prompt)]
            )
            
            # Parse the response
            content = response.content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            prompts = json.loads(content.strip())
            
            # Add style suffix to each prompt
            prompts = [f"{p}, {style_suffix}" for p in prompts]
            
            state["prompts"] = prompts
            state["current_step"] = "prompts_generated"
            print(f"[{state['video_id']}] Generated {len(prompts)} prompts")
            
        except Exception as e:
            state["error"] = f"Prompt generation failed: {str(e)}"
            print(f"[{state['video_id']}] Error: {state['error']}")
        
        return state
    
    async def generate_images(self, state: VideoGenerationState) -> VideoGenerationState:
        """Step 2: Generate images using DALL-E 3"""
        print(f"[{state['video_id']}] Step 2: Generating images...")
        
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
            print(f"[{state['video_id']}] Generated {len(image_paths)} images")
            
        except Exception as e:
            state["error"] = f"Image generation failed: {str(e)}"
            print(f"[{state['video_id']}] Error: {state['error']}")
        
        return state
    
    async def generate_audio(self, state: VideoGenerationState) -> VideoGenerationState:
        """Step 3: Generate narration audio using OpenAI TTS"""
        print(f"[{state['video_id']}] Step 3: Generating audio narration...")
        
        if state.get("error"):
            return state
        
        try:
            script = state["script"]
            voice = state["voice"]
            video_id = state["video_id"]
            
            audio_path = await self.audio_service.generate_narration(
                text=script,
                voice=voice,
                video_id=video_id
            )
            
            state["audio_path"] = audio_path
            state["current_step"] = "audio_generated"
            print(f"[{state['video_id']}] Generated audio: {audio_path}")
            
        except Exception as e:
            state["error"] = f"Audio generation failed: {str(e)}"
            print(f"[{state['video_id']}] Error: {state['error']}")
        
        return state
    
    async def assemble_video(self, state: VideoGenerationState) -> VideoGenerationState:
        """Step 4: Assemble images and audio into final video"""
        print(f"[{state['video_id']}] Step 4: Assembling video...")
        
        if state.get("error"):
            return state
        
        try:
            image_paths = state["image_paths"]
            audio_path = state["audio_path"]
            video_id = state["video_id"]
            
            result = await self.video_service.create_video(
                image_paths=image_paths,
                audio_path=audio_path,
                video_id=video_id
            )
            
            state["video_path"] = result["video_path"]
            state["duration"] = result["duration"]
            state["current_step"] = "completed"
            print(f"[{state['video_id']}] Video completed: {result['video_path']} (duration: {result['duration']}s)")
            
        except Exception as e:
            state["error"] = f"Video assembly failed: {str(e)}"
            print(f"[{state['video_id']}] Error: {state['error']}")
        
        return state
    
    async def run(self, initial_state: VideoGenerationState) -> VideoGenerationState:
        """Execute the workflow"""
        print(f"[{initial_state['video_id']}] Starting video generation workflow...")
        
        try:
            # Use ainvoke for async execution
            result = await self.workflow.ainvoke(initial_state)
            
            if result.get("error"):
                print(f"[{initial_state['video_id']}] Workflow failed: {result['error']}")
            else:
                print(f"[{initial_state['video_id']}] Workflow completed successfully!")
            
            return result
        except Exception as e:
            print(f"[{initial_state['video_id']}] Workflow error: {str(e)}")
            initial_state["error"] = str(e)
            return initial_state
