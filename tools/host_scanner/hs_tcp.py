# host_scanner/hs_tcp.py
import socket
import concurrent.futures

def _check_host(ip):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.3)  # 0.5 → 0.3 tezroq
        result = sock.connect_ex((ip, 80))
        sock.close()
        if result == 0 or result == 111:
            return {"ip": ip}
    except Exception:
        pass
    return None

def get_tcp_devices(subnet="192.168.1"):
    devices = []
    ips = [f"{subnet}.{i}" for i in range(1, 255)]

    with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
        results = executor.map(_check_host, ips)

    for r in results:
        if r:
            devices.append(r)
    return devices

def get_subnet():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
        sock.close()
        return ".".join(ip.split(".")[:3])
    except Exception:
        return "192.168.1"