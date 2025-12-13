import sys
from pathlib import Path

# Add parent directory to path to make imports work
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.routes import router
from models.database import init_db
from config.settings import settings

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="VisionPulse API",
    description="AI-powered video creation system",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

# Serve static files (videos, images, audio)
if settings.VIDEOS_DIR.exists():
    app.mount("/videos", StaticFiles(directory=str(settings.VIDEOS_DIR)), name="videos")
if settings.IMAGES_DIR.exists():
    app.mount("/images", StaticFiles(directory=str(settings.IMAGES_DIR)), name="images")
if settings.AUDIO_DIR.exists():
    app.mount("/audio", StaticFiles(directory=str(settings.AUDIO_DIR)), name="audio")

@app.get("/")
async def root():
    return {
        "message": "VisionPulse API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    print("Starting VisionPulse API Server...")
    print(f"Server will run on http://{settings.API_HOST}:{settings.API_PORT}")
    print(f"API Documentation: http://{settings.API_HOST}:{settings.API_PORT}/docs")
    uvicorn.run(
        "main:app",  # Fixed: use module name relative to current directory
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD
    )
