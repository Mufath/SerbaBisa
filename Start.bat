@echo off
title SerbaBisa
cd /d "%~dp0"

:: Cek apakah venv sudah ada, jika belum arahkan ke setup
if not exist "venv\Scripts\python.exe" (
    echo =====================================================================
    echo [WARNING] Sistem belum siap. Menjalankan Setup untuk PERTAMA KALI.
    echo [INFO] Proses ini mengunduh library AI dan dependensi lainnya.
    echo [INFO] ESTIMASI WAKTU: 5 - 15 Menit - tergantung kecepatan internet.
    echo [INFO] Mohon bersabar dan JANGAN TUTUP jendela ini. Ini BUKAN error.
    echo =====================================================================
    echo.
    call Setup.bat
)

echo.
echo   ============================================================
echo      SerbaBisa sedang berjalan di http://localhost:5000
echo      Jendela aplikasi akan terbuka otomatis.
echo      Biarkan jendela ini terbuka selama aplikasi dipakai!
echo   ============================================================
echo.

:: Membuka browser otomatis (Dinonaktifkan karena menggunakan PyWebView)
:: start "" cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:5000"

:: Jalankan aplikasi
"venv\Scripts\python.exe" app.py

pause
