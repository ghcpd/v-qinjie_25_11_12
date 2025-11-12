$current = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $current
# Pre
Set-ExecutionPolicy Bypass -Scope Process -Force
cd Project_A_PreMitigation_UI
./run_ui_tests.ps1
cd ..
# Post
cd Project_B_PostMitigation_UI
./run_ui_tests.ps1
cd ..
# Compare
python shared_artifacts/generate_compare_report.py
Pop-Location
Write-Host "Comparison report at shared_artifacts/compare_ui_security_report.md"
