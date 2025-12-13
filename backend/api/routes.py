from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import uuid

from api.schemas import (
    VideoCreateRequest, 
    VideoResponse, 
    StyleResponse, 
    VoiceResponse
)
from models.database import get_db, Video
from config.presets import VISUAL_STYLES, NARRATION_VOICES
from workflows.video_workflow import VideoGenerationWorkflow, VideoGenerationState
import asyncio

router = APIRouter(prefix="/api", tags=["videos"])

# Initialize workflow
workflow = VideoGenerationWorkflow()

async def process_video_generation(video_id: str, size: str, duration: int, db_session: Session):
    """Background task to process video generation"""
    db = next(get_db())
    
    try:
        # Get video from database
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            return
        
        # Update status to processing
        video.status = "processing"
        db.commit()
        
        # Create initial state
        initial_state: VideoGenerationState = {
            "video_id": video_id,
            "script": video.script,
            "style": video.style,
            "voice": video.voice,
            "size": size,
            "keywords": video.keywords or [],
            "negative_keywords": video.negative_keywords or [],
            "prompts": [],
            "best_prompt": "",
            "image_paths": [],
            "audio_path": "",
            "video_path": "",
            "duration": duration,
            "narration_text": None,
            "error": None,
            "current_step": "initializing"
        }
        
        # Run workflow - using await since it's async
        result = await workflow.run(initial_state)
        
        # Update database with results
        video = db.query(Video).filter(Video.id == video_id).first()
        if result.get("error"):
            video.status = "failed"
            video.error_message = result["error"]
        else:
            video.status = "completed"
            video.prompts = result.get("prompts")
            video.image_paths = result.get("image_paths")
            video.audio_path = result.get("audio_path")
            video.video_path = result["video_path"]
            video.duration = result.get("duration")
        
        db.commit()
        
    except Exception as e:
        print(f"Error processing video {video_id}: {str(e)}")
        video = db.query(Video).filter(Video.id == video_id).first()
        if video:
            video.status = "failed"
            video.error_message = str(e)
            db.commit()
    finally:
        db.close()

@router.post("/videos/create", response_model=VideoResponse)
async def create_video(
    request: VideoCreateRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new video generation job"""
    
    # Validate style and voice
    if request.style not in VISUAL_STYLES:
        raise HTTPException(status_code=400, detail=f"Invalid style: {request.style}")
    
    if request.voice not in NARRATION_VOICES:
        raise HTTPException(status_code=400, detail=f"Invalid voice: {request.voice}")
    
    # Create video record
    video = Video(
        id=str(uuid.uuid4()),
        title=request.title,
        script=request.script,
        style=request.style,
        voice=request.voice,
        keywords=request.keywords,
        negative_keywords=request.negative_keywords,
        status="pending"
    )
    
    db.add(video)
    db.commit()
    db.refresh(video)
    
    # Start background processing - create task directly
    import asyncio
    asyncio.create_task(process_video_generation(
        video.id, 
        request.size or "1280x720",
        request.duration or 8,
        db
    ))
    
    return VideoResponse(**video.to_dict())

@router.get("/videos", response_model=List[VideoResponse])
async def list_videos(db: Session = Depends(get_db)):
    """List all videos"""
    videos = db.query(Video).order_by(Video.created_at.desc()).all()
    return [VideoResponse(**v.to_dict()) for v in videos]

@router.get("/videos/{video_id}", response_model=VideoResponse)
async def get_video(video_id: str, db: Session = Depends(get_db)):
    """Get a specific video by ID"""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return VideoResponse(**video.to_dict())

@router.get("/styles", response_model=List[StyleResponse])
async def list_styles():
    """List all available visual styles"""
    return [
        StyleResponse(
            id=key,
            name=value["name"],
            description=value["description"]
        )
        for key, value in VISUAL_STYLES.items()
    ]

@router.get("/voices", response_model=List[VoiceResponse])
async def list_voices():
    """List all available narration voices"""
    return [
        VoiceResponse(
            id=key,
            name=value["name"],
            description=value["description"]
        )
        for key, value in NARRATION_VOICES.items()
    ]

@router.delete("/videos/{video_id}")
async def delete_video(video_id: str, db: Session = Depends(get_db)):
    """Delete a video"""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    db.delete(video)
    db.commit()
    
    return {"message": "Video deleted successfully"}
