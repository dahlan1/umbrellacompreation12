@echo off
title CyberCorp Game Launcher
color 0A
echo Launching CyberCorp Game...

:: Step 1: Check Python installation
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found! Install it first from python.org
    pause
    exit /b
)

:: Step 2: Launch Python backend
start "CyberCorp Backend" python cybercorp.py

:: Step 3: Wait for server to initialize
echo Waiting for server to start...
timeout /t 5 /nobreak >nul

:: Step 4: Open game in browser
start "" "game.html" || (
    echo [ERROR] Failed to open game.html
    echo Try opening it manually in your browser at:
    echo http://localhost:8000/game.html
)

echo Game should now be running!
pause