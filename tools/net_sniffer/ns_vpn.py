# net_sniffer/ns_vpn.py

import os
import sys
import threading
import struct
import socket

_DIR = os.path.dirname(os.path.abspath(__file__))
_BASE = os.path.dirname(os.path.dirname(_DIR))

if _DIR not in sys.path:
    sys.path.insert(0, _DIR)
if _BASE not in sys.path:
    sys.path.insert(0, _BASE)


class PacketParser:
    """IP paketini tahlil qiladi."""

    @staticmethod
    def parse_ip(data):
        try:
            if len(data) < 20:
                return None
            ihl = (data[0] & 0x0F) * 4
            proto = data[9]
            src_ip = socket.inet_ntoa(data[12:16])
            dst_ip = socket.inet_ntoa(data[16:20])
            payload = data[ihl:]
            return {
                "proto": proto,
                "src_ip": src_ip,
                "dst_ip": dst_ip,
                "payload": payload
            }
        except Exception:
            return None

    @staticmethod
    def parse_tcp(payload):
        try:
            if len(payload) < 20:
                return None
            src_port = struct.unpack("!H", payload[0:2])[0]
            dst_port = struct.unpack("!H", payload[2:4])[0]
            flags = payload[13]
            return {
                "src_port": src_port,
                "dst_port": dst_port,
                "flags": flags
            }
        except Exception:
            return None

    @staticmethod
    def parse_udp(payload):
        try:
            if len(payload) < 8:
                return None
            src_port = struct.unpack("!H", payload[0:2])[0]
            dst_port = struct.unpack("!H", payload[2:4])[0]
            return {
                "src_port": src_port,
                "dst_port": dst_port
            }
        except Exception:
            return None


class VpnPacketReader:
    """
    VpnService fd (file descriptor) dan paketlarni o'qiydi.
    fd — Java tarafidan beriladi (APK rejimida).
    """

    def __init__(self, callback):
        self.callback = callback
        self._running = False
        self._thread = None
        self._fd = None

    def start(self, fd):
        """fd — VpnService.establish() dan kelgan ParcelFileDescriptor."""
        self._fd = fd
        self._running = True
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        self._fd = None

    def _read_loop(self):
        try:
            with os.fdopen(self._fd, "rb") as tun:
                while self._running:
                    try:
                        packet = tun.read(65535)
                        if not packet:
                            continue
                        self._process(packet)
                    except Exception:
                        break
        except Exception:
            pass

    def _process(self, data):
        ip = PacketParser.parse_ip(data)
        if not ip:
            return

        proto_name = "OTHER"
        src_port = 0
        dst_port = 0

        if ip["proto"] == 6:  # TCP
            tcp = PacketParser.parse_tcp(ip["payload"])
            if tcp:
                proto_name = "TCP"
                src_port = tcp["src_port"]
                dst_port = tcp["dst_port"]

        elif ip["proto"] == 17:  # UDP
            udp = PacketParser.parse_udp(ip["payload"])
            if udp:
                proto_name = "UDP"
                src_port = udp["src_port"]
                dst_port = udp["dst_port"]

        conn = {
            "proto": proto_name,
            "local_ip": ip["src_ip"],
            "local_port": src_port,
            "remote_ip": ip["dst_ip"],
            "remote_port": dst_port,
            "state": "LIVE",
            "uid": "vpn"
        }

        # Loopback o'tkazib yuborish
        if ip["src_ip"].startswith("127.") or ip["dst_ip"].startswith("127."):
            return

        self.callback(conn)


# Global instance
_reader = None


def start_vpn(fd, callback):
    """Java VpnService fd berilganda ishga tushiradi."""
    global _reader
    _reader = VpnPacketReader(callback)
    _reader.start(fd)


def stop_vpn():
    """VpnService ni to'xtatadi."""
    global _reader
    if _reader:
        _reader.stop()
        _reader = None