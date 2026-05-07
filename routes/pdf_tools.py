import io
from flask import Blueprint, render_template, request, send_file, jsonify
from locales import m
from services.pdf_service import (
    process_pdf_merge, process_pdf_split, process_pdf_compress, process_pdf_rotate,
    process_pdf_resize, process_pdf_page_numbers, process_pdf_extract_images,
    process_pdf_protect, process_pdf_sign, process_pdf_unlock,
    process_pdf_read_fields, process_pdf_fill_form
)

bp = Blueprint("pdf", __name__)

# ── Page Routes ──────────────────────────────────

@bp.route("/merge")
def merge_page():
    return render_template("upload_tool.html", title="Gabung PDF", description="Jadiin banyak file PDF ke satu file aja", endpoint="/pdf/merge", accept=".pdf", multiple=True, options=[])

@bp.route("/split")
def split_page():
    return render_template("upload_tool.html", title="Pisah PDF", description="Potong-potong halaman PDF", endpoint="/pdf/split", accept=".pdf", multiple=False, options=[{"type": "text", "name": "pages", "label": "Page ranges (leave empty for all pages)", "placeholder": "e.g. 1-3, 5, 7-10"}])

@bp.route("/compress")
def compress_page():
    return render_template("upload_tool.html", title="Kompres PDF", description="Kecilin ukuran file PDF biar gampang dikirim", endpoint="/pdf/compress", accept=".pdf", multiple=False, options=[{"type": "select", "name": "quality", "label": "Tingkat Kompresi", "choices": [{"value": "medium", "label": "Standar (Seimbang)"}, {"value": "low", "label": "Maksimal (Kualitas Turun, Ukuran Terkecil)"}, {"value": "high", "label": "Minimal (Kualitas Terjaga Aman 100%)"}]}])

@bp.route("/rotate")
def rotate_page():
    return render_template("upload_tool.html", title="Putar PDF", description="Putar arah halaman PDF yang kebalik", endpoint="/pdf/rotate", accept=".pdf", multiple=False, options=[{"type": "select", "name": "angle", "label": "Rotation Angle", "choices": [{"value": "90", "label": "90° Clockwise"}, {"value": "180", "label": "180°"}, {"value": "270", "label": "90° Counter-clockwise"}]}, {"type": "text", "name": "pages", "label": "Pages To Rotate Detailed", "placeholder": "e.g. 1, 3, 5-7"}])

@bp.route("/resize")
def resize_page():
    return render_template("upload_tool.html", title="Ubah Ukuran", description="Ubah ukuran kertas atau dimensi PDF", endpoint="/pdf/resize", accept=".pdf", multiple=False, options=[{"type": "select", "name": "mode", "label": "Resize Mode", "choices": [{"value": "scale", "label": "Scale by percentage"}, {"value": "paper", "label": "Standard paper size"}]}, {"type": "number", "name": "scale", "label": "Scale (%)", "default": 100, "min": 10, "max": 500, "depends_on": {"mode": "scale"}}, {"type": "select", "name": "paper", "label": "Paper Size", "choices": [{"value": "a4", "label": "A4 (210 x 297 mm)"}, {"value": "letter", "label": "Letter (8.5 x 11 in)"}, {"value": "a3", "label": "A3 (297 x 420 mm)"}, {"value": "a5", "label": "A5 (148 x 210 mm)"}, {"value": "legal", "label": "Legal (8.5 x 14 in)"}], "depends_on": {"mode": "paper"}}])

@bp.route("/page-numbers")
def page_numbers_page():
    return render_template("upload_tool.html", title="Nomor Halaman", description="Kasih nomor halaman di PDF-mu", endpoint="/pdf/page-numbers", accept=".pdf", multiple=False, options=[{"type": "select", "name": "position", "label": "Position", "choices": [{"value": "bottom-center", "label": "Bottom Center"}, {"value": "bottom-right", "label": "Bottom Right"}, {"value": "bottom-left", "label": "Bottom Left"}, {"value": "top-center", "label": "Top Center"}, {"value": "top-right", "label": "Top Right"}, {"value": "top-left", "label": "Top Left"}]}, {"type": "number", "name": "start", "label": "Start number", "default": 1, "min": 0}, {"type": "number", "name": "fontsize", "label": "Font size", "default": 11, "min": 6, "max": 30}])

