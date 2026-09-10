@echo off
echo ========================================
echo    LetMeCook - AI Cooking Assistant
echo ========================================
echo.

:: Start Backend
echo [1/2] Starting FastAPI Backend...
cd /d %~dp0backend
start "LetMeCook Backend" cmd /k "python -m venv venv 2>nul & call venv\Scripts\activate & pip install -r requirements.txt -q & uvicorn app.main:app --reload --host 0.0.0.0 --port 8001"

:: Wait for backend to initialize
timeout /t 3 /nobreak >nul

:: Start Frontend
echo [2/2] Starting React Frontend...
cd /d %~dp0frontend
start "LetMeCook Frontend" cmd /k "npm install & npm run dev"

echo.
echo ========================================
echo   Backend:  http://localhost:8001
echo   Frontend: http://localhost:5173
echo   API Docs: http://localhost:8001/docs
echo ========================================
echo.
echo Both servers are starting in separate windows.
pause
