@echo off
title Perbaikan Error Rembg & Onnxruntime
cd /d "%~dp0"

echo ========================================================
echo        Memperbaiki Instalasi Rembg dan Onnxruntime
echo ========================================================
echo.

if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Folder venv belum ada. Jalankan Setup.bat dulu!
    pause
    exit /b 1
)

echo [INFO] Mengaktifkan Virtual Environment...
call venv\Scripts\activate.bat

echo [INFO] Memperbarui pip ke versi terbaru...
python -m pip install --upgrade pip

echo [INFO] Memaksa instalasi ulang onnxruntime dan rembg...
pip install --force-reinstall --no-cache-dir onnxruntime rembg

echo.
echo ========================================================
echo Selesai!
echo Jika ada teks berwarna MERAH di atas, tolong screenshot 
echo dan kirimkan pesannya untuk dicek.
echo Jika tidak ada yang merah, silakan jalankan Start.bat!
echo ========================================================
pause
