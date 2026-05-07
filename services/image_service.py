import io
import json
from PIL import Image, ImageDraw, ImageFont
from PIL.ExifTags import TAGS

IMAGE_ACCEPT = "image/png,image/jpeg,image/webp,image/bmp,image/tiff"

try:
    from rembg import remove as rembg_remove, new_session
    HAS_REMBG = True
except ImportError:
    HAS_REMBG = False

try:
    import pytesseract
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False

FORMAT_MAP = {
    "jpg": ("JPEG", "image/jpeg", "jpg"),
    "jpeg": ("JPEG", "image/jpeg", "jpg"),
    "png": ("PNG", "image/png", "png"),
    "webp": ("WEBP", "image/webp", "webp"),
    "bmp": ("BMP", "image/bmp", "bmp"),
    "tiff": ("TIFF", "image/tiff", "tiff"),
}

def get_pil_image(file):
    return Image.open(io.BytesIO(file.read()))

def image_to_bytes(img, fmt, quality=85):
    buf = io.BytesIO()
    save_kwargs = {"format": fmt}

    if fmt.upper() == "JPEG":
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
        save_kwargs["quality"] = quality
        save_kwargs["optimize"] = True
    elif fmt.upper() == "PNG":
        save_kwargs["optimize"] = True
    elif fmt.upper() == "WEBP":
        save_kwargs["quality"] = quality

    img.save(buf, **save_kwargs)
    buf.seek(0)
    return buf

def process_resize(file, mode, percentage=50, width=None, height=None, keep_ratio=True):
    img = get_pil_image(file)
    if mode == "percentage":
        pct = float(percentage) / 100.0
        new_size = (int(img.width * pct), int(img.height * pct))
    else:
        if not width and not height:
            raise ValueError("Enter at least width or height.")
        
        w = int(width) if width else None
        h = int(height) if height else None

        if keep_ratio:
            if w and h:
                ratio = min(w / img.width, h / img.height)
                new_size = (int(img.width * ratio), int(img.height * ratio))
            elif w:
                ratio = w / img.width
                new_size = (w, int(img.height * ratio))
            else:
                ratio = h / img.height
                new_size = (int(img.width * ratio), h)
        else:
            new_size = (w or img.width, h or img.height)

    img = img.resize(new_size, Image.LANCZOS)
    
    ext = file.filename.rsplit(".", 1)[1].lower() if "." in file.filename else "png"
    fmt_info = FORMAT_MAP.get(ext, FORMAT_MAP["png"])
    buf = image_to_bytes(img, fmt_info[0])
    name = file.filename.rsplit(".", 1)[0] + f"_resized.{fmt_info[2]}"
    return buf, fmt_info[1], name

def process_compress(file, quality=80):
    img = get_pil_image(file)
    buf = image_to_bytes(img, "JPEG", quality=quality)
    name = file.filename.rsplit(".", 1)[0] + "_compressed.jpg"
    return buf, "image/jpeg", name

def process_convert(files, target_format):
    import zipfile
    fmt_info = FORMAT_MAP.get(target_format, FORMAT_MAP["png"])

    if len(files) == 1:
        img = get_pil_image(files[0])
        buf = image_to_bytes(img, fmt_info[0])
        name = files[0].filename.rsplit(".", 1)[0] + f".{fmt_info[2]}"
        return buf, fmt_info[1], name
    else:
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in files:
                if f.filename:
                    try:
                        img = get_pil_image(f)
                        buf = image_to_bytes(img, fmt_info[0])
                        name = f.filename.rsplit(".", 1)[0] + f".{fmt_info[2]}"
                        zf.writestr(name, buf.getvalue())
                    except Exception:
                        continue
        zip_buf.seek(0)
        return zip_buf, "application/zip", "converted_images.zip"

def process_remove_bg(file, model_name="u2net"):
    if not HAS_REMBG:
        raise ImportError("Package 'rembg' is not installed.")
    
    input_data = file.read()
    session = new_session(model_name)
    output_data = rembg_remove(input_data, session=session)
    
    name = file.filename.rsplit(".", 1)[0] + "_nobg.png"
    return io.BytesIO(output_data), "image/png", name

