import io
import fitz
from PIL import Image
from utils.file_utils import make_zip

PDF_ACCEPT = "application/pdf"

PAPER_SIZES = {
    "a4": (595.28, 841.89),
    "letter": (612, 792),
    "a3": (841.89, 1190.55),
    "a5": (419.53, 595.28),
    "legal": (612, 1008),
}

def parse_page_ranges(spec: str, total: int) -> list[int]:
    if not spec.strip():
        return list(range(total))
    pages = set()
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            try:
                start, end = part.split("-", 1)
                s = max(1, int(start.strip()))
                e = min(total, int(end.strip()))
                pages.update(range(s - 1, e))
            except ValueError: continue
        else:
            try:
                p = int(part.strip()) - 1
                if 0 <= p < total: pages.add(p)
            except ValueError: continue
    return sorted(pages)

def process_pdf_merge(files):
    result = fitz.open()
    for f in files:
        doc = fitz.open(stream=f.read(), filetype="pdf")
        result.insert_pdf(doc)
        doc.close()
    output = io.BytesIO()
    result.save(output)
    result.close()
    output.seek(0)
    return output, "application/pdf", "merged.pdf"

def process_pdf_split(file, page_spec=""):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    pages = parse_page_ranges(page_spec, len(doc))
    
    if not pages:
        raise ValueError("No valid pages selected.")

    if len(pages) == 1:
        single = fitz.open()
        single.insert_pdf(doc, from_page=pages[0], to_page=pages[0])
        output = io.BytesIO()
        single.save(output)
        single.close()
        doc.close()
        output.seek(0)
        return output, "application/pdf", f"page_{pages[0]+1}.pdf"

    parts = []
    for p in pages:
        part = fitz.open()
        part.insert_pdf(doc, from_page=p, to_page=p)
        buf = io.BytesIO()
        part.save(buf)
        part.close()
        parts.append((f"page_{p + 1}.pdf", buf.getvalue()))

    doc.close()
    zip_buf = make_zip(parts)
    return zip_buf, "application/zip", "split_pages.zip"

def process_pdf_compress(file, quality="medium"):
    image_quality = {"low": 40, "medium": 75, "high": 90}.get(quality, 75)
    max_dim = {"low": 1200, "medium": 2000, "high": 9999}.get(quality, 2000)

    doc = fitz.open(stream=file.read(), filetype="pdf")
    if quality != "high":
        processed_xrefs = set()
        for page in doc:
            for img_info in page.get_images(full=True):
                xref = img_info[0]
                if xref in processed_xrefs: continue
                processed_xrefs.add(xref)
                try:
                    base_image = doc.extract_image(xref)
                    if not base_image: continue
                    pil_img = Image.open(io.BytesIO(base_image["image"]))
                    if pil_img.mode not in ("RGB", "L"):
                        pil_img = pil_img.convert("RGB")

                    if max(pil_img.size) > max_dim:
                        pil_img.thumbnail((max_dim, max_dim), Image.LANCZOS)

                    buf = io.BytesIO()
                    pil_img.save(buf, format="JPEG", quality=image_quality, optimize=True)
                    page.replace_image(xref, stream=buf.getvalue())
                except Exception: continue

    output = io.BytesIO()
    doc.save(output, garbage=4, deflate=True, clean=True)
    doc.close()
    output.seek(0)
    name = file.filename.rsplit(".", 1)[0] + "_compressed.pdf"
    return output, "application/pdf", name

def process_pdf_rotate(file, angle=90, page_spec=""):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    pages = parse_page_ranges(page_spec, len(doc))
    for p in pages:
        doc[p].set_rotation((doc[p].rotation + angle) % 360)
    output = io.BytesIO()
    doc.save(output)
    doc.close()
    output.seek(0)
    name = file.filename.rsplit(".", 1)[0] + "_rotated.pdf"
    return output, "application/pdf", name

def process_pdf_resize(file, mode="scale", scale=100, paper="a4"):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    new_doc = fitz.open()

    if mode == "scale":
        s = float(scale) / 100.0
        if s <= 0: raise ValueError("Scale must be greater than 0.")
        for page in doc:
            r = page.rect
            new_page = new_doc.new_page(width=r.width * s, height=r.height * s)
            new_page.show_pdf_page(new_page.rect, doc, page.number, rotate=page.rotation)
    else:
        target_w, target_h = PAPER_SIZES.get(paper, PAPER_SIZES["a4"])
        for page in doc:
            r = page.rect
            src_w, src_h = r.width, r.height
            if (src_w > src_h) != (target_w > target_h):
                pw, ph = target_h, target_w
            else:
                pw, ph = target_w, target_h
            fit = min(pw / src_w, ph / src_h)
            cw, ch = src_w * fit, src_h * fit
            x0, y0 = (pw - cw) / 2, (ph - ch) / 2
            new_page = new_doc.new_page(width=pw, height=ph)
            new_page.show_pdf_page(fitz.Rect(x0, y0, x0 + cw, y0 + ch), doc, page.number, rotate=page.rotation)

    output = io.BytesIO()
    new_doc.save(output, garbage=4, deflate=True)
    new_doc.close()
    doc.close()
    output.seek(0)
    name = file.filename.rsplit(".", 1)[0] + "_resized.pdf"
    return output, "application/pdf", name

