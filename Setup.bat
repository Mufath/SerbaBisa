@echo off
title Instalasi SerbaBisa
cd /d "%~dp0"
echo ========================================================
echo               Setup Awal SerbaBisa
echo ========================================================
echo.

:: Cek Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Python belum terinstal di komputermu!
    echo [INFO] Mencoba mengunduh dan menginstal Python secara otomatis...
    winget install -e --id Python.Python.3.11 --accept-package-agreements --accept-source-agreements
    if %errorlevel% neq 0 (
        echo [ERROR] Gagal menginstal Python otomatis!
        echo 1. Download manual Python 3.10+ dari: https://www.python.org/downloads/
        echo 2. PENTING: Ceklis "Add Python to PATH" saat instalasi.
        echo.
        pause
        exit /b 1
    )
    echo [INFO] Python berhasil diinstal! 
    echo [INFO] Silakan tutup jendela ini, buka CMD/terminal baru, dan jalankan Setup.bat lagi.
    pause
    exit /b 0
)

echo [INFO] Menyiapkan Virtual Environment (venv)...
if not exist "venv" (
    python -m venv venv
)

echo [INFO] Mengunduh library yang dibutuhkan...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo [INFO] Menyiapkan FFmpeg (Opsional untuk Audio/Video)...
powershell -ExecutionPolicy Bypass -File install_ffmpeg.ps1

echo.
echo ========================================================
echo Setup Selesai! 
echo Silakan jalankan 'Start.bat' untuk membuka aplikasi.
echo ========================================================
pause