def process_crop(file, mode="ratio", ratio_str="1:1", left=0, top=0, right=None, bottom=None):
    img = get_pil_image(file)
    if mode == "ratio":
        rw, rh = [int(x) for x in ratio_str.split(":")]
        target_ratio = rw / rh
        current_ratio = img.width / img.height

        if current_ratio > target_ratio:
            new_w = int(img.height * target_ratio)
            l = (img.width - new_w) // 2
            box = (l, 0, l + new_w, img.height)
        else:
            new_h = int(img.width / target_ratio)
            t = (img.height - new_h) // 2
            box = (0, t, img.width, t + new_h)
    else:
        r = int(right) if right is not None else img.width
        b = int(bottom) if bottom is not None else img.height
        box = (int(left), int(top), r, b)

    img = img.crop(box)
    ext = file.filename.rsplit(".", 1)[1].lower() if "." in file.filename else "png"
    fmt_info = FORMAT_MAP.get(ext, FORMAT_MAP["png"])
    buf = image_to_bytes(img, fmt_info[0])
    name = file.filename.rsplit(".", 1)[0] + f"_cropped.{fmt_info[2]}"
    return buf, fmt_info[1], name

def process_rotate(file, action="90"):
    img = get_pil_image(file)
    if action == "90":
        img = img.rotate(-90, expand=True)
    elif action == "180":
        img = img.rotate(180, expand=True)
    elif action == "270":
        img = img.rotate(90, expand=True)
    elif action == "flip_h":
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    elif action == "flip_v":
        img = img.transpose(Image.FLIP_TOP_BOTTOM)

    ext = file.filename.rsplit(".", 1)[1].lower() if "." in file.filename else "png"
    fmt_info = FORMAT_MAP.get(ext, FORMAT_MAP["png"])
    buf = image_to_bytes(img, fmt_info[0])
    name = file.filename.rsplit(".", 1)[0] + f"_rotated.{fmt_info[2]}"
    return buf, fmt_info[1], name

def process_watermark(file, text="Watermark", position="center", opacity=40, fontsize=36):
    img = get_pil_image(file).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    try:
        font = ImageFont.truetype("arial.ttf", fontsize)
    except OSError:
        font = ImageFont.load_default()

    alpha = int(255 * opacity / 100)
    fill = (255, 255, 255, alpha)

    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

    if position == "tiled":
        step_x = tw + 60
        step_y = th + 60
        for y in range(0, img.height + step_y, step_y):
            for x in range(0, img.width + step_x, step_x):
                draw.text((x, y), text, fill=fill, font=font)
    else:
        margin = 20
        positions = {
            "center": ((img.width - tw) / 2, (img.height - th) / 2),
            "bottom-right": (img.width - tw - margin, img.height - th - margin),
            "bottom-left": (margin, img.height - th - margin),
            "top-right": (img.width - tw - margin, margin),
            "top-left": (margin, margin),
        }
        pos = positions.get(position, positions["center"])
        draw.text(pos, text, fill=fill, font=font)

    result = Image.alpha_composite(img, overlay).convert("RGB")
    ext = file.filename.rsplit(".", 1)[1].lower() if "." in file.filename else "png"
    fmt_info = FORMAT_MAP.get(ext, FORMAT_MAP["png"])
    buf = image_to_bytes(result, fmt_info[0])
    name = file.filename.rsplit(".", 1)[0] + f"_watermarked.{fmt_info[2]}"
    return buf, fmt_info[1], name

def process_exif(file, action="view"):
    img = get_pil_image(file)
    if action == "view":
        exif_data = {}
        raw_exif = img._getexif()
        if raw_exif:
            for tag_id, value in raw_exif.items():
                tag_name = TAGS.get(tag_id, tag_id)
                if isinstance(value, bytes):
                    try:
                        value = value.decode("utf-8", errors="replace")
                    except Exception:
                        value = str(value)
                elif not isinstance(value, (str, int, float, list, dict, bool, type(None))):
                    value = str(value)
                exif_data[str(tag_name)] = value
        return exif_data
    else:
        cleaned = Image.new(img.mode, img.size)
        cleaned.putdata(list(img.getdata()))
        ext = file.filename.rsplit(".", 1)[1].lower() if "." in file.filename else "png"
        fmt_info = FORMAT_MAP.get(ext, FORMAT_MAP["png"])
        buf = image_to_bytes(cleaned, fmt_info[0])
        name = file.filename.rsplit(".", 1)[0] + f"_clean.{fmt_info[2]}"
        return buf, fmt_info[1], name

