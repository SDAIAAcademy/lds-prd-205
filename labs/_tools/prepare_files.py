# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Write the synthetic Qubbara Air files of LDS-PRD-205, the same bytes on every run.

Run from the course folder:  uv run labs/_tools/prepare_files.py
Writes: the data of every prototype state under labs/files/kit/, the contact-reason counts and
the idea memo, the fare-rule specification, the planted passenger export of the seeded copy, the
five recorded test sessions, the trainer's keys under labs/solutions/, and one zip per state.
Everything is synthetic: no real airline, person, booking or flight.
"""
import csv
import importlib.util
import io
import json
import random
import zipfile
from pathlib import Path

LABS = Path(__file__).resolve().parents[1]
FILES = LABS / "files"
KIT = FILES / "kit"
SOLUTIONS = LABS / "solutions"
STATES = ["start", "v1_step1", "v1_step2", "v1_step3", "v1_broken", "v2", "v3", "seeded"]
MODEL_STATES = ["v2", "v3", "seeded"]

RULES = {
    "B": {"id": "B-1", "name": "أساسي", "deadline_hours": 24, "deadline_text": "24 ساعة",
          "fee_per_passenger_segment": 150,
          "text": "يُسمح بالتغيير حتى 24 ساعة قبل الإقلاع، برسوم 150 ريالًا لكل مسافر عن كل رحلة، ويُدفع فرق السعر إن وُجد."},
    "V": {"id": "V-1", "name": "قيمة", "deadline_hours": 4, "deadline_text": "4 ساعات",
          "fee_per_passenger_segment": 75,
          "text": "يُسمح بالتغيير حتى 4 ساعات قبل الإقلاع، برسوم 75 ريالًا لكل مسافر عن كل رحلة، ويُدفع فرق السعر إن وُجد."},
    "F": {"id": "F-1", "name": "مرن", "deadline_hours": 1, "deadline_text": "ساعة واحدة",
          "fee_per_passenger_segment": 0,
          "text": "يُسمح بالتغيير حتى ساعة واحدة قبل الإقلاع دون رسوم، ويُدفع فرق السعر إن وُجد."},
}

STUB = {
    "_note": "Scripted stand-in for a hosted model (MODEL_MODE=stub). Fixed sentences filled from the facts in the prompt.",
    "allowed": "تستطيع تغيير حجزك وفق القاعدة {RULE_ID} لأجرة «{FAMILY}». رسوم التغيير لهذا الحجز بالريال: {FEE}، ويُضاف فرق السعر إن كانت الرحلة الجديدة أغلى. التغيير متاح حتى {DEADLINE} قبل الإقلاع.",
    "not_allowed": "لا يمكن تغيير هذا الحجز الآن وفق القاعدة {RULE_ID} لأجرة «{FAMILY}»، لأن التغيير يُغلق قبل الإقلاع بـ{DEADLINE}.",
    "no_rule": "تستطيع تغيير حجزك برسوم قدرها مئة ريال لكل مسافر، ويُضاف فرق السعر إن وُجد.",
}

ENV_EXAMPLE = """# انسخ هذا الملف باسم .env واملأه. الملف .env لا يدخل Git أبدًا.
# Copy to .env and fill it in. .env never enters Git.
# MODEL_MODE: stub (scripted stand-in, no key), hosted (a hosted model), fail (to test the fallback)
MODEL_MODE=stub
MODEL_BASE_URL=https://openrouter.ai/api/v1
MODEL_NAME=
MODEL_API_KEY=
MODEL_MAX_CALLS=30
"""

STATE_GITIGNORE = ".env\n__pycache__/\n"

START_README = """# نقطة البداية: شارح تغيير الحجز

مجلد البداية للمختبر 1.3. فيه البيانات الاصطناعية فقط، ولا برنامج فيه بعد.

- `data/fare_rules.json`: قواعد الأجرة الثلاث لطيران قُبّرة (قواعد الحالة الافتراضية، لا قواعد أي ناقل حقيقي).
- `data/bookings.csv`: ستة حجوزات للعرض، كلها لمسافر واحد ورحلة واحدة.

ضع هنا `BRIEF.md` و`AGENTS.md` من المختبرين 1.1 و1.2، ثم:

```
git init
git add .
git commit -m "Start: brief, context file and data"
```
"""

SEEDED_NOTES = """# ملاحظات البناء (آخر يوم قبل العرض)

