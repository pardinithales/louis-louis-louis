@echo off
TITLE LouiS Startup Script

ECHO ==================================================
ECHO              Starting LouiS Application
ECHO ==================================================
ECHO.

ECHO Starting Backend Server on http://localhost:8000
start "LouiS Backend" cmd /k "uvicorn backend.main:app --host 0.0.0.0 --port 8000"

ECHO Starting Frontend Server on http://localhost:8080
start "LouiS Frontend" cmd /k "python -m http.server 8080 --directory frontend"

ECHO.
ECHO Servers are launching in separate command windows.
ECHO.
ECHO To stop the application, simply close the two new command windows that opened.
ECHO.

pause 