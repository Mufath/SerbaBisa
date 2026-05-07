"""
fix_i18n_all.py — One-time batch fixer for SerbaBisa localization.
Fixes all hardcoded titles/h1s in templates and adds missing keys to locales.py.
Run once: python fix_i18n_all.py
"""
import os
import re

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates", "tools")

# ──────────────────────────────────────────────────────────────
# Mapping: filename → { key, id, en }
# key  = the _t() key to use
# id   = Indonesian text for UI_STRINGS["id"]
# en   = English text for UI_STRINGS["en"]
# ──────────────────────────────────────────────────────────────
TEMPLATE_TITLE_MAP = {
    "base64.html":              {"key": "Base64 Title",         "id": "Base64 Encode / Decode", "en": "Base64 Encode / Decode"},
    "calculator.html":          {"key": "Calculator Title",     "id": "Kalkulator",             "en": "Calculator"},
    "color_converter.html":     {"key": "Color Converter Title","id": "Konversi Warna",         "en": "Color Converter"},
    "cron_parser.html":         {"key": "Cron Parser Title",    "id": "Parser Cron",            "en": "Cron Expression Parser"},
    "css_formatter.html":       {"key": "Css Formatter",        "id": "Perapih CSS",            "en": "CSS Formatter"},
    "csv_json.html":            {"key": "CSV JSON Title",       "id": "Konverter CSV / JSON",   "en": "CSV / JSON Converter"},
    "hash_generator.html":      {"key": "Hash Generator Title", "id": "Pembuat Hash",           "en": "Hash Generator"},
    "html_formatter.html":      {"key": "HTML Formatter",       "id": "Perapih HTML",           "en": "HTML Formatter"},
    "js_formatter.html":        {"key": "Js Formatter",         "id": "Perapih JS",             "en": "JS Formatter"},
    "json_formatter.html":      {"key": "JSON Formatter Title", "id": "Perapih JSON",           "en": "JSON Formatter"},
    "json_yaml.html":           {"key": "JSON YAML Title",      "id": "Konverter JSON / YAML",  "en": "JSON / YAML Converter"},
    "jsonpath_tester.html":     {"key": "JSONPath Title",       "id": "Tester JSONPath",        "en": "JSONPath Tester"},
    "jwt_decoder.html":         {"key": "JWT Decoder Title",    "id": "Dekoder JWT",            "en": "JWT Decoder"},
    "lorem_ipsum.html":         {"key": "Lorem Ipsum Title",    "id": "Generator Lorem Ipsum",  "en": "Lorem Ipsum Generator"},
    "markdown_preview.html":    {"key": "Markdown Preview Title","id": "Pratinjau Markdown",    "en": "Markdown Preview"},
    "md_to_docx.html":          {"key": "Md To Docx Title",     "id": "Markdown ke Word",       "en": "Markdown to Word"},
    "md_to_pdf.html":           {"key": "Md To PDF Title",      "id": "Markdown ke PDF",        "en": "Markdown to PDF"},
    "number_base.html":         {"key": "Number Base Title",    "id": "Konverter Basis Bilangan","en": "Number Base Converter"},
    "password_generator.html":  {"key": "Password Gen Title",   "id": "Pembuat Password",       "en": "Password Generator"},
    "percentage_calc.html":     {"key": "Percentage Calc Title","id": "Kalkulator Persentase",   "en": "Percentage Calculator"},
    "pomodoro.html":            {"key": "Pomodoro Title",       "id": "Timer Pomodoro",          "en": "Pomodoro Timer"},
    "regex_tester.html":        {"key": "Regex Tester Title",   "id": "Uji Regex",               "en": "Regex Tester"},
    "slug_generator.html":      {"key": "Slug Gen Title",       "id": "Pembuat Slug",            "en": "Slug Generator"},
    "text_diff.html":           {"key": "Text Diff Title",      "id": "Bandingkan Teks",         "en": "Text Diff"},
    "timestamp_converter.html": {"key": "Timestamp Title",      "id": "Konverter Timestamp",     "en": "Timestamp Converter"},
    "url_encode.html":          {"key": "URL Encode Title",     "id": "URL Encoder / Decoder",   "en": "URL Encoder / Decoder"},
    "user_agent_parser.html":   {"key": "User Agent Title",     "id": "Parser User-Agent",       "en": "User-Agent Parser"},
    "uuid_generator.html":      {"key": "UUID Gen Title",       "id": "Generator UUID",          "en": "UUID Generator"},
    "word_counter.html":        {"key": "Word Counter Title",   "id": "Penghitung Kata",         "en": "Word Counter"},
}

