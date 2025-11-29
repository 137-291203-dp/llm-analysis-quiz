@echo off
echo ========================================
echo LLM Analysis Quiz - Local Testing
echo ========================================
echo.

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    echo.
)

REM Check if .env exists
if not exist ".env" (
    echo ❌ .env file not found!
    echo Please create .env file with your configuration.
    echo See AIPIPE_SETUP.md for instructions.
    pause
    exit /b 1
)

REM Install dependencies if needed
echo 🔧 Checking dependencies...
pip show flask-restx >nul 2>&1
if errorlevel 1 (
    echo Installing new dependencies...
    pip install flask-restx==1.3.0
    echo.
)

REM Install playwright browsers
echo 🎭 Installing Playwright browsers...
playwright install chromium

echo.
echo 🚀 Starting local development server...
echo.
echo Choose your mode:
echo 1. Standard API (basic)
echo 2. Swagger UI API (recommended)
echo.
set /p choice="Enter choice (1 or 2, default=2): "
if "%choice%"=="" set choice=2
if "%choice%"=="1" set choice=1

if "%choice%"=="2" (
    echo.
    echo 📚 Starting with Swagger UI...
    echo 🌐 API docs will be at: http://localhost:5000/docs/
    echo 🔗 API endpoints at: http://localhost:5000/api/v1/
    echo.
    echo Opening browser in 3 seconds...
    timeout /t 3 /nobreak >nul
    start http://localhost:5000/docs/
    python app_with_swagger.py
) else (
    echo.
    echo 📡 Starting standard API...
    echo 🌐 Server will be at: http://localhost:5000/
    echo.
    python app.py
)

pause
