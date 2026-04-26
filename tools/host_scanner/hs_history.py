# host_scanner/hs_history.py
# Skan natijalarini saqlaydi va yuklaydi

import os
import sys
import json
from datetime import datetime

_DIR = os.path.dirname(os.path.abspath(__file__))
_BASE = os.path.dirname(os.path.dirname(_DIR))
if _BASE not in sys.path:
    sys.path.insert(0, _BASE)

import tool_api as api

HISTORY_FILE = "history.json"
MAX_SCANS = 10  # Maksimal saqlash soni


def save_scan(devices):
    """
    Skan natijasini history.json ga saqlaydi.
    Faqat muhim ma'lumotlar saqlanadi.
    """
    history = api.load_tool_data(__file__, HISTORY_FILE, default=[])

    scan_entry = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "count": len(devices),
        "devices": []
    }

    for d in devices:
        scan_entry["devices"].append({
            "ip":          d.get("ip", "?"),
            "mac":         d.get("mac", "—"),
            "vendor":      d.get("vendor", "Noma'lum"),
            "hostname":    d.get("hostname", "—"),
            "os":          d.get("os", "Noma'lum"),
            "device_type": d.get("device_type", "Noma'lum"),
            "ping_ms":     d.get("ping", {}).get("ms"),
            "ports":       list(d.get("ports", {}).keys()),
        })

    # Oxirgi MAX_SCANS ta saqlanadi
    history.insert(0, scan_entry)
    history = history[:MAX_SCANS]

    api.save_tool_data(__file__, HISTORY_FILE, history)
    return history


def load_history():
    """
    Oxirgi skanlarni yuklaydi.
    Qaytaradi: [{date, count, devices}, ...]
    """
    return api.load_tool_data(__file__, HISTORY_FILE, default=[])


def get_last_scan():
    """
    Eng oxirgi skanni qaytaradi.
    """
    history = load_history()
    return history[0] if history else None