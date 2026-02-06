# SpeechFindr Backend

FastAPI backend for SpeechFindr application.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file with your OpenAI API key:
   - Copy `.env.example` to `.env`: `cp .env.example .env` (Linux/Mac) or copy the file manually (Windows)
   - Edit `.env` and replace `your_openai_api_key_here` with your actual OpenAI API key
   - **IMPORTANT**: Never commit the `.env` file! It contains sensitive credentials.
   - Get your API key from: https://platform.openai.com/api-keys
   
   Example `.env` file:
   ```
   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

3. Run the server:
```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

- `POST /fetch_youtube` - Fetch YouTube video
- `POST /upload_video` - Upload video file
- `GET /transcript?video_id=` - Get transcript
- `GET /search?keyword=&video_id=` - Search transcript
- `POST /summarize` - Generate summary

## Requirements

- Python 3.10+
- ffmpeg installed and in PATH
- OpenAI API key

