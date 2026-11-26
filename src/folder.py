import sys
import json
import os 
from pathlib import Path




def app_dir() -> Path:
    
    if sys.platform == "win32":
        base = Path(os.environ["APPDATA"])          
    else:
        return Exception("other platforms not supported only Windows") 
    
    folder = base / "PhoneWebcam"
    folder.mkdir(parents=True, exist_ok=True)       
    return folder


def load_json(path):
    with open(path,"r",encoding="utf-8") as f:
        config = json.load(f)
    return config


def resource_path(relative):
    base = getattr(sys, "_MEIPASS", Path(__file__).parent.parent)
    return Path(base) / relative




def load_config(default_webconfig) -> dict:
    path = app_dir() / "webconfig.json"

    if not path.exists():
        
        path.write_text(json.dumps(default_webconfig, indent=4), encoding="utf-8")
        print(f"Created default config at: {path}")
        return default_webconfig.copy()

    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"Config file is broken ({e}). using defaults")
        return default_webconfig.copy()

    
    return {**default_webconfig, **loaded}

def save_config(config: dict) -> None:

    path = app_dir() / "webconfig.json"
    temp_path = path.with_suffix(".tmp")

    temp_path.write_text(
        json.dumps(config, indent=4),
        encoding="utf-8"
    )

    os.replace(temp_path, path)