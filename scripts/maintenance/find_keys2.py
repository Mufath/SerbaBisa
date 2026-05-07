import os
import re
import sys
sys.path.append(r'd:\Mufath\Project\SerbaBisa')
from locales import UI_STRINGS

keys = list(UI_STRINGS['id'].keys())
keys_en = list(UI_STRINGS['en'].keys())
print(f"Total keys in id: {len(keys)}")

# find all _t('...') in templates
template_dir = r'd:\Mufath\Project\SerbaBisa\templates'
for root, _, files in os.walk(template_dir):
    for file in files:
        if file.endswith('.html'):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            matches = re.findall(r"_t\(['\"]([^'\"]+)['\"]\)", content)
            for m in set(matches):
                if m not in keys:
                    print(f"[{file}] Key not found in locales ID: '{m}'")
                if m not in keys_en:
                    print(f"[{file}] Key not found in locales EN: '{m}'")
