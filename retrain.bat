@echo off
cd /d "%~dp0"
title TW Lottery - Retrain LSTM Models

echo ==================================================
echo   TW Lottery AI - LSTM Model Retraining Tool
echo ==================================================
echo.
echo NOTE: This process may take several minutes depending on your CPU.
echo Once completed, new models will overwrite the old ones.
echo.
pause

echo.
echo Starting training script...
cd backend
if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe train.py
) else (
    echo [WARNING] .venv\Scripts\python.exe not found. Using system default Python.
    python train.py
)

echo.
echo ==================================================
echo   Training Complete! You can now close this window.
echo ==================================================
pause
exit
