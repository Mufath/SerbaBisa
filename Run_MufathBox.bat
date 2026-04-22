@echo off
title SerbaBisa
echo ========================================================
echo               Menjalankan SerbaBisa...
echo ========================================================
echo.
echo Mohon JANGAN TUTUP jendela hitam ini selama Anda memakai aplikasi!
echo Jendela browser akan otomatis terbuka...
echo.

cd /d "%~dp0"

:: Cek apakah venv ada
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Waduh, sistem inti belum siap!
    echo Tolong klik file '1_Setup_SerbaBisa.bat' dulu ya buat instalasi awal.
    pause
    exit /b 1
)

:: Jalankan langsung pakai python dari dalam venv tanpa activate.bat (anti-error pindah folder)
"venv\Scripts\python.exe" app.py
pause
