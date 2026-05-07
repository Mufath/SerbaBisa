# 🚀 Panduan Deployment Online (Render.com)

Aplikasi SerbaBisa sekarang sudah siap untuk dijalankan online menggunakan Docker. Berikut adalah langkah-langkah untuk mendeploynya ke **Render.com**.

## Langkah 1: Push Perubahan ke GitHub

Pastikan semua perubahan terbaru sudah di-push ke GitHub Anda:

```bash
git add .
git commit -m "Siapkan konfigurasi untuk deployment cloud"
git push origin cloud-deployment
```

## Langkah 2: Buat Akun di Render.com

1. Pergi ke [Render.com](https://render.com/) dan daftar menggunakan akun GitHub Anda.

## Langkah 3: Buat Web Service Baru

1. Klik tombol **"New +"** dan pilih **"Web Service"**.
2. Hubungkan repositori GitHub **SerbaBisa** Anda.
3. Render akan mendeteksi file `Dockerfile` secara otomatis.
4. **Penting:** Di bagian **Environment**, pastikan:
   - **Runtime:** `Docker`
   - **Region:** `Singapore` (paling cepat untuk akses dari Indonesia).
   - **Instance Type:** `Free` (atau berbayar jika ingin fitur Disk).

## Langkah 4: Konfigurasi Tambahan (Opsional)

Jika Anda menggunakan `render.yaml` (Blueprint), Anda bisa langsung menggunakan menu **"Blueprints"** di Render, lalu hubungkan repo GitHub Anda. Render akan menyiapkan semuanya secara otomatis.

---

## ⚠️ Catatan Penting Mengenai Penyimpanan Data

Pada **Free Tier (Gratis)** di Render:
- Penyimpanan file bersifat **sementara (ephemeral)**.
- Setiap kali aplikasi di-deploy ulang atau restart, data di folder `data/` (history & config) akan **terhapus**.
- **Solusi:** Jika ingin data tetap ada, Anda perlu menggunakan **Paid Plan ($7/month)** untuk mengaktifkan fitur "Persistent Disk" seperti yang sudah saya tulis di `render.yaml`.

---

## ✅ Verifikasi Setelah Deploy

Setelah statusnya **Live**, buka URL `.onrender.com` yang diberikan. Aplikasi seharusnya tampil sama persis dengan versi desktop, namun berjalan di browser!

**Selamat! Proyek Anda sekarang bisa diakses oleh siapa saja.**
