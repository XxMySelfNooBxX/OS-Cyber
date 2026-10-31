# start_project.ps1 — CyberBank QA Compliance & Digital Forensics Demo Launcher
$Root = $PSScriptRoot
if (-not $Root) { $Root = (Get-Location).Path }

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  CyberBank QA Compliance & Digital Forensics Platform" -ForegroundColor Cyan
Write-Host "  Launching 3-Tier Demo Architecture" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 1. Resolve Python executable dynamically
$Py = (Get-Command python -ErrorAction SilentlyContinue)?.Source
if (-not $Py) { $Py = (Get-Command python3 -ErrorAction SilentlyContinue)?.Source }
if (-not $Py) { $Py = (Get-Command py -ErrorAction SilentlyContinue)?.Source }
if (-not $Py) {
    $commonPythonPaths = @(
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "$env:ProgramFiles\Python312\python.exe",
        "$env:ProgramFiles\Python311\python.exe",
        "C:\Users\Shaurya\AppData\Local\Programs\Python\Python311\python.exe"
    )
    foreach ($cand in $commonPythonPaths) {
        if (Test-Path $cand) { $Py = $cand; break }
    }
}

if (-not $Py) {
    Write-Host "[!] Error: Python executable not found in PATH or standard directories." -ForegroundColor Red
    Write-Host "    Please ensure Python 3.11+ is installed." -ForegroundColor Yellow
    exit 1
}

Write-Host "[+] Python resolved: $Py" -ForegroundColor Green

# 2. Start Tier 1: Target Flask App (Port 5000)
Write-Host "[1/3] Starting Target Flask Application (http://127.0.0.1:5000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$Root\target-app'; Write-Host '--- Seeding Database ---' -ForegroundColor Cyan; & '$Py' seed_db.py; Write-Host '--- Starting Target Flask Server (Port 5000) ---' -ForegroundColor Green; & '$Py' app.py"
Start-Sleep -Seconds 2

# 3. Start Tier 2: Orchestrator FastAPI Backend (Port 8000)
Write-Host "[2/3] Starting Orchestrator FastAPI API (http://127.0.0.1:8000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$Root\orchestrator-api'; Write-Host '--- Starting Orchestrator API (Port 8000) ---' -ForegroundColor Green; & '$Py' main.py"
Start-Sleep -Seconds 2

# 4. Start Tier 3: React Vite Dashboard (Port 5173)
Write-Host "[3/3] Starting React Vite Dashboard (http://127.0.0.1:5173)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$Root\dashboard-ui'; Write-Host '--- Starting Dashboard UI (Port 5173) ---' -ForegroundColor Green; npm run dev"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  All services initiated in separate windows:" -ForegroundColor Green
Write-Host "   1. Target App:        http://127.0.0.1:5000" -ForegroundColor White
Write-Host "   2. Orchestrator API:  http://127.0.0.1:8000 (Swagger: /docs)" -ForegroundColor White
Write-Host "   3. React Governance:  http://127.0.0.1:5173" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Cyan
