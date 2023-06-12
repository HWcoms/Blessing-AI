@echo off
cd..
cd..
call venv\Scripts\activate.bat


cd src\PyDracula
pyside6-rcc resources.qrc -o dracula_modules\resources_rc.py
pause