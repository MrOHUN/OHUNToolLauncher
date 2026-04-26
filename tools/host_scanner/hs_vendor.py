# host_scanner/hs_vendor.py
# MAC manzildan ishlab chiqaruvchi nomini topadi

# Mashhur MAC prefikslar ro'yxati
VENDORS = {
    "00:50:56": "VMware",
    "00:0C:29": "VMware",
    "00:1A:11": "Google",
    "00:17:F2": "Apple",
    "00:1B:63": "Apple",
    "00:23:12": "Apple",
    "AC:BC:32": "Apple",
    "F0:DB:E2": "Apple",
    "00:16:CB": "Apple",
    "B8:27:EB": "Raspberry Pi",
    "DC:A6:32": "Raspberry Pi",
    "00:1D:AA": "Samsung",
    "00:12:FB": "Samsung",
    "8C:77:12": "Samsung",
    "00:26:37": "Samsung",
    "A0:07:98": "Samsung",
    "00:0F:00": "Xiaomi",
    "00:9E:C8": "Xiaomi",
    "F8:A2:D6": "Xiaomi",
    "28:6C:07": "Xiaomi",
    "64:09:80": "Huawei",
    "00:18:82": "Huawei",
    "00:E0:FC": "Huawei",
    "00:1E:10": "Huawei",
    "00:90:4C": "Epson",
    "00:13:D4": "Dell",
    "00:14:22": "Dell",
    "00:21:70": "Dell",
    "00:1C:42": "Parallels",
    "08:00:27": "VirtualBox",
    "00:50:BA": "D-Link",
    "00:17:9A": "D-Link",
    "00:1B:11": "D-Link",
    "00:26:5A": "D-Link",
    "00:18:E7": "Netgear",
    "00:14:6C": "Netgear",
    "20:E5:2A": "Netgear",
    "00:1F:33": "Netgear",
    "00:1A:2B": "TP-Link",
    "00:23:CD": "TP-Link",
    "F4:EC:38": "TP-Link",
    "00:0A:EB": "TP-Link",
    "00:50:7F": "ZyXEL",
    "00:13:49": "Sony",
    "00:1D:0D": "Sony",
    "00:24:BE": "Sony",
    "00:19:C5": "LG",
    "00:1E:75": "LG",
    "00:26:E2": "LG",
    "00:1C:62": "LG",
}


def get_vendor(mac):
    """
    MAC manzildan ishlab chiqaruvchi nomini topadi.
    Faqat birinchi 3 oktet (prefix) tekshiriladi.
    Topilmasa → 'Noma'lum' qaytaradi.
    """
    if not mac or mac == "—":
        return "Noma'lum"
    
    # MAC ni katta harfga o'tkazib prefix olamiz
    mac = mac.upper()
    prefix = mac[:8]  # "AA:BB:CC"
    
    return VENDORS.get(prefix, "Noma'lum")