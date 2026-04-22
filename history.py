import json
import os
from datetime import datetime, timedelta

HISTORY_FILE = "history.json"

def get_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def log_history(cat, tool):
    history = get_history()
    
    cat_id = cat['id']
    if cat_id == 'pdf':
        bg = 'rgba(229, 62, 62, 0.1)'
        color = 'var(--danger)'
    elif cat_id == 'image':
        bg = 'rgba(56, 161, 105, 0.1)'
        color = 'var(--success)'
    elif cat_id == 'calc':
        bg = 'rgba(221, 107, 32, 0.1)'
        color = 'var(--warning)'
    elif cat_id == 'text':
        bg = 'rgba(128, 90, 213, 0.1)'
        color = '#805ad5'
    else:
        bg = 'rgba(49, 130, 206, 0.1)'
        color = 'var(--primary)'

    history.insert(0, {
        "cat_id": cat['id'],
        "tool_id": tool['id'],
        "tool_name": tool['name'],
        "icon": tool['icon'],
        "bg": bg,
        "color": color,
        "timestamp": datetime.now().isoformat()
    })
    
    with open(HISTORY_FILE, "w") as f:
        json.dump(history[:500], f)  # Keep up to 500 items in history

def get_weekly_count():
    history = get_history()
    one_week_ago = datetime.now() - timedelta(days=7)
    count = 0
    for h in history:
        try:
            ts = datetime.fromisoformat(h['timestamp'])
            if ts > one_week_ago:
                count += 1
        except:
            pass
    return count

def format_time_ago(iso_str):
    try:
        ts = datetime.fromisoformat(iso_str)
        now = datetime.now()
        diff = now - ts
        
        if diff.days == 0:
            if diff.seconds < 60:
                return "Baru saja"
            elif diff.seconds < 3600:
                return f"{diff.seconds // 60} menit yang lalu"
            elif diff.seconds < 86400:
                return f"Hari ini, {ts.strftime('%H:%M')}"
        elif diff.days == 1:
            return f"Kemarin, {ts.strftime('%H:%M')}"
        else:
            return ts.strftime('%d %b %Y')
    except:
        return ""
