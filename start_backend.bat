@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo Starting ITS Agent backend on http://localhost:8000

if not exist ".venv\\Scripts\\python.exe" (
  echo Creating virtual environment...
  python -m venv .venv
)

call .venv\\Scripts\\activate
pip install -r requirements.txt

if exist ".env" (
  uvicorn backend.app.main:app --reload --port 8000 --env-file .env
) else (
  echo .env not found. The backend will use mock LLM mode unless DEEPSEEK_API_KEY is already set.
  uvicorn backend.app.main:app --reload --port 8000
)
