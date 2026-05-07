@echo off
:: Berpindah ke root direktori (asumsi script ada di folder scripts/)
cd /d "%~dp0\.."

title SerbaBisa Updater

echo ===========================================
echo       SERBABISA - UPDATE MANAGER
echo ===========================================
echo.

:: Tunggu sebentar agar proses aplikasi benar-benar tertutup
timeout /t 3 /nobreak > nul

echo [1/3] Menarik kode terbaru dari GitHub...
git pull
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Gagal menarik data dari GitHub. 
    echo Pastikan Anda memiliki koneksi internet dan Git terinstal.
    echo Jika ada perubahan lokal yang konflik, silakan commit atau stash dulu.
    echo.
    pause
    exit
)

echo.
echo [2/3] Memperbarui dependensi (jika ada)...
call venv\Scripts\python.exe -m pip install -r requirements.txt

echo.
echo [3/3] Update selesai! Memulai ulang aplikasi...
timeout /t 2 /nobreak > nul

:: Menjalankan kembali aplikasi
start "" "SerbaBisa.bat"
exit
