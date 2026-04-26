import os

TCP_STATES = {
    "01": "ESTABLISHED", "02": "SYN_SENT", "03": "SYN_RECV",
    "04": "FIN_WAIT1", "05": "FIN_WAIT2", "06": "TIME_WAIT",
    "07": "CLOSE", "08": "CLOSE_WAIT", "09": "LAST_ACK",
    "0A": "LISTEN", "0B": "CLOSING"
}

def _hex_ip(h):
    try:
        b = bytes.fromhex(h)
        return ".".join(str(x) for x in reversed(b))
    except Exception:
        return "0.0.0.0"

def _hex_port(h):
    try:
        return int(h, 16)
    except Exception:
        return 0

def _parse_file(path, proto):
    results = []
    try:
        with open(path, "r") as f:
            lines = f.readlines()[1:]
        for line in lines:
            parts = line.split()
            if len(parts) < 8:
                continue
            local = parts[1].split(":")
            remote = parts[2].split(":")
            if len(local) != 2 or len(remote) != 2:
                continue
            local_ip = _hex_ip(local[0])
            local_port = _hex_port(local[1])
            remote_ip = _hex_ip(remote[0])
            remote_port = _hex_port(remote[1])
            state_hex = parts[3].upper()
            state = TCP_STATES.get(state_hex, state_hex)
            uid = parts[7] if len(parts) > 7 else "0"

            # Faqat remote_ip 0.0.0.0 bo'lsa o'tkaz
            if remote_ip == "0.0.0.0":
                continue

            results.append({
                "proto": proto,
                "local_ip": local_ip,
                "local_port": local_port,
                "remote_ip": remote_ip,
                "remote_port": remote_port,
                "state": state,
                "uid": uid
            })
    except Exception as e:
        print(f"ns_reader xato ({path}): {e}")
    return results

def read_tcp():
    return _parse_file("/proc/net/tcp", "TCP")

def read_udp():
    return _parse_file("/proc/net/udp", "UDP")

def read_all():
    return read_tcp() + read_udp()