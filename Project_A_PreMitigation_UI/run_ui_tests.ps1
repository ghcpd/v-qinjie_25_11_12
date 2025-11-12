param([int]$repeat = 1, [string]$browser = 'chromium', [string]$viewport = '1280x720')
if (-Not (Test-Path .venv)) { python -m venv .venv }
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
python -m playwright install --with-deps

# Start server
mkdir logs -ErrorAction SilentlyContinue
mkdir results -ErrorAction SilentlyContinue
$proc = Start-Process -FilePath python -ArgumentList 'src\app.py' -PassThru
Write-Output "Server PID: $($proc.Id)"
Start-Sleep -Milliseconds 500

$env:BASE_URL = "http://localhost:5001"
python tests/test_pre_ui.py

# Stop server
Stop-Process -Id $proc.Id -Force
Write-Output "Tests finished. Results in results/"
