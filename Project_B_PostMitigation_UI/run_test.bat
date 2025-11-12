@echo off
REM Windows script to run Project B (Post-Mitigation) tests
REM Usage: run_test.bat

echo.
echo ========================================================================
echo Project B - Post-Mitigation UI Security Tests
echo ========================================================================
echo.

cd /d "%~dp0Project_B_PostMitigation_UI" || exit /b 1

REM Install dependencies
echo Installing dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    exit /b 1
)

echo.
echo Starting secure Flask application on http://127.0.0.1:5001
echo Press Ctrl+C to stop the server
echo.

REM Start Flask app in a new window
start "Project B Server" python src\app.py

REM Wait for server to start
timeout /t 3 /nobreak

REM Run tests
echo.
echo Running security validation tests...
echo.

python tests\test_post_ui.py

if errorlevel 1 (
    echo Tests completed with errors
) else (
    echo Tests completed successfully
)

echo.
echo Results saved to: results\results_post.json
echo Logs saved to: logs\test_post_ui.log
echo.
