try:
    import requests
except ImportError:
    import subprocess, sys
    subprocess.run([sys.executable, "-m", "pip", "install", "requests"])
    import requests

import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/json,*/*;q=0.8",
}

TIMEOUT = 10


def check_site(site, username):
    """
    Qaytaradi: (found: bool, url: str)

    errorType turlari:
      status_code  — 200 bo'lsa topildi
      message      — errorMsg sahifada bo'lmasa topildi (checkMode="present" bo'lsa: bo'lsa topildi)
      json_key     — JSON da errorKey bo'lmasa topildi
    """
    url = site["url"].format(username)

    # Qo'shimcha headerlar (masalan Imgur API uchun)
    headers = dict(HEADERS)
    if "headers_extra" in site:
        headers.update(site["headers_extra"])

    try:
        r = requests.get(
            url,
            headers=headers,
            timeout=TIMEOUT,
            allow_redirects=True
        )

        # --- STATUS CODE ---
        if site["errorType"] == "status_code":
            found = r.status_code == 200
            return found, url

        # --- MESSAGE (sahifada matn qidirish) ---
        elif site["errorType"] == "message":
            if r.status_code >= 400:
                return False, url

            error_msg = site.get("errorMsg", "")
            check_mode = site.get("checkMode", "absent")
            text_lower = r.text.lower()
            msg_lower = error_msg.lower()

            if check_mode == "present":
                # errorMsg BOR bo'lsa — topildi
                found = msg_lower in text_lower
            else:
                # errorMsg YO'Q bo'lsa — topildi (standart)
                found = msg_lower not in text_lower

            return found, url

        # --- JSON KEY ---
        elif site["errorType"] == "json_key":
            if r.status_code >= 400:
                return False, url
            try:
                data = r.json()
                error_key = site.get("errorKey", "error")
                # JSON da errorKey bo'lmasa — topildi
                found = error_key not in data
                return found, url
            except (json.JSONDecodeError, ValueError):
                return False, url

    except requests.exceptions.Timeout:
        return False, url
    except requests.exceptions.ConnectionError:
        return False, url
    except Exception:
        return False, url

    return False, url
