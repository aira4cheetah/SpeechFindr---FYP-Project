# SpeechFindr

A fast, reliable, and cost-efficient speech search & summarization application with React frontend and FastAPI backend.

## Features

- **YouTube Link or Video Upload**: Process videos from YouTube links or upload your own video files
- **Fast Transcription**: OpenAI Whisper with timestamp support and intelligent caching
- **Keyword Search**: Search transcripts with stopword filtering
- **Timestamp Navigation**: Click timestamps to instantly jump to video playback
- **AI Summarization**: Generate concise summaries using GPT-3.5-turbo (cost-efficient)

## Tech Stack

### Backend
- FastAPI
- OpenAI API (Whisper STT + GPT-3.5-turbo)
- yt-dlp (YouTube audio extraction)
- ffmpeg (audio processing)
- Local file caching system

### Frontend
- React + JavaScript
- Vite
- TailwindCSS
- React Player
- Dark futuristic theme (dark blue + black + gray)

## Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+
- ffmpeg installed and in PATH

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
```

3. Activate virtual environment:
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Create `.env` file:
   - Copy `.env.example` to `.env` (or create it manually)
   - Add your OpenAI API key:
   ```bash
   OPENAI_API_KEY=your_actual_api_key_here
   ```
   - **SECURITY**: Never commit the `.env` file! It's already in `.gitignore`
   - Get your API key from: https://platform.openai.com/api-keys

6. Run the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Create `.env` file with API URL:
```bash
VITE_API_URL=http://localhost:8000
```

3. Install dependencies:
```bash
npm install
```

4. Run the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

## Usage

1. **Input Video**: 
   - Enter a YouTube URL and click "Process", OR
   - Upload a video file

2. **Wait for Transcription**: The system will automatically transcribe the audio (cached results load instantly)

3. **Search Keywords**: 
   - Enter a keyword in the search bar (stopwords are blocked)
   - View highlighted matches in the transcript

4. **Navigate**: Click any timestamp to jump to that point in the video

5. **Summarize**: After searching, click "Summarize" to generate an AI summary of the keyword-relevant segments

## Performance Features

- **Intelligent Caching**: Transcripts and audio files are cached locally to avoid repeated API calls
- **Fast Response**: Streaming and incremental processing where possible
- **Cost Optimization**: Uses GPT-3.5-turbo and caches transcripts to minimize OpenAI API usage
- **Stopword Filtering**: Prevents meaningless searches to save API costs

## Project Structure

```
.
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── services/               # Business logic services
│   │   ├── youtube_service.py
│   │   ├── transcription_service.py
│   │   ├── search_service.py
│   │   └── summarization_service.py
│   ├── utils/                  # Utility functions
│   │   └── cache.py
│   └── cache/                  # Cached files (auto-generated)
│       ├── audio/
│       ├── transcripts/
│       └── metadata/
└── frontend/
    ├── src/
    │   ├── components/         # React components
    │   ├── services/            # API service functions
    │   ├── api/                # API client configuration
    │   └── App.jsx             # Main app component
    ├── .env                    # Environment variables (API URL)
    └── package.json
```

## API Endpoints

- `POST /fetch_youtube` - Fetch YouTube video and extract audio
- `POST /upload_video` - Upload video file
- `GET /transcript?video_id=` - Get transcript with timestamps
- `GET /search?keyword=&video_id=` - Search for keyword in transcript
- `POST /summarize` - Generate summary of segments

## Environment Variables

### Backend (.env)
```
OPENAI_API_KEY=your_openai_api_key_here
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
```

## Notes

- Stopwords (common words like "the", "a", "is", etc.) are blocked from keyword searches
- Transcripts are cached to avoid repeated OpenAI Whisper API calls
- Audio files are cached locally after extraction
- The system uses GPT-3.5-turbo for cost-efficient summarization
- API URL is configurable via frontend `.env` file

