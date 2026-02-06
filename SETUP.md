# SpeechFindr - Quick Setup Guide

## Prerequisites

1. **Python 3.10+** installed
2. **Node.js 18+** installed
3. **ffmpeg** installed and accessible in PATH
   - Download from: https://ffmpeg.org/download.html
   - Verify: `ffmpeg -version` in terminal

## Step-by-Step Setup

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from example:
# Copy .env.example to .env and add your OpenAI API key
# IMPORTANT: Never commit .env file - it contains your API key!

# Run the server
python main.py
```

The backend will run on `http://localhost:8000`

### 2. Frontend Setup

Open a **new terminal window**:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will run on `http://localhost:5173`

## Usage

1. Open `http://localhost:5173` in your browser
2. Enter a YouTube URL or upload a video file
3. Wait for transcription (cached videos load instantly)
4. Search for keywords in the transcript
5. Click timestamps to jump to video playback
6. Click "Summarize" to generate AI summaries

## Troubleshooting

### Backend Issues

- **Module not found**: Make sure virtual environment is activated
- **ffmpeg not found**: Install ffmpeg and add to PATH
- **OpenAI API errors**: Check your API key in `.env` file

### Frontend Issues

- **Cannot connect to backend**: Ensure backend is running on port 8000
- **Build errors**: Delete `node_modules` and run `npm install` again

## Project Structure

```
.
├── backend/          # FastAPI backend
│   ├── main.py      # API server
│   ├── services/    # Business logic
│   └── utils/       # Utilities
├── frontend/        # React frontend
│   └── src/         # Source code
└── cache/           # Auto-generated cache (audio, transcripts, metadata)
```

## Notes

- Transcripts and audio are cached locally to avoid repeated API calls
- Stopwords (common words) are blocked from keyword searches
- The system uses GPT-3.5-turbo for cost-efficient summarization

