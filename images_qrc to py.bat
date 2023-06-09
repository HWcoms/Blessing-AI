@echo off
call venv\Scripts\activate.bat
cd src\modules
pyside6-rcc images.qrc -o images_rc.py
pause