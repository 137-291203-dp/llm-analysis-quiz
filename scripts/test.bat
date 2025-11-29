@echo off
echo ========================================
echo LLM Analysis Quiz - Testing
echo ========================================
echo.

REM Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Run tests
echo Running endpoint tests...
echo.
python test_endpoint.py

echo.
pause