@bp.route("/extract-images")
def extract_images_page():
    return render_template("upload_tool.html", title="Ekstrak Gambar", description="Ambil semua gambar yang ada di PDF", endpoint="/pdf/extract-images", accept=".pdf", multiple=False, options=[])

@bp.route("/protect")
def protect_page():
    return render_template("upload_tool.html", title="Kunci PDF", description="Pasang password biar PDF aman", endpoint="/pdf/protect", accept=".pdf", multiple=False, options=[{"type": "password", "name": "user_password", "label": "Enter User Password", "placeholder": "Enter Password"}, {"type": "password", "name": "owner_password", "label": "Enter Owner Password", "placeholder": "Leave Empty Same Password"}])

@bp.route("/sign")
def sign_page():
    return render_template("upload_tool.html", title="Tanda Tangan", description="Tempel foto tanda tanganmu ke PDF", notes="Signature Tip", endpoint="/pdf/sign", accept=".pdf", multiple=False, options=[{"type": "file", "name": "signature", "label": "Signature Image Label", "accept": "image/png,image/jpeg", "required": True}, {"type": "text", "name": "pages", "label": "Pages To Rotate Detailed", "placeholder": "e.g. 1, 3, 5-7"}, {"type": "select", "name": "position", "label": "Position", "default": "bottom-right", "choices": [{"value": "bottom-right", "label": "Bottom Right"}, {"value": "bottom-center", "label": "Bottom Center"}, {"value": "bottom-left", "label": "Bottom Left"}, {"value": "top-right", "label": "Top Right"}, {"value": "top-center", "label": "Top Center"}, {"value": "top-left", "label": "Top Left"}]}, {"type": "number", "name": "width", "label": "Signature Width", "default": 140, "min": 30, "max": 400}, {"type": "number", "name": "margin", "label": "Margin Edge", "default": 36, "min": 0, "max": 200}, {"type": "number", "name": "opacity", "label": "Opacity (%)", "default": 100, "min": 10, "max": 100}])

@bp.route("/unlock")
def unlock_page():
    return render_template("upload_tool.html", title="Buka Kunci PDF", description="Hilangkan password dari PDF", endpoint="/pdf/unlock", accept=".pdf", multiple=False, options=[{"type": "password", "name": "password", "label": "PDF Password", "placeholder": "Enter Current Password"}])

@bp.route("/fill-form")
def fill_form_page():
    return render_template("tools/pdf_fill_form.html", title="Isi Formulir", description="Isi data formulir PDF secara otomatis", endpoint="/pdf/fill-form", accept=".pdf", multiple=False)

# ── Processing Routes ────────────────────────────

@bp.route("/merge", methods=["POST"])
def merge():
    files = request.files.getlist("files")
    if len(files) < 2:
        return jsonify(error=m("Please upload at least 2 PDF files.")), 400
    try:
        buf, mimetype, name = process_pdf_merge(files)
        return send_file(buf, mimetype=mimetype, as_attachment=True, download_name=name)
    except Exception as e:
        return jsonify(error=str(e)), 400

@bp.route("/split", methods=["POST"])
def split():
    files = request.files.getlist("files")
    if not files or not files[0].filename:
        return jsonify(error=m("No file uploaded.")), 400
    try:
        buf, mimetype, name = process_pdf_split(files[0], request.form.get("pages", ""))
        return send_file(buf, mimetype=mimetype, as_attachment=True, download_name=name)
    except Exception as e:
        return jsonify(error=str(e)), 400

@bp.route("/compress", methods=["POST"])
def compress():
    files = request.files.getlist("files")
    if not files or not files[0].filename:
        return jsonify(error=m("No file uploaded.")), 400
    buf, mimetype, name = process_pdf_compress(files[0], request.form.get("quality", "medium"))
    return send_file(buf, mimetype=mimetype, as_attachment=True, download_name=name)

