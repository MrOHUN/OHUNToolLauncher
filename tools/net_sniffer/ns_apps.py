# net_sniffer/ns_apps.py

import os
import re

_cache = {}

def _load_proc():
    """
    /proc/*/status dan UID + ilova nomini o'qiydi.
    Root siz ishlaydi — faqat o'z qurilmangdagi ilovalar.
    """
    result = {}
    try:
        for pid in os.listdir("/proc"):
            if not pid.isdigit():
                continue
            status_path = f"/proc/{pid}/status"
            cmdline_path = f"/proc/{pid}/cmdline"
            try:
                uid = None
                name = None
                with open(status_path, "r") as f:
                    for line in f:
                        if line.startswith("Uid:"):
                            uid = line.split()[1]
                        if line.startswith("Name:"):
                            name = line.split()[1]
                if uid and name:
                    # cmdline dan to'liqroq nom olishga urinish
                    try:
                        with open(cmdline_path, "r") as f:
                            cmd = f.read().split("\x00")[0]
                            if cmd:
                                name = cmd.split("/")[-1][:30]
                    except Exception:
                        pass
                    if uid not in result:
                        result[uid] = name
            except Exception:
                continue
    except Exception:
        pass
    return result

def _get_cache():
    global _cache
    if not _cache:
        _cache = _load_proc()
    return _cache

def get_app_name(uid):
    """UID dan ilova nomini qaytaradi."""
    cache = _get_cache()
    name = cache.get(str(uid))
    if name:
        return name
    return f"uid:{uid}"

def clear_cache():
    """Keshni tozalaydi — yangilanish uchun."""
    global _cache
    _cache = {}