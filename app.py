import os
from flask import Flask, render_template, request
from history import get_history, log_history, get_weekly_count, format_time_ago

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # 100 MB max upload

# Masukkan folder bin lokal ke dalam PATH agar FFmpeg dan tool eksternal lainnya langsung dikenali
bin_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin")
os.environ["PATH"] += os.pathsep + bin_path

TOOL_CATEGORIES = [
    {
        "id": "convert",
        "name": "Konversi Dokumen",
        "icon": "bi-file-earmark-arrow-right-fill",
        "tools": [
            {"id": "to-pdf", "name": "File ke PDF", "desc": "Bikin file PDF dari gambar atau teks", "icon": "bi-file-pdf-fill"},
            {"id": "pdf-to-word", "name": "PDF ke Word", "desc": "Ubah PDF ke Word (.docx) biar bisa diedit", "icon": "bi-file-word-fill"},
            {"id": "pdf-to-images", "name": "PDF ke Gambar", "desc": "Jadikan tiap halaman PDF sebagai gambar", "icon": "bi-file-image-fill"},
            {"id": "pdf-to-text", "name": "PDF ke Teks", "desc": "Ambil semua teks yang ada di dalam PDF", "icon": "bi-file-text-fill"},
            {"id": "pdf-to-excel", "name": "PDF ke Excel", "desc": "Sedot tabel dari PDF ke format Excel", "icon": "bi-file-earmark-spreadsheet-fill"},
            {"id": "html-to-pdf", "name": "HTML ke PDF", "desc": "Bikin PDF dari kode HTML", "icon": "bi-filetype-html"},
            {"id": "md-to-pdf", "name": "Markdown ke PDF", "desc": "Ubah catatan Markdown jadi PDF", "icon": "bi-markdown-fill"},
            {"id": "md-to-docx", "name": "Markdown ke Word", "desc": "Ubah Markdown jadi file Word", "icon": "bi-file-word-fill"},
            {"id": "ocr-pdf", "name": "OCR PDF", "desc": "Bikin PDF hasil scan jadi bisa dicopy teksnya", "icon": "bi-file-earmark-text-fill"},
            {"id": "cad-to-pdf", "name": "CAD ke PDF", "desc": "Ubah file gambar CAD (DXF/DWG) ke PDF", "icon": "bi-rulers"},
        ],
    },
    {
        "id": "pdf",
        "name": "Alat PDF",
        "icon": "bi-file-pdf-fill",
        "tools": [
            {"id": "merge", "name": "Gabung PDF", "desc": "Jadiin banyak file PDF ke satu file aja", "icon": "bi-union"},
            {"id": "split", "name": "Pisah PDF", "desc": "Potong-potong halaman PDF", "icon": "bi-scissors"},
            {"id": "compress", "name": "Kompres PDF", "desc": "Kecilin ukuran file PDF biar gampang dikirim", "icon": "bi-file-zip-fill"},
            {"id": "rotate", "name": "Putar PDF", "desc": "Putar arah halaman PDF yang kebalik", "icon": "bi-arrow-clockwise"},
            {"id": "resize", "name": "Ubah Ukuran", "desc": "Ubah ukuran kertas atau dimensi PDF", "icon": "bi-aspect-ratio-fill"},
            {"id": "page-numbers", "name": "Nomor Halaman", "desc": "Kasih nomor halaman di PDF-mu", "icon": "bi-123"},
            {"id": "extract-images", "name": "Ekstrak Gambar", "desc": "Ambil semua gambar yang ada di PDF", "icon": "bi-images"},
            {"id": "protect", "name": "Kunci PDF", "desc": "Pasang password biar PDF aman", "icon": "bi-lock-fill"},
            {"id": "unlock", "name": "Buka Kunci PDF", "desc": "Hilangkan password dari PDF", "icon": "bi-unlock-fill"},
            {"id": "sign", "name": "Tanda Tangan", "desc": "Tempel foto tanda tanganmu ke PDF", "icon": "bi-pen-fill"},
        ],
    },
    {
        "id": "spreadsheet",
        "name": "Lembar Sebar (Excel)",
        "icon": "bi-file-earmark-spreadsheet-fill",
        "tools": [
            {"id": "excel-to-csv", "name": "Excel ke CSV/JSON", "desc": "Ekspor lembar Excel ke CSV atau JSON", "icon": "bi-table"},
            {"id": "csv-to-excel", "name": "CSV/JSON ke Excel", "desc": "Buat file .xlsx dari CSV atau JSON", "icon": "bi-file-earmark-spreadsheet"},
            {"id": "excel-to-pdf", "name": "Excel ke PDF", "desc": "Ubah dokumen Excel ke PDF", "icon": "bi-file-pdf"},
            {"id": "merge", "name": "Gabung Workbook", "desc": "Gabung beberapa file Excel jadi satu", "icon": "bi-union"},
            {"id": "split", "name": "Pisah Sheet", "desc": "Ekspor tiap sheet jadi file .xlsx sendiri", "icon": "bi-scissors"},
            {"id": "info", "name": "Info & Pratinjau", "desc": "Lihat daftar sheet dan pratinjau baris", "icon": "bi-info-circle-fill"},
            {"id": "csv-tools", "name": "Toolkit CSV", "desc": "Filter, urutkan, dan hapus duplikat baris", "icon": "bi-funnel-fill"},
        ],
    },
    {
        "id": "image",
        "name": "Alat Gambar",
        "icon": "bi-image-fill",
        "tools": [
            {"id": "resize", "name": "Ubah Ukuran", "desc": "Ubah resolusi atau dimensi gambar", "icon": "bi-arrows-angle-expand"},
            {"id": "compress", "name": "Kompres Gambar", "desc": "Kecilin ukuran mb/kb gambar", "icon": "bi-file-zip-fill"},
            {"id": "convert", "name": "Konversi Format", "desc": "Ubah gambar ke JPG, PNG, WebP, dll", "icon": "bi-arrow-left-right"},
            {"id": "remove-bg", "name": "Hapus Background", "desc": "Bikin background jadi transparan pakai AI", "icon": "bi-eraser-fill"},
            {"id": "crop", "name": "Potong Gambar", "desc": "Crop gambar sesuai keinginan", "icon": "bi-crop"},
            {"id": "rotate", "name": "Putar / Balik", "desc": "Putar atau cerminkan foto", "icon": "bi-arrow-repeat"},
            {"id": "watermark", "name": "Watermark", "desc": "Kasih teks tanda air di fotomu", "icon": "bi-water"},
            {"id": "exif", "name": "Cek EXIF", "desc": "Lihat atau hapus data rahasia foto (metadata)", "icon": "bi-info-circle-fill"},
            {"id": "favicon", "name": "Bikin Favicon", "desc": "Bikin icon web (.ico) dari gambar biasa", "icon": "bi-app-indicator"},
            {"id": "ocr", "name": "Gambar ke Teks", "desc": "Ambil tulisan dari dalam gambar", "icon": "bi-card-text"},
            {"id": "animated", "name": "GIF / WebP", "desc": "Ubah bolak-balik antara GIF dan WebP animasi", "icon": "bi-film"},
            {"id": "palette", "name": "Palet Warna", "desc": "Cari tahu warna apa aja yang ada di foto", "icon": "bi-palette2"},
            {"id": "svg-to-png", "name": "SVG ke PNG", "desc": "Ubah gambar vektor SVG jadi PNG", "icon": "bi-filetype-svg"},
            {"id": "svg-optimize", "name": "Optimasi SVG", "desc": "Bersihin file SVG biar lebih ringan", "icon": "bi-file-minus-fill"},
        ],
    },
    {
        "id": "text",
        "name": "Teks & Data",
        "icon": "bi-braces",
        "tools": [
            {"id": "json-formatter", "name": "Perapih JSON", "desc": "Rapikan dan validasi struktur JSON", "icon": "bi-braces"},
            {"id": "csv-json", "name": "CSV / JSON", "desc": "Konversi antara CSV dan JSON", "icon": "bi-table"},
            {"id": "base64", "name": "Base64", "desc": "Encode dan decode data Base64", "icon": "bi-hash"},
            {"id": "url-encode", "name": "URL Encode", "desc": "Encode dan decode alamat URL", "icon": "bi-link-45deg"},
            {"id": "word-counter", "name": "Penghitung Kata", "desc": "Hitung kata, karakter, dan kalimat", "icon": "bi-type"},
            {"id": "markdown", "name": "Pratinjau Markdown", "desc": "Lihat tampilan Markdown sebagai HTML", "icon": "bi-markdown-fill"},
            {"id": "case-converter", "name": "Ubah Huruf", "desc": "Ubah antara huruf besar/kecil", "icon": "bi-type-bold"},
            {"id": "text-diff", "name": "Cek Perbedaan Teks", "desc": "Bandingkan dua teks secara berdampingan", "icon": "bi-file-diff-fill"},
            {"id": "regex-tester", "name": "Uji Regex", "desc": "Tes ekspresi reguler secara live", "icon": "bi-search"},
            {"id": "slug-generator", "name": "Pembuat Slug", "desc": "Buat slug ramah URL dari judul", "icon": "bi-link"},
            {"id": "json-yaml", "name": "JSON / YAML", "desc": "Konversi antara JSON dan YAML", "icon": "bi-filetype-yml"},
            {"id": "lorem-ipsum", "name": "Lorem Ipsum", "desc": "Buat teks pengisi otomatis", "icon": "bi-text-paragraph"},
        ],
    },
    {
        "id": "calc",
        "name": "Kalkulator",
        "icon": "bi-calculator-fill",
        "tools": [
            {"id": "calculator", "name": "Kalkulator", "desc": "Kalkulator dasar dan saintifik", "icon": "bi-calculator"},
            {"id": "unit-converter", "name": "Konversi Satuan", "desc": "Ubah antar berbagai satuan ukuran", "icon": "bi-arrow-left-right"},
            {"id": "color-converter", "name": "Konversi Warna", "desc": "Ubah warna HEX, RGB, HSL", "icon": "bi-palette-fill"},
            {"id": "percentage", "name": "Kalkulator Persen", "desc": "Hitung persentase dengan mudah", "icon": "bi-percent"},
            {"id": "date", "name": "Kalkulator Tanggal", "desc": "Hitung selisih antar tanggal", "icon": "bi-calendar-date-fill"},
            {"id": "timestamp", "name": "Unix Timestamp", "desc": "Ubah format Unix timestamp", "icon": "bi-clock-fill"},
            {"id": "number-base", "name": "Basis Bilangan", "desc": "Ubah antar basis bilangan (Biner, dll)", "icon": "bi-123"},
            {"id": "pomodoro", "name": "Timer Pomodoro", "desc": "Timer fokus dengan jeda istirahat", "icon": "bi-stopwatch-fill"},
        ],
    },
    {
        "id": "qr",
        "name": "QR & Barcode",
        "icon": "bi-qr-code",
        "tools": [
            {"id": "generate", "name": "Buat QR", "desc": "Buat kode QR dari teks atau URL", "icon": "bi-qr-code"},
            {"id": "read", "name": "Baca QR", "desc": "Scan kode QR dari sebuah gambar", "icon": "bi-qr-code-scan"},
            {"id": "barcode", "name": "Buat Barcode", "desc": "Mendukung Code128, EAN, UPC, dll", "icon": "bi-upc-scan"},
        ],
    },
    {
        "id": "security",
        "name": "Keamanan",
        "icon": "bi-shield-lock-fill",
        "tools": [
            {"id": "password-generator", "name": "Pembuat Password", "desc": "Buat password acak yang kuat", "icon": "bi-key-fill"},
            {"id": "hash-generator", "name": "Pembuat Hash", "desc": "Buat hash MD5, SHA-256", "icon": "bi-fingerprint"},
            {"id": "file-hash", "name": "Hash File", "desc": "Cek integritas file yang diunggah", "icon": "bi-file-earmark-lock-fill"},
        ],
    },
    {
        "id": "dev",
        "name": "Alat Pengembang",
        "icon": "bi-code-slash",
        "tools": [
            {"id": "uuid", "name": "Generator UUID", "desc": "Buat UUID v4 secara massal", "icon": "bi-hash"},
            {"id": "jwt", "name": "Dekoder JWT", "desc": "Decode token JWT secara lokal", "icon": "bi-key"},
            {"id": "user-agent", "name": "Parser User-Agent", "desc": "Cek info browser, OS, dan perangkat", "icon": "bi-window"},
            {"id": "sql-format", "name": "Perapih SQL", "desc": "Format kode SQL agar mudah dibaca", "icon": "bi-filetype-sql"},
            {"id": "xml-format", "name": "Perapih XML", "desc": "Format, validasi, dan minify XML", "icon": "bi-filetype-xml"},
            {"id": "html-format", "name": "Perapih HTML", "desc": "Format atau perkecil kode HTML", "icon": "bi-filetype-html"},
            {"id": "css-format", "name": "Perapih CSS", "desc": "Format atau perkecil kode CSS", "icon": "bi-filetype-css"},
            {"id": "js-format", "name": "Perapih JS", "desc": "Format atau perkecil JavaScript", "icon": "bi-filetype-js"},
            {"id": "cron", "name": "Parser Cron", "desc": "Validasi dan lihat jadwal cron job", "icon": "bi-calendar-week-fill"},
            {"id": "jsonpath", "name": "Tester JSONPath", "desc": "Query data JSON dengan JSONPath", "icon": "bi-search"},
        ],
    },
    {
        "id": "archive",
        "name": "Alat Arsip",
        "icon": "bi-file-zip-fill",
        "tools": [
            {"id": "zip", "name": "Buat ZIP", "desc": "Gabung banyak file jadi arsip .zip", "icon": "bi-file-zip"},
            {"id": "unzip", "name": "Ekstrak ZIP", "desc": "Keluarkan isi file dari arsip .zip", "icon": "bi-box-arrow-up"},
            {"id": "zip-info", "name": "Info ZIP", "desc": "Lihat isi dan ukuran file dalam arsip", "icon": "bi-info-circle-fill"},
        ],
    },
    {
        "id": "media",
        "name": "Audio & Video",
        "icon": "bi-camera-reels-fill",
        "tools": [
            {"id": "convert-audio", "name": "Konversi Audio", "desc": "Ubah lagu/suara ke format lain (MP3, WAV, dll)", "icon": "bi-music-note-beamed"},
            {"id": "convert-video", "name": "Konversi Video", "desc": "Ubah video ke format lain (MP4, MKV, dll)", "icon": "bi-camera-video-fill"},
            {"id": "extract-audio", "name": "Ekstrak Suara", "desc": "Ambil suara/lagu aja dari sebuah video", "icon": "bi-mic-fill"},
            {"id": "trim", "name": "Potong Media", "desc": "Potong bagian awal/akhir video atau audio", "icon": "bi-scissors"},
            {"id": "compress-video", "name": "Kompres Video", "desc": "Kecilin ukuran MB video-mu", "icon": "bi-file-zip-fill"},
            {"id": "video-to-gif", "name": "Video ke GIF", "desc": "Bikin meme GIF dari video", "icon": "bi-file-earmark-play-fill"},
            {"id": "subtitle-convert", "name": "Konversi Subtitle", "desc": "Ubah format subtitle SRT ke VTT atau sebaliknya", "icon": "bi-badge-cc-fill"},
            {"id": "burn-subtitles", "name": "Tanam Subtitle", "desc": "Patenkan subtitle langsung ke dalam video", "icon": "bi-fire"},
        ],
    },
]

