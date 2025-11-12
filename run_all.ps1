$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Definition
Write-Output "Running Project A tests (pre-mitigation)"
$REPEAT = $args[0]
if (-not $REPEAT) { $REPEAT = 1 }
$DB_SIZE = $args[1]
if (-not $DB_SIZE) { $DB_SIZE = 10 }
Push-Location "$ROOT\Project_A_PreMitigation_SQLi"
& .\run_tests.ps1 $REPEAT $DB_SIZE
Pop-Location

Write-Output "Running Project B tests (post-mitigation)"
Push-Location "$ROOT\Project_B_PostMitigation_SQLi"
& .\run_tests.ps1 $REPEAT $DB_SIZE
Pop-Location

python "$ROOT\generate_compare_report.py"
Write-Output "Compare report at $ROOT\compare_report.md"
