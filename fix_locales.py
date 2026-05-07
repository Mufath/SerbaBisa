import os

path = r'd:\Mufath\Project\SerbaBisa\locales.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace keys
content = content.replace('"tidy_format"', '"Tidy Format"')
content = content.replace('"tidy_beautify"', '"Tidy Beautify"')
content = content.replace('"minify_compress"', '"Minify Compress"')
content = content.replace('"json_example"', '"JSON Example"')
content = content.replace('"desc_json_formatter"', '"Desc JSON Formatter"')
content = content.replace('"desc_hash_gen"', '"Desc Hash Gen"')
content = content.replace('"desc_js_formatter"', '"Desc Js Formatter"')
content = content.replace('"start_date_ddmmyyyy"', '"Start Date Ddmmyyyy"')
content = content.replace('"rgb_format"', '"RGB Format"')
content = content.replace('"hsl_format"', '"HSL Format"')
content = content.replace('"keyword_case"', '"Keyword Case"')
content = content.replace('"invalid_base64_format"', '"Invalid Base64 Format"')

# Insert new keys if missing
if '"Activate"' not in content:
    # Add after "Process Now"
    content = content.replace('"Process Now": "Proses Sekarang",', '"Process Now": "Proses Sekarang",\n        "Activate": "Aktifkan",')
    content = content.replace('"Process Now": "Process Now",', '"Process Now": "Process Now",\n        "Activate": "Activate",')

# Let's ensure tidy_format is in EN as well
if '"Tidy Format":' not in content.split('"en":')[1]:
    en_replacements = """
        "Tidy Format": "Tidy (Format)",
        "Tidy Beautify": "Tidy (Beautify)",
        "Minify Compress": "Compress (Minify)",
        "JSON Example": 'Example: {"name":"Fath","campus":"UNAIR"}',
        "Desc JSON Formatter": 'Tidy up (Prettify), validate, or reduce (Minify) your JSON data.',
        "Desc Hash Gen": 'Generate MD5, SHA-1, SHA-256, and SHA-512 hashes instantly.',
        "Desc Js Formatter": 'Format messy JS code or compress it (Minify).',
        "Start Date Ddmmyyyy": 'Start Date (DD-MM-YYYY)',
        "RGB Format": 'RGB Format',
        "HSL Format": 'HSL Format',
        "Keyword Case": 'Keyword Case:',
        "Invalid Base64 Format": 'Invalid Base64 format',
    """
    content = content.replace('"Tidy Up": "Tidy Up",', '"Tidy Up": "Tidy Up",' + en_replacements)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated locales.py")
