@echo off
call ..\scripts\venv\Scripts\activate.bat
cd ..
set PYTHONPATH=%CD%
python src\main.py
pause