from config_manager import load_config, save_config
from locales import translate_ui, translate_tool

@app.context_processor
def inject_globals():
    config = load_config()
    lang = config.get("language", "id")
    
    # Menerjemahkan kategori dan alat
    translated_categories = []
    for cat in TOOL_CATEGORIES:
        new_cat = cat.copy()
        new_cat["name"] = translate_tool(cat["name"], lang)
        new_tools = []
        for tool in cat["tools"]:
            new_tool = tool.copy()
            new_tool["name"] = translate_tool(tool["name"], lang)
            new_tool["desc"] = translate_tool(tool["desc"], lang)
            new_tools.append(new_tool)
        new_cat["tools"] = new_tools
        translated_categories.append(new_cat)

    return {
        "tool_categories": translated_categories,
        "app_config": config,
        "_t": lambda key, **kwargs: translate_ui(key, lang=lang, **kwargs),
        "translate_tool": lambda text: translate_tool(text, lang)
    }
@app.before_request
def track_tool_usage():
    if request.method == "GET":
        path = request.path.strip("/")
        parts = path.split("/")
        if len(parts) == 2:
            cat_id, tool_id = parts
            for cat in TOOL_CATEGORIES:
                if cat["id"] == cat_id:
                    for tool in cat["tools"]:
                        if tool["id"] == tool_id:
                            log_history(cat, tool)
                            break