@bp.route("/rotate", methods=["POST"])
def rotate():
    files = request.files.getlist("files")
    if not files or not files[0].filename:
        return jsonify(error=m("No file uploaded.")), 400
    buf, mimetype, name = process_pdf_rotate(files[0], int(request.form.get("angle", 90)), request.form.get("pages", ""))
    return send_file(buf, mimetype=mimetype, as_attachment=True, download_name=name)

@bp.route("/resize", methods=["POST"])
def resize():
    files = request.files.getlist("files")
    if not files or not files[0].filename:
        return jsonify(error=m("No file uploaded.")), 400
    try:
        buf, mimetype, name = process_pdf_resize(
            files[0], request.form.get("mode", "scale"),
            request.form.get("scale", 100), request.form.get("paper", "a4")
        )
        return send_file(buf, mimetype=mimetype, as_attachment=True, download_name=name)
    except Exception as e:
        return jsonify(error=str(e)), 400

@bp.route("/page-numbers", methods=["POST"])
def page_numbers():
    files = request.files.getlist("files")
    if not files or not files[0].filename:
        return jsonify(error=m("No file uploaded.")), 400
    buf, mimetype, name = process_pdf_page_numbers(
        files[0], request.form.get("position", "bottom-center"),
        int(request.form.get("start", 1)), int(request.form.get("fontsize", 11))
    )
    return send_file(buf, mimetype=mimetype, as_attachment=True, download_name=name)

@bp.route("/extract-images", methods=["POST"])
def extract_images():
    files = request.files.getlist("files")
    if not files or not files[0].filename:
        return jsonify(error=m("No file uploaded.")), 400
    try:
        buf, mimetype, name = process_pdf_extract_images(files[0])
        return send_file(buf, mimetype=mimetype, as_attachment=True, download_name=name)
    except Exception as e:
        return jsonify(error=str(e)), 400

@bp.route("/protect", methods=["POST"])
def protect():
    files = request.files.getlist("files")
    if not files or not files[0].filename:
        return jsonify(error=m("No file uploaded.")), 400
    user_pw = request.form.get("user_password", "")
    if not user_pw: return jsonify(error=m("Please enter a password.")), 400
    buf, mimetype, name = process_pdf_protect(files[0], user_pw, request.form.get("owner_password", ""))
    return send_file(buf, mimetype=mimetype, as_attachment=True, download_name=name)

@bp.route("/sign", methods=["POST"])
def sign():
    files = request.files.getlist("files")
    if not files or not files[0].filename:
        return jsonify(error=m("No PDF uploaded.")), 400
    sig_file = request.files.get("signature")
    if not sig_file or not sig_file.filename:
        return jsonify(error=m("Please upload a signature image.")), 400
    try:
        buf, mimetype, name = process_pdf_sign(
            files[0], sig_file, request.form.get("position", "bottom-right"),
            float(request.form.get("width", 140)), float(request.form.get("margin", 36)),
            int(request.form.get("opacity", 100)), request.form.get("pages", "")
        )
        return send_file(buf, mimetype=mimetype, as_attachment=True, download_name=name)
    except Exception as e:
        return jsonify(error=str(e)), 400

@bp.route("/unlock", methods=["POST"])
def unlock():
    files = request.files.getlist("files")
    if not files or not files[0].filename:
        return jsonify(error=m("No file uploaded.")), 400
    try:
        buf, mimetype, name = process_pdf_unlock(files[0], request.form.get("password", ""))
        return send_file(buf, mimetype=mimetype, as_attachment=True, download_name=name)
    except Exception as e:
        return jsonify(error=str(e)), 400

@bp.route("/read-fields", methods=["POST"])
def read_fields():
    files = request.files.getlist("files")
    if not files or not files[0].filename:
        return jsonify(error=m("No file uploaded.")), 400
    fields = process_pdf_read_fields(files[0])
    return jsonify(fields=fields)

@bp.route("/fill-form", methods=["POST"])
def fill_form():
    files = request.files.getlist("files")
    if not files or not files[0].filename:
        return jsonify(error=m("No file uploaded.")), 400
    import json
    form_data = json.loads(request.form.get("form_data", "{}"))
    buf, mimetype, name = process_pdf_fill_form(files[0], form_data)
    return send_file(buf, mimetype=mimetype, as_attachment=True, download_name=name)
