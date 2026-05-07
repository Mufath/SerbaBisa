import os
import tempfile
import shutil
import mimetypes
from flask import Blueprint, render_template, request, jsonify, send_file, after_this_request
from locales import m

bp = Blueprint("download", __name__)

_DISCLAIMER_ID = (
    "<p style='color:var(--text-light);font-size:0.85rem;'>"
    "<strong>Catatan:</strong> Mengunduh konten yang dilindungi hak cipta untuk distribusi adalah ilegal. "
    "Gunakan hanya untuk keperluan pribadi yang sah.</p>"
)
_DISCLAIMER_EN = (
    "<p style='color:var(--text-light);font-size:0.85rem;'>"
    "<strong>Note:</strong> Downloading copyrighted content for distribution is illegal. "
    "Use only for legitimate personal purposes.</p>"
)
_SUPPORTED_ID = "<p>Mendukung YouTube, TikTok, Instagram, Twitter/X, Facebook, Vimeo, Reddit, dan ribuan platform lainnya.</p>"
_SUPPORTED_EN = "<p>Supports YouTube, TikTok, Instagram, Twitter/X, Facebook, Vimeo, Reddit, and thousands of other platforms.</p>"


def _disclaimer():
    from locales import get_lang
    lang = get_lang()
    return (_SUPPORTED_EN if lang == "en" else _SUPPORTED_ID) + (_DISCLAIMER_EN if lang == "en" else _DISCLAIMER_ID)


def _handle_ytdlp_error(e):
    msg = str(e)
    if "Video unavailable" in msg or "This video is not available" in msg:
        return jsonify(error=m("Video is unavailable or has been deleted.")), 400
    if "Private video" in msg:
        return jsonify(error=m("This video is private and cannot be downloaded.")), 400
    if "Sign in" in msg or "age" in msg.lower():
        return jsonify(error=m("This video requires login (age-restricted) and cannot be downloaded.")), 400
    if "HTTP Error 404" in msg:
        return jsonify(error=m("Content not found (404). Make sure the link is still valid.")), 400
    clean = msg.split("\n")[0][:200]
    return jsonify(error=m("Download failed: {msg}", msg=clean)), 400


def _send_largest_file(tmpdir, filename_filter=None):
    all_files = os.listdir(tmpdir)
    if not all_files:
        return None, None
    if filename_filter:
        all_files = [f for f in all_files if filename_filter(f)]
    if not all_files:
        return None, None
    filename = max(all_files, key=lambda f: os.path.getsize(os.path.join(tmpdir, f)))
    filepath = os.path.join(tmpdir, filename)

    @after_this_request
    def cleanup(response):
        shutil.rmtree(tmpdir, ignore_errors=True)
        return response

    mime = mimetypes.guess_type(filepath)[0] or "application/octet-stream"
    return filepath, (filename, mime)


def _validate_url(url):
    if not url:
        return m("URL cannot be empty!")
    if not url.startswith(("http://", "https://")):
        return m("Invalid URL. Make sure it starts with https://")
    return None


# ── Pengunduh Video ──────────────────────────────────────

@bp.route("/video", methods=["GET", "POST"])
def download_video():
    if request.method == "GET":
        return render_template(
            "upload_tool.html",
            title="Pengunduh Video",
            description="Unduh video dari YouTube, TikTok, Instagram, dan platform lainnya",
            notes=_disclaimer(),
            endpoint="/download/video",
            text_input=True,
            text_label="Video Link",
            text_placeholder="YouTube TikTok Example",
            options=[
                {
                    "type": "select",
                    "name": "quality",
                    "label": "Video Quality",
                    "default": "best",
                    "choices": [
                        {"value": "best",  "label": "Best Automatic"},
                        {"value": "1080",  "label": "Full HD (1080p)"},
                        {"value": "720",   "label": "HD (720p)"},
                        {"value": "480",   "label": "SD (480p)"},
                        {"value": "360",   "label": "Low (360p)"},
                    ],
                },
            ],
            button_text="Download Video",
        )

    url = request.form.get("text", "").strip()
    err = _validate_url(url)
    if err:
        return jsonify(error=err), 400

    quality = request.form.get("quality", "best")

    if quality == "best":
        fmt_str = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best[ext=mp4]/best"
    else:
        fmt_str = (
            f"bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/"
            f"bestvideo[height<={quality}]+bestaudio/"
            f"best[height<={quality}][ext=mp4]/best[height<={quality}]/best"
        )

    try:
        import yt_dlp
        tmpdir = tempfile.mkdtemp()
        ydl_opts = {
            "format": fmt_str,
            "outtmpl": os.path.join(tmpdir, "%(title).100s.%(ext)s"),
            "merge_output_format": "mp4",
            "quiet": True,
            "no_warnings": True,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)
    except ImportError:
        return jsonify(error=m("Library 'yt-dlp' is not installed. Please run Setup.bat again.")), 500
    except yt_dlp.utils.DownloadError as e:
        shutil.rmtree(tmpdir, ignore_errors=True)
        return _handle_ytdlp_error(e)
    except Exception as e:
        shutil.rmtree(tmpdir, ignore_errors=True)
        return jsonify(error=m("Unexpected error: {e}", e=e)), 500

    filepath, meta = _send_largest_file(tmpdir)
    if not filepath:
        return jsonify(error=m("File failed to download. Try a different link.")), 500

    filename, mime = meta
    return send_file(filepath, mimetype=mime, as_attachment=True, download_name=filename)


