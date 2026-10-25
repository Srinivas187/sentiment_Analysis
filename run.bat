@echo off
title Product Review Sentiment Classification System
echo ============================================================
echo  Product Review Sentiment Classification System - Batch-8
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)
echo [OK] Python found

REM Install dependencies if needed
echo.
echo [*] Checking/Installing Python dependencies...
pip install flask flask-cors mysql-connector-python bcrypt PyJWT python-dotenv numpy pandas scikit-learn >nul 2>&1
echo [OK] Python dependencies ready

REM Try to initialize the database (non-fatal if MySQL is not running)
echo.
echo [*] Attempting database initialization...
python database/init_db.py 2>nul
if errorlevel 1 (
    echo [WARN] Database initialization failed - MySQL may not be running.
    echo        The backend will start with limited database functionality.
) else (
    echo [OK] Database initialized
)

REM Start Flask backend in a new window
echo.
echo [*] Starting Flask backend server (http://localhost:5000)...
start "Flask Backend" cmd /c "python backend/app.py & pause"

REM Wait for backend to start
timeout /t 3 /nobreak >nul

REM Start React frontend
echo [*] Starting React frontend (http://localhost:3000)...
cd frontend
start "React Frontend" cmd /c "npm start & pause"
cd ..

echo.
echo ============================================================
echo  Both servers are starting!
echo   Backend  : http://localhost:5000
echo   Frontend : http://localhost:3000
echo.
echo  Close the server windows to stop.
echo ============================================================
pause
