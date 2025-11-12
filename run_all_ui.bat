@echo off
REM Windows batch script to run the complete UI security test suite
REM One-command execution for all tests and report generation

echo.
echo ========================================================================
echo UI Security Vulnerability Detection and Mitigation - Test Suite
echo ========================================================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    exit /b 1
)

REM Run the main test orchestrator
echo Running automated security tests...
echo.

python run_all_ui.py

if errorlevel 1 (
    echo.
    echo ERROR: Tests failed
    exit /b 1
)

echo.
echo ========================================================================
echo Tests completed successfully!
echo ========================================================================
echo.
echo Generated report: compare_ui_security_report.md
echo Pre-mitigation results: Project_A_PreMitigation_UI\results\results_pre.json
echo Post-mitigation results: Project_B_PostMitigation_UI\results\results_post.json
echo.
echo View the report:
echo   - type compare_ui_security_report.md
echo   - or open it in your text editor
echo.
