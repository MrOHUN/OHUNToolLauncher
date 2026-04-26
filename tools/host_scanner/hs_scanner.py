# host_scanner/hs_scanner.py
import os
import sys
import threading

_DIR = os.path.dirname(os.path.abspath(__file__))
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)

from hs_arp import get_arp_devices
from hs_udp import get_udp_devices
from hs_tcp import get_tcp_devices, get_subnet
from hs_vendor import get_vendor
from hs_hostname import get_hostname
from hs_ports import get_open_ports
from hs_os import get_os
from hs_banner import get_banners
from hs_ping import ping
from hs_device import get_device_type
from hs_history import save_scan


def _enrich(device, callback=None, all_devices=None):
    ip  = device.get("ip", "")
    mac = device.get("mac", "—")

    device["vendor"]   = get_vendor(mac)
    device["hostname"] = get_hostname(ip)
    device["os"]       = get_os(ip)
    device["ports"]    = get_open_ports(ip)
    device["banners"]  = get_banners(ip, device["ports"])
    device["ping"]     = ping(ip)

    device_type, icon = get_device_type(
        device["vendor"],
        device["os"],
        device["ports"]
    )
    device["device_type"] = device_type
    device["icon"]        = icon

    if callback and all_devices is not None:
        callback(all_devices)


def scan(callback=None):
    found = {}

    def _add(device):
        ip = device.get("ip")
        if not ip:
            return
        if ip not in found:
            found[ip] = device
            if callback:
                callback(list(found.values()))

    for d in get_arp_devices():
        _add(d)
    for d in get_udp_devices():
        _add(d)
    subnet = get_subnet()
    for d in get_tcp_devices(subnet):
        _add(d)

    devices = list(found.values())
    threads = []
    for device in devices:
        t = threading.Thread(
            target=_enrich,
            args=(device, callback, devices),
            daemon=True
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # Natijani saqlash
    save_scan(devices)

    return devices