def process_favicon(file, size_opt="all"):
    size_map = {
        "all": [16, 32, 48, 64, 128, 256],
        "standard": [16, 32, 48],
        "16": [16],
        "32": [32],
    }
    sizes = size_map.get(size_opt, size_map["all"])
    img = get_pil_image(file).convert("RGBA")
    icons = [img.resize((s, s), Image.LANCZOS) for s in sizes]
    buf = io.BytesIO()
    icons[0].save(buf, format="ICO", sizes=[(s, s) for s in sizes],
                  append_images=icons[1:] if len(icons) > 1 else [])
    buf.seek(0)
    return buf, "image/x-icon", "favicon.ico"

def process_animated(file, target="webp", quality=80, fps_override=0, lossless=False):
    src = Image.open(io.BytesIO(file.read()))
    frames = []
    durations = []
    try:
        while True:
            frame = src.copy()
            if frame.mode == "P":
                frame = frame.convert("RGBA")
            frames.append(frame)
            durations.append(src.info.get("duration", 100))
            src.seek(src.tell() + 1)
    except EOFError:
        pass

    if not frames:
        raise ValueError("No frames found in image.")

    if fps_override > 0:
        per_frame_ms = int(1000 / fps_override)
        durations = [per_frame_ms] * len(frames)

    loop = src.info.get("loop", 0)
    buf = io.BytesIO()
    base = file.filename.rsplit(".", 1)[0]

    if target == "webp":
        save_kwargs = {
            "format": "WEBP", "save_all": True, "append_images": frames[1:],
            "duration": durations, "loop": loop, "lossless": lossless,
        }
        if not lossless:
            save_kwargs["quality"] = quality
        frames[0].save(buf, **save_kwargs)
        buf.seek(0)
        return buf, "image/webp", base + ".webp"

    gif_frames = [f.convert("RGBA") for f in frames]
    disposal_frames = []
    for f in gif_frames:
        bg = Image.new("RGBA", f.size, (255, 255, 255, 255))
        bg.paste(f, mask=f.split()[3])
        disposal_frames.append(bg.convert("P", palette=Image.ADAPTIVE, colors=256))

    disposal_frames[0].save(
        buf, format="GIF", save_all=True, append_images=disposal_frames[1:],
        duration=durations, loop=loop, optimize=True, disposal=2,
    )
    buf.seek(0)
    return buf, "image/gif", base + ".gif"

def process_ocr(file):
    if not HAS_TESSERACT:
        raise ImportError("OCR requires 'pytesseract' package.")
    img = get_pil_image(file)
    text = pytesseract.image_to_string(img)
    return text.strip() or "(No text detected in image)"

