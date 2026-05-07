# Gunakan image Python yang ringan
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Instal dependensi sistem (FFmpeg, Tesseract, Zbar, dll)
RUN apt-get update && apt-get install -y \
    build-essential \
    libcairo2-dev \
    pkg-config \
    ffmpeg \
    tesseract-ocr \
    libzbar0 \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Salin requirements.txt lebih dulu untuk optimasi cache
COPY requirements.txt .

# Instal dependensi Python
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua file proyek ke dalam container
COPY . .

# Pastikan folder data ada
RUN mkdir -p data

# Ekspos port yang digunakan Hugging Face (default 7860)
EXPOSE 7860

# Jalankan aplikasi menggunakan gunicorn
# Kita menggunakan bind 0.0.0.0:$PORT agar bisa diakses dari luar
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-7860} --workers 4 --threads 2 app:app"]
