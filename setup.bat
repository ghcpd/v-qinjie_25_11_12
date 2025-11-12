@echo off
REM setup.bat - Windows CMD setup for this repository
REM This script will:
REM  - check Python is available
REM  - create .venv
REM  - activate venv and install dependencies

python -c "import sys, os; print(sys.executable)" >nul 2>&1
if errorlevel 1 (
    echo Python not installed or not in PATH. Install Python 3.8+ and rerun.
    exit /b 1
)

if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

call .venv\Scripts\activate.bat

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing requirements for Project A...
python -m pip install -r Project_A_PreMitigation_SQLi\requirements.txt || goto :error

echo Installing requirements for Project B...
python -m pip install -r Project_B_PostMitigation_SQLi\requirements.txt || goto :error

echo Setup completed. To activate venv in a new shell: .venv\Scripts\activate.bat
exit /b 0

:error

echo Failed to install some packages. See the errors above.
exit /b 2
