@echo off
echo ======================================================================
echo  Self-Healing AI Agent Framework Launcher
echo  An LLM-Based Self-Healing Framework for Reliable Multi-Step Task Automation
echo ======================================================================

echo [1/2] Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "Self-Healing Backend" cmd /k "cd backend && ..\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo [2/2] Starting Vite React Frontend on http://localhost:5173 ...
start "Self-Healing Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Both servers are launching:
echo   - Frontend: http://localhost:5173
echo   - Backend API: http://127.0.0.1:8000
echo   - Swagger Docs: http://127.0.0.1:8000/docs
echo ======================================================================
pause
