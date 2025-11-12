Set-StrictMode -Version Latest
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Push-Location $scriptDir
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install
python -u tests/test_pre_ui.py --repeat 1
Pop-Location
Write-Host "Pre-mitigation tests complete; see results_pre.json and results/ for artifacts" 
