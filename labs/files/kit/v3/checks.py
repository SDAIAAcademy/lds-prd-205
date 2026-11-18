# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""The five acceptance checks of the booking-change explainer.

Run beside app.py:            uv run checks.py
Or on another state folder:   uv run checks.py ../v2
Always in stub or fail mode: the checks never call a hosted model and never need a key.
"""
import importlib.util
import os
import sys
from pathlib import Path


def load_app(folder, mode):
    os.environ["MODEL_MODE"] = mode
    os.environ["MODEL_MAX_CALLS"] = "30"
    spec = importlib.util.spec_from_file_location(f"app_{mode}", folder / "app.py")
    app = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(app)
    return app


def c1(folder):
    """Given a one-passenger Basic booking 96 hours out, the page names rule B-1 and a fee of 150."""
    r = load_app(folder, "stub").explain("QB4K7M")
    return r.get("ok") and r.get("rule_id") == "B-1" and r.get("fee") == 150 and "B-1" in r.get("explanation", "")


def c2(folder):
    """Given three passengers on two segments (Value), the fee is 75 x 3 x 2 = 450."""
    r = load_app(folder, "stub").explain("QB3M9K")
    return r.get("ok") and r.get("fee") == 450


def c3(folder):
    """Given an unknown code, the page says so and the model is not called."""
    app = load_app(folder, "stub")
    r = app.explain("ZZ9ZZ9")
    return (not r.get("ok")) and bool(r.get("message")) and app.MODEL_CALLS == 0


def c4(folder):
    """Given the model fails, the rule text is still shown and nothing crashes."""
    try:
        r = load_app(folder, "fail").explain("QB7N2P")
    except Exception:
        return False
    return r.get("ok") and r.get("source") == "fallback" and "V-1" in r.get("explanation", "")


def c5(folder):
    """The page is Arabic and right to left, the field has a label, and the AI text is disclosed."""
    html = load_app(folder, "stub").page()
    return ('lang="ar"' in html and 'dir="rtl"' in html and '<label for="ref"' in html
            and "الذكاء الاصطناعي" in html)


CHECKS = [("C1", "حجز لمسافر واحد: القاعدة والرسوم صحيحتان", c1),
          ("C2", "ثلاثة مسافرين ورحلتان: الرسوم تُضرب", c2),
          ("C3", "رمز غير موجود: رسالة واضحة دون استدعاء النموذج", c3),
          ("C4", "تعطل النموذج: القاعدة تظهر ولا ينهار شيء", c4),
          ("C5", "الصفحة عربية من اليمين وفيها عنوان للحقل وإفصاح", c5)]


def run(folder):
    results = {}
    for cid, label, fn in CHECKS:
        try:
            ok = bool(fn(folder))
        except Exception as error:
            ok = False
            label += f" (خطأ: {type(error).__name__})"
        results[cid] = ok
        print(("نجح " if ok else "فشل ") + cid + " · " + label)
    print(f"النتيجة: {sum(results.values())} من {len(results)}")
    return results


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    target = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent
    run(target)
