Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  Self-Healing AI Agent Framework Launcher (PowerShell)" -ForegroundColor Cyan
Write-Host "  An LLM-Based Self-Healing Framework for Reliable Multi-Step Task Automation" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

$backendPath = Join-Path $PSScriptRoot "backend"
$frontendPath = Join-Path $PSScriptRoot "frontend"
$pythonPath = Join-Path $PSScriptRoot "venv\Scripts\python.exe"

Write-Host "`n[1/2] Starting FastAPI Backend on http://127.0.0.1:8000 ..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; & '$pythonPath' -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

Write-Host "[2/2] Starting React Frontend on http://localhost:5173 ..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; npm run dev"

Write-Host "`nServers launched in separate terminal windows!" -ForegroundColor Yellow
Write-Host "  - Frontend UI:    http://localhost:5173" -ForegroundColor White
Write-Host "  - Backend API:    http://127.0.0.1:8000" -ForegroundColor White
Write-Host "  - Interactive Docs: http://127.0.0.1:8000/docs" -ForegroundColor White
