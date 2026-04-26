# host_scanner/hs_ping.py
# Qurilmaga ping yuboradi, ms vaqtini o'lchaydi

import subprocess
import re
import time


def ping(ip):
    """
    Qurilmaga ping yuboradi.
    Qaytaradi: {"alive": True, "ms": 12.3}
    yoki:       {"alive": False, "ms": None}
    """
    try:
        start = time.time()
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "1", ip],
            capture_output=True, text=True, timeout=3
        )
        ms = (time.time() - start) * 1000

        if result.returncode == 0:
            # Aniq ms qiymatini olishga urinamiz
            match = re.search(r"time=(\d+\.?\d*)", result.stdout)
            if match:
                ms = float(match.group(1))
            return {"alive": True, "ms": round(ms, 1)}
    except Exception:
        pass
    return {"alive": False, "ms": None}