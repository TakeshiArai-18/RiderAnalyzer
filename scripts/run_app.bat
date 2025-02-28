@echo off
call ..\venv\Scripts\activate.bat
cd ..
set PYTHONPATH=%CD%
python src\main.py
pause