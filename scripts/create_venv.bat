@echo off
setlocal enabledelayedexpansion

echo Creating Python virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing required packages...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo Virtual environment setup complete.
echo To activate the environment, run: venv\Scripts\activate.bat

pause