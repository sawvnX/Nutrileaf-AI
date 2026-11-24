@echo off
setlocal
cd /d "%~dp0"
title NutriLeaf AI - Final Edition
 echo =====================================================
echo          NUTRILEAF AI - FINAL COMPLETE EDITION
echo =====================================================
where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found.
  echo Install Python 3.11 or 3.12 and tick "Add Python to PATH".
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
  echo [1/3] Creating isolated Python environment...
  python -m venv .venv
  if errorlevel 1 goto error
)
echo [2/3] Installing application dependencies...
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check --upgrade pip
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 goto error
echo [3/3] Starting local web server...
echo Keep this window open while using NutriLeaf AI.
start "" /min cmd /c "timeout /t 3 /nobreak >nul & start http://127.0.0.1:8000"
".venv\Scripts\python.exe" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
pause
exit /b 0
:error
echo.
echo Setup could not finish. Check internet access and Python 3.11/3.12.
pause
exit /b 1
