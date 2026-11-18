# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Qubbara Air, booking-change explainer: a training prototype.

State v1, step 3: the fare rule and the change fee are shown.
Standard library only. Run: uv run app.py, then open http://127.0.0.1:8205
"""
import csv
import json
import os
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_rules():
    return json.loads((HERE / "data" / "fare_rules.json").read_text(encoding="utf-8"))


def load_bookings():
    with open(HERE / "data" / "bookings.csv", encoding="utf-8", newline="") as f:
        return {row["ref"]: row for row in csv.DictReader(f)}


def page():
    return (HERE / "static" / "index.html").read_text(encoding="utf-8")


def explain(ref):
    ref = (ref or "").strip().upper()
    booking = BOOKINGS.get(ref)
    if booking is None:
        return {"ok": False, "message": "لم نجد حجزًا بهذا الرمز."}
    rule = RULES[booking["family"]]
    allowed = float(booking["hours_to_departure"]) >= rule["deadline_hours"]
    fee = rule["fee_per_passenger_segment"] if allowed else None
    return {"ok": True, "ref": ref, "route": booking["route"], "family": rule["name"],
            "rule_id": rule["id"], "rule_text": rule["text"], "allowed": allowed, "fee": fee}


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
        elif url.path == "/app.js":
            self.send(200, (HERE / "static" / "app.js").read_text(encoding="utf-8"), "text/javascript")
        elif url.path == "/api/explain":
            ref = urllib.parse.parse_qs(url.query).get("ref", [""])[0]
            self.send(200, json.dumps(explain(ref), ensure_ascii=False), "application/json")
        else:
            self.send(404, "not found", "text/plain")

    def log_message(self, fmt, *args):
        sys.stderr.write("request: " + (fmt % args) + "\n")


RULES = load_rules()
BOOKINGS = load_bookings()


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
