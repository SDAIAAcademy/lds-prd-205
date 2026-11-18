# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run the reference solution of every lab of LDS-PRD-205 and print PASS or the first difference.

Run from the course folder:   uv run labs/solutions/run_all.py          (all labs)
                              uv run labs/solutions/run_all.py 1.3      (one lab)
No hosted model is called and no key is needed: where a participant directs a coding agent, the
reference states under labs/files/kit/ stand in for the agent's work, and the model runs in stub
or fail mode. Lab 1.3 needs git. Temporary folders go under $LDS205_TMP when it is set.
"""
import csv
import importlib.util
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

LABS = Path(__file__).resolve().parents[1]
KIT = LABS / "files" / "kit"
SOL = LABS / "solutions"
REF = SOL / "reference"


def load_module(path, name, **env):
    for k, v in env.items():
        os.environ[k] = v
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def checks_on(state):
    checks = load_module(KIT / "v3" / "checks.py", "checks_ref")
    folder = KIT / state
    return {cid: bool(fn(folder)) for cid, _, fn in checks.CHECKS}


def expect(cond, message):
    if not cond:
        raise AssertionError(message)


def lab_1_1():
    text = (REF / "BRIEF.md").read_text(encoding="utf-8")
    for heading in ["## 1. السؤال", "## 2. مستوى الدقة", "## 3. النطاق", "## 4. البيانات", "## 5. القيود", "## 6. معايير الإنجاز"]:
        expect(heading in text, "reference brief misses " + heading)
    facts = json.loads((SOL / "case_facts.json").read_text(encoding="utf-8"))
    expect(f"{facts['change_rule_contacts']:,}" in text and f"{facts['contacts_total']:,}" in text,
           "brief numbers differ from contact_reasons.csv")
    memo = (LABS / "files" / "idea_memo.md").read_text(encoding="utf-8")
    expect(f"({facts['share_percent']}%)" in memo, "memo share differs from the data")
    print(f"  brief: six sections; {facts['change_rule_contacts']:,} of {facts['contacts_total']:,} contacts ({facts['share_percent']}%) as in the data")


def lab_1_2():
    plan = (LABS / "files" / "agent_plan.md").read_text(encoding="utf-8").splitlines()
    steps = {int(m.group(1)): line for line in plan if (m := re.match(r"(\d)\. ", line))}
    expect(len(steps) == 7, "the recorded plan has seven steps")
    markers = {2: "خطوة واحدة", 3: "قاعدة بيانات", 4: "موقع طيران", 5: "config.js", 6: "حزم"}
    for n, word in markers.items():
        expect(word in steps[n], f"plan step {n} lost its planted problem")
    agents = (REF / "AGENTS.md").read_text(encoding="utf-8")
    for rule in ["تغيير واحد في كل طلب", "اسأل قبل: إضافة أي حزمة", "أبدًا: مفتاح", "بيانات حقيقية", "BRIEF.md"]:
        expect(rule in agents, "reference context file misses: " + rule)
    print("  plan: 5 planted problems at steps 2 to 6; the reference context file blocks each one")


def git(repo, *args):
    env = dict(os.environ, GIT_AUTHOR_NAME="Participant", GIT_AUTHOR_EMAIL="participant@example.com",
               GIT_COMMITTER_NAME="Participant", GIT_COMMITTER_EMAIL="participant@example.com",
               GIT_AUTHOR_DATE="2027-03-01T09:00:00+03:00", GIT_COMMITTER_DATE="2027-03-01T09:00:00+03:00")
    out = subprocess.run(["git", "-c", "core.autocrlf=false", "-c", "init.defaultBranch=main", *args],
                         cwd=repo, env=env, capture_output=True, text=True, encoding="utf-8")
    expect(out.returncode == 0, "git " + " ".join(args) + " failed: " + out.stderr.strip()[:200])
    return out.stdout


def copy_state(state, repo):
    for path in (KIT / state).rglob("*"):
        if path.is_file() and "__pycache__" not in path.parts:
            target = repo / path.relative_to(KIT / state)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)


def smoke(repo, step):
    """What a participant checks by hand after each step, done by a script."""
    app = load_module(repo / "app.py", f"smoke_{step}_{os.urandom(3).hex()}")
    html = app.page()
    if step == 1:
        return 'lang="ar"' in html and '<label for="ref"' in html
    r = app.explain("QB4K7M")
    if step == 2:
        return r.get("ok") and r.get("family") == "أساسي"
    return r.get("ok") and r.get("rule_id") == "B-1" and r.get("fee") == 150


def remove_tree(path):
    def on_error(func, p, _):
        os.chmod(p, stat.S_IWRITE)
        func(p)
    shutil.rmtree(path, onexc=on_error) if sys.version_info >= (3, 12) else shutil.rmtree(path, onerror=on_error)


def lab_1_3():
    tmp = Path(tempfile.mkdtemp(prefix="lab13_", dir=os.environ.get("LDS205_TMP")))
    try:
        repo = tmp / "qubbara"
        repo.mkdir()
        copy_state("start", repo)
        shutil.copyfile(REF / "BRIEF.md", repo / "BRIEF.md")
        shutil.copyfile(REF / "AGENTS.md", repo / "AGENTS.md")
        git(repo, "init", "-q")
        git(repo, "add", ".")
        git(repo, "commit", "-q", "-m", "Start: brief, context file and data")
        for step, state, message in [(1, "v1_step1", "Step 1: page with the booking-code form"),
                                     (2, "v1_step2", "Step 2: look up the booking and show its fare"),
                                     (3, "v1_step3", "Step 3: show the rule and the change fee")]:
            copy_state(state, repo)
            expect(smoke(repo, step), f"step {step} does not pass its check")
            git(repo, "add", ".")
            git(repo, "commit", "-q", "-m", message)
        copy_state("v1_broken", repo)
        changed = git(repo, "diff", "--stat").strip().splitlines()
        try:
            broken_ok = smoke(repo, 3)
        except KeyError:
            broken_ok = False
        expect(not broken_ok, "the broken change should fail the step 3 check")
        git(repo, "restore", ".")
        expect(smoke(repo, 3), "after git restore the step 3 check should pass again")
        log = git(repo, "log", "--oneline").strip().splitlines()
        expect(len(log) == 4, f"expected 4 commits, found {len(log)}")
        print(f"  git: 4 commits, each step checked before its commit; the agent's tidy-up changed {changed[-1].strip()}, failed the check and was undone with git restore")
    finally:
        remove_tree(tmp)


def lab_1_4():
    mb = load_module(KIT / "v2" / "make_bookings.py", "mb")
    with open(KIT / "v2" / "data" / "bookings.csv", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    again = [{k: str(v) for k, v in r.items()} for r in mb.make_rows()]
    expect(rows == again, "make_bookings.py does not reproduce data/bookings.csv")
    multi = sum(1 for r in rows if int(r["passengers"]) * int(r["segments"]) > 1)
    app = load_module(KIT / "v2" / "app.py", "v2_stub", MODEL_MODE="stub", MODEL_MAX_CALLS="2")
    sources = [app.explain(ref)["source"] for ref in ["QB4K7M", "QB7N2P", "QB5D3X"]]
    expect(sources == ["model", "model", "fallback"], f"the call cap did not hold: {sources}")
    env_keys = set(re.findall(r"^([A-Z_]+)=", (KIT / "v2" / ".env.example").read_text(encoding="utf-8"), re.M))
    read_keys = set(re.findall(r'os\.environ\.get\("([A-Z_]+)"', (KIT / "v2" / "app.py").read_text(encoding="utf-8"))) - {"PORT"}
    expect(env_keys == read_keys, f".env.example {sorted(env_keys)} differs from what app.py reads {sorted(read_keys)}")
    for f in ["static/index.html", "static/app.js"]:
        expect("MODEL_API_KEY" not in (KIT / "v2" / f).read_text(encoding="utf-8"), "a key name reached the browser files")
    print(f"  data: {len(rows)} bookings, the same on a second run, {multi} with more than one passenger or segment")
    print(f"  cap of 2 calls: answers came from {sources}; .env.example names exactly what app.py reads")


def lab_2_1():
    v2, v3 = checks_on("v2"), checks_on("v3")
    expect(v2 == {"C1": True, "C2": False, "C3": False, "C4": True, "C5": True}, f"v2: {v2}")
    expect(all(v3.values()), f"v3: {v3}")
    fee = load_module(KIT / "v2" / "app.py", "v2_c2", MODEL_MODE="stub", MODEL_MAX_CALLS="30").explain("QB3M9K")["fee"]
    print(f"  v2: {sum(v2.values())} of 5 (C2 shows {fee} in place of 450; C3 calls the model); v3: 5 of 5")


def lab_2_2():
    scan = load_module(KIT / "limits_scan.py", "scan")
    found = scan.scan(KIT / "seeded")
    kinds = sorted({k for k, *_ in found})
    expect(kinds == ["package", "path", "personal", "secret"], f"scan kinds: {kinds}")
    expect(scan.scan(KIT / "v3") == [], "v3 should scan clean")
    seeded = checks_on("seeded")
    expect([c for c, ok in seeded.items() if not ok] == ["C5"], f"seeded checks: {seeded}")
    html = (KIT / "seeded" / "static" / "index.html").read_text(encoding="utf-8")
    hand = {"L5 lang/dir": 'lang="en"' in html and 'dir=' not in html,
            "L6 label/alt": "<label" not in html and "alt=" not in html,
            "L7 image of unknown origin": (KIT / "seeded" / "static" / "plane.svg").exists()
            and "نتائج البحث عن الصور" in (KIT / "seeded" / "NOTES.md").read_text(encoding="utf-8"),
            "L8 no AI disclosure": "الذكاء الاصطناعي" not in html}
    expect(all(hand.values()), f"hand items: {hand}")
    ids = [r["national_id"] for r in csv.DictReader(open(KIT / "seeded" / "data" / "passengers_export.csv", encoding="utf-8"))]
    gen = load_module(LABS / "_tools" / "prepare_files.py", "prep")
    expect(not any(gen.luhn_ok(i) for i in ids), "an ID in the planted export passes the check digit")
    print(f"  scan: {len(found)} lines in 4 kinds (L1 to L4); checks: C5 fails only; by hand: L5 to L8 present")
    print(f"  the {len(ids)} ID-shaped numbers all fail the check digit: synthetic by construction")


def lab_2_3():
    key = json.loads((SOL / "sessions_key.json").read_text(encoding="utf-8"))
    gen = load_module(LABS / "_tools" / "prepare_files.py", "prep2")
    tally = {}
    for s in gen.SESSIONS:
        for _, _, _, f in s["obs"]:
            if f:
                tally.setdefault(f, set()).add(s["id"])
    for f in key["findings"]:
        expect(len(tally[f["id"]]) == f["count"], f"{f['id']} count differs")
    text = (LABS / "files" / "sessions_case.md").read_text(encoding="utf-8")
    expect(text.count("## P") == 5 and "الذكاء الاصطناعي" in text, "five sessions with the disclosure line")
    table = (REF / "findings_table.md").read_text(encoding="utf-8")
    for f in key["findings"]:
        expect(f"{f['count']} من 5" in table, f"findings table misses {f['id']}")
    print("  findings:", ", ".join(f"{f['id']} {f['count']}/5" for f in key["findings"]),
          f"| T1 {key['task_success']['T1']}/5, T2 {key['task_success']['T2']}/5")


LABS_RUN = {"1.1": lab_1_1, "1.2": lab_1_2, "1.3": lab_1_3, "1.4": lab_1_4,
            "2.1": lab_2_1, "2.2": lab_2_2, "2.3": lab_2_3}

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    wanted = sys.argv[1:] or list(LABS_RUN)
    failed = 0
    for lab in wanted:
        try:
            LABS_RUN[lab]()
            print(f"PASS {lab}")
        except Exception as error:
            failed += 1
            print(f"FAIL {lab}: {error}")
    sys.exit(1 if failed else 0)
