Set-StrictMode -Version Latest
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Push-Location $scriptDir
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install
python -u tests/test_post_ui.py --repeat 1
Pop-Location
Write-Host "Post-mitigation tests complete; see results_post.json and results/ for artifacts" 
