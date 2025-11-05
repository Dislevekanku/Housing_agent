@echo off
REM Run all three agents in separate windows (Windows)

start "Data Scout Agent" cmd /k "cd /d %~dp0 && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 2 /nobreak > nul

start "Compliance Agent" cmd /k "cd /d %~dp0compliance-agent && python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload"
timeout /t 2 /nobreak > nul

start "Permit Liaison Agent" cmd /k "cd /d %~dp0permit-liaison-agent && python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload"

echo All agents started:
echo   Data Scout: http://localhost:8000
echo   Compliance: http://localhost:8001
echo   Permit Liaison: http://localhost:8002
echo.
echo Close the windows to stop the agents.
pause
