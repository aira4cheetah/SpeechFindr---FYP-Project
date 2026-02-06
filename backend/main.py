from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import os
from dotenv import load_dotenv

from services.youtube_service import YouTubeService
from services.transcription_service import TranscriptionService
from services.search_service import SearchService
from services.summarization_service import SummarizationService
from utils.cache import CacheManager

load_dotenv()

app = FastAPI(title="SpeechFindr API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
youtube_service = YouTubeService()
transcription_service = TranscriptionService()
search_service = SearchService()
summarization_service = SummarizationService()
cache_manager = CacheManager()


class YouTubeRequest(BaseModel):
    url: str


class SummarizeRequest(BaseModel):
    video_id: str
    keyword: str
    segments: List[dict]


@app.get("/")
async def root():
    return {"message": "SpeechFindr API is running"}


@app.post("/fetch_youtube")
async def fetch_youtube(request: YouTubeRequest):
    """Fetch YouTube video and extract audio"""
    try:
        video_id = youtube_service.extract_video_id(request.url)
        if not video_id:
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")
        
        # Always process fresh - no caching
        result = await youtube_service.fetch_and_extract_audio(request.url, video_id)
        result["url"] = request.url

        # If creator captions were found, save them into cache as the transcript
        if result.get('captions'):
            try:
                cache_manager.save_transcript(video_id, result['captions'])
            except Exception:
                pass

        return {
            "video_id": video_id,
            "title": result.get("title"),
            "duration": result.get("duration"),
            "url": request.url,
            "has_creator_captions": bool(result.get('captions'))
        }
    except Exception as e:
        import traceback
        error_detail = str(e)
        print(f"Error in fetch_youtube: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=error_detail)


@app.post("/upload_video")
async def upload_video(file: UploadFile = File(...)):
    """Upload video file and extract audio"""
    try:
        import hashlib
        import time
        
        # Generate unique video ID based on filename and timestamp
        filename_hash = hashlib.md5(file.filename.encode()).hexdigest()[:8]
        timestamp = int(time.time() * 1000) % 1000000
        video_id = f"upload_{filename_hash}_{timestamp}"
        
        # Use portable path
        from pathlib import Path
        backend_dir = Path(__file__).parent
        cache_audio_dir = backend_dir / "cache" / "audio"
        cache_audio_dir.mkdir(parents=True, exist_ok=True)
        temp_path = cache_audio_dir / f"{video_id}.{file.filename.split('.')[-1]}"
        
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Extract audio using ffmpeg
        audio_path = await youtube_service.extract_audio_from_file(str(temp_path), video_id)
        
        return {
            "video_id": video_id,
            "title": file.filename,
            "audio_path": audio_path,
            "filename": file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/transcript")
async def get_transcript(video_id: str = Query(...)):
    """Get transcript with timestamps"""
    try:
        # Always process fresh - no caching
        # Get audio path
        audio_path = cache_manager.get_audio_path(video_id)
        if not audio_path or not os.path.exists(audio_path):
            raise HTTPException(status_code=404, detail="Audio file not found. Please fetch the video first.")
        
        # If a cached transcript exists (e.g. creator captions saved during fetch), return it
        cached = cache_manager.get_transcript(video_id)
        if cached:
            return {
                "video_id": video_id,
                "transcript": cached,
                "cached": True
            }

        # Otherwise transcribe (fresh)
        transcript = await transcription_service.transcribe_with_timestamps(audio_path)

        return {
            "video_id": video_id,
            "transcript": transcript,
            "cached": False
        }
    except Exception as e:
        import traceback
        error_detail = str(e)
        print(f"Error in get_transcript: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=error_detail)


@app.get("/search")
async def search_keyword(
    keyword: str = Query(...),
    video_id: str = Query(...)
):
    """Search for keyword in transcript"""
    try:
        # Validate keyword (check for stopwords)
        if search_service.is_stopword(keyword):
            raise HTTPException(
                status_code=400,
                detail="Stopwords are not allowed in keyword search"
            )
        
        # Get transcript (always fresh - no cache)
        audio_path = cache_manager.get_audio_path(video_id)
        if not audio_path or not os.path.exists(audio_path):
            raise HTTPException(status_code=404, detail="Audio file not found. Please fetch the video first.")
        
        # Transcribe fresh
        transcript = await transcription_service.transcribe_with_timestamps(audio_path)
        
        # Search
        results = search_service.search_keyword(transcript, keyword)
        
        return {
            "video_id": video_id,
            "keyword": keyword,
            "matches": results["matches"],
            "segments": results["segments"],
            "total_count": results["total_count"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/summarize")
async def summarize(request: SummarizeRequest):
    """Summarize transcript segments"""
    try:
        # Validate keyword
        if search_service.is_stopword(request.keyword):
            raise HTTPException(
                status_code=400,
                detail="Stopwords are not allowed"
            )
        
        # Generate summary
        summary = await summarization_service.summarize_segments(
            request.segments,
            request.keyword
        )
        
        return {
            "video_id": request.video_id,
            "keyword": request.keyword,
            "summary": summary
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

