# 🚀 Quick Start Guide - SpeechFindr

## Prerequisites Check

Before starting, make sure you have:
- ✅ Python 3.10+ installed
- ✅ Node.js 18+ installed  
- ✅ ffmpeg installed and in PATH
- ✅ OpenAI API key (already in `backend/.env`)

## Quick Start (Windows)

### Option 1: Using Batch Files (Easiest)

1. **Start Backend** - Double-click `start-backend.bat` or run:
   ```powershell
   .\start-backend.bat
   ```

2. **Start Frontend** - Open a new terminal and double-click `start-frontend.bat` or run:
   ```powershell
   .\start-frontend.bat
   ```

### Option 2: Manual Setup

#### Step 1: Start Backend Server

Open PowerShell or Command Prompt:

```powershell
# Navigate to backend
cd backend

# Create virtual environment (first time only)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies (first time only)
pip install -r requirements.txt

# Run the server
python main.py
```

✅ Backend will run on: `http://localhost:8000`

#### Step 2: Start Frontend (New Terminal)

Open a **NEW** PowerShell or Command Prompt window:

```powershell
# Navigate to frontend
cd frontend

# Install dependencies (first time only)
npm install

# Run development server
npm run dev
```

✅ Frontend will run on: `http://localhost:5173`

## Access the Application

1. Open your browser
2. Go to: **http://localhost:5173**
3. You should see the SpeechFindr interface

## First Time Setup Checklist

### Backend
- [ ] Python 3.10+ installed
- [ ] Virtual environment created (`python -m venv venv`)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file exists with OpenAI API key (✅ Already done!)

### Frontend
- [ ] Node.js 18+ installed
- [ ] Dependencies installed (`npm install`)
- [ ] `.env` file exists with `VITE_API_URL=http://localhost:8000` (✅ Already done!)

## Verify Everything Works

1. **Backend is running**: Visit `http://localhost:8000` - you should see:
   ```json
   {"message": "SpeechFindr API is running"}
   ```

2. **Frontend is running**: Visit `http://localhost:5173` - you should see the SpeechFindr UI

3. **Test the app**:
   - Enter a YouTube URL (e.g., `https://www.youtube.com/watch?v=dQw4w9WgXcQ`)
   - Click "Process"
   - Wait for transcription
   - Try searching for keywords

## Troubleshooting

### Backend Issues

**Error: "Module not found"**
```powershell
# Make sure virtual environment is activated
.\venv\Scripts\activate
pip install -r requirements.txt
```

**Error: "ffmpeg not found"**
- Download ffmpeg from: https://ffmpeg.org/download.html
- Add to system PATH
- Restart terminal

**Error: "OPENAI_API_KEY not found"**
- Check that `backend/.env` exists
- Verify it contains: `OPENAI_API_KEY=sk-proj-...`

### Frontend Issues

**Error: "Cannot connect to backend"**
- Make sure backend is running on port 8000
- Check `frontend/.env` has: `VITE_API_URL=http://localhost:8000`

**Error: "npm install failed"**
```powershell
# Delete node_modules and try again
Remove-Item -Recurse -Force node_modules
npm install
```

## Stopping the Servers

- **Backend**: Press `Ctrl+C` in the backend terminal
- **Frontend**: Press `Ctrl+C` in the frontend terminal

## Next Steps

Once both servers are running:
1. Open `http://localhost:5173` in your browser
2. Enter a YouTube URL or upload a video
3. Wait for transcription
4. Search for keywords
5. Click timestamps to navigate
6. Generate summaries!

---

**Need Help?** Check the main `README.md` or `SETUP.md` for detailed information.

