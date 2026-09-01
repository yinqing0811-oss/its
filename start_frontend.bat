@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo Starting ITS frontend on http://localhost:5174
python -m http.server 5174
