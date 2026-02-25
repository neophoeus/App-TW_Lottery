@echo off
cd /d "%~dp0"
title App-TW_Lottery Launcher

echo ==================================================
echo       Starting App-TW_Lottery System
echo ==================================================

echo [1/3] Launching Backend API...
start "TW_Lottery_Backend" cmd /k "cd /d "%~dp0backend" && venv\Scripts\activate && python main.py"

echo [2/3] Launching Frontend UI...
start "TW_Lottery_Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo [3/3] Opening Browser...
timeout /t 6 /nobreak >nul
start http://localhost:3000

echo.
echo ==================================================
echo   Done! Close the terminal windows to stop.
echo ==================================================
timeout /t 3 >nul
exit
