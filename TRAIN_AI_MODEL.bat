@echo off
setlocal
cd /d "%~dp0"
title NutriLeaf AI - Train AI Model
if not exist ".venv\Scripts\python.exe" (
  echo First run START_NUTRILEAF.bat once.
  pause
  exit /b 1
)
echo This step requires labelled images in ml\data_raw\CLASS_NAME folders.
echo See DATASET_GUIDE.md before continuing.
pause
".venv\Scripts\python.exe" -m pip install -r requirements-ml.txt
if errorlevel 1 goto error
".venv\Scripts\python.exe" ml\prepare_dataset.py
if errorlevel 1 goto error
".venv\Scripts\python.exe" ml\train.py
if errorlevel 1 goto error
echo.
echo Training and held-out evaluation finished.
echo Restart NutriLeaf AI to load the newly trained model.
pause
exit /b 0
:error
echo Training stopped. Read the error above and DATASET_GUIDE.md.
pause
exit /b 1