def process_palette(file, count=8, method="quantize"):
    img = get_pil_image(file).convert("RGBA")
    bg = Image.new("RGB", img.size, (255, 255, 255))
    bg.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
    img = bg

    MAX_DIM = 600
    if max(img.size) > MAX_DIM:
        ratio = MAX_DIM / max(img.size)
        img = img.resize((int(img.width * ratio), int(img.height * ratio)), Image.LANCZOS)

    quant = img.quantize(colors=count, method=Image.Quantize.MEDIANCUT)
    pal_bytes = quant.getpalette()[: count * 3]
    colour_counts = quant.getcolors() or []
    counts_by_index = {idx: cnt for cnt, idx in colour_counts}
    total = sum(counts_by_index.values()) or 1
    palette_list = []
    for i in range(count):
        r, g, b = pal_bytes[i * 3], pal_bytes[i * 3 + 1], pal_bytes[i * 3 + 2]
        palette_list.append({
            "hex": f"#{r:02x}{g:02x}{b:02x}",
            "rgb": [r, g, b],
            "percent": round(counts_by_index.get(i, 0) * 100 / total, 1)
        })
    palette_list.sort(key=lambda p: -p["percent"])
    
    # Build a preview swatch PNG (one column per colour, weighted widths)
    swatch_w, swatch_h = 600, 120
    swatch = Image.new("RGB", (swatch_w, swatch_h), (255, 255, 255))
    draw = ImageDraw.Draw(swatch)
    weights = [max(p["percent"], 3) for p in palette_list]
    total_w = sum(weights)
    x = 0
    for p, w in zip(palette_list, weights):
        seg = int(swatch_w * w / total_w)
        draw.rectangle([x, 0, x + seg, swatch_h], fill=tuple(p["rgb"]))
        x += seg
    if x < swatch_w:
        draw.rectangle([x, 0, swatch_w, swatch_h], fill=tuple(palette_list[-1]["rgb"]))

    swatch_buf = io.BytesIO()
    swatch.save(swatch_buf, format="PNG")
    import base64
    swatch_b64 = base64.b64encode(swatch_buf.getvalue()).decode()
    
    return palette_list, swatch_b64

def process_svg_to_png(file, width=0, transparent=True):
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPM
    
    svg_bytes = file.read()
    svg_stream = io.BytesIO(svg_bytes)
    drawing = svg2rlg(svg_stream)
    if drawing is None:
        raise ValueError("SVG parser returned no drawing — is the file valid?")

    if width > 0 and drawing.width > 0:
        scale = width / drawing.width
        drawing.width *= scale
        drawing.height *= scale
        drawing.scale(scale, scale)

    png_bytes = renderPM.drawToString(drawing, fmt="PNG", bg=0xffffff)
    
    if transparent:
        img = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
        datas = img.getdata()
        new_data = [
            (r, g, b, 0) if (r, g, b) == (255, 255, 255) else (r, g, b, a)
            for (r, g, b, a) in datas
        ]
        img.putdata(new_data)
        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        buf.seek(0)
        out_bytes = buf.getvalue()
    else:
        out_bytes = png_bytes

    name = file.filename.rsplit(".", 1)[0] + ".png"
    return io.BytesIO(out_bytes), "image/png", name

def process_svg_optimize(file, strip_comments=True, strip_metadata=True, collapse_ws=True, decimals=3):
    import re
    raw = file.read()
    try:
        svg = raw.decode("utf-8")
    except UnicodeDecodeError:
        svg = raw.decode("utf-8", errors="ignore")

    original_size = len(raw)

    if strip_comments:
        svg = re.sub(r"<!--[\s\S]*?-->", "", svg)

    if strip_metadata:
        for tag in ("metadata", "title", "desc"):
            svg = re.sub(rf"<{tag}\b[^>]*>[\s\S]*?</{tag}>", "", svg, flags=re.IGNORECASE)
            svg = re.sub(rf"<{tag}\b[^/]*/>", "", svg, flags=re.IGNORECASE)
        svg = re.sub(r"\s+(sodipodi|inkscape|adobe|sketch):[a-zA-Z_-]+\s*=\s*\"[^\"]*\"", "", svg)
        svg = re.sub(r"\s+xmlns:(sodipodi|inkscape|adobe|sketch)\s*=\s*\"[^\"]*\"", "", svg)

    def _round(m):
        num = float(m.group(0))
        if num == int(num):
            return str(int(num))
        s = f"{num:.{decimals}f}".rstrip("0").rstrip(".")
        return s or "0"
    svg = re.sub(r"-?\d+\.\d+", _round, svg)

    if collapse_ws:
        svg = re.sub(r">\s+<", "><", svg)
        svg = re.sub(r"\s{2,}", " ", svg)
        svg = svg.strip()

    optimized_bytes = svg.encode("utf-8")
    saved_pct = round((original_size - len(optimized_bytes)) * 100 / original_size, 1) if original_size else 0
    name = file.filename.rsplit(".", 1)[0] + "_optimized.svg"
    
    return io.BytesIO(optimized_bytes), "image/svg+xml", name, original_size, len(optimized_bytes), saved_pct
