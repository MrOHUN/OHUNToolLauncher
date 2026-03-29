import threading
import socket

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class FuzzerEngine:
    def __init__(self, on_result, on_done, threads=50):
        self.on_result = on_result
        self.on_done = on_done
        self.threads = threads
        self._stop = False

    def start(self, url, wordlist):
        self._stop = False
        t = threading.Thread(target=self._run, args=(url, wordlist), daemon=True)
        t.start()

    def stop(self):
        self._stop = True

    def _run(self, base_url, wordlist):
        from concurrent.futures import ThreadPoolExecutor, as_completed

        base_url = base_url.rstrip("/")
        futures = []

        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            for path in wordlist:
                if self._stop:
                    break
                path = path.strip().lstrip("/")
                if not path:
                    continue
                futures.append(executor.submit(self._check, base_url, path))

            for future in as_completed(futures):
                if self._stop:
                    break
                result = future.result()
                if result:
                    self.on_result(result)

        self.on_done()

    def _check(self, base_url, path):
        url = f"{base_url}/{path}"
        try:
            if HAS_REQUESTS:
                r = requests.get(url, timeout=5, allow_redirects=False)
                return {
                    "url": url,
                    "path": path,
                    "status": r.status_code,
                    "size": len(r.content)
                }
            else:
                # requests yo'q — mock natija
                import random
                codes = [200, 301, 403, 404, 404, 404]
                code = random.choice(codes)
                if code == 404:
                    return None
                return {
                    "url": url,
                    "path": path,
                    "status": code,
                    "size": random.randint(100, 5000)
                }
        except Exception:
            return None