# ──────────────────────────────────────────────────────────────
# Additional hardcoded strings found in specific templates
# Each entry: (filename, old_text, new_text)
# ──────────────────────────────────────────────────────────────
EXTRA_KEYS_NEEDED = {
    # base64.html
    "Plain Text Label":         {"id": "Teks Biasa",               "en": "Plain Text"},
    "Error Label":              {"id": "Galat",                    "en": "Error"},
    "Invalid Base64":           {"id": "Format Base64 tidak valid", "en": "Invalid Base64 format"},
    # color_converter.html
    "CSS Code Label":           {"id": "Kode CSS (Tinggal Copy)",   "en": "CSS Code (Copy Ready)"},
    "Copy Code":                {"id": "Salin Kode",               "en": "Copy Code"},
    "RGB Format Label":         {"id": "Format RGB",               "en": "RGB Format"},
    "HSL Format Label":         {"id": "Format HSL",               "en": "HSL Format"},
    # cron_parser.html
    "Expression Label":         {"id": "Ekspresi:",                "en": "Expression:"},
    "Check Schedule":           {"id": "Cek Jadwal",               "en": "Check Schedule"},
    "Weekday 9am":              {"id": "Hari kerja jam 9 pagi",    "en": "Weekdays at 9 AM"},
    "Schedule Description":     {"id": "Deskripsi Jadwal",         "en": "Schedule Description"},
    "Next Schedules":           {"id": "Jadwal Jalan Berikutnya",  "en": "Next Scheduled Runs"},
    "Enter Cron First":         {"id": "Masukin dulu ekspresi cron-nya.", "en": "Please enter a cron expression."},
    "Checking":                 {"id": "Lagi ngecek...",           "en": "Checking..."},
    "Expression Invalid":       {"id": "Waduh, kodenya salah",    "en": "Invalid expression"},
    "Expression Valid":         {"id": "Ekspresi valid!",          "en": "Expression valid!"},
    "Network Error":            {"id": "Ada masalah jaringan",     "en": "Network error"},
    # password_generator.html
    "Click To Copy":            {"id": "Klik buat nyalin",        "en": "Click to copy"},
    "Select At Least One":      {"id": "Pilih minimal satu opsi", "en": "Select at least one option"},
    "Strength Weak":            {"id": "Lemah",                   "en": "Weak"},
    "Strength Fair":            {"id": "Lumayan",                 "en": "Fair"},
    "Strength Strong":          {"id": "Kuat",                    "en": "Strong"},
    "Strength Very Strong":     {"id": "Kuat Banget",             "en": "Very Strong"},
    "Security Label":           {"id": "Keamanan",                "en": "Security"},
    "Bits Entropy":             {"id": "bits entropi",            "en": "bits of entropy"},
    # json_formatter.html
    "JSON Formatter Title":     {"id": "Perapih JSON",             "en": "JSON Formatter"},
    "JSON Input Label":         {"id": "Input JSON",               "en": "JSON Input"},
    "Paste Raw JSON":           {"id": "Tempelkan JSON mentah di sini...", "en": "Paste raw JSON here..."},
    "JSON Valid Formatted":     {"id": "JSON Valid & Berhasil Dirapikan",  "en": "JSON Valid & Formatted"},
    "JSON Valid Minified":      {"id": "JSON Valid (Minified)",    "en": "JSON Valid (Minified)"},
    # calculator.html
    "Calculator Title":         {"id": "Kalkulator",              "en": "Calculator"},
    "Not Valid":                {"id": "Tidak valid",             "en": "Not valid"},
    # csv_json.html — already has good _t usage, title only
    "CSV JSON Title":           {"id": "Konverter CSV / JSON",    "en": "CSV / JSON Converter"},
    # pomodoro — mostly good, title only
    "Pomodoro Title":           {"id": "Timer Pomodoro",          "en": "Pomodoro Timer"},
    # Other titles
    "Base64 Title":             {"id": "Base64 Encode / Decode",  "en": "Base64 Encode / Decode"},
    "Color Converter Title":    {"id": "Konversi Warna",          "en": "Color Converter"},
    "Cron Parser Title":        {"id": "Parser Cron",             "en": "Cron Expression Parser"},
    "Hash Generator Title":     {"id": "Pembuat Hash",            "en": "Hash Generator"},
    "JSON YAML Title":          {"id": "Konverter JSON / YAML",   "en": "JSON / YAML Converter"},
    "JSONPath Title":           {"id": "Tester JSONPath",         "en": "JSONPath Tester"},
    "JWT Decoder Title":        {"id": "Dekoder JWT",             "en": "JWT Decoder"},
    "Lorem Ipsum Title":        {"id": "Generator Lorem Ipsum",   "en": "Lorem Ipsum Generator"},
    "Markdown Preview Title":   {"id": "Pratinjau Markdown",      "en": "Markdown Preview"},
    "Md To Docx Title":         {"id": "Markdown ke Word",        "en": "Markdown to Word"},
    "Md To PDF Title":          {"id": "Markdown ke PDF",         "en": "Markdown to PDF"},
    "Number Base Title":        {"id": "Konverter Basis Bilangan","en": "Number Base Converter"},
    "Password Gen Title":       {"id": "Pembuat Password",        "en": "Password Generator"},
    "Percentage Calc Title":    {"id": "Kalkulator Persentase",   "en": "Percentage Calculator"},
    "Regex Tester Title":       {"id": "Uji Regex",              "en": "Regex Tester"},
    "Slug Gen Title":           {"id": "Pembuat Slug",           "en": "Slug Generator"},
    "Text Diff Title":          {"id": "Bandingkan Teks",        "en": "Text Diff"},
    "Timestamp Title":          {"id": "Konverter Timestamp",    "en": "Timestamp Converter"},
    "URL Encode Title":         {"id": "URL Encoder / Decoder",  "en": "URL Encoder / Decoder"},
    "User Agent Title":         {"id": "Parser User-Agent",      "en": "User-Agent Parser"},
    "UUID Gen Title":           {"id": "Generator UUID",         "en": "UUID Generator"},
    "Word Counter Title":       {"id": "Penghitung Kata",        "en": "Word Counter"},
}


