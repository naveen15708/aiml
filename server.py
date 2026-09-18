from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from model import assess

ROOT = Path(__file__).parent


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, content_type: str, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/api/health":
            self._send(200, "application/json", b'{"status":"ok"}')
            return
        if self.path == "/":
            asset = ROOT / "static" / "index.html"
            content_type = "text/html; charset=utf-8"
        elif self.path in ("/static/app.js", "/static/styles.css"):
            asset = ROOT / self.path.lstrip("/")
            content_type = "application/javascript; charset=utf-8" if asset.suffix == ".js" else "text/css; charset=utf-8"
        else:
            self._send(404, "text/plain; charset=utf-8", b"Not found")
            return
        self._send(200, content_type, asset.read_bytes())

    def do_POST(self) -> None:
        if self.path != "/api/assess":
            self._send(404, "application/json", b'{"error":"Not found"}')
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            result = assess(json.loads(self.rfile.read(length)))
        except (ValueError, json.JSONDecodeError) as exc:
            self._send(400, "application/json", json.dumps({"error": str(exc)}).encode())
            return
        self._send(200, "application/json", json.dumps(result).encode())

    def log_message(self, format: str, *args: object) -> None:
        return


if __name__ == "__main__":
    print("Decision support system running at http://localhost:8000")
    ThreadingHTTPServer(("localhost", 8000), Handler).serve_forever()
