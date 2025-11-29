@echo off
echo ========================================
echo LLM Analysis Quiz - Quick Start
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Check if .env exists
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Creating .env from .env.example...
    copy .env.example .env
    echo.
    echo Please edit .env file with your credentials before running the server.
    echo.
    pause
    exit /b 1
)

REM Check if requirements are installed
echo Checking dependencies...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo.
    echo Installing Playwright browsers...
    playwright install chromium
    echo.
)

REM Create directories
if not exist "downloads\" mkdir downloads
if not exist "temp\" mkdir temp
if not exist "logs\" mkdir logs

REM Start the application
echo Starting LLM Analysis Quiz API...
echo.
echo Server will start on http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
python app.py
