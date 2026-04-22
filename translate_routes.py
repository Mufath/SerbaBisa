import os
import re
import importlib.util

app_path = "app.py"
spec = importlib.util.spec_from_file_location("app", app_path)
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)
categories = app_module.TOOL_CATEGORIES

tool_map = {}
for cat in categories:
    cat_id = cat["id"]
    for tool in cat["tools"]:
        tool_id = tool["id"]
        endpoint = f"/{cat_id}/{tool_id}"
        tool_map[endpoint] = (tool["name"], tool["desc"])

routes_dir = "routes"
files = [f for f in os.listdir(routes_dir) if f.endswith(".py")]

for filename in files:
    filepath = os.path.join(routes_dir, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # We want to replace title="..." and description="..." where the block matches an endpoint.
    # We can split by render_template to isolate each route.
    parts = content.split('render_template(')
    new_parts = [parts[0]]
    
    for part in parts[1:]:
        # Find endpoint string
        ep_match = re.search(r'endpoint\s*=\s*"([^"]+)"', part)
        if ep_match:
            ep = ep_match.group(1)
            if ep in tool_map:
                new_title, new_desc = tool_map[ep]
                # Replace title="Old" with title="New"
                # Handle escaping quotes if needed, but normally it's just title="Title"
                part = re.sub(r'title\s*=\s*"[^"]+"', f'title="{new_title}"', part)
                part = re.sub(r'description\s*=\s*"[^"]+"', f'description="{new_desc}"', part)
        new_parts.append(part)
        
    new_content = 'render_template('.join(new_parts)
    
    if new_content != content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Updated {filename}")

print("Translation script finished.")