- أضفت صورة طائرة للصفحة، أخذتها من نتائج البحث عن الصور.
- طلبت من الوكيل أن يحسّن عرض النص العربي، فأضاف حزمة إلى requirements.txt. لم أراجعها.
- طلبت من الوكيل أن يجعل الشرح أسرع، فأضاف استدعاءً للنموذج من المتصفح.
- لأختبر بأسماء حقيقية نسختُ passengers_export.csv من تصدير نظام الحجوزات إلى مجلد data.
- ملف القواعد يُقرأ من سطح المكتب عندي إن وُجد، لأعدّل القواعد بسرعة.
- غيّرت تصميم الصفحة: الحقل بلا عنوان ليبدو أنظف، وحذفت السطر الطويل في أسفلها.
"""

FIRST = ["عبدالرحمن", "نورة", "فهد", "سارة", "خالد", "منى", "سعود", "ريم", "ماجد", "هيا", "بدر", "جواهر"]
LAST = ["الحربي", "العتيبي", "القحطاني", "الشهري", "الغامدي", "الدوسري", "المطيري", "الزهراني"]


def load_make_bookings():
    spec = importlib.util.spec_from_file_location("make_bookings", KIT / "v2" / "make_bookings.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def write_json(path, data):
    write_text(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def write_csv(path, rows):
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    write_text(path, buffer.getvalue())


def luhn_ok(digits):
    total = 0
    for i, ch in enumerate(reversed(digits)):
        d = int(ch)
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def invalid_id(rng):
    """A ten-digit number in the shape of a Saudi ID whose check digit is wrong by construction."""
    body = "1" + "".join(rng.choice("0123456789") for _ in range(8))
    for last in "0123456789":
        if not luhn_ok(body + last):
            return body + last
    raise AssertionError("unreachable")


def contact_reasons(rng):
    reasons = [("تغيير حجز: الرسوم والقواعد", 0.24), ("تغيير حجز: التنفيذ", 0.09),
               ("الأمتعة", 0.18), ("استرداد", 0.14), ("تسجيل الوصول والمقاعد", 0.12),
               ("تأخر رحلة", 0.10), ("أخرى", 0.13)]
    counts = {name: 0 for name, _ in reasons}
    for _ in range(6000):
        x, acc = rng.random(), 0.0
        for name, p in reasons:
            acc += p
            if x < acc:
                counts[name] += 1
                break
        else:
            counts["أخرى"] += 1
    return [{"reason": k, "contacts": v} for k, v in counts.items()]


# The five recorded sessions: each observation carries the finding it supports.
SESSIONS = [
    {"id": "P1", "profile": "تسافر شهريًا للعمل، تحجز من الجوال", "obs": [
        ("T1", "ok", "كتبت الرمز QB3M9K، وقرأت «رسوم التغيير بالريال: 450» خلال دقيقة.", None),
        ("T1", "say", "«450 لكل واحد منا أم للثلاثة؟»", "F2"),
        ("T1", "say", "«طيب، كم فرق السعر؟ هذا الذي يهمني.»", "F4"),
        ("T1", "do", "مرّرت الصفحة إلى أسفلها تبحث عن زر للتغيير.", "F1"),
        ("T2", "ok", "مع QB2H8W فهمت أن التغيير غير ممكن الآن.", None)]},
    {"id": "P2", "profile": "يسافر مع أسرته في الإجازات", "obs": [
        ("T1", "ok", "وجد الرسوم وقرأ الشرح كاملًا.", None),
        ("T1", "say", "«أين أضغط لأغيّر الموعد؟»", "F1"),
        ("T1", "say", "«الرسوم واضحة، لكن لا أعرف السعر الجديد.»", "F4"),
        ("T1", "do", "لم ينظر إلى السطر الرمادي أسفل الصفحة، وسأل لاحقًا: «من كتب هذا الشرح؟»", "F3"),
        ("T2", "ok", "فهم أن الحجز لا يُغيَّر الآن.", None)]},
    {"id": "P3", "profile": "طالبة، أول رحلة تحجزها بنفسها", "obs": [
        ("T1", "fail", "لم تجد رمز الحجز في رسالة التأكيد المطبوعة، وأعطاها الميسّر إياه بعد دقيقتين.", "F5"),
        ("T1", "say", "«هل 450 رسوم كل مسافر؟»", "F2"),
        ("T1", "say", "«وإذا كانت الرحلة الجديدة أغلى، كم أدفع؟»", "F4"),
        ("T1", "do", "لم تلحظ أن الشرح مكتوب بالذكاء الاصطناعي.", "F3"),
        ("T2", "ok", "فهمت أن التغيير غير ممكن.", None)]},
    {"id": "P4", "profile": "متقاعد، يحجز عبر مكتب سفر عادة", "obs": [
        ("T1", "say", "«أين الرمز؟ لم أره قط.»", "F5"),
        ("T1", "ok", "بعد أن وجده قرأ الرسوم وفهمها.", None),
        ("T1", "do", "ضغط «اعرض الشرح» مرة ثانية ظنًّا أنه زر التنفيذ.", "F1"),
        ("T1", "do", "لم يرَ سطر الإفصاح.", "F3"),
        ("T2", "fail", "فهم «لا يمكن تغيير هذا الحجز» على أنه إلغاء للحجز، وقلق.", None)]},
    {"id": "P5", "profile": "موظفة مبيعات، تسافر أسبوعيًا", "obs": [
        ("T1", "ok", "وجدت الرسوم خلال ثوانٍ.", None),
        ("T1", "say", "«450 للمجموعة؟ لا تقولها الصفحة صراحة.»", "F2"),
        ("T1", "say", "«بدون فرق السعر لن أقرر شيئًا.»", "F4"),
        ("T1", "say", "«الشرح مكتوب بالذكاء الاصطناعي؟ هل هو رسمي إذن؟ وأين أغيّر؟»", "F1"),
        ("T2", "ok", "فهمت أن التغيير غير ممكن.", None)]},
]
FINDINGS = {
    "F1": "يظن المستخدم أن الصفحة تنفّذ التغيير، ويبحث عن زر لذلك",
    "F2": "لا يعرف هل الرسوم المعروضة للمسافر الواحد أم للحجز كله",
    "F3": "لا يلحظ أن الشرح مكتوب بالذكاء الاصطناعي",
    "F4": "يحتاج إلى فرق السعر ليقرر، والصفحة لا تعرضه",
    "F5": "لا يجد رمز الحجز",
}


def sessions_files():
    lines = ["# خمس جلسات اختبار مسجلة: شارح تغيير الحجز (الحالة v3)", "",
             "ملاحظات الميسّر من خمس جلسات قصيرة. المشاركون اصطناعيون، ويُشار إليهم برموز فقط.",
             "المهمة 1 (T1): «حجزك QB3M9K لثلاثة مسافرين ذهابًا وعودة. هل تستطيع تغيير رحلة العودة، وكم يكلّف؟»",
             "المهمة 2 (T2): «حجزك QB2H8W. هل تستطيع تغييره الآن؟»",
             "قبل كل جلسة قال الميسّر: «هذا نموذج أولي على بيانات اصطناعية، والشرح فيه يكتبه الذكاء الاصطناعي. لن يتغير أي حجز.»", ""]
    tally = {f: [] for f in FINDINGS}
    task = {"T1": 0, "T2": 0}
    for s in SESSIONS:
        lines += [f"## {s['id']} · {s['profile']}", ""]
        n = 1
        failed = set()
        for t, kind, text, finding in s["obs"]:
            label = {"ok": "نجح", "fail": "تعثّر", "say": "قال", "do": "فعل"}[kind]
            lines.append(f"{n}. [{t}] {label}: {text}")
            n += 1
            if finding and s["id"] not in tally[finding]:
                tally[finding].append(s["id"])
            if kind == "fail":
                failed.add(t)
        for t in task:
            if t not in failed:
                task[t] += 1
        lines.append("")
    write_text(FILES / "sessions_case.md", "\n".join(lines))
    key = {"findings": [{"id": f, "text": FINDINGS[f], "participants": tally[f], "count": len(tally[f])}
                        for f in FINDINGS],
           "task_success": task, "sessions": len(SESSIONS)}
    write_json(SOLUTIONS / "sessions_key.json", key)
    return key


def idea_files(rng):
    rows = contact_reasons(rng)
    write_csv(FILES / "contact_reasons.csv", rows)
    total = sum(r["contacts"] for r in rows)
    change_rules = next(r["contacts"] for r in rows if r["reason"] == "تغيير حجز: الرسوم والقواعد")
    share = round(100 * change_rules / total)
    memo = f"""# مذكرة فكرة: شارح تغيير الحجز