# ── Pengunduh Audio ──────────────────────────────────────

@bp.route("/audio", methods=["GET", "POST"])
def download_audio():
    if request.method == "GET":
        return render_template(
            "upload_tool.html",
            title=m("Audio Downloader"),
            description=m("Download audio/music in MP3 format from various platforms"),
            notes=_disclaimer(),
            endpoint="/download/audio",
            text_input=True,
            text_label=m("Audio Link"),
            text_placeholder=m("YouTube TikTok Example"),
            options=[
                {
                    "type": "select",
                    "name": "bitrate",
                    "label": m("Audio Quality Bitrate"),
                    "default": "192",
                    "choices": [
                        {"value": "320", "label": m("Best 320kbps")},
                        {"value": "192", "label": m("Standard 192kbps")},
                        {"value": "128", "label": m("Saver 128kbps")},
                    ],
                },
            ],
            button_text=m("Download Audio MP3"),
        )

    url = request.form.get("text", "").strip()
    err = _validate_url(url)
    if err:
        return jsonify(error=err), 400

    bitrate = request.form.get("bitrate", "192")
    if bitrate not in ("128", "192", "320"):
        bitrate = "192"

    try:
        import yt_dlp
        tmpdir = tempfile.mkdtemp()
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(tmpdir, "%(title).100s.%(ext)s"),
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": bitrate,
            }],
            "quiet": True,
            "no_warnings": True,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)
    except ImportError:
        return jsonify(error=m("Library 'yt-dlp' is not installed. Please run Setup.bat again.")), 500
    except yt_dlp.utils.DownloadError as e:
        shutil.rmtree(tmpdir, ignore_errors=True)
        return _handle_ytdlp_error(e)
    except Exception as e:
        shutil.rmtree(tmpdir, ignore_errors=True)
        return jsonify(error=m("Unexpected error: {e}", e=e)), 500

    filepath, meta = _send_largest_file(
        tmpdir,
        filename_filter=lambda f: f.lower().endswith(".mp3")
    )
    if not filepath:
        filepath, meta = _send_largest_file(tmpdir)
    if not filepath:
        return jsonify(error=m("Audio file failed to download. Make sure FFmpeg is installed for MP3 format.")), 500

    filename, mime = meta
    return send_file(filepath, mimetype=mime or "audio/mpeg", as_attachment=True, download_name=filename)


# ── Pengunduh Gambar ─────────────────────────────────────

@bp.route("/image", methods=["GET", "POST"])
def download_image():
    if request.method == "GET":
        return render_template(
            "upload_tool.html",
            title=m("Image Downloader"),
            description=m("Download photos or thumbnails from social media and video platforms"),
            notes=(
                m("<p>Download images/photos from Instagram posts, YouTube thumbnails, Twitter photos, and more.</p>")
                + _disclaimer()
            ),
            endpoint="/download/image",
            text_input=True,
            text_label=m("Image Post Link"),
            text_placeholder=m("Instagram Example"),
            options=[],
            button_text=m("Download Image"),
        )

    url = request.form.get("text", "").strip()
    err = _validate_url(url)
    if err:
        return jsonify(error=err), 400

    try:
        import yt_dlp
        tmpdir = tempfile.mkdtemp()
        ydl_opts = {
            "skip_download": True,
            "writethumbnail": True,
            "outtmpl": os.path.join(tmpdir, "%(title).100s.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
    except ImportError:
        return jsonify(error=m("Library 'yt-dlp' is not installed. Please run Setup.bat again.")), 500
    except yt_dlp.utils.DownloadError as e:
        shutil.rmtree(tmpdir, ignore_errors=True)
        return _handle_ytdlp_error(e)
    except Exception as e:
        shutil.rmtree(tmpdir, ignore_errors=True)
        return jsonify(error=m("Unexpected error: {e}", e=e)), 500

    img_exts = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
    filepath, meta = _send_largest_file(
        tmpdir,
        filename_filter=lambda f: os.path.splitext(f)[1].lower() in img_exts
    )

    if not filepath:
        thumb = (info or {}).get("thumbnail", "")
        shutil.rmtree(tmpdir, ignore_errors=True)
        if thumb:
            return jsonify(text=m("Image not directly downloadable, but you can access the thumbnail at:\n{thumb}", thumb=thumb))
        return jsonify(error=m("No image/photo available to download from this link.")), 400

    filename, mime = meta
    return send_file(filepath, mimetype=mime or "image/jpeg", as_attachment=True, download_name=filename)
