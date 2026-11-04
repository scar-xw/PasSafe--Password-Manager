@echo off
REM Builds PasSafe.exe (run on Windows). Output: dist\PasSafe.exe
python -m pip install --upgrade customtkinter cryptography pyinstaller
python -m PyInstaller --onefile --windowed --name PasSafe --collect-all customtkinter app.py
echo.
echo Done. Your program is in the dist folder.
pause
