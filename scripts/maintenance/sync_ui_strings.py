import sys

# Path ke proyek
BASE_DIR = r"d:\Mufath\Project\SerbaBisa"
sys.path.append(BASE_DIR)

from locales import UI_STRINGS

id_dict = UI_STRINGS.get("id", {})
en_dict = UI_STRINGS.get("en", {})

# Tambahkan kunci yang kurang di EN (menggunakan nilai ID sebagai placeholder sementara atau di-translate sebisa mungkin)
for k, v in id_dict.items():
    if k not in en_dict:
        en_dict[k] = v  # Fallback to ID value

# Tambahkan kunci yang kurang di ID (menggunakan nilai EN sebagai placeholder)
for k, v in en_dict.items():
    if k not in id_dict:
        id_dict[k] = v

with open('locales.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Create a new UI_STRINGS block
new_ui_strings = "UI_STRINGS = {\n"
new_ui_strings += '    "id": {\n'
for k, v in sorted(id_dict.items()):
    k_esc = k.replace('"', '\\"')
    v_esc = v.replace('"', '\\"')
    new_ui_strings += f'        "{k_esc}": "{v_esc}",\n'
new_ui_strings += '    },\n    "en": {\n'
for k, v in sorted(en_dict.items()):
    k_esc = k.replace('"', '\\"')
    v_esc = v.replace('"', '\\"')
    new_ui_strings += f'        "{k_esc}": "{v_esc}",\n'
new_ui_strings += '    },\n}'

import re
# Temukan blok UI_STRINGS di locales.py
# Mulai dari UI_STRINGS = { sampai akhir dari dict en
# Kita akan cari posisinya dengan string find
start_idx = content.find("UI_STRINGS = {")
# Cari TOOL_TRANSLATIONS = { yang merupakan blok setelahnya
end_idx = content.find("TOOL_TRANSLATIONS = {", start_idx)

if start_idx != -1 and end_idx != -1:
    new_content = content[:start_idx] + new_ui_strings + "\n\n\n" + content[end_idx:]
    with open('locales.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("UI_STRINGS synchronized successfully!")
else:
    print("Failed to find UI_STRINGS boundaries")
