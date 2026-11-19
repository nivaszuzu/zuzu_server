import http.server
import json
import os
import socketserver
import urllib.error
import urllib.parse
import urllib.request

DATA_DIR = os.environ.get("DATA_DIR", "/data")
DATA_FILE = os.path.join(DATA_DIR, "zuzu_dataset.json")
PORT = int(os.environ.get("PORT", "8080"))
MAX_BODY_BYTES = 10 * 1024 * 1024
ALLOWED_STATIC = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/manifest.json": ("manifest.json", "application/manifest+json"),
    "/icon-192.png": ("icon-192.png", "image/png"),
}
ALLOWED_CALDAV_METHODS = {"GET", "PUT", "DELETE", "REPORT", "PROPFIND"}
os.makedirs(DATA_DIR, exist_ok=True)


class ZuzuHandler(http.server.BaseHTTPRequestHandler):
    def send_security_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")

    def do_GET(self):
        path = urllib.parse.urlsplit(self.path).path
        if path == "/api/data":
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, "rb") as f:
                    payload = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_security_headers()
                self.end_headers()
                self.wfile.write(payload)
            else:
                self.send_response(404)
                self.send_security_headers()
                self.end_headers()
            return

        if path in ALLOWED_STATIC:
            filename, ctype = ALLOWED_STATIC[path]
            if os.path.exists(filename):
                with open(filename, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", ctype)
                self.send_security_headers()
                self.end_headers()
                self.wfile.write(content)
                return

        self.send_response(404)
        self.send_security_headers()
        self.end_headers()

    def do_POST(self):
        path = urllib.parse.urlsplit(self.path).path
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length <= 0 or length > MAX_BODY_BYTES:
            self.send_response(413)
            self.send_security_headers()
            self.end_headers()
            return

        raw_body = self.rfile.read(length).decode("utf-8", errors="replace")

        if path == "/api/data":
            try:
                parsed = json.loads(raw_body)
                if not isinstance(parsed, dict) or not isinstance(parsed.get("orders"), list):
                    raise ValueError("Invalid dataset structure")
                tmp_file = DATA_FILE + ".tmp"
                with open(tmp_file, "w", encoding="utf-8") as f:
                    json.dump(parsed, f, indent=2)
                os.replace(tmp_file, DATA_FILE)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_security_headers()
                self.end_headers()
                self.wfile.write(b'{"status":"saved"}')
            except Exception:
                self.send_response(400)
                self.send_security_headers()
                self.end_headers()
                self.wfile.write(b'{"error":"invalid_payload"}')
            return

        if path == "/api/radicale-proxy":
            try:
                req_data = json.loads(raw_body)
                method = str(req_data.get("method", "GET")).upper()
                url = str(req_data.get("url", ""))
                parsed_url = urllib.parse.urlsplit(url)
                if method not in ALLOWED_CALDAV_METHODS or parsed_url.scheme not in ("http", "https"):
                    self.send_response(400)
                    self.send_security_headers()
                    self.end_headers()
                    return
                headers = req_data.get("headers", {})
                if not isinstance(headers, dict):
                    headers = {}
                if not any(k.lower() == "user-agent" for k in headers):
                    headers["User-Agent"] = "ZuzuBeautyStudio-CalDAV/1.0"
                body_str = str(req_data.get("body", ""))
                data_bytes = body_str.encode("utf-8") if body_str else None
                req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
                try:
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        resp_body = resp.read().decode("utf-8", errors="replace")
                        out = json.dumps({"status": resp.status, "body": resp_body}).encode("utf-8")
                except urllib.error.HTTPError as he:
                    out = json.dumps({"status": he.code, "body": he.read().decode("utf-8", errors="replace")}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_security_headers()
                self.end_headers()
                self.wfile.write(out)
            except Exception as exc:
                out = json.dumps({"status": 502, "body": str(exc)}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_security_headers()
                self.end_headers()
                self.wfile.write(out)
            return

        self.send_response(404)
        self.send_security_headers()
        self.end_headers()


if __name__ == "__main__":
    with socketserver.TCPServer(("0.0.0.0", PORT), ZuzuHandler) as httpd:
        print(f"Zuzu Beauty Studio running on port {PORT}")
        httpd.serve_forever()
