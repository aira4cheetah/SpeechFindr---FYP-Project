# Fix for OpenAI/httpx Compatibility Issue

## Quick Fix

Run these commands in your **activated virtual environment**:

```powershell
# Make sure you're in the backend directory with venv activated
cd backend
.\venv\Scripts\activate

# Upgrade OpenAI and httpx to compatible versions
pip install --upgrade openai httpx

# Reinstall all requirements to ensure compatibility
pip install -r requirements.txt --upgrade
```

## Alternative: Fresh Install

If the above doesn't work, try a fresh install:

```powershell
cd backend
.\venv\Scripts\activate

# Uninstall problematic packages
pip uninstall openai httpx -y

# Reinstall with updated versions
pip install openai>=1.12.0 httpx>=0.25.0

# Reinstall all requirements
pip install -r requirements.txt
```

Then try running again:
```powershell
python main.py
```

