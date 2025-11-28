# VisionPulse - AI Video Creation System

Transform written scripts into fully generated short videos using AI imagery and narration powered by OpenAI.

## Features

- 🎬 **Automated Video Generation**: From script to video in one click
- 🎨 **Multiple Visual Styles**: Choose from preset artistic styles
- 🎙️ **AI Narration**: Multiple voice options using OpenAI TTS
- 🖼️ **AI Image Generation**: DALL-E 3 powered visuals
- 🎥 **Cinematic Motion Effects**: Ken Burns zoom, pan effects for dynamic feel
- 📊 **Clean Dashboard**: Simple Next.js interface with video gallery
- ⚡ **LangGraph Workflow**: Sequential pipeline for reliable generation

> **Note on OpenAI Sora**: Currently using DALL-E 3 images with cinematic motion effects. When OpenAI Sora becomes publicly available via API, the system is designed to easily integrate native video generation for even more dynamic results.

## Tech Stack

- **Backend**: Python, LangGraph, FastAPI, OpenAI API
- **Frontend**: Next.js 14, React, TailwindCSS
- **Video Processing**: MoviePy
- **Database**: SQLite with SQLAlchemy

## Quick Start

### 1. Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your OpenAI API key
```

### 3. Run Backend

```bash
# Start FastAPI server
python -m uvicorn backend.main:app --reload
```

API will be available at: http://localhost:8000

### 4. Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Dashboard will be available at: http://localhost:3000

## Project Structure

```
VisionPulse/
├── backend/
│   ├── api/                 # FastAPI routes
│   ├── workflows/           # LangGraph workflows
│   ├── services/            # Business logic
│   ├── models/              # Database models
│   └── config/              # Configuration files
├── frontend/                # Next.js application
├── output/                  # Generated files
│   ├── videos/
│   ├── images/
│   └── audio/
├── requirements.txt
├── .env
└── README.md
```

## Usage

1. Open the dashboard at http://localhost:3000
2. Click "Create New Video"
3. Paste your script
4. Choose a visual style
5. Select a narration voice
6. Add keywords (optional)
7. Click "Generate Video"
8. Download your finished video!

## API Endpoints

- `POST /api/videos/create` - Create a new video
- `GET /api/videos` - List all videos
- `GET /api/videos/{video_id}` - Get video details
- `GET /api/styles` - List available styles
- `GET /api/voices` - List available voices

## License

MIT
