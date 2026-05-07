import io
from flask import Blueprint, render_template, request, send_file, jsonify
from locales import m
from services.image_service import (
    HAS_REMBG, HAS_TESSERACT, IMAGE_ACCEPT,
    process_resize, process_compress, process_convert, process_remove_bg,
    process_crop, process_rotate, process_watermark, process_exif,
    process_favicon, process_animated, process_ocr, process_palette,
    process_svg_to_png, process_svg_optimize
)

bp = Blueprint("image", __name__)

# ── Page Routes ──────────────────────────────────

@bp.route("/resize")
def resize_page():
    return render_template("upload_tool.html",
        title=m("Resize Title"),
        description=m("Desc Resize Image"),
        endpoint="/image/resize",
        accept=IMAGE_ACCEPT,
        multiple=False,
        options=[
            {"type": "select", "name": "mode", "label": m("Resize Mode"),
             "choices": [
                 {"value": "percentage", "label": m("By Percentage")},
                 {"value": "dimensions", "label": m("By Dimensions")},
             ]},
            {"type": "number", "name": "percentage", "label": m("Scale (%)"), "default": 50, "min": 1, "max": 1000,
             "depends_on": {"mode": "percentage"}},
            {"type": "number", "name": "width", "label": "Width",
             "depends_on": {"mode": "dimensions"}},
            {"type": "number", "name": "height", "label": "Height",
             "depends_on": {"mode": "dimensions"}},
            {"type": "checkbox", "name": "keep_ratio", "label": "Aspect Ratio",
             "check_label": "Keep Aspect Ratio", "default": True,
             "depends_on": {"mode": "dimensions"}},
        ])

@bp.route("/compress")
def compress_page():
    return render_template("upload_tool.html",
        title=m("Compress Title"),
        description=m("Desc Compress Image"),
        endpoint="/image/compress",
        accept=IMAGE_ACCEPT,
        multiple=False,
        options=[
            {"type": "range", "name": "quality", "label": "Quality",
             "default": 80, "min": 10, "max": 100, "step": 5, "suffix": "%"},
        ])

@bp.route("/convert")
def convert_page():
    return render_template("upload_tool.html",
        title=m("Convert Format Title"),
        description=m("Desc Image Convert"),
        endpoint="/image/convert",
        accept=IMAGE_ACCEPT,
        multiple=True,
        options=[
            {"type": "select", "name": "format", "label": "Convert To",
             "choices": [
                 {"value": "png", "label": "PNG"},
                 {"value": "jpg", "label": "JPG"},
                 {"value": "webp", "label": "WebP"},
                 {"value": "bmp", "label": "BMP"},
                 {"value": "tiff", "label": "TIFF"},
             ]},
        ])

@bp.route("/remove-bg")
def remove_bg_page():
    return render_template("upload_tool.html",
        title=m("Remove BG Title"),
        description=m("Desc Remove BG"),
        notes="Tips AI Model",
        endpoint="/image/remove-bg",
        accept=IMAGE_ACCEPT,
        multiple=False,
        options=[
            {"type": "select", "name": "model", "label": "AI Model", "default": "u2net",
             "choices": [
                 {"value": "u2net", "label": "U2net Standard"},
                 {"value": "isnet-general-use", "label": "Isnet Accurate"},
                 {"value": "u2net_human_seg", "label": "U2net Human"},
             ]},
        ])

@bp.route("/crop")
def crop_page():
    return render_template("upload_tool.html",
        title=m("Crop Title"),
        description=m("Desc Crop Image"),
        endpoint="/image/crop",
        accept=IMAGE_ACCEPT,
        multiple=False,
        options=[
            {"type": "select", "name": "mode", "label": "Crop Mode",
             "choices": [
                 {"value": "ratio", "label": "Center Crop"},
                 {"value": "custom", "label": "Custom Coords"},
             ]},
            {"type": "select", "name": "ratio", "label": "Aspect Ratio",
             "choices": [
                 {"value": "1:1", "label": "Square"},
                 {"value": "4:3", "label": "4:3"},
                 {"value": "3:2", "label": "3:2"},
                 {"value": "16:9", "label": "16:9"},
                 {"value": "9:16", "label": "Vertical"},
             ],
             "depends_on": {"mode": "ratio"}},
            {"type": "number", "name": "left", "label": "Top Left", "default": 0,
             "depends_on": {"mode": "custom"}},
            {"type": "number", "name": "top", "label": "Top Center", "default": 0,
             "depends_on": {"mode": "custom"}},
            {"type": "number", "name": "right", "label": "Top Right",
             "depends_on": {"mode": "custom"}},
            {"type": "number", "name": "bottom", "label": "Bottom Right",
             "depends_on": {"mode": "custom"}},
        ])