def process_pdf_page_numbers(file, position="bottom-center", start=1, fontsize=11):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    for i, page in enumerate(doc):
        num = start + i
        r = page.rect
        margin = 36
        pos_map = {
            "bottom-center": fitz.Point(r.width / 2, r.height - margin),
            "bottom-right": fitz.Point(r.width - margin, r.height - margin),
            "bottom-left": fitz.Point(margin, r.height - margin),
            "top-center": fitz.Point(r.width / 2, margin + fontsize),
            "top-right": fitz.Point(r.width - margin, margin + fontsize),
            "top-left": fitz.Point(margin, margin + fontsize),
        }
        point = pos_map.get(position, pos_map["bottom-center"])
        # align = 1 if "center" in position else (2 if "right" in position else 0)
        page.insert_text(point, str(num), fontsize=fontsize, fontname="helv", color=(0.3, 0.3, 0.3))
    output = io.BytesIO()
    doc.save(output)
    doc.close()
    output.seek(0)
    name = file.filename.rsplit(".", 1)[0] + "_numbered.pdf"
    return output, "application/pdf", name

def process_pdf_extract_images(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    images = []
    for i, page in enumerate(doc):
        for img_idx, img_info in enumerate(page.get_images(full=True)):
            xref = img_info[0]
            try:
                base_image = doc.extract_image(xref)
                if not base_image: continue
                ext = base_image.get("ext", "png")
                images.append((f"page{i+1}_img{img_idx+1}.{ext}", base_image["image"]))
            except Exception: continue
    doc.close()
    if not images: raise ValueError("No images found in the PDF.")
    
    if len(images) == 1:
        ext = images[0][0].rsplit(".", 1)[1]
        mime = f"image/{'jpeg' if ext in ('jpg','jpeg') else ext}"
        return io.BytesIO(images[0][1]), mime, images[0][0]
    
    zip_buf = make_zip(images)
    name = file.filename.rsplit(".", 1)[0] + "_images.zip"
    return zip_buf, "application/zip", name

def process_pdf_protect(file, user_pw, owner_pw=""):
    if not owner_pw: owner_pw = user_pw
    doc = fitz.open(stream=file.read(), filetype="pdf")
    perm = fitz.PDF_PERM_PRINT | fitz.PDF_PERM_COPY
    output = io.BytesIO()
    doc.save(output, encryption=fitz.PDF_ENCRYPT_AES_256, user_pw=user_pw, owner_pw=owner_pw, permissions=perm)
    doc.close()
    output.seek(0)
    name = file.filename.rsplit(".", 1)[0] + "_protected.pdf"
    return output, "application/pdf", name

def process_pdf_sign(file, sig_file, position="bottom-right", sig_width=140, margin=36, opacity=100, page_spec=""):
    sig_img = Image.open(sig_file).convert("RGBA")
    if opacity < 100:
        r, g, b, a = sig_img.split()
        a = a.point(lambda v: int(v * opacity / 100.0))
        sig_img = Image.merge("RGBA", (r, g, b, a))
    
    sig_buf = io.BytesIO()
    sig_img.save(sig_buf, format="PNG")
    sig_bytes = sig_buf.getvalue()
    sig_ratio = sig_img.height / sig_img.width if sig_img.width else 1.0
    sig_h = sig_width * sig_ratio

    doc = fitz.open(stream=file.read(), filetype="pdf")
    target = parse_page_ranges(page_spec, len(doc))
    if not target: raise ValueError("No valid pages selected.")

    for pno in target:
        page = doc[pno]
        r = page.rect
        x0 = r.width - margin - sig_width if "right" in position else ((r.width - sig_width) / 2 if "center" in position else margin)
        y0 = r.height - margin - sig_h if "bottom" in position else margin
        page.insert_image(fitz.Rect(x0, y0, x0 + sig_width, y0 + sig_h), stream=sig_bytes, keep_proportion=True, overlay=True)

    output = io.BytesIO()
    doc.save(output, garbage=4, deflate=True)
    doc.close()
    output.seek(0)
    name = file.filename.rsplit(".", 1)[0] + "_signed.pdf"
    return output, "application/pdf", name

def process_pdf_unlock(file, password=""):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    if doc.needs_pass:
        if not doc.authenticate(password):
            doc.close()
            raise ValueError("Incorrect password.")
    output = io.BytesIO()
    doc.save(output)
    doc.close()
    output.seek(0)
    name = file.filename.rsplit(".", 1)[0] + "_unlocked.pdf"
    return output, "application/pdf", name

def process_pdf_read_fields(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    fields = []
    for page in doc:
        for field in page.widgets():
            if field.field_name and field.field_name not in [f["name"] for f in fields]:
                fields.append({"name": field.field_name, "type": field.field_type_string, "value": field.field_value})
    doc.close()
    return fields

def process_pdf_fill_form(file, form_data):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    for page in doc:
        for field in page.widgets():
            if field.field_name in form_data:
                field.field_value = str(form_data[field.field_name])
                field.update()
    output = io.BytesIO()
    doc.save(output)
    doc.close()
    output.seek(0)
    name = file.filename.rsplit(".", 1)[0] + "_filled.pdf"
    return output, "application/pdf", name
