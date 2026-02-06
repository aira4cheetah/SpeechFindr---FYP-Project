import os
from openai import OpenAI
from typing import List, Dict
import asyncio
from pathlib import Path
import subprocess
import shutil


class TranscriptionService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        self.client = OpenAI(api_key=api_key)
        self.ffmpeg_path = self._find_ffmpeg()
        self.max_file_size = 25 * 1024 * 1024  # 25MB limit for OpenAI
    
    def _find_ffmpeg(self):
        """Find ffmpeg executable"""
        ffmpeg_path = shutil.which('ffmpeg')
        if ffmpeg_path:
            return ffmpeg_path
        
        local_appdata = os.getenv('LOCALAPPDATA', '')
        if local_appdata:
            winget_path = Path(local_appdata) / 'Microsoft' / 'WinGet' / 'Packages'
            if winget_path.exists():
                matches = list(winget_path.glob('*FFmpeg*/ffmpeg-*-full_build/bin/ffmpeg.exe'))
                if matches:
                    return str(matches[0])
        return None
    
    def _get_audio_duration(self, audio_path: str) -> float:
        """Get audio duration in seconds using ffprobe"""
        if not self.ffmpeg_path:
            return 0.0
        
        # Try to find ffprobe (cross-platform)
        ffprobe_path = None
        ffmpeg_dir = Path(self.ffmpeg_path).parent
        
        # Try platform-specific extensions
        if os.name == 'nt':  # Windows
            ffprobe_path = ffmpeg_dir / 'ffprobe.exe'
            if not ffprobe_path.exists():
                ffprobe_path = None
        else:  # Linux/Mac
            ffprobe_path = ffmpeg_dir / 'ffprobe'
            if not ffprobe_path.exists():
                ffprobe_path = None
        
        # Try system PATH
        if not ffprobe_path or not ffprobe_path.exists():
            ffprobe_system = shutil.which('ffprobe')
            if ffprobe_system:
                ffprobe_path = Path(ffprobe_system)
            else:
                return 0.0
        
        try:
            cmd = [
                str(ffprobe_path),
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                audio_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=10)
            return float(result.stdout.strip())
        except:
            return 0.0
    
    def _split_audio_chunk(self, audio_path: str, start_time: float, duration: float, output_path: str) -> str:
        """Extract a chunk of audio from the file"""
        if not self.ffmpeg_path:
            raise RuntimeError("ffmpeg not found. Cannot split audio file.")
        
        cmd = [
            self.ffmpeg_path,
            '-i', audio_path,
            '-ss', str(start_time),
            '-t', str(duration),
            '-acodec', 'libmp3lame',
            '-ab', '64k',  # Lower bitrate for smaller files
            '-ar', '16000',  # Lower sample rate (sufficient for speech)
            '-ac', '1',  # Mono
            '-y',  # Overwrite
            str(output_path)
        ]
        subprocess.run(cmd, capture_output=True, check=True, timeout=300)
        return str(output_path)
    
    def _convert_to_mp3_sync(self, audio_path: str) -> str:
        """Convert audio file to MP3 format synchronously"""
        audio_file = Path(audio_path)
        
        # If already MP3 and under size limit, return as-is
        if audio_file.suffix.lower() == '.mp3':
            file_size = os.path.getsize(audio_path)
            if file_size <= self.max_file_size:
                return audio_path
        
        # Convert to MP3
        output_path = audio_file.parent / f"{audio_file.stem}_converted.mp3"
        
        if not self.ffmpeg_path:
            raise RuntimeError("ffmpeg not found. Cannot convert audio file.")
        
        cmd = [
            self.ffmpeg_path,
            '-i', audio_path,
            '-acodec', 'libmp3lame',
            '-ab', '64k',  # Lower bitrate to reduce file size
            '-ar', '16000',  # Lower sample rate (sufficient for speech)
            '-ac', '1',  # Mono (sufficient for speech)
            '-y',  # Overwrite
            str(output_path)
        ]
        subprocess.run(cmd, capture_output=True, check=True, timeout=600)
        return str(output_path)
    
    async def transcribe_with_timestamps(self, audio_path: str) -> List[Dict]:
        """Transcribe audio file with timestamps using OpenAI Whisper"""
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Check file size and format
        file_size = os.path.getsize(audio_path)
        file_ext = Path(audio_path).suffix.lower()
        supported_formats = ['.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm']
        
        # Convert if needed (wrong format)
        if file_ext not in supported_formats:
            print(f"Converting audio file format ({file_ext})...")
            audio_path = await asyncio.get_event_loop().run_in_executor(
                None, self._convert_to_mp3_sync, audio_path
            )
            file_size = os.path.getsize(audio_path)
        
        # If file is too large, split into chunks
        if file_size > self.max_file_size:
            print(f"File too large ({file_size / 1024 / 1024:.2f}MB). Splitting into chunks...")
            return await self._transcribe_large_file(audio_path)
        
        # Process normally for smaller files
        return await self._transcribe_single_file(audio_path)
    
    async def _transcribe_large_file(self, audio_path: str) -> List[Dict]:
        """Transcribe large audio file by splitting into chunks"""
        # Get audio duration
        duration = await asyncio.get_event_loop().run_in_executor(
            None, self._get_audio_duration, audio_path
        )
        
        if duration == 0:
            # Fallback: estimate from file size (rough estimate: 1MB ≈ 1 minute at 64kbps)
            file_size_mb = os.path.getsize(audio_path) / 1024 / 1024
            duration = file_size_mb * 60  # Rough estimate
        
        # Calculate chunk size (aim for ~20MB chunks to be safe)
        # At 64kbps mono, ~20MB ≈ 40 minutes
        chunk_duration = 40 * 60  # 40 minutes in seconds
        num_chunks = int(duration / chunk_duration) + 1
        
        print(f"Audio duration: {duration/60:.1f} minutes. Splitting into {num_chunks} chunks...")
        
        all_segments = []
        audio_dir = Path(audio_path).parent
        base_name = Path(audio_path).stem
        
        # Process each chunk
        for i in range(num_chunks):
            start_time = i * chunk_duration
            chunk_dur = min(chunk_duration, duration - start_time)
            
            if chunk_dur <= 0:
                break
            
            print(f"Processing chunk {i+1}/{num_chunks} (time: {start_time/60:.1f}-{(start_time+chunk_dur)/60:.1f} min)...")
            
            # Create chunk file
            chunk_path = audio_dir / f"{base_name}_chunk_{i}.mp3"
            
            # Extract chunk
            await asyncio.get_event_loop().run_in_executor(
                None, self._split_audio_chunk, audio_path, start_time, chunk_dur, str(chunk_path)
            )
            
            # Transcribe chunk
            try:
                chunk_segments = await self._transcribe_single_file(str(chunk_path))
                
                # Adjust timestamps by adding chunk start time
                for segment in chunk_segments:
                    segment['start'] += start_time
                    segment['end'] += start_time
                
                all_segments.extend(chunk_segments)
            except Exception as e:
                print(f"Error transcribing chunk {i+1}: {str(e)}")
                # Continue with other chunks
            finally:
                # Clean up chunk file
                try:
                    if chunk_path.exists():
                        os.remove(chunk_path)
                except:
                    pass
        
        # Sort segments by start time
        all_segments.sort(key=lambda x: x['start'])
        
        print(f"Transcription complete. Total segments: {len(all_segments)}")
        return all_segments
    
    async def _transcribe_single_file(self, audio_path: str) -> List[Dict]:
        """Transcribe a single audio file"""
        def transcribe():
            # Try with verbose_json first for timestamps, fallback to simple format
            try:
                with open(audio_path, "rb") as audio_file:
                    # Try with verbose_json for timestamps
                    transcript = self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="verbose_json"
                    )
                    return transcript
            except Exception as e:
                # If verbose_json fails, try simple format
                print(f"verbose_json failed, trying simple format: {str(e)}")
                with open(audio_path, "rb") as audio_file:
                    transcript = self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )
                    # Convert simple response to verbose format
                    if hasattr(transcript, 'text'):
                        return {"text": transcript.text, "segments": []}
                    elif isinstance(transcript, dict) and 'text' in transcript:
                        return {"text": transcript['text'], "segments": []}
                    return transcript
        
        # Run in thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, transcribe)
        
        # Format transcript with timestamps
        formatted_transcript = []
        
        # Process segments - handle both dict and object responses
        if isinstance(result, dict):
            # If response is a dict
            if 'segments' in result and result['segments']:
                for segment in result['segments']:
                    formatted_transcript.append({
                        "start": segment.get('start', 0.0),
                        "end": segment.get('end', 0.0),
                        "text": segment.get('text', '').strip()
                    })
            elif 'text' in result:
                # Fallback: single segment
                formatted_transcript.append({
                    "start": 0.0,
                    "end": 0.0,
                    "text": result.get('text', '').strip()
                })
        else:
            # If response is an object
            if hasattr(result, 'segments') and result.segments:
                for segment in result.segments:
                    formatted_transcript.append({
                        "start": getattr(segment, 'start', 0.0),
                        "end": getattr(segment, 'end', 0.0),
                        "text": getattr(segment, 'text', '').strip()
                    })
            elif hasattr(result, 'text'):
                formatted_transcript.append({
                    "start": 0.0,
                    "end": 0.0,
                    "text": getattr(result, 'text', '').strip()
                })
        
        return formatted_transcript if formatted_transcript else [{"start": 0.0, "end": 0.0, "text": ""}]

