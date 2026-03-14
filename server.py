"""
Serveur local avec proxy API pour contourner le CORS.
- Sert les fichiers statiques (index.html, etc.)
- Proxifie /api/* vers patrilog.com
"""
import http.server
from http.server import ThreadingHTTPServer
import urllib.request
import urllib.parse
import urllib.error
import os
import socket
import time

PORT = int(os.environ.get("PORT", 8090))
API_BASE = "https://patrilog.com"

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/healthz":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(b"OK")
            return

        if self.path.startswith("/api/"):
            self.proxy_request()
        else:
            super().do_GET()

    def proxy_request(self):
        url = API_BASE + self.path
        start = time.time()
        try:
            req = urllib.request.Request(url)
            req.add_header("User-Agent", "Mozilla/5.0")
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
                duration = time.time() - start
                print(f"[INFO] proxy {self.command} {self.path} -> {url} status={resp.status} time={duration:.2f}s")

                self.send_response(resp.status)
                self.send_header("Content-Type", resp.headers.get("Content-Type", "application/json"))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(data)
        except (urllib.error.URLError, socket.timeout) as e:
            print(f"[ERROR] urlopen failed for {url}: {e}")
            self.send_response(502)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(f"Proxy error: {e}".encode())
        except Exception as e:
            print(f"[ERROR] uncaught proxy error for {url}: {e}")
            self.send_response(500)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(f"Internal error: {e}".encode())

    def log_message(self, format, *args):
        # Shorter log
        print(f"[{self.log_date_time_string()}] {args[0]}")

print(f"Serveur démarré sur http://localhost:{PORT}")
print(f"Proxy API: /api/* → {API_BASE}/api/*")
ThreadingHTTPServer(("", PORT), ProxyHandler).serve_forever()
