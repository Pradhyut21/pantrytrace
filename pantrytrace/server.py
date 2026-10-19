"""Loopback-only web interface for the PantryTrace research prototype."""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from . import list_scenarios, run_case

WEB = Path(__file__).resolve().parents[1] / "web"


class Handler(BaseHTTPRequestHandler):
    server_version = "PantryTrace/0.1"

    def valid_host(self):
        port = self.server.server_port
        return self.headers.get("Host") in {f"127.0.0.1:{port}", f"localhost:{port}"}

    def send_json(self, payload, status=200):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if not self.valid_host():
            return self.send_json({"error": "Host not allowed"}, 403)
        path = urlparse(self.path).path
        if path == "/api/scenarios":
            return self.send_json(list_scenarios())
        if path == "/api/health":
            return self.send_json({"status": "ok", "mode": "fixture", "version": "0.1.0"})
        names = {"/": "index.html", "/app.js": "app.js", "/style.css": "style.css"}
        if path not in names:
            return self.send_json({"error": "Not found"}, 404)
        file = WEB / names[path]
        if not file.is_file():
            return self.send_json({"error": "Asset unavailable"}, 404)
        data = file.read_bytes()
        types = {".html": "text/html", ".js": "text/javascript", ".css": "text/css"}
        self.send_response(200)
        self.send_header("Content-Type", types[file.suffix] + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if not self.valid_host():
            return self.send_json({"error": "Host not allowed"}, 403)
        if urlparse(self.path).path != "/api/run":
            return self.send_json({"error": "Not found"}, 404)
        origin = self.headers.get("Origin")
        host = self.headers.get("Host", "")
        if origin and origin != "http://" + host:
            return self.send_json({"error": "Cross-origin requests are disabled"}, 403)
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 4096:
                return self.send_json({"error": "Expected a small JSON request"}, 400)
            body = json.loads(self.rfile.read(length))
            if not isinstance(body, dict):
                raise ValueError("Expected a JSON object")
            if body.get("mode", "fixture") != "fixture":
                return self.send_json({"error": "Web workbench runs fixture mode. Verify sponsor connections with the CLI before live work."}, 422)
            result = run_case(scenario=body.get("scenario", "ambiguous"), mode="fixture")
        except (ValueError, TypeError, KeyError, UnicodeDecodeError) as exc:
            return self.send_json({"error": str(exc)}, 400)
        return self.send_json(result)


def serve(port=8765):
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"PantryTrace local workbench: http://127.0.0.1:{server.server_port}", flush=True)
    print("Synthetic fixtures only. Press Ctrl+C to stop.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
