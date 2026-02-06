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
        # Also request creator-provided subtitles (but do NOT request automatic captions)
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',  # Prefer m4a (faster) or best audio
            'outtmpl': str(audio_path.with_suffix('.%(ext)s')),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '64',  # Lower quality for faster processing
            }],
            'quiet': True,
            'no_warnings': True,
            'ffmpeg_location': ffmpeg_dir,  # Tell yt-dlp where to find ffmpeg
            'noplaylist': True,  # Don't download playlists
            'extract_flat': False,
            'no_check_certificate': True,  # Faster connection
            # Subtitles options: write creator subtitles, but do not write automatic captions
            'writesubtitles': True,
            'writeautomaticsub': False,
            'subtitlesformat': 'vtt',
        }
        
        def download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return {
                    "title": info.get('title', 'Unknown'),
                    "duration": info.get('duration', 0),
                    "audio_path": str(audio_path),
                    "cached": False,
                    "info": info
                }
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, download)

        # After download, check for any subtitle files (creator-provided)
        # Look for .vtt or .srt files for this video_id in the cache dir
        captions_segments = None
        try:
            for ext in ('.vtt', '.srt'):
                # match files like video_id*.vtt
                matches = list(self.cache_dir.glob(f"{video_id}*{ext}"))
                if matches:
                    # Prefer the first match
                    subtitle_path = matches[0]
                    try:
                        text = subtitle_path.read_text(encoding='utf-8')
                    except Exception:
                        text = subtitle_path.read_text(encoding='latin-1')

                    # Parse VTT/SRT into segments
                    if ext == '.vtt':
                        captions_segments = self._parse_vtt(text)
                    else:
                        captions_segments = self._parse_srt(text)
                    break
        except Exception:
            captions_segments = None

        if captions_segments:
            result['captions'] = captions_segments

        return result

    def _parse_vtt(self, vtt_text: str):
        """Simple WebVTT parser returning segments list with start/end/text"""
        segments = []
        lines = vtt_text.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if '-->' in line:
                # timestamp line
                try:
                    times = line.split('-->')
                    start = self._vtt_time_to_seconds(times[0].strip())
                    end = self._vtt_time_to_seconds(times[1].strip())
                    i += 1
                    # collect text lines
                    texts = []
                    while i < len(lines) and lines[i].strip() != '':
                        texts.append(lines[i].strip())
                        i += 1
                    segments.append({
                        'start': start,
                        'end': end,
                        'text': ' '.join(texts).strip()
                    })
                except Exception:
                    i += 1
            else:
                i += 1
        return segments

    def _vtt_time_to_seconds(self, t: str) -> float:
        # formats: HH:MM:SS.mmm or MM:SS.mmm
        parts = t.split(':')
        parts = [p.replace(',', '.') for p in parts]
        parts = [float(p) for p in parts]
        if len(parts) == 3:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        elif len(parts) == 2:
            return parts[0] * 60 + parts[1]
        return 0.0

    def _parse_srt(self, srt_text: str):
        """Simple SRT parser returning segments list with start/end/text"""
        segments = []
        blocks = srt_text.split('\n\n')
        for block in blocks:
            lines = [l.strip() for l in block.splitlines() if l.strip()]
            if len(lines) >= 2:
                # first line may be index, second timestamps
                if '-->' in lines[0]:
                    time_line = lines[0]
                    text_lines = lines[1:]
                else:
                    time_line = lines[1]
                    text_lines = lines[2:]
                try:
                    times = time_line.split('-->')
                    start = self._vtt_time_to_seconds(times[0].strip())
                    end = self._vtt_time_to_seconds(times[1].strip())
                    segments.append({
                        'start': start,
                        'end': end,
                        'text': ' '.join(text_lines).strip()
                    })
                except Exception:
                    continue
        return segments
    
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
            '-ab', '64k',
            '-ar', '16000',
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