@bp.route("/rotate")
def rotate_page():
    return render_template("upload_tool.html",
        title=m("Rotate Title"),
        description=m("Desc Rotate Flip"),
        endpoint="/image/rotate",
        accept=IMAGE_ACCEPT,
        multiple=False,
        options=[
            {"type": "select", "name": "action", "label": "Action",
             "choices": [
                 {"value": "90", "label": "Rotate 90 Clockwise"},
                 {"value": "180", "label": "Rotate 180°"},
                 {"value": "270", "label": "Rotate 90 Counter-clockwise"},
                 {"value": "flip_h", "label": "Flip Horizontal"},
                 {"value": "flip_v", "label": "Flip Vertical"},
             ]},
        ])

@bp.route("/exif")
def exif_page():
    return render_template("upload_tool.html",
        title=m("Exif Title"),
        description=m("Desc Check EXIF"),
        endpoint="/image/exif",
        accept=IMAGE_ACCEPT,
        multiple=False,
        options=[
            {"type": "select", "name": "action", "label": "Action",
             "choices": [
                 {"value": "view", "label": "View EXIF"},
                 {"value": "strip", "label": "Strip EXIF"},
             ]},
        ])

@bp.route("/favicon")
def favicon_page():
    return render_template("upload_tool.html",
        title=m("Favicon Title"),
        description=m("Desc Create Favicon"),
        endpoint="/image/favicon",
        accept=IMAGE_ACCEPT,
        multiple=False,
        options=[
            {"type": "select", "name": "sizes", "label": "Sizes To Include",
             "choices": [
                 {"value": "all", "label": "All Sizes"},
                 {"value": "standard", "label": "Standard Sizes"},
                 {"value": "16", "label": "16x16 only"},
                 {"value": "32", "label": "32x32 only"},
             ]},
        ],
        button_text="Buat Favicon")

@bp.route("/animated")
def animated_page():
    return render_template("upload_tool.html",
        title=m("Animated Title"),
        description=m("Desc Animated GIF WebP"),
        endpoint="/image/animated",
        accept=".gif,.webp",
        multiple=False,
        options=[
            {"type": "select", "name": "target", "label": "Output Format",
             "choices": [
                 {"value": "webp", "label": "Animated Webp"},
                 {"value": "gif", "label": "Animated Gif"},
             ]},
            {"type": "range", "name": "quality", "label": "Webp Quality",
             "default": 80, "min": 10, "max": 100, "step": 5, "suffix": "%",
             "depends_on": {"target": "webp"}},
            {"type": "number", "name": "fps", "label": "Override FPS",
             "default": 0, "min": 0, "max": 60},
            {"type": "checkbox", "name": "lossless", "label": "Lossless Webp",
             "check_label": "Lossless Webp", "default": False,
             "depends_on": {"target": "webp"}},
        ])

@bp.route("/ocr")
def ocr_page():
    return render_template("upload_tool.html",
        title=m("OCR Image Title"),
        description=m("Desc Image to Text"),
        endpoint="/image/ocr",
        accept=IMAGE_ACCEPT,
        multiple=False,
        options=[])

@bp.route("/palette")
def palette_page():
    return render_template("upload_tool.html",
        title=m("Palette Title"),
        description=m("Desc Color Palette"),
        endpoint="/image/palette",
        accept=IMAGE_ACCEPT,
        multiple=False,
        options=[
            {"type": "number", "name": "count", "label": "Number of colors", "default": 8, "min": 2, "max": 32},
            {"type": "select", "name": "method", "label": "Method", "default": "quantize",
             "choices": [
                 {"value": "quantize", "label": "Pillow Quantize"},
                 {"value": "grid", "label": "Grid Sampling"},
             ]},
        ])

@bp.route("/svg-to-png")
def svg_to_png_page():
    return render_template("upload_tool.html",
        title=m("SVG PNG Title"),
        description=m("Desc SVG to PNG"),
        endpoint="/image/svg-to-png",
        accept=".svg",
        multiple=False,
        options=[
            {"type": "number", "name": "width", "label": "Output Width Px",
             "default": 0, "min": 0, "max": 8192},
            {"type": "checkbox", "name": "transparent", "label": "Background",
             "default": True, "check_label": "Transparent Bg"},
        ])

