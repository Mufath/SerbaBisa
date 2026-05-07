import os
import json
import requests
import subprocess
import threading
import time

def get_local_version():
    try:
        version_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "version.json")
        if os.path.exists(version_file):
            with open(version_file, "r") as f:
                data = json.load(f)
                return data.get("version", "1.0.0")
    except Exception:
        pass
    return "1.0.0"

def check_for_updates():
    try:
        local_version = get_local_version()
        repo_url = "https://raw.githubusercontent.com/Mufath/SerbaBisa/main/version.json"
        response = requests.get(repo_url, timeout=5)
        if response.status_code == 200:
            remote_data = response.json()
            remote_version = remote_data.get("version", "1.0.0")
            
            if remote_version != local_version:
                return {
                    "update_available": True, 
                    "local": local_version, 
                    "remote": remote_version
                }
        return {"update_available": False, "local": local_version}
    except Exception as e:
        return {"update_available": False, "local": get_local_version(), "error": str(e)}

def run_updater():
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        updater_path = os.path.join(base_dir, "scripts", "updater.bat")
        
        if os.path.exists(updater_path):
            # Run updater in a new console so it doesn't die with the app
            subprocess.Popen([updater_path], shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
            
            # Signal app shutdown
            def shutdown_later():
                time.sleep(2)
                os._exit(0)
            
            threading.Thread(target=shutdown_later).start()
            return True
        return False
    except Exception:
        return False
