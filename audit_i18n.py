import os
import re
import sys

# Path ke proyek
BASE_DIR = r"d:\Mufath\Project\SerbaBisa"

# Import locales secara manual
sys.path.append(BASE_DIR)
try:
    from locales import TOOL_TRANSLATIONS, UI_STRINGS
except ImportError as e:
    print(f"Error importing locales: {e}")
    TOOL_TRANSLATIONS = {}
    UI_STRINGS = {"id": {}, "en": {}}

def check_dict_sync():
    print("--- CEK SINKRONISASI DICTIONARY ---")
    id_keys = set(UI_STRINGS.get("id", {}).keys())
    en_keys = set(UI_STRINGS.get("en", {}).keys())
    
    missing_in_en = id_keys - en_keys
    missing_in_id = en_keys - id_keys
    
    if missing_in_en:
        print(f"[!] Ada {len(missing_in_en)} kunci di ID tapi HILANG di EN:")
        for k in sorted(list(missing_in_en))[:10]:
            print(f"    - {k}")
        if len(missing_in_en) > 10: print("    ...")
            
    if missing_in_id:
        print(f"[!] Ada {len(missing_in_id)} kunci di EN tapi HILANG di ID:")
        for k in sorted(list(missing_in_id))[:10]:
            print(f"    - {k}")
        if len(missing_in_id) > 10: print("    ...")
            
    if not missing_in_en and not missing_in_id:
        print("[OK] UI_STRINGS tersinkronisasi dengan sempurna!")
    print()

def audit_file(filepath):
    untranslated = []
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
        # Cari semua pemanggilan _t('...') atau translate_tool('...')
        t_calls = re.findall(r'_t\([\'"]([^\'"]+)[\'"]\)', content)
        for key in t_calls:
            if key not in UI_STRINGS.get('id', {}) and key not in UI_STRINGS.get('en', {}):
                untranslated.append(f"MISSING KEY: {key}")
                
        # Cari hardcoded title block
        if "{% block title %}" in content and "_t(" not in content.split("{% block title %}")[1].split("{%")[0]:
            title_text = content.split("{% block title %}")[1].split("{%")[0].strip()
            if "SerbaBisa" in title_text:
                untranslated.append(f"HARDCODED TITLE: {title_text}")
                
        # Cari hardcoded h1
        h1_matches = re.findall(r'<h1>([^<{]+)</h1>', content)
        for h1 in h1_matches:
            if "{{" not in h1:
                untranslated.append(f"HARDCODED H1: {h1.strip()}")

    return list(set(untranslated))

def main():
    check_dict_sync()
    
    print("--- MULAI AUDIT LOKALISASI TEMPLATE ---")
    folders = [os.path.join(BASE_DIR, 'templates')]
    
    total_issues = 0
    for folder in folders:
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.endswith('.html'):
                    path = os.path.join(root, file)
                    issues = audit_file(path)
                    if issues:
                        print(f"[!] File: {os.path.relpath(path, BASE_DIR)}")
                        for m in issues:
                            print(f"    - {m}")
                        total_issues += len(issues)
    
    if total_issues == 0:
        print("\n[OK] Tidak ditemukan masalah hardcoded/missing key pada template utama!")
    else:
        print(f"\n--- SELESAI: Ditemukan {total_issues} masalah ---")

if __name__ == "__main__":
    main()
