@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
title TW Lottery AI Predictor Launcher

echo ==================================================
echo       TW Lottery AI Predictor (Portable Version)
echo ==================================================
echo.

REM 1. Check if Python is installed on user machine
echo [1/3] Checking Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Python was not found on your system!
    echo Automatically opening the Python download page...
    echo Please install Python 3.10 or newer.
    echo.
    echo *IMPORTANT*: Make sure to check "Add Python to PATH" during installation!
    echo.
    timeout /t 5
    start https://www.python.org/downloads/
    pause
    exit
)

REM 2. Verify and setup Python virtual environment and dependencies
echo [2/3] Initializing AI engine environment...
if not exist "backend\.venv" (
    echo Creating Python virtual environment (this might take a few minutes for the first time)...
    python -m venv backend\.venv
)

echo Checking and installing required libraries (Pandas, TensorFlow, etc.)...
backend\.venv\Scripts\pip.exe install -r backend\requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies. Please check your network connection and try again.
    pause
    exit
)

REM 3. Start backend application (main.py will automatically launch default browser)
echo [3/3] Launching AI engine...
cd backend
.venv\Scripts\python.exe main.py
