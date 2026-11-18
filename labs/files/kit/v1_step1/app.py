# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Qubbara Air, booking-change explainer: a training prototype.

State v1, step 1: a page with the booking-code form, served on this computer only.
Standard library only. Run: uv run app.py, then open http://127.0.0.1:8205
"""
import os
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent


def page():
    return (HERE / "static" / "index.html").read_text(encoding="utf-8")


class Handler(BaseHTTPRequestHandler):
    def send(self, status, body, kind):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", kind + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        if url.path == "/":
            self.send(200, page(), "text/html")
        else:
            self.send(404, "not found", "text/plain")

    def log_message(self, fmt, *args):
        sys.stderr.write("request: " + (fmt % args) + "\n")


def main():
    port = int(os.environ.get("PORT", "8205"))
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Open http://127.0.0.1:{port}  Stop with Ctrl+C.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
