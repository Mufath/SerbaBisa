@echo off
title SerbaBisa
cd /d "%~dp0"

:: Cek apakah venv sudah ada, jika belum arahkan ke setup
if not exist "venv\Scripts\python.exe" (
    echo [WARNING] Sistem belum siap. Menjalankan Setup dulu...
    echo.
    call Setup.bat
)

echo.
echo   ============================================================
echo      SerbaBisa sedang berjalan di http://localhost:5000
echo      Browser kamu akan terbuka otomatis.
echo      JANGAN TUTUP jendela ini selama aplikasi dipakai!
echo   ============================================================
echo.

:: Membuka browser otomatis
start "" cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:5000"

:: Jalankan aplikasi
"venv\Scripts\python.exe" app.py

pause
