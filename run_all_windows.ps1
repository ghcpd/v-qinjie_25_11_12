Param(
  [int]$REPEAT = 1,
  [int]$DB_SIZE = 10
)

$ErrorActionPreference = 'Stop'
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
Write-Output "Root: $ScriptRoot"

# Check Python availability
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python executable not found on PATH. Please install Python or add it to PATH."
    exit 1
}

# Export env vars for scripts (these scripts also accept args, keeping both for compatibility)
$env:REPEAT = $REPEAT
$env:DB_SIZE = $DB_SIZE

Write-Output "Running Project A (pre-mitigation) with REPEAT=$REPEAT DB_SIZE=$DB_SIZE"
Push-Location (Join-Path $ScriptRoot 'Project_A_PreMitigation_SQLi')
try {
    .\run_tests.ps1 $REPEAT $DB_SIZE
} catch {
    Write-Error "Project A tests failed: $_"
    Pop-Location
    exit 2
}
Pop-Location

Write-Output "Running Project B (post-mitigation) with REPEAT=$REPEAT DB_SIZE=$DB_SIZE"
Push-Location (Join-Path $ScriptRoot 'Project_B_PostMitigation_SQLi')
try {
    .\run_tests.ps1 $REPEAT $DB_SIZE
} catch {
    Write-Error "Project B tests failed: $_"
    Pop-Location
    exit 3
}
Pop-Location

# Generate compare report
Write-Output "Generating compare report..."
try {
    python "$ScriptRoot\generate_compare_report.py"
} catch {
    Write-Error "Failed to generate compare report: $_"
    exit 4
}

Write-Output "Done. Compare report at $ScriptRoot\compare_report.md"
exit 0
