@echo off
title Tambah ke Menu Konteks
cd /d "%~dp0"
echo ========================================================
echo   Menambahkan "Buka SerbaBisa" ke Menu Klik Kanan...
echo ========================================================
echo.

:: Cek Administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Akses Ditolak!
    echo Silakan tutup jendela ini, lalu KLIK KANAN file AddContextMenu.bat
    echo dan pilih "Run as Administrator".
    echo.
    pause
    exit /b 1
)

set APP_PATH=%~dp0Start.bat
set ICON_PATH=%~dp0static\favicon.ico

:: Menambahkan ke context menu untuk klik file (*)
reg add "HKCR\*\shell\SerbaBisa" /ve /d "Buka dengan SerbaBisa" /f >nul
reg add "HKCR\*\shell\SerbaBisa" /v "Icon" /d "%ICON_PATH%" /f >nul
reg add "HKCR\*\shell\SerbaBisa\command" /ve /d "\"%APP_PATH%\"" /f >nul

:: Menambahkan ke context menu untuk klik kanan di ruang kosong (Directory\Background)
reg add "HKCR\Directory\Background\shell\SerbaBisa" /ve /d "Buka SerbaBisa" /f >nul
reg add "HKCR\Directory\Background\shell\SerbaBisa" /v "Icon" /d "%ICON_PATH%" /f >nul
reg add "HKCR\Directory\Background\shell\SerbaBisa\command" /ve /d "\"%APP_PATH%\"" /f >nul

echo [INFO] Registrasi berhasil! 
echo Coba klik kanan sebuah file atau klik kanan di ruang kosong folder.
echo.
pause
