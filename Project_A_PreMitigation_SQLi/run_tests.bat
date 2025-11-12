@echo off
REM Test execution script for Project A (Pre-Mitigation) - Windows version

setlocal

cd /d "%~dp0"

echo ==========================================
echo Project A - Pre-Mitigation SQLi Tests
echo ==========================================

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
python -m pip install -q --upgrade pip
python -m pip install -q -r requirements.txt

REM Create necessary directories
if not exist "logs" mkdir logs
if not exist "results" mkdir results
if not exist "data" mkdir data

REM Initialize database
echo Initializing database...
python data\init_db.py

REM Set environment variables
if "%REPEAT_COUNT%"=="" set REPEAT_COUNT=1
if "%DB_SIZE%"=="" set DB_SIZE=small

REM Run tests
echo Running vulnerability tests...
python tests\test_pre_vuln.py

echo.
echo ==========================================
echo Tests completed!
echo Results saved to: results\results_pre.json
echo ==========================================

deactivate

endlocal

