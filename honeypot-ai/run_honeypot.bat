@echo off
echo [INFO] Installing Dependencies...
pip install -r requirements.txt

echo [INFO] Starting AI Honeypot System...
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
pause
