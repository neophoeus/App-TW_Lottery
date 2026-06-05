@echo off
cd /d "%~dp0"
title TW Lottery AI - Frontend Static Packager

echo ==================================================
echo       TW Lottery AI - Frontend Static Packager
echo ==================================================
echo.

REM 1. Run build in Next.js frontend directory
echo [1/3] Building frontend (Next.js Static Export)...
cd frontend
call npm run build
if errorlevel 1 (
    echo [ERROR] Frontend compilation failed. Please check Next.js config.
    pause
    exit
)
cd ..

REM 2. Refresh static folder in backend
echo [2/3] Cleaning up old static directory...
if exist "backend\static" (
    rd /s /q "backend\static"
)
mkdir "backend\static"

REM 3. Copy built files from frontend/out to backend/static
echo [3/3] Copying static web pages to backend server...
xcopy /e /y /i "frontend\out" "backend\static"
if errorlevel 1 (
    echo [ERROR] Failed to copy static assets.
    pause
    exit
)

REM 4. Copy required portable assets to Windows TEMP folder to avoid OneDrive file-locking conflicts
echo [4/5] Preparing clean distribution files in TEMP directory...
if exist "%TEMP%\TW_Lottery_Pack" (
    rd /s /q "%TEMP%\TW_Lottery_Pack"
)
mkdir "%TEMP%\TW_Lottery_Pack"
mkdir "%TEMP%\TW_Lottery_Pack\backend"

xcopy /e /y /i "backend\core" "%TEMP%\TW_Lottery_Pack\backend\core" >nul
xcopy /e /y /i "backend\data" "%TEMP%\TW_Lottery_Pack\backend\data" >nul
xcopy /e /y /i "backend\models" "%TEMP%\TW_Lottery_Pack\backend\models" >nul
xcopy /e /y /i "backend\static" "%TEMP%\TW_Lottery_Pack\backend\static" >nul
copy "backend\main.py" "%TEMP%\TW_Lottery_Pack\backend\" >nul
copy "backend\requirements.txt" "%TEMP%\TW_Lottery_Pack\backend\" >nul
copy "run.bat" "%TEMP%\TW_Lottery_Pack\" >nul
copy "README.md" "%TEMP%\TW_Lottery_Pack\" >nul

REM 5. Compress to ZIP package automatically for distribution
echo [5/5] Creating ZIP package (App-TW_Lottery_Portable.zip)...
if exist "App-TW_Lottery_Portable.zip" (
    del "App-TW_Lottery_Portable.zip"
)
powershell -Command "Compress-Archive -Path $env:TEMP/TW_Lottery_Pack/* -DestinationPath App-TW_Lottery_Portable.zip -Force"
if errorlevel 1 (
    echo [ERROR] Failed to create ZIP package.
    rd /s /q "%TEMP%\TW_Lottery_Pack"
    pause
    exit
)

REM Clean up temporary files in TEMP directory
rd /s /q "%TEMP%\TW_Lottery_Pack"

echo.
echo ==================================================
echo   Build Successful!
echo   Your portable installer ZIP is ready:
echo   - App-TW_Lottery_Portable.zip (Created in the root directory)
echo ==================================================
pause