من: غيداء الصبّاغ، مديرة المنتج، القنوات الرقمية، طيران قُبّرة
إلى: فريق المنتج والتصميم

## ما لاحظناه

في شهر واحد سجّل مركز الاتصال {total:,} تواصل (`contact_reasons.csv`). منها {change_rules:,} تواصلًا ({share}%) سببه سؤال عن رسوم تغيير الحجز وقاعدته، دون طلب تنفيذ التغيير. تقول وفاء الخلف، قائدة مركز الاتصال، إن موظف المركز في كل واحد منها يقرأ القاعدة من نظام الأجرة ويحسب الرسوم ثم يشرحها.

## الفكرة

صفحة يكتب فيها المسافر رمز حجزه فيرى: هل يستطيع التغيير الآن، وكم الرسوم، وما القاعدة، بعربية واضحة. الرسوم يحسبها النظام من القواعد، والشرح يكتبه نموذج لغوي مستضاف.

## ما لا نعرفه

- هل يفهم المسافر الشرح ويقرر دون اتصال؟
- هل يكفي ما نعرضه ليقرر، أم يحتاج إلى شيء آخر؟
- هل يثق بشرح مكتوب بالذكاء الاصطناعي؟

## القيود التي أعرفها

- لا وصول إلى نظام الحجوزات الحقيقي ولا إلى بيانات المسافرين في هذه المرحلة: بيانات اصطناعية فقط (طلال الصغيّر، مسؤول حماية البيانات).
- مفتاح نموذج بحد إنفاق يعطيه م. ريان التريكي، قائد الهندسة، لمدة الورشة فقط.
- الصفحة بالعربية أولًا، ومن اليمين إلى اليسار.
- لدينا أسبوع واحد قبل اجتماع قرار الربع القادم: نبني مشروعًا تجريبيًا أم لا.
"""
    write_text(FILES / "idea_memo.md", memo)
    spec = ["# مواصفات قواعد تغيير الحجز (طيران قُبّرة، قواعد الحالة الافتراضية)", "",
            "| الأجرة | رمز القاعدة | آخر موعد للتغيير قبل الإقلاع | الرسوم لكل مسافر عن كل رحلة (ريال) |",
            "|---|---|---|---|"]
    for r in RULES.values():
        spec.append(f"| {r['name']} | {r['id']} | {r['deadline_text']} | {r['fee_per_passenger_segment']} |")
    spec += ["", "نص كل قاعدة:", ""]
    spec += [f"- **{r['id']}**: {r['text']}" for r in RULES.values()]
    spec += ["", "الرسوم = رسوم القاعدة × عدد المسافرين × عدد الرحلات في الحجز. فرق السعر لا يُعرف إلا عند اختيار الرحلة الجديدة.",
             "بعد آخر موعد للتغيير لا يُقبل التغيير."]
    write_text(FILES / "fare_rules_spec.md", "\n".join(spec) + "\n")
    return {"contacts_total": total, "change_rule_contacts": change_rules, "share_percent": share}


def passengers_export(rng):
    rows = []
    for i in range(12):
        rows.append({"full_name": f"{rng.choice(FIRST)} {rng.choice(LAST)}",
                     "national_id": invalid_id(rng),
                     "birth_date": f"19{rng.randint(60, 99)}-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
                     "booking_ref": f"QB{rng.choice('ACDEFH')}{rng.randint(10, 99)}{rng.choice('KMNP')}"})
    assert not any(luhn_ok(r["national_id"]) for r in rows)
    return rows


def zip_state(state):
    folder = KIT / state
    target = KIT / f"{state}.zip"
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
        for path in sorted(p for p in folder.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.name != ".env"):
            info = zipfile.ZipInfo(f"{state}/" + path.relative_to(folder).as_posix(), (2027, 3, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, path.read_bytes())


def main():
    mb = load_make_bookings()
    full = mb.make_rows()
    sample = full[:6]
    rules = RULES
    for state in STATES:
        folder = KIT / state
        write_json(folder / "data" / "fare_rules.json", rules)
        mb.write(folder / "data" / "bookings.csv", full if state in MODEL_STATES else sample)
        write_text(folder / ".gitignore", STATE_GITIGNORE)
        if state in MODEL_STATES:
            write_json(folder / "data" / "stub_answers.json", STUB)
            write_text(folder / ".env.example", ENV_EXAMPLE)
    write_text(KIT / "start" / "README.md", START_README)
    rng = random.Random(205)
    write_csv(KIT / "seeded" / "data" / "passengers_export.csv", passengers_export(rng))
    write_text(KIT / "seeded" / "NOTES.md", SEEDED_NOTES)
    memo = idea_files(random.Random(2051))
    key = sessions_files()
    for state in STATES:
        zip_state(state)
    multi = [r for r in full if int(r["passengers"]) * int(r["segments"]) > 1]
    facts = {"bookings_sample": len(sample), "bookings_full": len(full),
             "bookings_multi_passenger_or_segment": len(multi), **memo}
    write_json(SOLUTIONS / "case_facts.json", facts)
    print("states:", len(STATES), "| bookings:", len(sample), "then", len(full),
          "| multi-passenger or multi-segment:", len(multi))
    print("contacts:", memo["contacts_total"], "| fee-and-rule questions:", memo["change_rule_contacts"],
          f"({memo['share_percent']}%)")
    print("findings:", ", ".join(f"{f['id']} {f['count']}/5" for f in key["findings"]),
          "| task success:", key["task_success"])


if __name__ == "__main__":
    main()
