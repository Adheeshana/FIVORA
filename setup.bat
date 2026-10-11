@echo off
title FIVORA App Setup

echo ===================================================
echo Welcome to FIVORA - Fabric Inspection System!
echo ===================================================
echo.

echo [1/3] Checking if Python is installed...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Python is not installed or not added to PATH!
    echo Please install Python (3.9 - 3.11) and make sure to tick "Add Python to PATH" during installation.
    echo.
    pause
    exit /b
)

if not exist venv (
    echo [2/3] Creating a secure Virtual Environment...
    python -m venv venv
)

echo Activating environment...
call venv\Scripts\activate

echo [3/3] Installing necessary AI Models and Libraries...
echo (This may take 10-15 minutes depending on your internet speed. Please wait...)
pip install -r requirements.txt --default-timeout=1000

echo.
echo ===================================================
echo Installation Complete! Starting FIVORA App...
echo ===================================================
python main_app.py

pause