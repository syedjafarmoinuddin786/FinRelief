@echo off
echo ===================================================
echo Starting FinRelief Application...
echo ===================================================

echo [1/2] Starting FastAPI Backend on Port 8000...
start "FinRelief Backend" cmd /k "cd backend && .venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000"

echo [2/2] Starting Frontend Web Server on Port 3000...
start "FinRelief Frontend" cmd /k "cd frontend && ..\backend\.venv\Scripts\python.exe -m http.server 3000"

echo.
echo Servers are starting up in the background! 
echo Opening your web browser to http://localhost:3000 in 3 seconds...
timeout /t 3 /nobreak >nul

start http://localhost:3000

echo.
echo Application is running! You should see two new black command prompt windows open (these are your servers).
echo Leave those windows open while you use the app. To stop the app, simply close those two windows.
echo.
pause
