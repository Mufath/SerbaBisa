import os

path = r'd:\Mufath\Project\SerbaBisa\templates\tools\json_formatter.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("_t('json_example')", "_t('JSON Example')")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated json_formatter.html")
