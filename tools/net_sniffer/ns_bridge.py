# net_sniffer/ns_bridge.py

import os
import sys
import threading

_DIR = os.path.dirname(os.path.abspath(__file__))
_BASE = os.path.dirname(os.path.dirname(_DIR))

if _DIR not in sys.path:
    sys.path.insert(0, _DIR)
if _BASE not in sys.path:
    sys.path.insert(0, _BASE)


def _is_apk():
    return os.path.exists("/data/data/com.ohun.toollauncher")


class VpnBridge:
    def __init__(self, on_packet):
        self.on_packet = on_packet
        self._running = False
        self._service = None
        self._mock_thread = None

    def start(self):
        if _is_apk():
            self._start_real()
        else:
            print("VpnBridge: Mock rejimida...")
            self._start_mock()

    def _start_real(self):
        try:
            import importlib
            jnius = importlib.import_module("jnius")
            autoclass = jnius.autoclass

            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            context = PythonActivity.mActivity

            Intent = autoclass("android.content.Intent")
            NetSnifferVpnService = autoclass(
                "com.ohun.netsniffer.NetSnifferVpnService"
            )
            intent = Intent(context, NetSnifferVpnService)
            context.startService(intent)

            import time
            time.sleep(1.5)

            self._service = NetSnifferVpnService.getInstance()
            if self._service:
                fd = self._service.getFd()
                if fd > 0:
                    from ns_vpn import start_vpn
                    self._running = True
                    start_vpn(fd, self.on_packet)
                else:
                    print("VpnBridge: fd xato")
            else:
                print("VpnBridge: instance null")

        except Exception as e:
            print("VpnBridge real xato: " + str(e))
            self._start_mock()

    def _start_mock(self):
        import time
        import random

        self._running = True

        mock_data = [
            {"proto": "TCP", "local_ip": "192.168.1.5", "local_port": 54231,
             "remote_ip": "142.250.185.46", "remote_port": 443,
             "state": "LIVE", "uid": "vpn"},
            {"proto": "TCP", "local_ip": "192.168.1.5", "local_port": 55100,
             "remote_ip": "157.240.22.35", "remote_port": 443,
             "state": "LIVE", "uid": "vpn"},
            {"proto": "UDP", "local_ip": "192.168.1.5", "local_port": 45123,
             "remote_ip": "8.8.8.8", "remote_port": 53,
             "state": "LIVE", "uid": "vpn"},
            {"proto": "TCP", "local_ip": "192.168.1.5", "local_port": 50001,
             "remote_ip": "104.244.42.65", "remote_port": 443,
             "state": "LIVE", "uid": "vpn"},
            {"proto": "UDP", "local_ip": "192.168.1.5", "local_port": 41000,
             "remote_ip": "1.1.1.1", "remote_port": 53,
             "state": "LIVE", "uid": "vpn"},
        ]

        def _loop():
            seen = set()
            while self._running:
                for pkt in mock_data:
                    if not self._running:
                        break
                    key = (pkt["remote_ip"], pkt["remote_port"])
                    if key not in seen:
                        seen.add(key)
                        self.on_packet(pkt)
                    time.sleep(random.uniform(0.5, 2.0))
                time.sleep(2)

        self._mock_thread = threading.Thread(target=_loop, daemon=True)
        self._mock_thread.start()

    def stop(self):
        self._running = False
        if _is_apk():
            try:
                import importlib
                jnius = importlib.import_module("jnius")
                from ns_vpn import stop_vpn
                stop_vpn()
                if self._service:
                    self._service.stopVpn()
            except Exception as e:
                print("VpnBridge stop xato: " + str(e))