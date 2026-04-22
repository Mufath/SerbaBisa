import os
import re

dirs_to_check = ['templates', 'routes', '.']
files_to_check = []

for d in dirs_to_check:
    if d == '.':
        for f in os.listdir('.'):
            if f.endswith('.py') or f.endswith('.bat') or f.endswith('.html'):
                files_to_check.append(f)
    else:
        for root, _, files in os.walk(d):
            for f in files:
                if f.endswith('.py') or f.endswith('.html') or f.endswith('.js') or f.endswith('.bat'):
                    files_to_check.append(os.path.join(root, f))

for filepath in files_to_check:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Do not replace mufathz or SerbaBisa in @mufathz context if any
    new_content = content.replace("SerbaBisa", "SerbaBisa")
    new_content = new_content.replace("SerbaBisa", "SerbaBisa")
    new_content = new_content.replace("SerbaBisa", "SerbaBisa")
    # Replace any leftover isolated 'SerbaBisa' in titles
    new_content = re.sub(r'(?i)\bMufath\b(?!\w)', 'SerbaBisa', new_content)
    # Restore user's specific instagram if accidentally touched (though regex \b handles it)
    new_content = new_content.replace("@mufathz", "@mufathz")

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
print("Renamed everywhere!")
