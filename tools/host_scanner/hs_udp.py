# host_scanner/hs_udp.py
# UDP broadcast orqali tarmoqdagi qurilmalarni topadi

import socket
import struct

def get_udp_devices():
    """
    UDP broadcast yuborib javob bergan qurilmalarni topadi.
    Qaytaradi: [{"ip": "192.168.1.x"}, ...]
    """
    devices = []
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(2)

        # Broadcast yuborish
        sock.sendto(b"", ("255.255.255.255", 5005))

        # Javoblarni yig'ish
        while True:
            try:
                _, addr = sock.recvfrom(1024)
                ip = addr[0]
                if {"ip": ip} not in devices:
                    devices.append({"ip": ip})
            except socket.timeout:
                break
    except Exception:
        pass
    finally:
        sock.close()
    return devices