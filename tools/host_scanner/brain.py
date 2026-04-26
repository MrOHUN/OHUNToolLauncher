```
# HOST SCANNER — BRAIN v4.0

## NIMA QILADI?
Tarmoqdagi qurilmalarni topadi + chuqur tahlil qiladi.
WiFi yoki mobil internet — avtomatik subnet topadi.
Har qurilma: IP, MAC, vendor, hostname, OS, ping, qurilma turi, ochiq portlar, banner.

## FAYL STRUKTURASI
host_scanner/
├── meta.json       ← nom, rang, icon, version, author, description
├── main.py         ← open_ui() + tool_manager integratsiya
├── hs_arp.py       ← /proc/net/arp dan IP + MAC o'qiydi
├── hs_udp.py       ← UDP broadcast, javob bergan IP lar
├── hs_tcp.py       ← subnet bo'yicha TCP skan, 200 thread
├── hs_vendor.py    ← MAC → ishlab chiqaruvchi nomi (50+ prefix)
├── hs_hostname.py  ← IP → qurilma nomi
├── hs_ports.py     ← TCP 50 port + UDP 8 port, 100 thread
├── hs_os.py        ← TTL orqali OS aniqlaydi
├── hs_banner.py    ← ochiq portdan xizmat versiyasini o'qiydi
├── hs_ping.py      ← ping + ms vaqti
├── hs_device.py    ← qurilma turini aniqlaydi
├── hs_history.py   ← skan natijalarini saqlaydi
├── hs_scanner.py   ← barcha usullarni birlashtiradi
├── hs_card.py      ← DeviceCard widget + _show_info popup
└── hs_ui.py        ← HostScannerUI: progress, filter, sort, export

## HAR BIR FAYL NIMA QILADI?

### meta.json
{"name": "Host Scanner", "icon": "[H]", "color": "#00BFFF",
 "version": "4.0", "author": "OHUN", "description": "Tarmoqdagi qurilmalarni topadi va tahlil qiladi"}

### main.py
- is_active() → focus() → return
- HostScannerUI() yaratiladi
- content._popup = popup
- register(TOOL_NAME, content, popup)
- on_dismiss → unregister YO'Q
- sys.path da _DIR va _BASE (OHUN/) bo'lishi kerak

### hs_arp.py
- /proc/net/arp o'qiydi
- MAC = 00:00:00:00:00:00 bo'lsa → o'tkazib yuboradi
- Qaytaradi: [{"ip": "...", "mac": "..."}]

### hs_udp.py
- 255.255.255.255:5005 ga broadcast yuboradi
- timeout=2 sekund
- Qaytaradi: [{"ip": "..."}] — MAC yo'q

### hs_tcp.py
- get_subnet() → socket orqali telefonning IP sidan subnet oladi
- get_tcp_devices(subnet) → 1-254 gacha, 200 thread
- connect_ex() → 0 yoki 111 → qurilma bor
- timeout=0.3 sekund har IP uchun

### hs_vendor.py
- VENDORS dict — 50+ MAC prefix → ishlab chiqaruvchi
- get_vendor(mac) → mac.upper()[:8] prefix bilan qidiradi
- Topilmasa → "Noma'lum"
- Apple, Samsung, Xiaomi, Huawei, TP-Link, Netgear, D-Link...

### hs_hostname.py
- get_hostname(ip) → socket.gethostbyaddr(ip)[0]
- Topilmasa → "—"

### hs_ports.py
- TCP_PORTS — 50 port: HTTP, HTTPS, SSH, FTP, Telnet, SMTP,
  POP3, IMAP, RDP, VNC, MySQL, PostgreSQL, MongoDB, Redis,
  MSSQL, RTSP, RTMP, DNS, DHCP, SNMP, UPnP, SMB, NFS,
  Elasticsearch, Flask, Django, Dev-Server va boshqalar
- UDP_PORTS — 8 port: DNS, DHCP, NTP, SNMP, mDNS, UPnP, NetBIOS
- get_open_ports(ip) → TCP 100 thread + UDP 8 thread
- Qaytaradi: {80: "HTTP", 53: "DNS(UDP)", ...}

### hs_os.py
- ping -c 1 -W 1 {ip} → TTL o'qiydi
- TTL <= 64  → "Linux/Android"
- TTL <= 128 → "Windows"
- TTL <= 255 → "Router/IoT"
- Topilmasa → "Noma'lum"

### hs_banner.py
- PROBES dict — har port uchun so'rov
- get_banner(ip, port) → birinchi javob qatori, max 60 belgi
- get_banners(ip, open_ports) → {22: "OpenSSH 8.2", 80: "Apache 2.4"}
- Faqat PROBES da bor portlar uchun ishlaydi

### hs_ping.py
- ping(ip) → subprocess ping -c 1 -W 1
- ms ni regex bilan oladi
- Qaytaradi: {"alive": True, "ms": 12.3} yoki {"alive": False, "ms": None}

### hs_device.py
- get_device_type(vendor, os_name, ports) → (tur, icon)
- Vendor + OS + portlar kombinatsiyasidan aniqlaydi
- Router[R], Printer[P], IP Kamera[C], Smart TV[TV],
  Windows PC[W], Linux Server[S], Android[A], NAS[N], IoT[I]
- Topilmasa → ("Noma'lum", "[?]")

### hs_history.py
- tool_api orqali history.json saqlaydi
- save_scan(devices) → oxirgi 10 ta skan
- load_history() → [{date, count, devices}]
- get_last_scan() → eng oxirgi skan
- Har skan uchun: ip, mac, vendor, hostname, os, device_type, ping_ms, ports

### hs_scanner.py
- sys.path ga _DIR qo'shiladi
- 3 usul ketma-ket: ARP → UDP → TCP
- found = {} — IP kalit, takror yo'q
- _enrich(device) → vendor+hostname+os+ports+banners+ping+device_type
- Har qurilma uchun alohida thread — parallel boyitish
- scan() oxirida save_scan() chaqiriladi
- callback(devices) → yangi ma'lumot kelganda UI ga xabar

### hs_card.py
- DeviceCard(device) — kartochka (height=190):
  - 1-qator: icon + IP (font 18) + ping ms + [+] + [i]
  - 2-qator: device_type + vendor (font 13)
  - 3-qator: hostname + OS (font 12)
  - 4-qator: portlar + bannerlar (font 11)
- ping yashil = online, qizil = offline
- [+] → IP clipboard
- [i] → batafsil popup:
  - IP, MAC, Tur, Vendor, Hostname, OS, Ping, Portlar+bannerlar
  - [IP nusxalash] [Yopish]

### hs_ui.py
- sys.path ga _DIR va _BASE qo'shiladi
- HostScannerUI:
  - title bar: [-][>> Host Scanner][x]
  - scan tugmasi (height=48)
  - ProgressBar (height=8) — 0→90% skan, 100% tayyor
  - status label
  - Filter qatori: [Hammasi][Onlayn][Portli]
  - Sort qatori: [IP tartib][Tur tartib]
  - ScrollView → DeviceCard lar
  - [Eksport] tugmasi — skan tugagach chiqadi
- _render(devices) → filter + sort qo'llab natijalarni chizadi
- _export() → hammasi clipboard ga, "Nusxalandi!" 2 soniya

## UI KO'RINISH
[-]  >> Host Scanner  [x]
[Tekshirish]
[████████░░] progress
3 ta qurilma topildi
[Hammasi] [Onlayn] [Portli]
[IP tartib] [Tur tartib]

[R] 192.168.1.1    5ms  [+][i]
Router              TP-Link
router-home         Router/IoT
HTTP->Apache  HTTPS

[A] 192.168.1.5    12ms  [+][i]
Android             Samsung
android-abc         Linux/Android
SSH->OpenSSH 8.2

[Eksport]

## TIL KALITLARI
hs_title, hs_scan, hs_scanning, hs_found, hs_no_devices,
hs_no_ports, hs_copy_ip, hs_close, hs_export, hs_copied,
hs_filter_all, hs_filter_online, hs_filter_ports,
hs_sort_ip, hs_sort_type

## IMPORT XATOLARI VA YECHIMLARI
- hs_ui.py va hs_scanner.py da sys.path ga _DIR qo'shilishi shart
- hs_ui.py da _BASE = os.path.dirname(os.path.dirname(_DIR)) → OHUN/
- Izoh (#) qatorlari import qatorlariga aralashmasin!
- hs_card.py da ham sys.path ga _DIR va _BASE qo'shilishi kerak

## MUAMMOLAR VA YECHIMLARI
| Muammo | Yechim |
|--------|--------|
| No module named 'hs_udp' | hs_scanner.py ga sys.path qo'shildi |
| No module named 'hs_os' | hs_os.py fayli yaratildi |
| name 'host_scanner' is not defined | hs_ui.py ga sys.path + _BASE qo'shildi |
| Tugma matni ko'rinmadi | TEXT_COLOR oq qilindi |
| [i] popup pastda | pos_hint center_y=0.6 |
| Emoji ko'rinmadi | Android emoji ko'rsatmaydi — normal |
| Banner # izoh aralashdi | Izoh qatorini o'chirib to'g'rilandi |
| Mobil internetda 1 IP | Normal — operator gateway |
| Debug logger kerak emas | o'chirildi |
| UI katta bo'ldi | hs_card.py + hs_ui.py ga bo'lindi |

## VERSIYALAR
| Versiya | Nima | Holat |
|---------|------|-------|
| v1.0 | ARP+UDP+TCP, tool_manager, [-][x] | ✅ |
| v2.0 | vendor, hostname, portlar, kartochka UI | ✅ |
| v3.0 | OS aniqlash, banner grabbing, 30 port | ✅ |
| v4.0 | ping, device_type, history, 200 thread, filter, sort, export, progress | ✅ |

## KEYINGI BOSQICHLAR
- MAC vendor bazasini 500+ ga oshirish
- WiFi da to'liq sinash
- history ko'rish UI — oxirgi skanlar
```

Tayyor! 🚀