@app.route("/")
def index():
    recent = get_history()
    config = load_config()
    lang = config.get("language", "id")
    for r in recent:
        r['time_str'] = format_time_ago(r['timestamp'], lang=lang)
    weekly_count = get_weekly_count()
    return render_template("index.html", recent_history=recent[:3], weekly_count=weekly_count)

@app.route("/history")
def history_page():
    recent = get_history()
    config = load_config()
    lang = config.get("language", "id")
    for r in recent:
        r['time_str'] = format_time_ago(r['timestamp'], lang=lang)
    return render_template("history.html", history=recent)

@app.route("/settings")
def settings_page():
    return render_template("settings.html")

from flask import jsonify
@app.route("/api/settings", methods=["POST"])
def api_settings():
    data = request.json
    if not data:
        return jsonify({"success": False}), 400
    save_config(data)
    return jsonify({"success": True})


@app.errorhandler(413)
def too_large(e):
    return {"error": "Waduh, ukuran file-nya kegedean nih! Maksimal cuma 100 MB ya."}, 413


@app.errorhandler(500)
def server_error(e):
    return {"error": "Yah, ada error dari server nih. Coba lagi atau periksa file-mu ya!"}, 500


# Register blueprints
from routes.convert_tools import bp as convert_bp
from routes.pdf_tools import bp as pdf_bp
from routes.image_tools import bp as image_bp
from routes.text_tools import bp as text_bp
from routes.calculator_tools import bp as calc_bp
from routes.qr_tools import bp as qr_bp
from routes.security_tools import bp as security_bp
from routes.spreadsheet_tools import bp as spreadsheet_bp
from routes.dev_tools import bp as dev_bp
from routes.archive_tools import bp as archive_bp
from routes.media_tools import bp as media_bp

