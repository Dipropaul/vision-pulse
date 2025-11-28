"""
VisionPulse System Test
Run this script to verify your setup is working correctly
"""

import os
import sys
from pathlib import Path

print("🧪 VisionPulse System Test")
print("=" * 50)
print()

# Test 1: Check Python version
print("1. Checking Python version...")
version = sys.version_info
if version.major >= 3 and version.minor >= 8:
    print(f"   ✓ Python {version.major}.{version.minor}.{version.micro}")
else:
    print(f"   ✗ Python version too old. Need 3.8+, found {version.major}.{version.minor}")
    sys.exit(1)

# Test 2: Check required packages
print("\n2. Checking required packages...")
required_packages = [
    "fastapi",
    "uvicorn",
    "langgraph",
    "langchain",
    "langchain_openai",
    "openai",
    "moviepy",
    "sqlalchemy",
    "pydantic",
]

missing_packages = []
for package in required_packages:
    try:
        __import__(package)
        print(f"   ✓ {package}")
    except ImportError:
        print(f"   ✗ {package} - NOT FOUND")
        missing_packages.append(package)

if missing_packages:
    print(f"\n   ⚠️  Missing packages: {', '.join(missing_packages)}")
    print("   Run: pip install -r requirements.txt")
    sys.exit(1)

# Test 3: Check .env file
print("\n3. Checking configuration...")
env_path = Path(".env")
if env_path.exists():
    print("   ✓ .env file exists")
    
    # Check for API key
    with open(env_path) as f:
        content = f.read()
        if "OPENAI_API_KEY" in content:
            if "your_openai_api_key_here" in content:
                print("   ⚠️  OpenAI API key not set in .env")
                print("   Edit .env and add your actual API key")
            else:
                print("   ✓ OpenAI API key configured")
        else:
            print("   ✗ OPENAI_API_KEY not found in .env")
else:
    print("   ✗ .env file not found")
    print("   Copy .env.example to .env and configure it")
    sys.exit(1)

# Test 4: Check output directories
print("\n4. Checking output directories...")
dirs_to_check = ["output/videos", "output/images", "output/audio"]
for dir_path in dirs_to_check:
    path = Path(dir_path)
    if path.exists():
        print(f"   ✓ {dir_path}")
    else:
        print(f"   ⚠️  {dir_path} will be created on first run")

# Test 5: Import backend modules
print("\n5. Checking backend modules...")
try:
    from backend.config.settings import settings
    print("   ✓ backend.config.settings")
    
    from backend.models.database import init_db
    print("   ✓ backend.models.database")
    
    from backend.workflows.video_workflow import VideoGenerationWorkflow
    print("   ✓ backend.workflows.video_workflow")
    
    from backend.services.image_service import ImageService
    print("   ✓ backend.services.image_service")
    
    from backend.services.audio_service import AudioService
    print("   ✓ backend.services.audio_service")
    
    from backend.services.video_service import VideoService
    print("   ✓ backend.services.video_service")
    
except ImportError as e:
    print(f"   ✗ Import error: {e}")
    sys.exit(1)

# Test 6: Initialize database
print("\n6. Testing database initialization...")
try:
    from backend.models.database import init_db, engine
    init_db()
    print("   ✓ Database initialized successfully")
except Exception as e:
    print(f"   ✗ Database error: {e}")
    sys.exit(1)

# Test 7: Test OpenAI connection (if API key is set)
print("\n7. Testing OpenAI API connection...")
try:
    from openai import OpenAI
    
    # Check if API key looks valid
    api_key = os.getenv("OPENAI_API_KEY", "")
    if api_key and not api_key.startswith("your_"):
        try:
            client = OpenAI(api_key=api_key)
            # Test with a simple models list call (cheap/free)
            models = client.models.list()
            print("   ✓ OpenAI API connection successful")
        except Exception as e:
            print(f"   ⚠️  OpenAI API error: {str(e)[:100]}")
            print("   Check your API key and internet connection")
    else:
        print("   ⚠️  OpenAI API key not configured")
        print("   Add your API key to .env to test API connection")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Final summary
print("\n" + "=" * 50)
print("✅ System test complete!")
print()
print("Next steps:")
print("1. Edit .env and add your OpenAI API key")
print("2. Start backend:  .\\start-backend.ps1")
print("3. Start frontend: .\\start-frontend.ps1")
print("4. Open http://localhost:3000")
print()
print("For detailed instructions, see QUICKSTART.md")
