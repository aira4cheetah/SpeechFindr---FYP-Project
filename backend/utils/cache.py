import json
import os
from pathlib import Path
from typing import Optional, List, Dict


class CacheManager:
    def __init__(self):
        # Use relative path from backend directory (portable)
        backend_dir = Path(__file__).parent.parent
        self.cache_dir = backend_dir / "cache"
        self.transcripts_dir = self.cache_dir / "transcripts"
        self.metadata_dir = self.cache_dir / "metadata"
        self.audio_dir = self.cache_dir / "audio"
        
        # Create directories
        self.transcripts_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        self.audio_dir.mkdir(parents=True, exist_ok=True)
    
    def get_transcript(self, video_id: str) -> Optional[List[Dict]]:
        """Get cached transcript"""
        transcript_path = self.transcripts_dir / f"{video_id}.json"
        if transcript_path.exists():
            with open(transcript_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None
    
    def save_transcript(self, video_id: str, transcript: List[Dict]):
        """Save transcript to cache"""
        transcript_path = self.transcripts_dir / f"{video_id}.json"
        with open(transcript_path, "w", encoding="utf-8") as f:
            json.dump(transcript, f, indent=2, ensure_ascii=False)
    
    def get_metadata(self, cache_key: str) -> Optional[Dict]:
        """Get cached metadata"""
        metadata_path = self.metadata_dir / f"{cache_key}.json"
        if metadata_path.exists():
            with open(metadata_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None
    
    def save_metadata(self, cache_key: str, metadata: Dict):
        """Save metadata to cache"""
        metadata_path = self.metadata_dir / f"{cache_key}.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def get_audio_path(self, video_id: str) -> Optional[str]:
        """Get audio file path"""
        # Try different extensions
        for ext in [".mp3", ".wav", ".m4a"]:
            audio_path = self.audio_dir / f"{video_id}{ext}"
            if audio_path.exists():
                return str(audio_path)
        return None

