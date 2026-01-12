# Project B: Run tests script for patched application
# This script runs the full test cycle for Project B

$ErrorActionPreference = "Stop"

$ProjectDir = Get-Location
$SrcDir = "$ProjectDir\src"
$DataDir = "$ProjectDir\data"
$LogsDir = "$ProjectDir\logs"
$TestsDir = "$ProjectDir\tests"
$ResultsDir = "$ProjectDir\results"

Write-Host "========================================" -ForegroundColor Green
Write-Host "Project B: Post-Mitigation Tests" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Ensure directories exist
New-Item -ItemType Directory -Force -Path $DataDir | Out-Null
New-Item -ItemType Directory -Force -Path $LogsDir | Out-Null
New-Item -ItemType Directory -Force -Path $ResultsDir | Out-Null

# Initialize database
Write-Host "Initializing database..." -ForegroundColor Cyan
Push-Location $SrcDir
$PythonCmd = & python -c "import sys; print(sys.executable)"
& $PythonCmd init_db.py
Pop-Location

if ($LASTEXITCODE -ne 0) {
    Write-Host "Database initialization failed!" -ForegroundColor Red
    exit 1
}

# Start Flask app in background
Write-Host "Starting Flask application..." -ForegroundColor Cyan
Push-Location $SrcDir
$AppProcess = Start-Process -FilePath python -ArgumentList "app.py" -PassThru -RedirectStandardOutput "$LogsDir\app_output.log" -RedirectStandardError "$LogsDir\app_error.log"
$AppPID = $AppProcess.Id
Write-Host "Flask app started with PID: $AppPID" -ForegroundColor Green
Pop-Location

# Wait for app to start
Start-Sleep -Seconds 3

# Run tests
Write-Host "Running tests..." -ForegroundColor Cyan
Push-Location $TestsDir
& python test_post_vuln.py
$TestResult = $LASTEXITCODE
Pop-Location

# Kill Flask app
Write-Host "Stopping Flask application..." -ForegroundColor Cyan
try {
    Stop-Process -Id $AppPID -Force -ErrorAction SilentlyContinue
    Write-Host "Flask app stopped" -ForegroundColor Green
} catch {
    Write-Host "Could not stop Flask app" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Test Run Completed" -ForegroundColor Green
Write-Host "Results: $ResultsDir\results_post.json" -ForegroundColor Green
Write-Host "Logs: $LogsDir" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

exit $TestResult
