@echo off
REM run_all.bat - wrapper to run run_all_windows.ps1 with default args
REM Usage: run_all.bat [REPEAT] [DB_SIZE] (both optional)
setlocal enabledelayedexpansion
set REPEAT=%1
set DB_SIZE=%2
if "%REPEAT%"=="" set REPEAT=1
if "%DB_SIZE%"=="" set DB_SIZE=10

REM Resolve script directory
set SCRIPT_DIR=%~dp0
PowerShell.exe -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%run_all_windows.ps1" %REPEAT% %DB_SIZE%
endlocal
