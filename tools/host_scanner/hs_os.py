# host_scanner/hs_os.py
# TTL qiymatidan OS turini aniqlaydi

import subprocess
import re


def get_os(ip):
    """
    Ping yuborib TTL qiymatini o'qiydi.
    TTL → OS turi:
    64  → Linux / Android
    128 → Windows
    255 → Router / Cisco
    Qaytaradi: "Linux/Android", "Windows", "Router", "Noma'lum"
    """
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "1", ip],
            capture_output=True, text=True, timeout=3
        )
        output = result.stdout

        # TTL qiymatini topamiz
        match = re.search(r"ttl=(\d+)", output, re.IGNORECASE)
        if not match:
            return "Noma'lum"

        ttl = int(match.group(1))

        if ttl <= 64:
            return "Linux/Android 🐧"
        elif ttl <= 128:
            return "Windows 🖥️"
        elif ttl <= 255:
            return "Router/IoT 📡"
        else:
            return "Noma'lum"

    except Exception:
        return "Noma'lum"