@bp.route("/svg-optimize")
def svg_optimize_page():
    return render_template("upload_tool.html",
        title=m("SVG Optimize Title"),
        description=m("Desc SVG Optimizer"),
        endpoint="/image/svg-optimize",
        accept=".svg",
        multiple=False,
        options=[
            {"type": "checkbox", "name": "strip_comments", "label": "Komentar",
             "default": True, "check_label": "Remove Comments"},
            {"type": "checkbox", "name": "strip_metadata", "label": "Metadata",
             "default": True, "check_label": "Remove Metadata"},
            {"type": "checkbox", "name": "collapse_whitespace", "label": "Spasi",
             "default": True, "check_label": "Collapse Whitespace"},
            {"type": "number", "name": "decimals", "label": "Max decimal places for numbers",
             "default": 3, "min": 0, "max": 6},
        ])

@bp.route("/watermark")
def watermark_page():
    return render_template("upload_tool.html",
        title=m("Watermark Title"),
        description=m("Desc Watermark"),
        endpoint="/image/watermark",
        accept=IMAGE_ACCEPT,
        multiple=False,
        options=[
            {"type": "text", "name": "text", "label": "Watermark Text", "placeholder": "Watermark Text Placeholder"},
            {"type": "select", "name": "position", "label": "Position Label",
             "choices": [
                 {"value": "center", "label": "Tengah"},
                 {"value": "bottom-right", "label": "Bottom Right"},
                 {"value": "bottom-left", "label": "Bottom Left"},
                 {"value": "top-right", "label": "Top Right"},
                 {"value": "top-left", "label": "Top Left"},
                 {"value": "tiled", "label": "Tiled (repeated)"},
             ]},
            {"type": "range", "name": "opacity", "label": "Opasitas",
             "default": 40, "min": 10, "max": 100, "step": 5, "suffix": "%"},
            {"type": "number", "name": "fontsize", "label": "Font Size", "default": 36, "min": 10, "max": 200},
        ])

# ── Processing Routes ────────────────────────────

@bp.route("/resize", methods=["POST"])
def resize():
    files = request.files.getlist("files")
    if not files or not files[0].filename:
        return jsonify(error=m("No file uploaded.")), 400
    try:
        buf, mimetype, name = process_resize(
            files[0], request.form.get("mode", "percentage"),
            request.form.get("percentage", 50),
            request.form.get("width"), request.form.get("height"),
            request.form.get("keep_ratio") == "on"
        )
        return send_file(buf, mimetype=mimetype, as_attachment=True, download_name=name)
    except Exception as e:
        return jsonify(error=str(e)), 400

@bp.route("/compress", methods=["POST"])
def compress():
    files = request.files.getlist("files")
    if not files or not files[0].filename:
        return jsonify(error=m("No file uploaded.")), 400
    buf, mimetype, name = process_compress(files[0], int(request.form.get("quality", 80)))
    return send_file(buf, mimetype=mimetype, as_attachment=True, download_name=name)

@bp.route("/convert", methods=["POST"])
def convert():
    files = request.files.getlist("files")
    if not files or not files[0].filename:
        return jsonify(error=m("No file uploaded.")), 400
    buf, mimetype, name = process_convert(files, request.form.get("format", "png"))
    return send_file(buf, mimetype=mimetype, as_attachment=True, download_name=name)

@bp.route("/remove-bg", methods=["POST"])
def remove_bg():
    if not HAS_REMBG:
        return jsonify(error=m("Package 'rembg' is not installed.")), 400
    files = request.files.getlist("files")
    if not files or not files[0].filename:
        return jsonify(error=m("No file uploaded.")), 400
    try:
        buf, mimetype, name = process_remove_bg(files[0], request.form.get("model", "u2net"))
        return send_file(buf, mimetype=mimetype, as_attachment=True, download_name=name)
    except Exception as e:
        return jsonify(error=str(e)), 500

@bp.route("/crop", methods=["POST"])
def crop():
    files = request.files.getlist("files")
    if not files or not files[0].filename:
        return jsonify(error=m("No file uploaded.")), 400
    buf, mimetype, name = process_crop(
        files[0], request.form.get("mode", "ratio"),
        request.form.get("ratio", "1:1"),
        request.form.get("left", 0), request.form.get("top", 0),
        request.form.get("right"), request.form.get("bottom")
    )
    return send_file(buf, mimetype=mimetype, as_attachment=True, download_name=name)

@bp.route("/rotate", methods=["POST"])
def rotate():
    files = request.files.getlist("files")
    if not files or not files[0].filename:
        return jsonify(error=m("No file uploaded.")), 400
    buf, mimetype, name = process_rotate(files[0], request.form.get("action", "90"))
    return send_file(buf, mimetype=mimetype, as_attachment=True, download_name=name)

