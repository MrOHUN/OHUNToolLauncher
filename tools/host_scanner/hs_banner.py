#host_scanner/hs_banner.py
# Ochiq portdan xizmat versiyasini o'qiydi

import socket


# Har port uchun so'rov — xizmat javob berishi uchun
PROBES = {
    22:   b"",                        # SSH o'zi yuboradi
    80:   b"HEAD / HTTP/1.0\r\n\r\n", # HTTP
    443:  b"HEAD / HTTP/1.0\r\n\r\n", # HTTPS
    8080: b"HEAD / HTTP/1.0\r\n\r\n", # HTTP-Alt
    21:   b"",                        # FTP o'zi yuboradi
    25:   b"",                        # SMTP o'zi yuboradi
    110:  b"",                        # POP3 o'zi yuboradi
    143:  b"",                        # IMAP o'zi yuboradi
    3306: b"",                        # MySQL o'zi yuboradi
    554:  b"",                        # RTSP o'zi yuboradi
}


def get_banner(ip, port):
    """
    Portga ulanib birinchi javobni o'qiydi.
    Qaytaradi: "OpenSSH 8.2p1", "Apache 2.4.41" yoki "—"
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect((ip, port))

        # So'rov yuborish (kerak bo'lsa)
        probe = PROBES.get(port, b"")
        if probe:
            sock.send(probe)

        # Javob o'qish
        banner = sock.recv(1024).decode("utf-8", errors="ignore").strip()
        sock.close()

        # Faqat birinchi qator — qisqa va aniq
        first_line = banner.split("\n")[0].strip()

        # 60 belgidan uzun bo'lsa qisqartir
        if len(first_line) > 60:
            first_line = first_line[:60] + "..."

        return first_line if first_line else "—"

    except Exception:
        return "—"


def get_banners(ip, open_ports):
    """
    Barcha ochiq portlar uchun banner o'qiydi.
    Qaytaradi: {22: "OpenSSH 8.2p1", 80: "Apache 2.4.41"}
    """
    banners = {}
    for port in open_ports:
        if port in PROBES:
            banner = get_banner(ip, port)
            if banner != "—":
                banners[port] = banner
    return banners