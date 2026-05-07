import os

replacements = {
    "_t('dashboard_title')": "_t('Dashboard Title')",
    "_t('change_theme')": "_t('Change Theme')",
    "_t('process_now')": "_t('Process Now')",
    "_t('result_label')": "_t('Result Label')",
    "_t('activate')": "_t('Activate')",
    "_t('enter_text')": "_t('Text Input')",
    "_t('case_converter')": "_t('Case Converter')",
    "_t('tidy_format')": "_t('Tidy Format')",
    "_t('minify_compress')": "_t('Minify Compress')",
}

template_dir = r'd:\Mufath\Project\SerbaBisa\templates'
for root, _, files in os.walk(template_dir):
    for file in files:
        if file.endswith('.html'):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content = content
            for old, new in replacements.items():
                new_content = new_content.replace(old, new)
            
            if content != new_content:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated {file}")
