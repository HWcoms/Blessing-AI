@echo off
call ..\..\venv\Scripts\activate.bat

pyside6-rcc images.qrc -o images_rc.py
pause