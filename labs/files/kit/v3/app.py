# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Qubbara Air, booking-change explainer: a training prototype.

State v3: after the five acceptance checks. The fee is computed by code for every passenger
and segment; an unknown booking stops before the model is called.
Standard library only. Run: uv run app.py, then open http://127.0.0.1:8205
Synthetic data only. The model key is read from the environment or from .env, never from code.
"""
import csv
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODEL_CALLS = 0


def load_env():
    """Read KEY=value lines from .env beside this file, without overriding the environment."""
    env_file = HERE / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def load_rules():
    return json.loads((HERE / "data" / "fare_rules.json").read_text(encoding="utf-8"))


def load_bookings():
    with open(HERE / "data" / "bookings.csv", encoding="utf-8", newline="") as f:
        return {row["ref"]: row for row in csv.DictReader(f)}


class ModelError(Exception):
    pass


def call_model(prompt):
    """Return the model's text. MODEL_MODE: stub (default), hosted, fail."""
    global MODEL_CALLS
    limit = int(os.environ.get("MODEL_MAX_CALLS", "30"))
    if MODEL_CALLS >= limit:
        raise ModelError("call limit reached")
    MODEL_CALLS += 1
    mode = os.environ.get("MODEL_MODE", "stub")
    if mode == "fail":
        raise ModelError("model unavailable (fail mode)")
    if mode == "stub":
        return stub_answer(prompt)
    key = os.environ.get("MODEL_API_KEY", "")
    base = os.environ.get("MODEL_BASE_URL", "").rstrip("/")
    name = os.environ.get("MODEL_NAME", "")
    if not (key and base and name):
        raise ModelError("hosted mode needs MODEL_API_KEY, MODEL_BASE_URL and MODEL_NAME in .env")
    body = json.dumps({
        "model": name,
        "temperature": 0.2,
        "max_tokens": 300,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    }).encode("utf-8")
    request = urllib.request.Request(
        base + "/chat/completions", data=body,
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"].strip()
    except (urllib.error.URLError, TimeoutError, KeyError, IndexError, ValueError) as error:
        raise ModelError(str(error))


SYSTEM_PROMPT = (
    "أنت تشرح لمسافر بالعربية الفصحى البسيطة قاعدة تغيير حجزه. استعمل القاعدة والأرقام "
    "المعطاة فقط، ولا تخترع رقمًا ولا قاعدة. ثلاث جمل على الأكثر. اذكر رمز القاعدة."
)


def stub_answer(prompt):
    """The scripted stand-in for the model: fills a fixed sentence from the facts in the prompt."""
    answers = json.loads((HERE / "data" / "stub_answers.json").read_text(encoding="utf-8"))
    facts = dict(line.split(": ", 1) for line in prompt.splitlines() if ": " in line)
    if "RULE_ID" not in facts:
        return answers["no_rule"]
    template = answers["allowed"] if facts.get("ALLOWED") == "yes" else answers["not_allowed"]
    return template.format(**facts)


def build_prompt(booking, rule, fee, allowed):
    return "\n".join([
        "RULE_ID: " + rule["id"],
        "FAMILY: " + rule["name"],
        "RULE_TEXT: " + rule["text"],
        "PASSENGERS: " + booking["passengers"],
        "SEGMENTS: " + booking["segments"],
        "ALLOWED: " + ("yes" if allowed else "no"),
        "FEE: " + (str(fee) if fee is not None else "-"),
        "DEADLINE: " + rule["deadline_text"],
    ])


def fallback_text(rule, fee, allowed):
    if not allowed:
        return f"لا يمكن تغيير هذا الحجز الآن. القاعدة {rule['id']}: {rule['text']}"
    return f"رسوم التغيير بالريال: {fee}، ويُضاف فرق السعر إن وُجد. القاعدة {rule['id']}: {rule['text']}"


def explain(ref):
    ref = (ref or "").strip().upper().replace(" ", "")
    booking = BOOKINGS.get(ref)
    if booking is None:
        return {"ok": False,
                "message": "لم نجد حجزًا بهذا الرمز. الرمز ستة أحرف وأرقام، تجده في رسالة تأكيد الحجز."}
    rule = RULES[booking["family"]]
    allowed = float(booking["hours_to_departure"]) >= rule["deadline_hours"]
    fee = None
    if allowed:
        fee = rule["fee_per_passenger_segment"] * int(booking["passengers"]) * int(booking["segments"])
    try:
        text, source = call_model(build_prompt(booking, rule, fee, allowed)), "model"
    except ModelError:
        text, source = fallback_text(rule, fee, allowed), "fallback"
    return {"ok": True, "ref": ref, "route": booking["route"], "family": rule["name"],
            "rule_id": rule["id"], "allowed": allowed, "fee": fee,
            "passengers": int(booking["passengers"]), "segments": int(booking["segments"]),
            "explanation": text, "source": source,
            "mode": os.environ.get("MODEL_MODE", "stub")}


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
        elif url.path == "/app.js":
            self.send(200, (HERE / "static" / "app.js").read_text(encoding="utf-8"), "text/javascript")
        elif url.path == "/api/explain":
            ref = urllib.parse.parse_qs(url.query).get("ref", [""])[0]
            self.send(200, json.dumps(explain(ref), ensure_ascii=False), "application/json")
        else:
            self.send(404, "not found", "text/plain")

    def log_message(self, fmt, *args):
        sys.stderr.write("request: " + (fmt % args) + "\n")


load_env()
RULES = load_rules()
BOOKINGS = load_bookings()


def main():
    port = int(os.environ.get("PORT", "8205"))
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Open http://127.0.0.1:{port}  (model mode: {os.environ.get('MODEL_MODE', 'stub')}). Stop with Ctrl+C.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
