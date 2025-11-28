# VisionPulse - System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                    (Next.js Dashboard)                          │
│                   http://localhost:3000                         │
├─────────────────────────────────────────────────────────────────┤
│  • Video Gallery with Real-time Updates                        │
│  • Create Video Form (Script, Style, Voice, Keywords)          │
│  • Video Playback & Download                                   │
│  • Status Indicators (Pending, Processing, Completed, Failed)  │
└─────────────────────────────────────────────────────────────────┘
                              ↕ HTTP/REST
┌─────────────────────────────────────────────────────────────────┐
│                         API LAYER                               │
│                    (FastAPI Backend)                            │
│                   http://localhost:8000                         │
├─────────────────────────────────────────────────────────────────┤
│  Endpoints:                                                     │
│  • POST /api/videos/create → Create video job                  │
│  • GET  /api/videos        → List all videos                   │
│  • GET  /api/videos/{id}   → Get video details                 │
│  • DELETE /api/videos/{id} → Delete video                      │
│  • GET  /api/styles        → List visual styles                │
│  • GET  /api/voices        → List narration voices             │
├─────────────────────────────────────────────────────────────────┤
│  • Background Task Processing                                   │
│  • CORS Middleware                                             │
│  • Static File Serving (videos, images, audio)                │
└─────────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│                    LANGGRAPH WORKFLOW                           │
│                (Sequential State Machine)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  State: VideoGenerationState                                   │
│  ├── video_id                                                  │
│  ├── script                                                    │
│  ├── style                                                     │
│  ├── voice                                                     │
│  ├── keywords                                                  │
│  ├── prompts          (generated)                              │
│  ├── image_paths      (generated)                              │
│  ├── audio_path       (generated)                              │
│  ├── video_path       (generated)                              │
│  └── error            (if any)                                 │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Node 1: generate_prompts()                             │  │
│  │  ────────────────────────────────────────────────────── │  │
│  │  Input:  script, style, keywords                        │  │
│  │  Uses:   GPT-4o                                         │  │
│  │  Output: 6-7 detailed image prompts                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                       ↓                                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Node 2: generate_images()                              │  │
│  │  ────────────────────────────────────────────────────── │  │
│  │  Input:  prompts                                        │  │
│  │  Uses:   DALL-E 3                                       │  │
│  │  Output: 6-7 PNG images (1024x1024)                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                       ↓                                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Node 3: generate_audio()                               │  │
│  │  ────────────────────────────────────────────────────── │  │
│  │  Input:  script, voice                                  │  │
│  │  Uses:   OpenAI TTS                                     │  │
│  │  Output: MP3 narration file                             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                       ↓                                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Node 4: assemble_video()                               │  │
│  │  ────────────────────────────────────────────────────── │  │
│  │  Input:  images, audio                                  │  │
│  │  Uses:   MoviePy                                        │  │
│  │  Output: Final MP4 video (1920x1080, H.264)            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                       ↓                                         │
│                      END                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│                      SERVICE LAYER                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  ImageService                                           │   │
│  │  • generate_images(prompts, video_id)                   │   │
│  │  • Uses: OpenAI DALL-E 3 API                            │   │
│  │  • Downloads and saves images locally                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  AudioService                                           │   │
│  │  • generate_narration(text, voice, video_id)            │   │
│  │  • Uses: OpenAI TTS API                                 │   │
│  │  • Generates MP3 audio                                  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  VideoService                                           │   │
│  │  • create_video(images, audio, video_id)                │   │
│  │  • Uses: MoviePy                                        │   │
│  │  • Assembles and renders final video                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL APIS                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   GPT-4o     │  │  DALL-E 3    │  │  OpenAI TTS  │         │
│  │              │  │              │  │              │         │
│  │ Text → JSON  │  │ Text → Image │  │ Text → Audio │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
│  All powered by OpenAI API (api.openai.com)                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│                   DATA PERSISTENCE                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  SQLite Database (visionpulse.db)                        │  │
│  │  ──────────────────────────────────────────────────────  │  │
│  │  Table: videos                                           │  │
│  │  • id, title, script, style, voice                       │  │
│  │  • keywords, negative_keywords                           │  │
│  │  • prompts, image_paths, audio_path, video_path         │  │
│  │  • status, error_message                                 │  │
│  │  • created_at, updated_at                                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  File System (output/)                                   │  │
│  │  ──────────────────────────────────────────────────────  │  │
│  │  output/                                                 │  │
│  │  ├── videos/{video_id}.mp4                               │  │
│  │  ├── images/{video_id}/image_000.png                     │  │
│  │  │            └── image_001.png                          │  │
│  │  │            └── ...                                    │  │
│  │  └── audio/{video_id}/narration.mp3                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘


