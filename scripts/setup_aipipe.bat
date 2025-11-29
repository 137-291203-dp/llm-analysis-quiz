@echo off
echo ========================================
echo AI Pipe Setup for LLM Analysis Quiz
echo ========================================
echo.

REM Check if .env exists
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
    echo.
)

echo Setting up AI Pipe (FREE option)...
echo.
echo Your AI Pipe token:
echo eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjI0ZHMyMDAwMTM3QGRzLnN0dWR5LmlpdG0uYWMuaW4ifQ.FT58rnxmrP86dlZ_nDaIwZHfXxhUrqyWfs99UbSEmNU
echo.

REM Create a temporary file with the configuration
echo STUDENT_EMAIL=24ds2000137@ds.study.iitm.ac.in> temp_config.txt
echo STUDENT_SECRET=your-secret-here>> temp_config.txt
echo.>> temp_config.txt
echo # AI Pipe (FREE option - recommended for students)>> temp_config.txt
echo AIPIPE_TOKEN=eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjI0ZHMyMDAwMTM3QGRzLnN0dWR5LmlpdG0uYWMuaW4ifQ.FT58rnxmrP86dlZ_nDaIwZHfXxhUrqyWfs99UbSEmNU>> temp_config.txt
echo.>> temp_config.txt
echo # OpenAI (Paid option - fallback)>> temp_config.txt
echo # OPENAI_API_KEY=your-openai-key>> temp_config.txt
echo.>> temp_config.txt
echo PORT=5000>> temp_config.txt

echo Configuration created in temp_config.txt
echo.
echo Please:
echo 1. Open .env file
echo 2. Replace with content from temp_config.txt
echo 3. Change STUDENT_SECRET to your own secret
echo 4. Save the file
echo.

pause

echo.
echo Testing configuration...
python -c "from config import Config; Config.validate(); print('✓ Configuration valid!')" 2>nul
if errorlevel 1 (
    echo ❌ Configuration has issues. Please check your .env file.
) else (
    echo ✅ Configuration looks good!
    echo.
    echo Next steps:
    echo 1. Run: python app.py
    echo 2. Test: python test_endpoint.py
)

echo.
echo Cleaning up...
del temp_config.txt

pause
