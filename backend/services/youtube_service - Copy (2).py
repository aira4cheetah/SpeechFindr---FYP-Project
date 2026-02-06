import yt_dlp
import os
import asyncio
from pathlib import Path
import subprocess
import shutil


class YouTubeService:
    def __init__(self):
        # Use relative path from backend directory (portable)
        backend_dir = Path(__file__).parent.parent
        self.cache_dir = backend_dir / "cache" / "audio"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ffmpeg_path = self._find_ffmpeg()
    
    def _find_ffmpeg(self):
        """Find ffmpeg executable in common locations"""
        # First, try to find it in PATH
        ffmpeg_path = shutil.which('ffmpeg')
        if ffmpeg_path:
            return ffmpeg_path
        
        # Check common winget installation location
        local_appdata = os.getenv('LOCALAPPDATA', '')
        if local_appdata:
            winget_path = Path(local_appdata) / 'Microsoft' / 'WinGet' / 'Packages'
            if winget_path.exists():
                for ffmpeg_dir in winget_path.glob('*FFmpeg*'):
                    ffmpeg_exe = ffmpeg_dir / 'ffmpeg-*-full_build' / 'bin' / 'ffmpeg.exe'
                    # Try to find matching pattern
                    matches = list(ffmpeg_dir.glob('ffmpeg-*-full_build/bin/ffmpeg.exe'))
                    if matches:
                        return str(matches[0])
        
        # Check Program Files (Windows only)
        if os.name == 'nt':  # Windows
            program_files = os.getenv('ProgramFiles')
            if program_files and Path(program_files).exists():
                # Limit search depth to avoid long searches
                for root, dirs, files in os.walk(program_files):
                    # Limit depth to 3 levels
                    depth = root[len(program_files):].count(os.sep)
                    if depth > 3:
                        dirs[:] = []  # Don't recurse deeper
                        continue
                    if 'ffmpeg.exe' in files:
                        return os.path.join(root, 'ffmpeg.exe')
        
        return None
    
    def extract_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL"""
        import re
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    async def fetch_and_extract_audio(self, url: str, video_id: str) -> dict:
        """Fetch YouTube video and extract audio only"""
        audio_path = self.cache_dir / f"{video_id}.mp3"
        
        # Note: Caching is handled in main.py via metadata cache
        # This function always downloads/extracts audio
        
        # Check if ffmpeg is available
        if not self.ffmpeg_path or not os.path.exists(self.ffmpeg_path):
            raise RuntimeError(
                "ffmpeg is not installed or not found. "
                "Please install ffmpeg using: winget install ffmpeg "
                "or download from https://ffmpeg.org/download.html "
                "and add it to your system PATH. "
                "After installation, restart your terminal and backend server."
            )
        
        # Verify ffmpeg works
        try:
            subprocess.run([self.ffmpeg_path, '-version'], capture_output=True, check=True, timeout=5)
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            raise RuntimeError(
                f"ffmpeg found at {self.ffmpeg_path} but cannot be executed. "
                "Please reinstall ffmpeg or check file permissions."
            )
        
        # Download audio only using yt-dlp - optimized for speed
        # Set ffmpeg location for yt-dlp
        ffmpeg_dir = str(Path(self.ffmpeg_path).parent)
        
        # Use best audio format and extract directly to mp3 for faster processing
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',  # Prefer m4a (faster) or best audio
            'outtmpl': str(audio_path.with_suffix('.%(ext)s')),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '128',  # Lower quality for faster processing
            }],
            'quiet': True,
            'no_warnings': True,
            'ffmpeg_location': ffmpeg_dir,  # Tell yt-dlp where to find ffmpeg
            'noplaylist': True,  # Don't download playlists
            'extract_flat': False,
            'no_check_certificate': True,  # Faster connection
        }
        
        def download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return {
                    "title": info.get('title', 'Unknown'),
                    "duration": info.get('duration', 0),
                    "audio_path": str(audio_path),
                    "cached": False
                }
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, download)
        
        return result
    
    async def extract_audio_from_file(self, video_path: str, video_id: str) -> str:
        """Extract audio from uploaded video file using ffmpeg"""
        audio_path = self.cache_dir / f"{video_id}.mp3"
        
        if audio_path.exists():
            return str(audio_path)
        
        # Check if ffmpeg is available
        if not self.ffmpeg_path or not os.path.exists(self.ffmpeg_path):
            raise RuntimeError(
                "ffmpeg is not installed or not found. "
                "Please install ffmpeg using: winget install ffmpeg "
                "or download from https://ffmpeg.org/download.html"
            )
        
        # Use ffmpeg to extract audio
        cmd = [
            self.ffmpeg_path,
            '-i', video_path,
            '-vn',
            '-acodec', 'libmp3lame',
            '-ab', '192k',
            '-ar', '44100',
            '-y',
            str(audio_path)
        ]
        
        def run_ffmpeg():
            subprocess.run(cmd, capture_output=True, check=True)
            return str(audio_path)
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, run_ffmpeg)
        
        # Clean up original video file
        try:
            os.remove(video_path)
        except:
            pass
        
        return result