@bp.route("/watermark", methods=["POST"])
def watermark():
    files = request.files.getlist("files")
    if not files or not files[0].filename:
        return jsonify(error=m("No file uploaded.")), 400
    buf, mimetype, name = process_watermark(
        files[0], request.form.get("text", "Watermark"),
        request.form.get("position", "center"),
        int(request.form.get("opacity", 40)),
        int(request.form.get("fontsize", 36))
    )
    return send_file(buf, mimetype=mimetype, as_attachment=True, download_name=name)

@bp.route("/exif", methods=["POST"])
def exif():
    files = request.files.getlist("files")
    if not files or not files[0].filename:
        return jsonify(error=m("No file uploaded.")), 400
    action = request.form.get("action", "view")
    if action == "view":
        data = process_exif(files[0], action)
        if not data: return jsonify(text=m("No EXIF data found."))
        import json
        return jsonify(text=json.dumps(data, indent=2, ensure_ascii=False))
    else:
        buf, mimetype, name = process_exif(files[0], action)
        return send_file(buf, mimetype=mimetype, as_attachment=True, download_name=name)

@bp.route("/favicon", methods=["POST"])
def favicon():
    files = request.files.getlist("files")
    if not files or not files[0].filename:
        return jsonify(error=m("No file uploaded.")), 400
    buf, mimetype, name = process_favicon(files[0], request.form.get("sizes", "all"))
    return send_file(buf, mimetype=mimetype, as_attachment=True, download_name=name)

@bp.route("/animated", methods=["POST"])
def animated():
    files = request.files.getlist("files")
    if not files or not files[0].filename:
        return jsonify(error=m("No file uploaded.")), 400
    try:
        buf, mimetype, name = process_animated(
            files[0], request.form.get("target", "webp"),
            int(request.form.get("quality", 80)),
            int(request.form.get("fps", 0)),
            request.form.get("lossless") == "on"
        )
        return send_file(buf, mimetype=mimetype, as_attachment=True, download_name=name)
    except Exception as e:
        return jsonify(error=str(e)), 400

@bp.route("/ocr", methods=["POST"])
def ocr():
    if not HAS_TESSERACT:
        return jsonify(error=m("OCR requires 'pytesseract'.")), 400
    files = request.files.getlist("files")
    if not files or not files[0].filename:
        return jsonify(error=m("No file uploaded.")), 400
    text = process_ocr(files[0])
    return jsonify(text=text)

@bp.route("/palette", methods=["POST"])
def palette():
    files = request.files.getlist("files")
    if not files or not files[0].filename:
        return jsonify(error=m("No file uploaded.")), 400
    palette_list, swatch_b64 = process_palette(
        files[0], int(request.form.get("count", 8)),
        request.form.get("method", "quantize")
    )
    lines = ["Color palette:"]
    for p in palette_list:
        lines.append(f"  {p['hex']}  rgb({p['rgb'][0]}, {p['rgb'][1]}, {p['rgb'][2]})   {p['percent']}%")
    lines.append("")
    lines.append(f"<img src='data:image/png;base64,{swatch_b64}' style='max-width:100%;border-radius:6px;margin-top:.6rem'>")
    return jsonify(text="\n".join(lines))

@bp.route("/svg-to-png", methods=["POST"])
def svg_to_png():
    files = request.files.getlist("files")
    if not files or not files[0].filename:
        return jsonify(error=m("No file uploaded.")), 400
    try:
        buf, mimetype, name = process_svg_to_png(
            files[0], int(request.form.get("width", 0)),
            request.form.get("transparent") == "on"
        )
        return send_file(buf, mimetype=mimetype, as_attachment=True, download_name=name)
    except Exception as e:
        return jsonify(error=str(e)), 400

@bp.route("/svg-optimize", methods=["POST"])
def svg_optimize():
    files = request.files.getlist("files")
    if not files or not files[0].filename:
        return jsonify(error=m("No file uploaded.")), 400
    buf, mimetype, name, original, optimized, saved = process_svg_optimize(
        files[0], request.form.get("strip_comments") == "on",
        request.form.get("strip_metadata") == "on",
        request.form.get("collapse_whitespace") == "on",
        int(request.form.get("decimals", 3))
    )
    resp = send_file(buf, mimetype=mimetype, as_attachment=True, download_name=name)
    resp.headers["X-Original-Size"] = str(original)
    resp.headers["X-Optimized-Size"] = str(optimized)
    resp.headers["X-Saved-Percent"] = str(saved)
    return resp
