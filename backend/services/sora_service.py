"""
OpenAI Sora-2 Pro Video Generation Service
Direct HTTP integration with Sora API endpoints
"""

from pathlib import Path
from typing import Optional
import asyncio
import aiofiles
import httpx

from config.settings import settings


class SoraService:
    """Service for generating videos using OpenAI Sora-2 or Sora-2 Pro"""
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = "https://api.openai.com/v1/videos"
        self.videos_dir = settings.VIDEOS_DIR
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate_video(
        self, 
        prompt: str, 
        duration: int,
        video_id: str,
        size: str = "1280x720",
        use_pro: bool = True,
        reference_images: list = None
    ) -> dict:
        """
        Generate video using OpenAI Sora-2 or Sora-2 Pro API
        
        Args:
            prompt: Text description of the video to generate
            duration: Desired video duration in seconds (4, 8, or 12)
            video_id: Unique identifier for the video
            size: Output resolution (e.g., "1280x720", "720x1280")
            use_pro: Use sora-2-pro (slower, higher quality) vs sora-2 (faster)
            reference_images: List of paths to reference images (max 2)
            
        Returns:
            Dictionary with video_path and duration
        """
        model = "sora-2-pro" if use_pro else "sora-2"
        print(f"[{video_id}] Generating video with {model}...")
        print(f"[{video_id}] Prompt: {prompt[:100]}...")
        print(f"[{video_id}] Size: {size}")
        
        # Default to 8 seconds if not specified
        duration = duration or 8
        if duration <= 4:
            seconds = "4"
        elif duration <= 8:
            seconds = "8"
        else:
            seconds = "12"  # Max for Sora
        
        # Create video generation job
        print(f"[{video_id}] Creating video job (size={size}, duration={seconds}s)...")
        
        # Prepare request body
        request_body = {
            "model": model,
            "prompt": prompt,
            "size": size,
            "seconds": seconds
        }
        
        # Add reference images if provided (first 2 images)
        if reference_images:
            # For now, use first image as input_reference
            # Note: Sora API may support multiple images in future
            first_img = reference_images[0]
            print(f"[{video_id}] Using reference image: {first_img}")
            # Note: input_reference would need multipart upload
            # For HTTP implementation, this may require different approach
        
        # POST to https://api.openai.com/v1/videos
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.base_url,
                headers=self.headers,
                json=request_body
            )
            response.raise_for_status()
            video_job = response.json()
        
        job_id = video_job["id"]
        print(f"[{video_id}] ✅ Job created: {job_id}")
        print(f"[{video_id}] Status: {video_job['status']}")
        print(f"[{video_id}] Polling for completion...")
        
        # Poll until the video is ready (with timeout)
        max_wait_time = 600  # 10 minutes max (Sora can take longer)
        poll_interval = 5  # Check every 5 seconds
        elapsed_time = 0
        
        while elapsed_time < max_wait_time:
            # GET https://api.openai.com/v1/videos/{video_id}
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/{job_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                job_status = response.json()
            
            status = job_status["status"]
            progress = job_status.get("progress", 0)
            
            print(f"[{video_id}] Status: {status} | Progress: {progress}% (elapsed: {elapsed_time}s)")
            
            if status == "completed":
                print(f"[{video_id}] ✅ Video generation complete!")
                
                # Download the generated video
                await self._download_video_from_api(job_id, video_id)
                
                return {
                    "video_path": f"/videos/{video_id}.mp4",
                    "duration": int(seconds)
                }
                
            elif status == "failed":
                error_info = job_status.get("error", {})
                error_msg = error_info.get("message", "Unknown error") if isinstance(error_info, dict) else str(error_info)
                print(f"[{video_id}] ❌ Video generation failed: {error_msg}")
                raise Exception(f"Sora video generation failed: {error_msg}")
            
            # Wait before polling again
            await asyncio.sleep(poll_interval)
            elapsed_time += poll_interval
        
        # Timeout
        raise Exception(f"Video generation timed out after {max_wait_time} seconds")
    
    async def remix_video(
        self,
        video_id: str,
        source_video_id: str,
        prompt: str
    ) -> dict:
        """
        Create a remix of a completed video using a refreshed prompt
        
        Args:
            video_id: New video identifier
            source_video_id: The OpenAI video job ID to remix
            prompt: Updated text prompt for remix
            
        Returns:
            Dictionary with video_path and duration
        """
        print(f"[{video_id}] Remixing video {source_video_id}...")
        print(f"[{video_id}] Remix prompt: {prompt[:100]}...")
        
        # POST to https://api.openai.com/v1/videos/{video_id}/remix
        request_body = {"prompt": prompt}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/{source_video_id}/remix",
                headers=self.headers,
                json=request_body
            )
            response.raise_for_status()
            remix_job = response.json()
        
        job_id = remix_job["id"]
        print(f"[{video_id}] ✅ Remix job created: {job_id}")
        print(f"[{video_id}] Polling for completion...")
        
        # Poll until ready
        max_wait_time = 600
        poll_interval = 5
        elapsed_time = 0
        
        while elapsed_time < max_wait_time:
            # GET https://api.openai.com/v1/videos/{video_id}
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/{job_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                job_status = response.json()
            
            status = job_status["status"]
            progress = job_status.get("progress", 0)
            
            print(f"[{video_id}] Status: {status} | Progress: {progress}% (elapsed: {elapsed_time}s)")
            
            if status == "completed":
                print(f"[{video_id}] ✅ Remix complete!")
                
                # Download the remixed video
                await self._download_video_from_api(job_id, video_id)
                
                seconds = job_status.get("seconds", "8")
                return {
                    "video_path": f"/videos/{video_id}.mp4",
                    "duration": int(seconds)
                }
                
            elif status == "failed":
                error_info = job_status.get("error", {})
                error_msg = error_info.get("message", "Unknown error") if isinstance(error_info, dict) else str(error_info)
                print(f"[{video_id}] ❌ Remix failed: {error_msg}")
                raise Exception(f"Video remix failed: {error_msg}")
            
            await asyncio.sleep(poll_interval)
            elapsed_time += poll_interval
        
        raise Exception(f"Remix timed out after {max_wait_time} seconds")
    
    async def _download_video_from_api(self, job_id: str, video_id: str) -> Path:
        """Download video content using Sora API"""
        video_path = self.videos_dir / f"{video_id}.mp4"
        video_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"[{video_id}] Downloading video from Sora API...")
        
        # GET https://api.openai.com/v1/videos/{video_id}/content
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.get(
                f"{self.base_url}/{job_id}/content",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            response.raise_for_status()
            content = response.content
        
        # Write video file
        async with aiofiles.open(video_path, "wb") as f:
            await f.write(content)
        
        print(f"[{video_id}] ✅ Video saved to: {video_path}")
        return video_path
