$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $here
pip install -r requirements.txt
python -m playwright install
param([int]$repeat = 1, [string]$browser = "chromium", [string]$viewport = "1024x768")
python tests/test_pre_ui.py --repeat $repeat --browser $browser --viewport $viewport
Pop-Location
Write-Host "Results written to results/results_pre.json"
