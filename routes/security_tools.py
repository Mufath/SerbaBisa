import hashlib
import io
from flask import Blueprint, render_template, request, jsonify, send_file
from locales import m

bp = Blueprint("security", __name__)

HASH_ALGOS = ["md5", "sha1", "sha256", "sha512"]


@bp.route("/password-generator")
def password_generator():
    return render_template("tools/password_generator.html")


@bp.route("/hash-generator")
def hash_generator():
    return render_template("tools/hash_generator.html")


@bp.route("/file-hash", methods=["GET", "POST"])
def file_hash():
    if request.method == "GET":
        return render_template(
            "upload_tool.html",
            title="Hash File",
            description="Cek integritas file yang diunggah",
            endpoint="/security/file-hash",
            accept="*",
            multiple=False,
            button_text="Hitung",
        )

    f = request.files.get("files")
    if not f:
        return jsonify({"error": m("No file uploaded.")}), 400

    hashers = {name: hashlib.new(name) for name in HASH_ALGOS}
    total = 0
    chunk_size = 1024 * 1024  # 1 MB
    while True:
        chunk = f.stream.read(chunk_size)
        if not chunk:
            break
        total += len(chunk)
        for h in hashers.values():
            h.update(chunk)

    lines = [f"File:      {f.filename}", f"Size:      {total:,} bytes", ""]
    for name in HASH_ALGOS:
        lines.append(f"{name.upper():<8}   {hashers[name].hexdigest()}")

    return jsonify({"text": "\n".join(lines)})


# ── File Vault ─────────────────────────────────────────

@bp.route("/file-vault", methods=["GET", "POST"])
def file_vault():
    if request.method == "GET":
        return render_template(
            "upload_tool.html",
            title="Brankas File",
            description="Kunci dan sembunyikan file apa saja dengan password",
            notes="<p><strong>Penting:</strong> Kami tidak menyimpan password Anda. Jika Anda lupa, file Anda tidak akan pernah bisa dibuka kembali!</p>",
            endpoint="/security/file-vault",
            accept="*",
            multiple=False,
            options=[
                {"type": "password", "name": "password", "label": "Password", "placeholder": "Masukkan password untuk kunci/buka rahasia", "required": True},
                {"type": "select", "name": "action", "label": "Aksi", "default": "encrypt",
                 "choices": [
                     {"value": "encrypt", "label": "Kunci File (Encrypt)"},
                     {"value": "decrypt", "label": "Buka File (Decrypt)"},
                 ]},
            ],
            button_text="Proses"
        )

    try:
        from cryptography.fernet import Fernet
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        import base64
        import os
    except ImportError:
        return jsonify(error=m("Library 'cryptography' is not installed. Please run Setup.bat again.")), 500

    f = request.files.get("files")
    if not f or not f.filename:
        return jsonify(error=m("Please upload a file first.")), 400

    password_str = request.form.get("password")
    if not password_str:
        return jsonify(error=m("Password is required!")), 400

    action = request.form.get("action", "encrypt")

    salt = b"serbabisa_vault_salt_123"
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password_str.encode("utf-8")))
    f_cipher = Fernet(key)

    file_data = f.read()
    output = io.BytesIO()

    if action == "encrypt":
        try:
            encrypted_data = f_cipher.encrypt(file_data)
            output.write(encrypted_data)
            output.seek(0)
            name = f.filename + ".locked"
        except Exception as e:
            return jsonify(error=m("Encryption failed: {e}", e=e)), 500
    else:
        try:
            decrypted_data = f_cipher.decrypt(file_data)
            output.write(decrypted_data)
            output.seek(0)
            name = f.filename.replace(".locked", "")
            if name == f.filename:
                name = "decrypted_" + f.filename
        except Exception:
            return jsonify(error=m("Wrong password or the file is invalid/corrupted!")), 400

    return send_file(output, as_attachment=True, download_name=name)


# ── Steganography ──────────────────────────────────────

@bp.route("/steganography", methods=["GET", "POST"])
def steganography():
    if request.method == "GET":
        return render_template(
            "upload_tool.html",
            title="Pesan Rahasia Gambar",
            description="Sembunyikan pesan rahasia di dalam gambar biasa tanpa ketahuan",
            notes="<p>Gunakan format <strong>PNG</strong> agar piksel tidak terkompres. Hindari upload JPG yang sudah dimasukkan pesan (karena algoritma kompresi JPG dapat merusak pesan).</p>",
            endpoint="/security/steganography",
            accept=".png,.bmp,.tiff",
            multiple=False,
            options=[
                {"type": "select", "name": "action", "label": "Aksi", "default": "hide",
                 "choices": [
                     {"value": "hide", "label": "Sembunyikan Pesan (Hide)"},
                     {"value": "extract", "label": "Baca Pesan Rahasia (Extract)"},
                 ]},
                {"type": "text", "name": "message", "label": "Pesan (hanya jika menyembunyikan)", "placeholder": "Ketik pesan rahasia di sini...", "depends_on": {"action": "hide"}},
            ],
            button_text="Jalankan"
        )

    f = request.files.get("files")
    if not f or not f.filename:
        return jsonify(error=m("Please upload an image.")), 400

    action = request.form.get("action", "hide")

    try:
        from PIL import Image
        img = Image.open(io.BytesIO(f.read()))
    except Exception:
        return jsonify(error=m("Invalid image file.")), 400

    if img.mode != "RGB":
        img = img.convert("RGB")

    if action == "hide":
        msg = request.form.get("message", "")
        if not msg:
            return jsonify(error=m("Secret message cannot be empty.")), 400

        msg += "#####"  # End of message marker
        msg_bytes = msg.encode("utf-8")
        binary_msg = "".join([format(b, "08b") for b in msg_bytes])

        pixels = img.load()
        width, height = img.size

        if len(binary_msg) > width * height * 3:
            return jsonify(error=m("Message is too long for this image size.")), 400

        msg_idx = 0
        for y in range(height):
            for x in range(width):
                if msg_idx >= len(binary_msg):
                    break
                r, g, b = pixels[x, y]
                if msg_idx < len(binary_msg):
                    r = (r & ~1) | int(binary_msg[msg_idx]); msg_idx += 1
                if msg_idx < len(binary_msg):
                    g = (g & ~1) | int(binary_msg[msg_idx]); msg_idx += 1
                if msg_idx < len(binary_msg):
                    b = (b & ~1) | int(binary_msg[msg_idx]); msg_idx += 1
                pixels[x, y] = (r, g, b)
            if msg_idx >= len(binary_msg):
                break

        output = io.BytesIO()
        img.save(output, format="PNG")
        output.seek(0)
        name = f.filename.rsplit(".", 1)[0] + "_secret.png"
        return send_file(output, mimetype="image/png", as_attachment=True, download_name=name)

    elif action == "extract":
        pixels = img.load()
        width, height = img.size
        binary_chunk = ""
        decoded_msg = ""
        marker = "#####"

        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                for bit in [r & 1, g & 1, b & 1]:
                    binary_chunk += str(bit)
                    if len(binary_chunk) == 8:
                        char = chr(int(binary_chunk, 2))
                        decoded_msg += char
                        binary_chunk = ""
                        if decoded_msg.endswith(marker):
                            prefix = m("Your Secret Message:\n")
                            return jsonify(text=prefix + decoded_msg[:-len(marker)])
                if len(decoded_msg) > 100000:
                    return jsonify(text=m("Message is too long or there is no secret message."))

        return jsonify(text=m("No secret message found in this image."))
