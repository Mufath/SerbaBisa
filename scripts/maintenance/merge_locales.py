import re

with open('locales.py', 'r', encoding='utf-8') as f:
    content = f.read()

# We want to extract the three dictionaries and merge them
# Actually, since it's a python file, we can import it!
import sys
sys.path.append('.')
from locales import TOOL_TRANSLATIONS, TOOL_TRANSLATIONS_ID_TO_EN, TOOL_TRANSLATIONS_EN_TO_ID

# Merge them into a single ID -> EN dictionary
merged_translations = {}

# Priority 1: Existing TOOL_TRANSLATIONS
merged_translations.update(TOOL_TRANSLATIONS)

# Priority 2: TOOL_TRANSLATIONS_ID_TO_EN
for k, v in TOOL_TRANSLATIONS_ID_TO_EN.items():
    if k not in merged_translations:
        merged_translations[k] = v

# Priority 3: Reverse of TOOL_TRANSLATIONS_EN_TO_ID (just in case there are missing ones)
for k, v in TOOL_TRANSLATIONS_EN_TO_ID.items():
    if v not in merged_translations:
        merged_translations[v] = k

print(f"Total entries in merged dict: {len(merged_translations)}")

# Now let's generate the code for the merged dictionary
merged_code = "TOOL_TRANSLATIONS = {\n"
for k, v in sorted(merged_translations.items()):
    k_esc = k.replace('"', '\\"')
    v_esc = v.replace('"', '\\"')
    merged_code += f'    "{k_esc}": "{v_esc}",\n'
merged_code += "}\n\n"

merged_code += """def translate_tool(text, lang="id"):
    if not text:
        return text
    # If it's a known UI key, use translate_ui
    ui_text = translate_ui(text, lang)
    if ui_text != text:
        return ui_text
        
    if lang == "en":
        return TOOL_TRANSLATIONS.get(text, text)
    elif lang == "id":
        # Usually text from backend is already in ID, but if it's in EN we translate it back
        for k, v in TOOL_TRANSLATIONS.items():
            if v == text:
                return k
        return text
    return text
"""

# Now we need to replace the section in locales.py starting from TOOL_TRANSLATIONS
# We will use regex to find the start of TOOL_TRANSLATIONS and the end of translate_tool
start_idx = content.find("TOOL_TRANSLATIONS = {")
end_idx = content.find("def m(", start_idx)

if start_idx != -1 and end_idx != -1:
    new_content = content[:start_idx] + merged_code + content[end_idx:]
    with open('locales.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("locales.py updated successfully!")
else:
    print("Could not find boundaries for replacement.")
