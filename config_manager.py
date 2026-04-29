import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

DEFAULT_CONFIG = {
    "username": "Sobat",
    "theme": "light",
    "language": "id"
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Merge with default config to ensure all keys exist
            config = DEFAULT_CONFIG.copy()
            config.update(data)
            return config
    except Exception:
        return DEFAULT_CONFIG.copy()

def save_config(config_data):
    current = load_config()
    current.update(config_data)
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(current, f, indent=4)
        return True
    except Exception:
        return False
