# Run Project A
Push-Location Project_A_PreMitigation_UI
./run_ui_tests.ps1
Pop-Location
Copy-Item -Path Project_A_PreMitigation_UI\results\results_pre.json -Destination results\results_pre.json -Force -ErrorAction SilentlyContinue

# Run Project B
Push-Location Project_B_PostMitigation_UI
./run_ui_tests.ps1
Pop-Location
Copy-Item -Path Project_B_PostMitigation_UI\results\results_post.json -Destination results\results_post.json -Force -ErrorAction SilentlyContinue

# Generate comparison report
python compare_results.py
Write-Output "All tests executed and report generated: compare_ui_security_report.md"
