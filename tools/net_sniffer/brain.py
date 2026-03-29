Ha, net_sniffer tool braini:

```
# NET SNIFFER — BRAIN v1.0

## NIMA QILADI?
O'z qurilmadagi faol tarmoq ulanishlarini ko'rsatadi.
Pydroid da mock paketlar bilan ishlaydi (UI test).
APK (v1.0) da haqiqiy VpnService orqali barcha trafik ko'rinadi.
Root siz ishlaydi — VpnService rasmiy Android API.

## FAYL STRUKTURASI
net_sniffer/
├── meta.json       ← nom, rang, icon, version, author, description
├── main.py         ← open_ui() + tool_manager integratsiya
├── ns_reader.py    ← /proc/net/tcp+udp fallback (Android 9-)
├── ns_apps.py      ← UID → ilova nomi (/proc/*/status)
├── ns_card.py      ← har ulanish kartochkasi + [i] popup
├── ns_ui.py        ← asosiy UI, filter, tozalash, eksport
├── ns_vpn.py       ← IP/TCP/UDP paket parser (fd dan o'qiydi)
├── ns_bridge.py    ← Pydroid mock / APK real VpnService ko'prigi
└── VpnService.java ← APK uchun Java bridge (Buildozer v1.0)

## HAR BIR FAYL NIMA QILADI?

### meta.json
{"name": "Net Sniffer", "icon": "[N]", "color": "#00FF88",
 "version": "1.0", "author": "OHUN",
 "description": "Faol tarmoq ulanishlarini ko'rsatadi"}

### main.py
- is_active() → focus() → return
- NetSnifferUI() yaratiladi
- content._popup = popup
- register(TOOL_NAME, content, popup)
- on_dismiss → unregister YO'Q
- sys.path da _DIR va _BASE (OHUN/) bo'lishi kerak

### ns_reader.py
- _hex_ip(h) → hex IP ni oddiy IP ga: "0101A8C0" → "192.168.1.1"
- _hex_port(h) → hex portni intga: "0050" → 80
- TCP_STATES dict → {01:"ESTABLISHED", 02:"SYN_SENT"...}
- read_tcp() → /proc/net/tcp o'qiydi
- read_udp() → /proc/net/udp o'qiydi
- read_all() → read_tcp() + read_udp()
- remote_ip 0.0.0.0 bo'lsa → o'tkazib yuboradi
- Android 10+ da Permission denied → bo'sh list qaytaradi, crash yo'q

### ns_apps.py
- _load_proc() → /proc/*/status → UID + ilova nomi
- get_app_name(uid) → UID dan ilova nomi
- Topilmasa → "uid:{uid}"
- _cache dict — har so'rovda qayta o'qilmaydi
- clear_cache() → keshni tozalaydi

### ns_vpn.py
- PacketParser.parse_ip(data) → proto, src_ip, dst_ip, payload
- PacketParser.parse_tcp(payload) → src_port, dst_port, flags
- PacketParser.parse_udp(payload) → src_port, dst_port
- VpnPacketReader(callback) → fd dan paketlarni o'qiydi
- start(fd) → threading loop ishga tushadi
- stop() → loop to'xtatiladi
- Loopback (127.x.x.x) o'tkazib yuboriladi
- start_vpn(fd, callback) → global instance
- stop_vpn() → global instance to'xtatiladi

### ns_bridge.py
- _is_apk() → /data/data/com.ohun.toollauncher mavjudligini tekshiradi
- VpnBridge(on_packet) → Pydroid yoki APK rejimini avtomatik tanlaydi
- start() → _is_apk() True → _start_real(), False → _start_mock()
- _start_real() → importlib orqali jnius yuklanadi (crash bo'lsa mock ga tushadi)
  → PythonActivity context → Intent → NetSnifferVpnService ishga tushadi
  → getFd() → ns_vpn.start_vpn(fd, callback)
- _start_mock() → 5 ta mock paket, threading loop, 0.5-2s oraliq
  → Mock paketlar: Google(142.250.185.46), Facebook(157.240.22.35),
    DNS(8.8.8.8), Cloudflare(104.244.42.65), DNS(1.1.1.1)
- stop() → _running = False → APK da stop_vpn() + stopVpn()

### ns_card.py
- sys.path ga _DIR va _BASE qo'shiladi
- ConnectionCard(conn) — kartochka (height=90):
  - 1-qator: [TCP/UDP] + remote_ip:port (font 14) + holat (rangli)
  - 2-qator: ilova nomi — uid:vpn yoki real nom (font 12)
  - 3-qator: :local_port → :remote_port + [i] tugmasi
- STATE_COLORS: ESTABLISHED→yashil, LISTEN→ko'k, TIME_WAIT→sariq,
  CLOSE_WAIT→to'q sariq, LIVE→yashil, boshqa→kulrang
- RoundedRectangle fon (0.12, 0.12, 0.15, 1)
- [i] → batafsil popup: proto, ilova, UID, lokal, masofaviy, holat
  → [Yopish] tugmasi

### ns_ui.py
- sys.path ga _DIR va _BASE qo'shiladi
- Til hard-code (Uzbekcha) — tool o'z tilini o'zi hal qiladi
- NetSnifferUI:
  - title bar: [-][>> Net Sniffer][x]
  - Filter qatori: [Hammasi][TCP][UDP][Jonli]
  - [Tozalash] tugmasi (qizil) + status label
  - ProgressBar (height=6) — ulanish soniga qarab
  - ScrollView → ConnectionCard lar
  - [Eksport] → barcha ulanishlar clipboard ga
- _connections = {} — key: "remote_ip:port", value: conn dict
- _on_packet(conn) → key bo'yicha qo'shadi, Clock orqali _render()
- _render() → filter qo'llab kartochkalar chiziladi
- _minimize() → bridge.stop() + popup.dismiss()
- _close() → bridge.stop() + tool_manager.close()

### VpnService.java
- package: com.ohun.netsniffer
- NetSnifferVpnService extends VpnService
- onCreate() → instance = this
- onStartCommand() → startVpn()
- startVpn():
  - Builder: address=10.0.0.1/32, route=0.0.0.0/0, DNS=8.8.8.8, MTU=65535
  - establish() → vpnInterface (ParcelFileDescriptor)
- getFd() → vpnInterface.getFd() → Python ga beriladi
- stopVpn() → vpnInterface.close() + stopSelf()
- getInstance() → static instance (Python Pyjnius orqali chaqiradi)

## UI KO'RINISH
[-]  >> Net Sniffer  [x]
[Hammasi] [TCP] [UDP] [Jonli]
[Tozalash]          5 ta ulanish
[██████████] progress

[TCP] 142.250.185.46:443        LIVE
uid:vpn
  :54231 → :443                  [i]

[UDP] 8.8.8.8:53                LIVE
uid:vpn
  :45123 → :53                   [i]

[Eksport]

## REJIMLAR
- Pydroid → mock 5 ta paket, UI test ✅
- APK v1.0 → haqiqiy VpnService, barcha trafik ✅

## MUAMMOLAR VA YECHIMLARI
| Muammo | Yechim |
|--------|--------|
| jnius import crash | importlib.import_module() ishlatildi |
| _is_apk() noto'g'ri | os.path.exists() APK papkasini tekshiradi |
| Mock ishlamadi | _start_real xato bo'lsa _start_mock fallback |
| /proc/net/tcp Permission denied | Android 10+ — ns_reader bo'sh list qaytaradi |
| f-string syntax xato | "+" bilan string birlashtirish ishlatildi |

## VERSIYALAR
| Versiya | Nima | Holat |
|---------|------|-------|
| v1.0 | VpnBridge mock+real, PacketParser, UI, filter, eksport | ✅ |
| v2.0 | Geo IP, ilova nomi (real), trafik miqdori | 🔜 |

## KEYINGI BOSQICHLAR
- Geo IP — IP dan mamlakat/shahar aniqlash
- Real ilova nomi APK da (PackageManager orqali)
- Trafik miqdori — yuborilgan/qabul baytlar
- Buildozer da VpnService permission qo'shish
```

Tayyor! Saqlab qo'y 🚀
Yo'q, brainda yo'q — hozir qo'shamiz:

```
## BUILDOZER (v1.0) UCHUN QO'SHIMCHALAR

### buildozer.spec
android.permissions = INTERNET, BIND_VPN_SERVICE

### AndroidManifest.xml (buildozer templates/)
<service android:name="com.ohun.netsniffer.NetSnifferVpnService"
         android:permission="android.permission.BIND_VPN_SERVICE">
    <intent-filter>
        <action android:name="android.net.VpnService"/>
    </intent-filter>
</service>

### VpnService.java joylashuvi
- Buildozer loyiha papkasida: src/com/ohun/netsniffer/VpnService.java
- Buildozer avtomatik compile qiladi

### Foydalanuvchi ruxsati
- Birinchi ishga tushganda Android "VPN ruxsat berasizmi?" so'raydi
- Foydalanuvchi "OK" bosishi kerak
- Ruxsat berilmasa → mock rejimga tushadi
```

Shu qismni brain ga qo'shib qo'y — Buildozer vaqtida kerak bo'ladi!