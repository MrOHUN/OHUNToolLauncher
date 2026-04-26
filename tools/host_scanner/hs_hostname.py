# host_scanner/hs_hostname.py
# IP manzildan qurilma nomini topadi

import socket


def get_hostname(ip):
    """
    IP manzildan qurilma nomini topadi.
    Topilmasa → '—' qaytaradi.
    """
    try:
        hostname = socket.gethostbyaddr(ip)[0]
        return hostname
    except Exception:
        return "—"