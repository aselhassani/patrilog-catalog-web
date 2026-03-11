"""
Serveur local avec proxy API pour contourner le CORS.
- Sert les fichiers statiques (index.html, etc.)
- Proxifie /api/* vers patrilog.com
"""
import http.server
import urllib.request
import urllib.parse
import os

PORT = int(os.environ.get("PORT", 8090))
API_BASE = "https://patrilog.com"

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api/"):
            self.proxy_request()
        else:
            super().do_GET()

    def proxy_request(self):
        url = API_BASE + self.path
        try:
            req = urllib.request.Request(url)
            req.add_header("User-Agent", "Mozilla/5.0")
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
                self.send_response(resp.status)
                self.send_header("Content-Type", resp.headers.get("Content-Type", "application/json"))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(data)
        except Exception as e:
            self.send_response(502)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(f"Proxy error: {e}".encode())

    def log_message(self, format, *args):
        # Shorter log
        print(f"[{self.log_date_time_string()}] {args[0]}")

print(f"Serveur démarré sur http://localhost:{PORT}")
print(f"Proxy API: /api/* → {API_BASE}/api/*")
http.server.HTTPServer(("", PORT), ProxyHandler).serve_forever()
