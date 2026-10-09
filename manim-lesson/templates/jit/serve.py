"""JIT 播放器本地服务器:静态服务 + manifest.json 禁缓存。

用法: python serve.py [端口=8766]   (在 jit/ 目录下运行)
"""
import functools
import http.server
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


class H(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        if self.path.split("?")[0].endswith("manifest.json"):
            self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8766
    print(f"JIT 播放器: http://localhost:{port}/player.html")
    http.server.ThreadingHTTPServer(("127.0.0.1", port), functools.partial(H, directory=ROOT)).serve_forever()
