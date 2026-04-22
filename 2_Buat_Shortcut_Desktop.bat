@echo off
title Buat Shortcut SerbaBisa
cd /d "%~dp0"
echo ========================================================
echo         Membuat Shortcut SerbaBisa di Desktop...
echo ========================================================
echo.

set SCRIPT_NAME=Run_SerbaBisa.bat
set TARGET_PATH=%~dp0%SCRIPT_NAME%
set ICON_PATH=%~dp0static\favicon.ico
set SHORTCUT_PATH=%USERPROFILE%\Desktop\SerbaBisa.lnk

:: Hapus shortcut lama jika ada
if exist "%SHORTCUT_PATH%" del "%SHORTCUT_PATH%"

:: Buat script VBS sementara
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%SHORTCUT_PATH%" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%TARGET_PATH%" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%~dp0" >> CreateShortcut.vbs
echo oLink.Description = "Buka SerbaBisa" >> CreateShortcut.vbs
echo oLink.IconLocation = "%ICON_PATH%" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs

:: Jalankan VBS
cscript /nologo CreateShortcut.vbs

:: Hapus VBS
del CreateShortcut.vbs

echo Berhasil! Coba cek layar Desktop Anda sekarang.
echo Ada ikon SerbaBisa baru di sana!
echo.
pause
