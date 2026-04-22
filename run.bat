@echo off
setlocal

:: Mengarahkan ke folder tempat file bat ini berada
cd /d "%~dp0"

:: Cek apakah Python terinstal di Windows
where python >nul 2>nul
if errorlevel 1 (
    echo.
    echo   Python tidak ditemukan! Silakan instal Python 3.10 atau yang lebih baru.
    echo   Pastikan centang "Add Python to PATH" saat instalasi.
    echo.
    pause
    exit /b 1
)

:: Cek folder venv (disesuaikan dengan folder kamu: venv tanpa titik)
if not exist "venv\Scripts\python.exe" (
    echo.
    echo   Memulai setup pertama kali: Membuat virtual environment...
    echo   (Ini hanya sekali dan membutuhkan koneksi internet)
    echo.
    python -m venv venv
    if errorlevel 1 (
        echo.
        echo   Gagal membuat virtual environment.
        pause
        exit /b 1
    )
)

:: Mengaktifkan virtual environment
call "venv\Scripts\activate.bat"

echo.
echo   Sedang mengecek library (dependencies)...
:: Menginstal library yang kurang, termasuk rembg[cpu] dan Flask
pip install --quiet --disable-pip-version-check -r requirements.txt
pip install --quiet --disable-pip-version-check "rembg[cpu]"

if errorlevel 1 (
    echo.
    echo   Gagal menginstal library. Cek koneksi internet dan coba lagi.
    pause
    exit /b 1
)

echo.
echo   ============================================================
echo      SerbaBisa TOOLS sedang berjalan di http://localhost:5000
echo      Browser kamu akan terbuka otomatis dalam sekejap.
echo      Tutup jendela ini untuk mematikan server.
echo   ============================================================
echo.

:: Membuka browser otomatis ke alamat localhost
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:5000"

:: Menjalankan aplikasi utama
python app.py

pause