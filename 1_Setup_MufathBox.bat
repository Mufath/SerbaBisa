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
    echo [ERROR] Waduh, Python belum terinstal di komputermu nih!
    echo.
    echo 1. Tolong download Python versi 3.10 atau yang lebih baru dari:
    echo    https://www.python.org/downloads/
    echo.
    echo 2. PENTING: Saat instalasi, jangan lupa Ceklis kotak yang tulisannya:
    echo    "Add Python to PATH" atau "Add python.exe to PATH" di paling bawah!
    echo.
    echo Kalo udah diinstall, buka lagi file ini ya!
    pause
    exit /b 1
)

echo [INFO] Menyiapkan folder Virtual Environment (venv)...
if not exist "venv" (
    python -m venv venv
) else (
    echo [INFO] venv sudah ada. Kalau error, hapus folder venv dan jalankan ulang file ini.
)

echo.
echo [INFO] Mengunduh komponen rahasia (butuh koneksi internet)...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo [INFO] Menyiapkan FFmpeg (Untuk pemutar Audio/Video)...
powershell -ExecutionPolicy Bypass -File install_ffmpeg.ps1

echo.
echo ========================================================
echo Mantap! Setup Selesai 100%%!
echo Sekarang silakan klik ganda '2_Buat_Shortcut_Desktop.bat'
echo supaya aplikasi ini gampang dibuka dari layar depanmu.
echo ========================================================
pause
