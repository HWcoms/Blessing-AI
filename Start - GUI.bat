@echo off
call "%CD%\venv\Scripts\activate"

cd src/PyDracula
python main.py
pause