## Data Flow Example

1. User submits form on dashboard
   ↓
2. POST /api/videos/create
   ↓
3. Create video record in database (status: pending)
   ↓
4. Start background task with LangGraph workflow
   ↓
5. Update status to "processing"
   ↓
6. Node 1: GPT-4o generates prompts
   ↓
7. Node 2: DALL-E 3 creates images
   ↓
8. Node 3: OpenAI TTS generates audio
   ↓
9. Node 4: MoviePy assembles video
   ↓
10. Update database with file paths (status: completed)
    ↓
11. Frontend polls and shows completed video
    ↓
12. User downloads video


## Technology Stack Overview

┌────────────────────────────────────────────────────────┐
│                    FRONTEND                            │
├────────────────────────────────────────────────────────┤
│  Framework:    Next.js 14 (React 18)                  │
│  Language:     TypeScript                             │
│  Styling:      TailwindCSS                            │
│  Data Fetch:   SWR (React Hooks for Data Fetching)   │
│  HTTP Client:  Axios                                  │
│  Icons:        Lucide React                           │
│  Dates:        date-fns                               │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│                    BACKEND                             │
├────────────────────────────────────────────────────────┤
│  Framework:    FastAPI (Async)                        │
│  Language:     Python 3.8+                            │
│  Workflow:     LangGraph (State Machine)              │
│  LLM:          LangChain + OpenAI                     │
│  Database:     SQLAlchemy + SQLite                    │
│  Video:        MoviePy                                │
│  Image:        Pillow (PIL)                           │
│  Validation:   Pydantic                               │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│                   AI SERVICES                          │
├────────────────────────────────────────────────────────┤
│  Provider:     OpenAI                                 │
│  Models:                                              │
│    • GPT-4o          (Prompt Generation)              │
│    • DALL-E 3        (Image Generation)               │
│    • TTS-1           (Text-to-Speech)                 │
└────────────────────────────────────────────────────────┘


## Request Flow Diagram

User Action → Frontend → Backend → LangGraph → Services → OpenAI

┌─────────┐
│  User   │ Creates Video Request
└────┬────┘
     │
     ↓
┌─────────────────┐
│  Next.js UI     │ Form Submission
└────┬────────────┘
     │ HTTP POST
     ↓
┌─────────────────┐
│  FastAPI        │ Validates & Creates DB Record
└────┬────────────┘
     │ Triggers Background Task
     ↓
┌─────────────────┐
│  LangGraph      │ Executes Workflow
└────┬────────────┘
     │ Sequential Nodes
     ↓
     ├→ Node 1 → ImageService → OpenAI (GPT-4o)
     │
     ├→ Node 2 → ImageService → OpenAI (DALL-E 3)
     │
     ├→ Node 3 → AudioService → OpenAI (TTS)
     │
     └→ Node 4 → VideoService → MoviePy (Local)
          │
          ↓
     ┌────────────────┐
     │  File System   │ Saves Video
     └────┬───────────┘
          │
          ↓
     ┌────────────────┐
     │  Database      │ Updates Status
     └────┬───────────┘
          │
          ↓
     ┌────────────────┐
     │  Frontend      │ Polls & Displays (SWR)
     └────┬───────────┘
          │
          ↓
     ┌────────────────┐
     │  User          │ Downloads Video
     └────────────────┘


## Deployment Architecture (Future)

┌──────────────────────────────────────────────────────────┐
│                      Production                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Frontend:  Vercel / Netlify                            │
│  Backend:   AWS EC2 / Google Cloud Run                  │
│  Database:  PostgreSQL (RDS)                            │
│  Storage:   AWS S3 / Google Cloud Storage               │
│  Queue:     Redis + Celery (for background tasks)       │
│  Monitor:   Prometheus + Grafana                        │
│  Logs:      CloudWatch / Stackdriver                    │
│                                                          │
└──────────────────────────────────────────────────────────┘
