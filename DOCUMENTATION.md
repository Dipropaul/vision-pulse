# VisionPulse - Complete System Documentation

## 🎯 Overview

VisionPulse is an AI-powered video creation system that transforms written scripts into fully generated short videos using OpenAI's APIs. The system uses LangGraph for orchestrating a sequential workflow that handles prompt generation, image creation, narration, and video assembly.

## ✅ Yes, It's Possible with Only OpenAI API!

**Absolutely YES!** This entire system uses **only OpenAI APIs**:

1. **GPT-4o** - Generates image prompts from your script
2. **DALL-E 3** - Creates visual content for each scene
3. **OpenAI TTS** - Generates professional narration audio
4. **MoviePy** - Local library to assemble everything (no API needed)

**No other AI services required!** Just one OpenAI API key does everything.

## 🏗️ Architecture Overview

### Sequential Workflow (LangGraph)

```
┌─────────────────────────────────────────────────────────────┐
│                    LangGraph Workflow                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Generate Prompts (GPT-4o)                              │
│     Input: Script, Style, Keywords                         │
│     Output: 6-7 detailed image prompts                     │
│              ↓                                             │
│  2. Generate Images (DALL-E 3)                             │
│     Input: Image prompts                                   │
│     Output: 6-7 high-quality images                        │
│              ↓                                             │
│  3. Generate Audio (OpenAI TTS)                            │
│     Input: Script text, Voice selection                    │
│     Output: MP3 narration file                             │
│              ↓                                             │
│  4. Assemble Video (MoviePy)                               │
│     Input: Images + Audio                                  │
│     Output: Final MP4 video                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### System Components

#### Backend (Python)
- **FastAPI**: REST API server
- **LangGraph**: Workflow orchestration
- **OpenAI SDK**: All AI operations
- **MoviePy**: Video assembly
- **SQLAlchemy**: Database ORM
- **SQLite**: Data persistence

#### Frontend (Next.js)
- **React 18**: UI framework
- **Next.js 14**: Server-side rendering
- **TailwindCSS**: Styling
- **SWR**: Data fetching
- **Axios**: HTTP client

## 📋 Features Implemented

### ✅ User Features
- [x] Simple dashboard showing all created videos
- [x] "Create New Video" button
- [x] Paste script manually
- [x] Choose from 8 preset video styles
- [x] Choose from 6 preset narration voices
- [x] Add keywords and negative keywords
- [x] Automatic generation of 6-7 prompts
- [x] Automatic image generation (DALL-E 3)
- [x] Automatic narration generation (OpenAI TTS)
- [x] Automatic video assembly
- [x] Download finished videos
- [x] Real-time status updates
- [x] Video gallery with previews
- [x] Delete videos

### ✅ Technical Features
- [x] LangGraph sequential workflow
- [x] FastAPI REST API
- [x] OpenAI API integration
- [x] Database persistence
- [x] Background processing
- [x] Error handling
- [x] File management
- [x] CORS configuration
- [x] Static file serving

## 🎨 Visual Styles

1. **Cinematic** - Professional film-like quality with dramatic lighting
2. **Anime** - Japanese animation style with vibrant colors
3. **Realistic** - Photorealistic imagery
4. **Watercolor** - Soft watercolor painting aesthetic
5. **Cyberpunk** - Futuristic neon-lit dystopian aesthetic
6. **Minimalist** - Clean, simple, and elegant design
7. **Fantasy** - Magical and enchanted worlds
8. **Comic Book** - Bold comic book illustration style

## 🎙️ Narration Voices

1. **Alloy** - Neutral and balanced voice
2. **Echo** - Warm and engaging voice
3. **Fable** - Expressive storytelling voice
4. **Onyx** - Deep and authoritative voice
5. **Nova** - Energetic and dynamic voice
6. **Shimmer** - Bright and cheerful voice

## 🔄 Workflow Details

### Step 1: Prompt Generation
- **AI Model**: GPT-4o
- **Input**: User script, selected style, keywords
- **Process**: 
  - Analyzes the script narrative
  - Breaks it into 6-7 visual scenes
  - Generates detailed DALL-E prompts
  - Applies style modifiers
  - Incorporates keywords
- **Output**: Array of 6-7 image generation prompts

### Step 2: Image Generation
- **AI Model**: DALL-E 3
- **Input**: Generated prompts
- **Process**: 
  - Generates high-quality 1024x1024 images
  - Downloads and saves locally
  - Sequential processing to avoid rate limits
- **Output**: 6-7 PNG image files

### Step 3: Audio Generation
- **AI Model**: OpenAI TTS
- **Input**: Original script, voice selection
- **Process**: 
  - Converts text to natural speech
  - Uses selected voice profile
  - Generates MP3 audio
- **Output**: MP3 narration file

### Step 4: Video Assembly
- **Library**: MoviePy
- **Input**: Images + Audio
- **Process**: 
  - Calculates timing (audio duration ÷ image count)
  - Resizes images to 1920x1080
  - Creates video clips with equal durations
  - Adds audio track
  - Renders final video
- **Output**: MP4 video file (H.264 codec)

## 📊 Database Schema

### Videos Table
```sql
CREATE TABLE videos (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    script TEXT NOT NULL,
    style TEXT NOT NULL,
    voice TEXT NOT NULL,
    keywords JSON,
    negative_keywords JSON,
    prompts JSON,
    image_paths JSON,
    audio_path TEXT,
    video_path TEXT,
    status TEXT DEFAULT 'pending',
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Status Values
- `pending`: Job created, not started
- `processing`: Workflow in progress
- `completed`: Video successfully generated
- `failed`: Error occurred during generation

## 🌐 API Endpoints

### POST /api/videos/create
Create a new video generation job.

**Request Body:**
```json
{
  "title": "My Awesome Video",
  "script": "Your narration script here...",
  "style": "cinematic",
  "voice": "alloy",
  "keywords": ["sunset", "mountains"],
  "negative_keywords": ["people", "text"]
}
```

**Response:**
```json
{
  "id": "uuid-here",
  "title": "My Awesome Video",
  "status": "pending",
  ...
}
```

### GET /api/videos
List all videos with their current status.

### GET /api/videos/{video_id}
Get details of a specific video.

### DELETE /api/videos/{video_id}
Delete a video and its files.

### GET /api/styles
List all available visual styles.

### GET /api/voices
List all available narration voices.

## 🔧 Configuration

### Environment Variables

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4o
OPENAI_IMAGE_MODEL=dall-e-3
OPENAI_TTS_MODEL=tts-1

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=True

# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Storage Configuration
VIDEOS_DIR=./output/videos
IMAGES_DIR=./output/images
AUDIO_DIR=./output/audio

# Database
DATABASE_URL=sqlite:///./visionpulse.db
```

## 💻 Code Structure

### Backend Services

#### ImageService (`backend/services/image_service.py`)
- Handles DALL-E 3 image generation
- Downloads and saves images locally
- Manages image file organization

#### AudioService (`backend/services/audio_service.py`)
- Handles OpenAI TTS audio generation
- Supports all 6 voice options
- Saves MP3 files locally

#### VideoService (`backend/services/video_service.py`)
- Assembles images and audio into video
- Handles video timing and synchronization
- Manages video rendering and export

### LangGraph Workflow

#### VideoGenerationWorkflow (`backend/workflows/video_workflow.py`)
- Defines the sequential state machine
- Manages workflow state transitions
- Handles error propagation
- Coordinates all services

### Frontend Components

#### VideoGallery (`frontend/components/VideoGallery.tsx`)
- Displays grid of video cards
- Shows status indicators
- Handles video playback
- Provides download and delete actions

#### CreateVideoModal (`frontend/components/CreateVideoModal.tsx`)
- Form for video creation
- Style and voice selection
- Keyword management
- Form validation and submission

## 🚀 Performance Considerations

### Generation Time
- **Prompt Generation**: 5-15 seconds
- **Image Generation**: 30-60 seconds (6-7 images)
- **Audio Generation**: 10-20 seconds
- **Video Assembly**: 15-30 seconds
- **Total**: 2-5 minutes per video

### Optimization Strategies
1. **Parallel Image Generation**: Could be added to reduce image generation time
2. **Caching**: Reuse prompts or images for similar requests
3. **Background Processing**: FastAPI BackgroundTasks for non-blocking operations
4. **CDN**: Serve videos from CDN for faster delivery

### Rate Limits
- **DALL-E 3**: ~50 requests per minute
- **GPT-4o**: 500 requests per minute
- **TTS**: 50 requests per minute

The system respects these limits through sequential processing.

## 💰 Cost Analysis

### Per Video Cost (Approximate)

#### GPT-4o (Prompt Generation)
- Input: ~500 tokens
- Output: ~300 tokens
- Cost: $0.02 - $0.05

#### DALL-E 3 (Image Generation)
- 6-7 images at 1024x1024
- Cost per image: $0.04
- Total: $0.24 - $0.28

#### OpenAI TTS (Audio Generation)
- ~200-500 words
- Cost: $0.015 per 1K characters
- Total: $0.02 - $0.10

**Total Cost Per Video: $0.30 - $0.45**

### Monthly Usage Estimates

- **10 videos/month**: $3-5
- **50 videos/month**: $15-25
- **100 videos/month**: $30-45

## 🛡️ Error Handling

### Workflow-Level Errors
- Each step checks for errors from previous steps
- Errors are captured and stored in database
- Workflow gracefully terminates on error
- User sees error message in UI

### API-Level Errors
- OpenAI API errors are caught and logged
- Rate limit errors trigger retries
- Network errors are handled gracefully
- Validation errors return clear messages

### File Management Errors
- Disk space checks before generation
- File permission validations
- Cleanup of partial files on failure

## 🔒 Security Considerations

### API Key Protection
- `.env` file not committed to git
- API key never exposed to frontend
- Server-side API calls only

### Input Validation
- Script length limits
- Style and voice validation
- Keyword sanitization
- SQL injection prevention (ORM)

### File Access
- Files served through API only
- No direct filesystem access from frontend
- Path traversal prevention

## 🧪 Testing

### Manual Testing Checklist
- [ ] Create video with all styles
- [ ] Test all voice options
- [ ] Add keywords and verify in images
- [ ] Test negative keywords
- [ ] Verify video downloads
- [ ] Test video deletion
- [ ] Check error handling
- [ ] Verify status updates

## 📈 Future Enhancements

### Potential Features
1. **Video Editing**: Trim, reorder, or modify scenes
2. **Music**: Add background music option
3. **Transitions**: Fade effects between images
4. **Text Overlays**: Add titles or captions
5. **Batch Processing**: Generate multiple videos
6. **Templates**: Pre-made script templates
7. **Sharing**: Direct social media upload
8. **Analytics**: View counts and engagement

### Technical Improvements
1. **Parallel Processing**: Speed up image generation
2. **Queue System**: Redis/Celery for job management
3. **Cloud Storage**: S3 for video files
4. **Authentication**: User accounts and management
5. **Websockets**: Real-time progress updates
6. **Video Previews**: Show progress during generation
7. **Custom Models**: Fine-tuned DALL-E models
8. **Monitoring**: Prometheus/Grafana dashboards

## 📚 Learning Resources

### Technologies Used
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [MoviePy Documentation](https://zulko.github.io/moviepy/)

## 🤝 Contributing

To extend this system:
1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

MIT License - Free to use for personal or commercial projects.

---

**Built with ❤️ using OpenAI APIs, LangGraph, FastAPI, and Next.js**
