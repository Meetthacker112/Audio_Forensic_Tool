@echo off
title Forensic Audio Analysis Tool
color 0A

echo.
echo ========================================
echo   FORENSIC AUDIO ANALYSIS TOOL v1.0
echo ========================================
echo.
echo Starting the forensic audio analysis application...
echo Please wait while the system initializes...
echo.

REM Change to application directory
cd /d "%~dp0"

REM Activate virtual environment and run application
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" main.py
) else (
    python main.py
)

if errorlevel 1 (
    echo.
    echo ========================================
    echo   APPLICATION ERROR
    echo ========================================
    echo An error occurred while running the application.
    echo Please check:
    echo  1. Python is installed
    echo  2. All dependencies are installed
    echo  3. Check logs folder for details
    echo.
    echo Press any key to exit...
    pause >nul
)
