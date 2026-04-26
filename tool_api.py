# tool_api.py
import os
import json

_launcher_version = "0.4.1"


def get_launcher_version():
    return _launcher_version


def get_tool_dir(tool_main_file):
    return os.path.dirname(os.path.abspath(tool_main_file))


def get_data_file(tool_main_file, filename):
    tool_dir = get_tool_dir(tool_main_file)
    return os.path.join(tool_dir, filename)


def save_tool_data(tool_main_file, filename, data):
    path = get_data_file(tool_main_file, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_tool_data(tool_main_file, filename, default=None):
    path = get_data_file(tool_main_file, filename)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return default


def notify(message):
    print(f"[OHUN] {message}")