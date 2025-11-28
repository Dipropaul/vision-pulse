# VisionPulse - Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### Prerequisites
- Python 3.8 or higher
- Node.js 18 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Automated Setup

```powershell
# Run the setup script
.\setup.ps1
```

This will:
- Create a Python virtual environment
- Install all Python dependencies
- Install all Node.js dependencies
- Create a `.env` file from the template

### Manual Setup

If you prefer manual setup:

```powershell
# 1. Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Create .env file
cp .env.example .env

# 4. Install frontend dependencies
cd frontend
npm install
cd ..
```

### Configure OpenAI API Key

Edit `.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=sk-your-api-key-here
```

## 🎬 Running the Application

### Option 1: Using Helper Scripts

**Terminal 1 - Backend:**
```powershell
.\start-backend.ps1
```

**Terminal 2 - Frontend:**
```powershell
.\start-frontend.ps1
```

### Option 2: Manual Commands

**Terminal 1 - Backend:**
```powershell
.\venv\Scripts\Activate.ps1
python -m uvicorn backend.main:app --reload
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```

### Access the Application

- **Dashboard:** http://localhost:3000
- **API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## 📖 How to Use

1. **Open the Dashboard** at http://localhost:3000
2. **Click "Create New Video"**
3. **Fill in the form:**
   - Title: Name your video
   - Script: Paste your narration script
   - Style: Choose a visual style (cinematic, anime, etc.)
   - Voice: Select a narration voice
   - Keywords: (Optional) Add keywords to guide image generation
   - Negative Keywords: (Optional) Add things to avoid in images
4. **Click "Create Video"**
5. **Wait for processing** (takes 2-5 minutes depending on script length)
6. **Download** your finished video!

## 🎨 Available Styles

- **Cinematic:** Professional film-like quality
- **Anime:** Japanese animation style
- **Realistic:** Photorealistic imagery
- **Watercolor:** Soft painting aesthetic
- **Cyberpunk:** Futuristic neon-lit style
- **Minimalist:** Clean and elegant
- **Fantasy:** Magical enchanted worlds
- **Comic Book:** Bold illustration style

## 🎙️ Available Voices

- **Alloy:** Neutral and balanced
- **Echo:** Warm and engaging
- **Fable:** Expressive storytelling
- **Onyx:** Deep and authoritative
- **Nova:** Energetic and dynamic
- **Shimmer:** Bright and cheerful

## 🏗️ System Architecture

### LangGraph Sequential Workflow

The video generation follows a sequential pipeline:

```
1. Generate Prompts (GPT-4o)
   ↓
2. Generate Images (DALL-E 3)
   ↓
3. Generate Narration (OpenAI TTS)
   ↓
4. Assemble Video (MoviePy)
```

### Technology Stack

**Backend:**
- LangGraph: Orchestrates the sequential workflow
- FastAPI: REST API server
- OpenAI API: Image generation, text-to-speech, and GPT-4o
- MoviePy: Video assembly
- SQLite: Database for video metadata

**Frontend:**
- Next.js 14: React framework
- TailwindCSS: Styling
- SWR: Data fetching and caching
- Lucide React: Icons

## 📁 Project Structure

```
VisionPulse/
├── backend/
│   ├── api/              # FastAPI routes
│   ├── workflows/        # LangGraph workflows
│   ├── services/         # Business logic
│   │   ├── image_service.py   # DALL-E 3 integration
│   │   ├── audio_service.py   # OpenAI TTS integration
│   │   └── video_service.py   # Video assembly
│   ├── models/           # Database models
│   └── config/           # Configuration & presets
├── frontend/             # Next.js dashboard
│   ├── app/             # Next.js App Router
│   ├── components/      # React components
│   └── lib/             # API client
├── output/              # Generated content
│   ├── videos/
│   ├── images/
│   └── audio/
├── requirements.txt     # Python dependencies
└── .env                 # Configuration
```

## 🔧 Configuration

Edit `.env` to customize:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o
OPENAI_IMAGE_MODEL=dall-e-3
OPENAI_TTS_MODEL=tts-1

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Frontend URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 💰 Cost Estimation

Using OpenAI API, approximate costs per video:

- **GPT-4o (prompts):** $0.02 - $0.05
- **DALL-E 3 (6-7 images):** $0.24 - $0.28
- **TTS (narration):** $0.02 - $0.10

**Total per video:** ~$0.30 - $0.45

## 🐛 Troubleshooting

### Backend won't start
- Ensure virtual environment is activated
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify `.env` file exists with valid `OPENAI_API_KEY`

### Frontend won't start
- Ensure Node.js dependencies are installed: `cd frontend && npm install`
- Check that backend is running on port 8000

### Video generation fails
- Check OpenAI API key is valid
- Ensure you have sufficient API credits
- Check backend logs for specific error messages

### "Module not found" errors
- Reactivate virtual environment: `.\venv\Scripts\Activate.ps1`
- Reinstall dependencies: `pip install -r requirements.txt`

## 🎯 API Endpoints

- `POST /api/videos/create` - Create new video
- `GET /api/videos` - List all videos
- `GET /api/videos/{id}` - Get video details
- `DELETE /api/videos/{id}` - Delete video
- `GET /api/styles` - List available styles
- `GET /api/voices` - List available voices

Full API documentation: http://localhost:8000/docs

## 📝 Example Scripts

### Short Video (30-45 seconds)
```
Welcome to the future of AI. In this digital age, artificial intelligence 
is transforming how we create, learn, and innovate. From generative art 
to intelligent assistants, AI is opening new possibilities every day. 
Join us on this incredible journey into tomorrow.
```

### Medium Video (60-90 seconds)
```
Once upon a time, in a world where magic and technology coexisted, 
a young inventor discovered an ancient artifact. This mysterious device 
held the power to bend reality itself. As she unlocked its secrets, 
she realized that the greatest inventions come not from machines, 
but from the human imagination. Her journey would change everything.
```

## 🤝 Support

For issues, questions, or contributions:
- Check the API documentation at `/docs`
- Review the backend logs in the terminal
- Ensure all dependencies are up to date

## 📜 License

MIT License - feel free to use for personal or commercial projects!
