import asyncio
from pathlib import Path
from typing import List
from openai import AsyncOpenAI
import httpx

from config.settings import settings

class ImageService:
    """Service for generating images using DALL-E 3"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.images_dir = settings.IMAGES_DIR
    
    async def generate_images(self, prompts: List[str], video_id: str) -> List[str]:
        """
        Generate images for all prompts
        
        Args:
            prompts: List of image generation prompts
            video_id: Unique identifier for the video
            
        Returns:
            List of file paths to generated images
        """
        image_paths = []
        
        for idx, prompt in enumerate(prompts):
            max_retries = 2
            retry_count = 0
            success = False
            
            while retry_count <= max_retries and not success:
                try:
                    print(f"  Generating image {idx + 1}/{len(prompts)}..." + (f" (retry {retry_count})" if retry_count > 0 else ""))
                    
                    # Modify prompt on retry to make it safer
                    modified_prompt = prompt
                    if retry_count > 0:
                        modified_prompt = self._sanitize_prompt(prompt)
                        print(f"  Using sanitized prompt for retry...")
                    
                    # Generate image with DALL-E 3
                    response = await self.client.images.generate(
                        model=settings.OPENAI_IMAGE_MODEL,
                        prompt=modified_prompt,
                        size=settings.DEFAULT_IMAGE_SIZE,
                        quality="standard",
                        n=1
                    )
                    
                    # Download the image
                    image_url = response.data[0].url
                    image_path = await self._download_image(image_url, video_id, idx)
                    image_paths.append(str(image_path))
                    
                    print(f"  ✓ Image {idx + 1} saved: {image_path}")
                    success = True
                    
                except Exception as e:
                    error_str = str(e)
                    retry_count += 1
                    
                    # Check if it's a content policy violation
                    if "content_policy_violation" in error_str or "safety system" in error_str:
                        if retry_count <= max_retries:
                            print(f"  ⚠ Content policy violation, retrying with sanitized prompt...")
                            continue
                        else:
                            print(f"  ⚠ Failed after {max_retries} retries, using placeholder image...")
                            # Create a placeholder image
                            image_path = await self._create_placeholder_image(video_id, idx, "Content Filtered")
                            image_paths.append(str(image_path))
                            success = True
                    else:
                        print(f"  ✗ Failed to generate image {idx + 1}: {error_str}")
                        raise
        
        # Convert file paths to URL paths
        url_paths = [f"/images/{video_id}/image_{idx:03d}.png" for idx in range(len(image_paths))]
        return url_paths
    
    def _sanitize_prompt(self, prompt: str) -> str:
        """Sanitize prompt to remove potentially unsafe content"""
        # Remove potentially problematic words and make it more generic
        sanitized = prompt
        
        # Remove specific names, violence, political content
        unsafe_words = ['war', 'weapon', 'gun', 'violence', 'blood', 'death', 'kill', 'attack', 'fight']
        for word in unsafe_words:
            sanitized = sanitized.replace(word, '')
        
        # Add safety prefix
        sanitized = f"A safe, family-friendly, artistic visualization: {sanitized}"
        
        return sanitized
    
    async def _create_placeholder_image(self, video_id: str, index: int, message: str) -> Path:
        """Create a simple placeholder image when generation fails"""
        from PIL import Image, ImageDraw, ImageFont
        
        video_dir = self.images_dir / video_id
        video_dir.mkdir(parents=True, exist_ok=True)
        
        image_path = video_dir / f"image_{index:03d}.png"
        
        # Create a simple colored image with text
        img = Image.new('RGB', (1024, 1024), color=(50, 50, 80))
        draw = ImageDraw.Draw(img)
        
        # Draw text
        text = f"Image {index + 1}\n{message}"
        bbox = draw.textbbox((0, 0), text)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((1024 - text_width) // 2, (1024 - text_height) // 2)
        draw.text(position, text, fill=(200, 200, 200))
        
        img.save(image_path)
        return image_path
    
    async def _download_image(self, url: str, video_id: str, index: int) -> Path:
        """Download image from URL and save to disk"""
        video_dir = self.images_dir / video_id
        video_dir.mkdir(parents=True, exist_ok=True)
        
        image_path = video_dir / f"image_{index:03d}.png"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            
            with open(image_path, "wb") as f:
                f.write(response.content)
        
        return image_path
