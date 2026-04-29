# 🛠️ SerbaBisa

**SerbaBisa** adalah toolkit serbaguna berbasis Desktop (Native PyWebView) untuk membantu berbagai tugas digital Anda, seperti konversi file, manipulasi gambar, pengolahan teks, dan banyak lagi secara lokal tanpa upload data ke internet.

---

## Cara Mendapatkan Kode

Sebelum memulai, pastikan Anda sudah memiliki folder project ini di komputer Anda. Ada dua cara:

### A. Bagi Pengguna Umum (Rekomendasi)
1.  Klik tombol hijau **"Code"** di bagian atas halaman GitHub ini.
2.  Pilih **"Download ZIP"**.
3.  Ekstrak (unzip) file yang sudah didownload ke folder pilihan Anda (misalnya di `D:\SerbaBisa`).

### B. Bagi Developer (Menggunakan Git)
Buka Terminal/CMD, lalu jalankan perintah:
```bash
git clone https://github.com/Mufath/SerbaBisa.git
cd SerbaBisa
```

---

## Panduan Instalasi & Penggunaan

Ikuti langkah-langkah di bawah ini untuk menyiapkan aplikasi di komputer Anda (Windows).

### 1. Instalasi Awal (Hanya Sekali)
Double-klik file **`Setup.bat`**.
*   Skrip ini akan mengecek apakah Python sudah terinstal.
*   Skrip akan mengunduh semua library yang dibutuhkan (membutuhkan koneksi internet).
*   Skrip akan mencoba memasang FFmpeg untuk pengolahan audio/video.

### 2. Membuat Shortcut (Opsional)
Double-klik file **`Shortcut.bat`**.
*   Ini akan membuat ikon **SerbaBisa** di layar Desktop Anda agar aplikasi mudah dibuka kapan saja.

### 3. Menjalankan Aplikasi
Double-klik file **`Start.bat`** (atau pakai shortcut di Desktop).
*   Jendela aplikasi SerbaBisa (Desktop App) akan terbuka otomatis.
*   Anda bisa mengubah profil, tema gelap/terang, dan bahasa (Inggris/Indonesia) melalui menu Pengaturan. Pengaturan Anda akan disimpan secara permanen.

---

## Struktur File Utama

Berikut adalah penjelasan mengenai file-file penting di dalam folder ini:

### Skrip Peluncur (Launchers)
*   `Setup.bat`: Digunakan saat pertama kali install atau jika ada error library.
*   `Start.bat`: Cara utama menjalankan aplikasi.
*   `Shortcut.bat`: Membuat jalan pintas ke Desktop.

### Alat Bantu (Utilities)
*   `locales.py`: Sistem terjemahan dwibahasa (Inggris & Indonesia).
*   `config_manager.py`: Manajemen pengaturan aplikasi.
*   `history.py`: Mengelola riwayat aktivitas Anda di aplikasi.
*   `AddContextMenu.bat`: Skrip untuk menambahkan SerbaBisa ke menu klik kanan Windows.
*   `install_ffmpeg.ps1`: Skrip otomatis untuk memasang FFmpeg.

### Folder Inti
*   `/static`: Berisi file gambar, CSS, dan JavaScript untuk tampilan.
*   `/templates`: Berisi file HTML untuk setiap halaman fitur.
*   `/routes`: Logika utama untuk setiap fitur aplikasi.
*   `/venv`: Folder lingkungan Python (jangan dihapus agar aplikasi tetap jalan).

---

## Troubleshooting (Masalah Umum)

*   **Python tidak ditemukan:** Pastikan Anda sudah mengunduh Python dari [python.org](https://www.python.org/) dan mencentang **"Add Python to PATH"** saat instalasi.
*   **Gagal install library:** Pastikan koneksi internet stabil saat menjalankan `Setup.bat`.
*   **Video tidak bisa diproses:** Jalankan kembali `Setup.bat` untuk memastikan FFmpeg terpasang dengan benar.

---

*Dikembangkan dengan ❤️ untuk kemudahan produktivitas lokal yang aman.*
