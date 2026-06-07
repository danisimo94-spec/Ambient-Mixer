@echo off
cd /d "%~dp0"

where pythonw.exe >nul 2>nul
if not errorlevel 1 (
    start "" pythonw.exe "%~dp0main.py"
    exit /b
)

where pyw.exe >nul 2>nul
if not errorlevel 1 (
    start "" pyw.exe "%~dp0main.py"
    exit /b
)

python "%~dp0main.py"
