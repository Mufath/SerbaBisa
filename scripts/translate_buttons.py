import os
import re

routes_dir = 'routes'
files = [f for f in os.listdir(routes_dir) if f.endswith('.py')]
for filename in files:
    filepath = os.path.join(routes_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Translate common button texts
    content = re.sub(r'button_text\s*=\s*"Convert"', 'button_text="Konversi"', content)
    content = re.sub(r'button_text\s*=\s*"Compress"', 'button_text="Kompres"', content)
    content = re.sub(r'button_text\s*=\s*"Extract"', 'button_text="Ekstrak"', content)
    content = re.sub(r'button_text\s*=\s*"Merge"', 'button_text="Gabungkan"', content)
    content = re.sub(r'button_text\s*=\s*"Split"', 'button_text="Pisahkan"', content)
    content = re.sub(r'button_text\s*=\s*"Rotate"', 'button_text="Putar"', content)
    content = re.sub(r'button_text\s*=\s*"Resize"', 'button_text="Ubah Ukuran"', content)
    content = re.sub(r'button_text\s*=\s*"Protect"', 'button_text="Kunci"', content)
    content = re.sub(r'button_text\s*=\s*"Unlock"', 'button_text="Buka Kunci"', content)
    content = re.sub(r'button_text\s*=\s*"Sign"', 'button_text="Tanda Tangan"', content)
    content = re.sub(r'button_text\s*=\s*"Generate"', 'button_text="Buat"', content)
    content = re.sub(r'button_text\s*=\s*"Read"', 'button_text="Baca"', content)
    content = re.sub(r'button_text\s*=\s*"Trim"', 'button_text="Potong"', content)
    content = re.sub(r'button_text\s*=\s*"Burn subtitles"', 'button_text="Tanam Subtitle"', content)
    content = re.sub(r'button_text\s*=\s*"Format JSON"', 'button_text="Rapikan JSON"', content)
    content = re.sub(r'button_text\s*=\s*"Encode"', 'button_text="Proses Encode"', content)
    content = re.sub(r'button_text\s*=\s*"Decode"', 'button_text="Proses Decode"', content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
print('Buttons translated!')
