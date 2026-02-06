# How to Install FFmpeg on Windows

FFmpeg is required for processing YouTube videos and extracting audio. Follow these steps:

## Option 1: Using Chocolatey (Recommended - Easiest)

1. **Install Chocolatey** (if not already installed):
   - Open PowerShell as Administrator
   - Run: `Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))`

2. **Install FFmpeg**:
   ```powershell
   choco install ffmpeg
   ```

3. **Restart your terminal** and verify:
   ```powershell
   ffmpeg -version
   ```

## Option 2: Manual Installation

1. **Download FFmpeg**:
   - Go to: https://www.gyan.dev/ffmpeg/builds/
   - Download: `ffmpeg-release-essentials.zip` (or latest version)

2. **Extract the ZIP file**:
   - Extract to: `C:\ffmpeg` (or any location you prefer)

3. **Add to PATH**:
   - Press `Win + X` and select "System"
   - Click "Advanced system settings"
   - Click "Environment Variables"
   - Under "System variables", find and select "Path", then click "Edit"
   - Click "New" and add: `C:\ffmpeg\bin` (or your ffmpeg bin folder path)
   - Click "OK" on all dialogs

4. **Verify installation**:
   - Close and reopen your terminal
   - Run: `ffmpeg -version`
   - You should see version information

## Option 3: Using Winget (Windows 10/11)

```powershell
winget install ffmpeg
```

Then restart your terminal.

## Verify Installation

After installation, verify it works:

```powershell
ffmpeg -version
ffprobe -version
```

Both commands should show version information.

## Troubleshooting

- **"ffmpeg is not recognized"**: Make sure you restarted your terminal after adding to PATH
- **Still not working**: Try restarting your computer
- **Check PATH**: Run `echo $env:PATH` in PowerShell to see if ffmpeg bin folder is listed

## After Installation

Once ffmpeg is installed, restart your backend server:
```powershell
cd backend
.\venv\Scripts\activate
python main.py
```

