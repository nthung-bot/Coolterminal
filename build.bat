@echo off
setlocal
title CoolTerminal Build

echo.
echo  ====================================================
echo    CoolTerminal v1.0  Build Script
echo  ====================================================
echo.

:: ---- Verify Python ----
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Python not found. Install from https://python.org
    pause & exit /b 1
)

:: ---- Install build tools ----
echo  [1/5] Installing build dependencies...
pip install pyinstaller psutil --quiet
if %errorlevel% neq 0 ( echo  [ERROR] pip failed. & pause & exit /b 1 )
echo         Done.

:: ---- Clean ----
if exist dist       rmdir /s /q dist
if exist build      rmdir /s /q build
if exist dist_tools rmdir /s /q dist_tools
mkdir dist_tools

:: ---- Build coolterm.exe ----
echo  [2/5] Building coolterm.exe ...
python -m PyInstaller ^
    --onefile ^
    --name coolterm ^
    --console ^
    --distpath dist_tools ^
    --add-data "coolterm_pkg;coolterm_pkg" ^
    --hidden-import psutil ^
    coolterm.py
if %errorlevel% neq 0 ( echo  [ERROR] coolterm build failed. & pause & exit /b 1 )
echo         Done.

:: ---- Build terconfig.exe ----
echo  [3/5] Building terconfig.exe ...
python -m PyInstaller ^
    --onefile ^
    --name terconfig ^
    --console ^
    --distpath dist_tools ^
    --add-data "coolterm_pkg;coolterm_pkg" ^
    --hidden-import psutil ^
    terconfig.py
if %errorlevel% neq 0 ( echo  [ERROR] terconfig build failed. & pause & exit /b 1 )
echo         Done.

:: ---- Also copy to dist\ for standalone use ----
echo  [4/5] Copying standalone EXEs to dist\ ...
mkdir dist
copy dist_tools\coolterm.exe  dist\coolterm.exe  >nul
copy dist_tools\terconfig.exe dist\terconfig.exe >nul
echo         Done.

:: ---- Build CoolTerminal-Setup.exe ----
echo  [5/5] Building CoolTerminal-Setup.exe (self-contained installer) ...
python -m PyInstaller ^
    --onefile ^
    --name CoolTerminal-Setup ^
    --console ^
    --add-data "dist_tools\coolterm.exe;." ^
    --add-data "dist_tools\terconfig.exe;." ^
    --hidden-import winreg ^
    install.py
if %errorlevel% neq 0 ( echo  [ERROR] installer build failed. & pause & exit /b 1 )
echo         Done.

echo.
echo  ====================================================
echo    Build complete!
echo.
echo    dist\CoolTerminal-Setup.exe  -- Installer (share this)
echo    dist\coolterm.exe            -- Standalone display tool
echo    dist\terconfig.exe           -- Config tool
echo  ====================================================
echo.

:: ---- Optional: Inno Setup ----
set ISCC="%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if exist %ISCC% (
    echo  Inno Setup found - building professional installer...
    %ISCC% setup.iss
    echo  Output\CoolTerminal-Installer.exe ready.
) else (
    echo  [INFO] Inno Setup not installed - PyInstaller installer is used.
    echo         https://jrsoftware.org/isdl.php for the traditional .exe wizard.
)

pause
