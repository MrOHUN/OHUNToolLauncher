# host_scanner/hs_device.py
# Qurilma turini aniqlaydi — port + vendor + OS asosida

def get_device_type(vendor, os_name, ports):
    """
    Vendor, OS va ochiq portlar asosida qurilma turini aniqlaydi.
    Qaytaradi: (tur, icon)
    """
    vendor_low = vendor.lower()
    ports_set = set(ports.keys())

    # --- Router ---
    if any(v in vendor_low for v in ["tp-link", "netgear", "d-link", "zyxel", "asus", "linksys", "mikrotik", "ubiquiti"]):
        return "Router", "[R]"

    if "router/iot" in os_name.lower():
        if {80, 443} & ports_set:
            return "Router", "[R]"

    # --- Printer ---
    if any(v in vendor_low for v in ["epson", "canon", "hp", "brother", "xerox", "lexmark"]):
        return "Printer", "[P]"
    if 9100 in ports_set:  # JetDirect
        return "Printer", "[P]"

    # --- IP Kamera ---
    if 554 in ports_set or 8554 in ports_set:
        return "IP Kamera", "[C]"

    # --- Smart TV ---
    if any(v in vendor_low for v in ["samsung", "lg", "sony", "philips", "hisense"]):
        if "linux" in os_name.lower():
            if not {22, 3306} & ports_set:
                return "Smart TV", "[TV]"

    # --- Windows PC ---
    if "windows" in os_name.lower():
        return "Windows PC", "[W]"
    if {3389, 445, 139} & ports_set:
        return "Windows PC", "[W]"

    # --- Linux Server ---
    if 22 in ports_set and {80, 443, 3306, 5432} & ports_set:
        return "Linux Server", "[S]"

    # --- Android ---
    if "linux/android" in os_name.lower():
        if any(v in vendor_low for v in ["samsung", "xiaomi", "huawei", "apple", "google"]):
            return "Telefon", "[M]"
        return "Android", "[A]"

    # --- NAS ---
    if {445, 2049, 5984} & ports_set:
        return "NAS", "[N]"

    # --- IoT ---
    if 1900 in ports_set and len(ports_set) <= 3:
        return "IoT", "[I]"

    return "Noma'lum", "[?]"