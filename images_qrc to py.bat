@echo off
call venv\Scripts\activate.bat
cd src\modules
pyside6-rcc images.qrc -o images_rc.py

cd ..
cd PyDracula
pyside6-rcc resources.qrc -o dracula_modules\resources_rc.py
pause