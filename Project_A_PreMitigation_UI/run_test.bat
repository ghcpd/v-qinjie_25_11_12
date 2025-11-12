@echo off
REM Windows script to run Project A (Pre-Mitigation) tests
REM Usage: run_test.bat [repeat_count]

echo.
echo ========================================================================
echo Project A - Pre-Mitigation UI Security Tests
echo ========================================================================
echo.

cd /d "%~dp0Project_A_PreMitigation_UI" || exit /b 1

REM Install dependencies
echo Installing dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    exit /b 1
)

echo.
echo Starting vulnerable Flask application on http://127.0.0.1:5000
echo Press Ctrl+C to stop the server
echo.

REM Start Flask app in a new window
start "Project A Server" python src\app.py

REM Wait for server to start
timeout /t 3 /nobreak

REM Run tests
echo.
echo Running vulnerability detection tests...
echo.

python tests\test_pre_ui.py

if errorlevel 1 (
    echo Tests completed with errors
) else (
    echo Tests completed successfully
)

echo.
echo Results saved to: results\results_pre.json
echo Logs saved to: logs\test_pre_ui.log
echo.
