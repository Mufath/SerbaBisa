$ErrorActionPreference = "Stop"
$BinDir = Join-Path $PSScriptRoot "bin"
if (!(Test-Path $BinDir)) {
    New-Item -ItemType Directory -Path $BinDir | Out-Null
}

$ZipPath = Join-Path $PSScriptRoot "ffmpeg.zip"
$ExtractPath = Join-Path $PSScriptRoot "ffmpeg_extracted"

if (Test-Path (Join-Path $BinDir "ffmpeg.exe")) {
    Write-Host "FFmpeg sudah terinstal."
    exit 0
}

Write-Host "Mengunduh FFmpeg (~35MB)..."
Invoke-WebRequest -Uri "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip" -OutFile $ZipPath

Write-Host "Mengekstrak file..."
Expand-Archive -Path $ZipPath -DestinationPath $ExtractPath -Force

Write-Host "Menyalin file inti..."
Get-ChildItem -Path "$ExtractPath\*\bin\*.exe" | Copy-Item -Destination $BinDir -Force

Write-Host "Membersihkan file sementara..."
Remove-Item $ZipPath -Force
Remove-Item $ExtractPath -Recurse -Force

Write-Host "Instalasi FFmpeg Selesai!"
