# host_scanner/hs_ports.py
import socket
import concurrent.futures

TCP_PORTS = {
    # Web
    80:    "HTTP",
    443:   "HTTPS",
    8080:  "HTTP-Alt",
    8443:  "HTTPS-Alt",
    8888:  "HTTP-Dev",
    3000:  "Dev-Server",
    5000:  "Flask",
    8000:  "Django",
    # Remote
    22:    "SSH",
    23:    "Telnet",
    3389:  "RDP",
    5900:  "VNC",
    5901:  "VNC-2",
    # Mail
    25:    "SMTP",
    110:   "POP3",
    143:   "IMAP",
    465:   "SMTPS",
    993:   "IMAPS",
    995:   "POP3S",
    587:   "SMTP-Alt",
    # File
    21:    "FTP",
    445:   "SMB",
    139:   "NetBIOS",
    2049:  "NFS",
    69:    "TFTP",
    # Database
    3306:  "MySQL",
    5432:  "PostgreSQL",
    27017: "MongoDB",
    6379:  "Redis",
    1433:  "MSSQL",
    5984:  "CouchDB",
    9200:  "Elasticsearch",
    7474:  "Neo4j",
    # Media
    554:   "RTSP",
    1935:  "RTMP",
    8554:  "RTSP-Alt",
    # Router/IoT
    53:    "DNS",
    67:    "DHCP",
    161:   "SNMP",
    1900:  "UPnP",
    7547:  "TR-069",
    8181:  "Router-Alt",
    # Proxy
    3128:  "Squid",
    8118:  "Privoxy",
    1080:  "SOCKS",
    # Other
    9090:  "Webmin",
    10000: "Webmin-Alt",
    2222:  "SSH-Alt",
    4444:  "Metasploit",
    6666:  "IRC",
    6667:  "IRC-Alt",
}

UDP_PORTS = {
    53:   "DNS",
    67:   "DHCP",
    123:  "NTP",
    161:  "SNMP",
    5353: "mDNS",
    1900: "UPnP",
    137:  "NetBIOS",
    138:  "NetBIOS-DGM",
}


def _check_tcp(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.4)
        result = sock.connect_ex((ip, port))
        sock.close()
        if result == 0:
            return port
    except Exception:
        pass
    return None


def _check_udp(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1)
        sock.sendto(b"\x00", (ip, port))
        sock.recvfrom(1024)
        sock.close()
        return port
    except socket.timeout:
        # Timeout = port ochiq (javob bermadi, lekin yopiq emas)
        return port
    except Exception:
        pass
    return None


def get_open_ports(ip):
    """
    TCP + UDP portlarni parallel tekshiradi.
    Qaytaradi: {80: "HTTP", 53: "DNS(UDP)", ...}
    """
    open_ports = {}

    # TCP — 100 thread
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = {
            executor.submit(_check_tcp, ip, port): (port, name)
            for port, name in TCP_PORTS.items()
        }
        for future in concurrent.futures.as_completed(futures):
            port, name = futures[future]
            if future.result():
                open_ports[port] = name

    # UDP — alohida
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = {
            executor.submit(_check_udp, ip, port): (port, name)
            for port, name in UDP_PORTS.items()
        }
        for future in concurrent.futures.as_completed(futures):
            port, name = futures[future]
            if future.result():
                open_ports[port] = f"{name}(UDP)"

    return open_ports