import requests
import os
import threading
from tool_api import get_data_file

def download_file(url, on_progress=None, on_done=None, on_error=None):
    def _run():
        try:
            headers = {
                "Range": "bytes=0-",
                "User-Agent": "Mozilla/5.0"
            }
            r = requests.get(url, headers=headers, stream=True, timeout=30)
            
            filename = url.split("/")[-1].split("?")[0]
            if "." not in filename:
                filename = "download.mp4"
            
            # downloads/ papkasi tool papkasi ichida
            download_dir = get_data_file(__file__, "downloads")
            os.makedirs(download_dir, exist_ok=True)
            
            save_path = os.path.join(download_dir, filename)
            
            total = int(r.headers.get("content-length", 0))
            downloaded = 0
            
            with open(save_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if on_progress and total:
                            percent = downloaded / total * 100
                            on_progress(percent, downloaded, total)
            
            if on_done:
                on_done(save_path)
                
        except Exception as e:
            if on_error:
                on_error(str(e))
    
    t = threading.Thread(target=_run)
    t.daemon = True
    t.start()