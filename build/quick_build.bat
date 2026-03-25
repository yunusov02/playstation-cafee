@echo off
echo ========================================
echo PlayStation Cafe Manager - Quick Build
echo ========================================
echo.

cd /d "%~dp0\.."

echo Cleaning previous builds...
if exist dist rmdir /s /q dist
if exist build\build rmdir /s /q build\build
if exist build\*.spec del /q build\*.spec

echo.
echo Building executable...
python build\build.py

echo.
echo Done! Check the 'dist' folder.
pause