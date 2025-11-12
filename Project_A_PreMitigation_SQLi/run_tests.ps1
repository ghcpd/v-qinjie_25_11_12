$PROJECT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Definition
python -m venv "$PROJECT_DIR\.venv";
& "$PROJECT_DIR\.venv\Scripts\Activate.ps1";
python -m pip install -r "$PROJECT_DIR\requirements.txt";
$REPEAT = $args[0] -as [int]
if (-not $REPEAT) { $REPEAT = 1 }
$DB_SIZE = $args[1] -as [int]
if (-not $DB_SIZE) { $DB_SIZE = 4 }
$env:REPEAT = $REPEAT
$env:DB_SIZE = $DB_SIZE
python "$PROJECT_DIR\setup_db.py";
python "$PROJECT_DIR\tests\test_pre_vuln.py";
Write-Output "Results written to $PROJECT_DIR\results\results_pre.json";
