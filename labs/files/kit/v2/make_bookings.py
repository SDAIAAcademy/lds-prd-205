# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Write data/bookings.csv: 40 synthetic Qubbara Air bookings, the same file on every run.

No real person, booking or flight. Seed 205. The first seven rows are fixed on purpose: the six
demonstration bookings of the first version, then one booking for three passengers on two
segments. Run: uv run make_bookings.py
"""
import csv
import random
from pathlib import Path

FIXED = [
    # ref, family, passengers, segments, route, hours to departure
    ("QB4K7M", "B", 1, 1, "الرياض - جدة", 96),
    ("QB7N2P", "V", 1, 1, "جدة - الدمام", 30),
    ("QB9R5T", "F", 1, 1, "الدمام - أبها", 3),
    ("QB2H8W", "B", 1, 1, "أبها - الرياض", 10),
    ("QB5D3X", "V", 1, 1, "الرياض - تبوك", 72),
    ("QB8F6Y", "F", 1, 1, "تبوك - جدة", 200),
    ("QB3M9K", "V", 3, 2, "الرياض - المدينة المنورة - الرياض", 50),
]
CITIES = ["الرياض", "جدة", "الدمام", "أبها", "تبوك", "المدينة المنورة", "القصيم", "جازان"]
LETTERS = "ACDEFHJKMNPRTWXY"
DIGITS = "23456789"


def make_rows(seed=205, total=40):
    rng = random.Random(seed)
    rows = [dict(zip(["ref", "family", "passengers", "segments", "route", "hours_to_departure"], r))
            for r in FIXED]
    used = {r["ref"] for r in rows}
    while len(rows) < total:
        ref = "QB" + "".join(rng.choice(LETTERS + DIGITS) for _ in range(4))
        if ref in used:
            continue
        used.add(ref)
        a, b = rng.sample(CITIES, 2)
        segments = rng.choice([1, 1, 1, 2])
        route = f"{a} - {b}" if segments == 1 else f"{a} - {b} - {a}"
        rows.append({
            "ref": ref,
            "family": rng.choice("BBBVVF"),
            "passengers": rng.choice([1, 1, 1, 2, 2, 3, 4]),
            "segments": segments,
            "route": route,
            "hours_to_departure": rng.choice([2, 5, 12, 20, 30, 48, 72, 120, 240, 400]),
        })
    return rows


def write(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "data" / "bookings.csv"
    rows = make_rows()
    write(out, rows)
    print(f"wrote data/bookings.csv: {len(rows)} bookings")
