@echo off
setlocal
cd /d "%~dp0"

py -3.14 --version >nul 2>&1
if errorlevel 1 (
    echo Python 3.14 was not found.
    echo Install Python 3.14 from https://www.python.org/downloads/ and run this file again.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating a Python 3.14 virtual environment...
    py -3.14 -m venv .venv
)

echo Installing or updating application libraries...
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt

echo Starting the Streamlit app at http://localhost:8501
.venv\Scripts\python.exe -m streamlit run app.py
endlocal
