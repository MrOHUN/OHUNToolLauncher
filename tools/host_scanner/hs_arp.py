# host_scanner/hs_arp.py
# /proc/net/arp dan qurilmalarni o'qiydi

def get_arp_devices():
    """
    /proc/net/arp faylidan IP va MAC manzillarni o'qiydi.
    Qaytaradi: [{"ip": "192.168.1.1", "mac": "aa:bb:cc:dd:ee:ff"}, ...]
    """
    devices = []
    try:
        with open("/proc/net/arp", "r") as f:
            lines = f.readlines()[1:]  # birinchi qator — sarlavha
        for line in lines:
            parts = line.split()
            if len(parts) >= 4:
                ip = parts[0]
                mac = parts[3]
                if mac != "00:00:00:00:00:00":
                    devices.append({"ip": ip, "mac": mac})
    except Exception:
        pass
    return devices