app.register_blueprint(convert_bp, url_prefix="/convert")
app.register_blueprint(pdf_bp, url_prefix="/pdf")
app.register_blueprint(image_bp, url_prefix="/image")
app.register_blueprint(text_bp, url_prefix="/text")
app.register_blueprint(calc_bp, url_prefix="/calc")
app.register_blueprint(qr_bp, url_prefix="/qr")
app.register_blueprint(security_bp, url_prefix="/security")
app.register_blueprint(spreadsheet_bp, url_prefix="/spreadsheet")
app.register_blueprint(dev_bp, url_prefix="/dev")
app.register_blueprint(archive_bp, url_prefix="/archive")
app.register_blueprint(media_bp, url_prefix="/media")

import threading
import webview
import time

class WebviewApi:
    def save_file(self, b64data, filename):
        import base64
        window = webview.active_window()
        result = window.create_file_dialog(webview.SAVE_DIALOG, save_filename=filename)
        if result:
            try:
                with open(result[0], 'wb') as f:
                    f.write(base64.b64decode(b64data))
                return True
            except Exception as e:
                print("Error saving file:", e)
        return False

if __name__ == "__main__":
    def start_flask():
        app.run(debug=False, port=5000)
        
    # Jalankan server Flask di thread terpisah agar tidak memblokir UI
    t = threading.Thread(target=start_flask)
    t.daemon = True
    t.start()
    
    # Beri sedikit waktu agar server siap sebelum window dibuat
    time.sleep(1)
    # Buat jendela aplikasi desktop (Native UI)
    import os
    api = WebviewApi()
    webview.create_window("SerbaBisa", "http://127.0.0.1:5000", width=1200, height=800, min_size=(800, 600), js_api=api)
    webview.start(private_mode=False)
