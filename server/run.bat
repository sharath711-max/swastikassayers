@echo off
echo ========================================
echo    Swastik Assayers Server
echo ========================================
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Starting server on http://localhost:5000
echo API Documentation: http://localhost:5000/docs
echo.
cd /d %~dp0
uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
pause