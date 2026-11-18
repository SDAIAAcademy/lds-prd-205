# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""A first pass of the limits checklist: what a script can find in a prototype folder.

Run: uv run limits_scan.py <folder>     (for example: uv run limits_scan.py seeded)
Finds four kinds of limit: secrets written in files, paths of one computer, packages nobody
vetted, and files that look like real personal data. It reads files and changes nothing.
The other items of the checklist (accessibility, right to left, licences, AI disclosure) are
checked by hand: a script that finds nothing does not make a prototype safe.
"""
import csv
import re
import sys
from pathlib import Path

TEXT = {".py", ".js", ".html", ".css", ".md", ".json", ".txt", ".toml", ".csv", ".cfg", ".ini", ".yml", ".yaml"}
SECRET = re.compile(r"(api[_-]?key|secret|token|password)\w*\s*[:=]\s*['\"]([^'\"]{12,})['\"]", re.I)
LOCAL_PATH = re.compile(r"([A-Za-z]:[\\/](Users|Documents and Settings)[\\/]|/home/[a-z]|/Users/[A-Za-z])")
ID_LIKE = re.compile(r"\b[12]\d{9}\b")
PERSONAL_COLUMNS = {"national_id", "id_number", "passport", "birth_date", "date_of_birth", "mobile", "phone", "email", "full_name"}
VETTED = set()  # the reference prototype uses the standard library only


def files(folder):
    for path in sorted(folder.rglob("*")):
        if path.is_file() and path.suffix.lower() in TEXT and "__pycache__" not in path.parts:
            if path.name in (".env.example", "limits_scan.py"):
                continue
            yield path


def scan(folder):
    findings = []
    for path in files(folder):
        rel = path.relative_to(folder).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        for n, line in enumerate(text.splitlines(), 1):
            if SECRET.search(line):
                findings.append(("secret", rel, n, "سرّ مكتوب في ملف"))
            if LOCAL_PATH.search(line):
                findings.append(("path", rel, n, "مسار على جهاز شخص واحد"))
        if path.suffix == ".csv":
            with open(path, encoding="utf-8", newline="") as f:
                header = next(csv.reader(f), [])
            personal = sorted(PERSONAL_COLUMNS & {h.strip().lower() for h in header})
            ids = len(ID_LIKE.findall(text))
            if personal or ids:
                findings.append(("personal", rel, 1, f"أعمدة شخصية: {', '.join(personal) or 'لا'}؛ أرقام بشكل الهوية: {ids}"))
    for name in ("requirements.txt", "pyproject.toml", "package.json"):
        req = folder / name
        if req.exists():
            for n, line in enumerate(req.read_text(encoding="utf-8").splitlines(), 1):
                pkg = line.split("#")[0].strip()
                if not pkg or pkg.startswith("["):
                    continue
                base = re.split(r"[=<>~! ]", pkg)[0]
                if base not in VETTED:
                    pinned = "==" in pkg
                    findings.append(("package", name, n, f"حزمة لم تُفحص: {base}" + ("" if pinned else " (بلا إصدار مثبت)")))
    return findings


LABELS = {"secret": "سر", "path": "مسار", "package": "حزمة", "personal": "بيانات شخصية"}

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2:
        print("Usage: uv run limits_scan.py <folder>")
        sys.exit(0)
    folder = Path(sys.argv[1]).resolve()
    if not folder.is_dir():
        print("Not a folder:", sys.argv[1])
        sys.exit(0)
    found = scan(folder)
    for kind, rel, n, note in found:
        print(f"[{LABELS[kind]}] {rel}:{n} · {note}")
    kinds = sorted({k for k, *_ in found})
    print(f"المجموع: {len(found)}، من {len(kinds)} أنواع من أصل 4. أكمل القائمة باليد: الوصول، والاتجاه، والتراخيص، والإفصاح.")