def fix_template_titles():
    """Fix block title, top_title, and h1 in all templates."""
    fixed = 0
    for filename, info in TEMPLATE_TITLE_MAP.items():
        filepath = os.path.join(TEMPLATES_DIR, filename)
        if not os.path.exists(filepath):
            print(f"  SKIP {filename} (not found)")
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        original = content
        key = info["key"]
        t_call = "{{ _t('" + key + "') }}"

        # Fix {% block title %}XXX - SerbaBisa{% endblock %}
        content = re.sub(
            r'\{%\s*block title\s*%\}.*?-\s*SerbaBisa\s*\{%\s*endblock\s*%\}',
            f'{{% block title %}}{t_call} - SerbaBisa{{% endblock %}}',
            content
        )

        # Fix {% block top_title %}XXX{% endblock %}
        content = re.sub(
            r'\{%\s*block top_title\s*%\}.*?\{%\s*endblock\s*%\}',
            f'{{% block top_title %}}{t_call}{{% endblock %}}',
            content
        )

        # Fix <h1>XXX</h1> (only the first one in tool-header)
        # Match h1 that does NOT already contain {{ _t or {{ translate
        content = re.sub(
            r'(<h1>)(?!\s*\{\{)(.*?)(</h1>)',
            r'\1' + t_call + r'\3',
            content,
            count=1
        )

        if content != original:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            fixed += 1
            print(f"  [OK] {filename} -- title/h1 fixed -> _t('{key}')")
        else:
            print(f"  [SKIP] {filename} -- already OK")
    
    print(f"\n  Fixed {fixed} template titles.\n")


def generate_locales_additions():
    """Generate the text to add to locales.py for missing keys."""
    # Combine title keys and extra keys
    all_keys = {}
    for info in TEMPLATE_TITLE_MAP.values():
        all_keys[info["key"]] = {"id": info["id"], "en": info["en"]}
    all_keys.update(EXTRA_KEYS_NEEDED)

    print("\n" + "="*70)
    print("KEYS TO ADD TO locales.py UI_STRINGS")
    print("="*70)
    
    print('\n# -- Add these to UI_STRINGS["id"] --')
    for key, vals in sorted(all_keys.items()):
        escaped_val = vals["id"].replace('"', '\\"')
        print(f'        "{key}": "{escaped_val}",')
    
    print('\n# -- Add these to UI_STRINGS["en"] --')
    for key, vals in sorted(all_keys.items()):
        escaped_val = vals["en"].replace('"', '\\"')
        print(f'        "{key}": "{escaped_val}",')

    return all_keys


if __name__ == "__main__":
    print("="*70)
    print("SerbaBisa i18n Batch Fixer")
    print("="*70)
    
    print("\n[1/2] Fixing template titles and h1 tags...")
    fix_template_titles()
    
    print("[2/2] Generating locales.py additions...")
    all_keys = generate_locales_additions()
    
    print(f"\nTotal new keys needed: {len(all_keys)}")
    print("\nDone! Now manually:")
    print("  1. Add the keys above to locales.py")
    print("  2. Fix special cases (json_formatter, password_generator, etc.)")
