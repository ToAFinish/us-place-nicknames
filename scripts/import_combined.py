"""Import a "combined" CSV file (one row per place, nicknames separated by ";")
into the data/ files (one row per nickname).

Use this script when you edit the combined file in a spreadsheet program.

Usage:
  python scripts/import_combined.py cities   path/to/city_nicknames_combined.csv
  python scripts/import_combined.py counties path/to/county_nicknames_combined.csv
  python scripts/import_combined.py states   path/to/state_nicknames_combined.csv

Add --dry-run to see the changes without writing files.

The script:
  - replaces data/<level>.csv with the contents of the combined file,
  - removes empty nicknames and duplicate nicknames (capital letters are ignored),
  - removes "<X>" when the same place also has "A <X>" or "The <X>" (keeps the longer one),
  - keeps the source and notes values of nicknames that did not change,
  - keeps county_type and county_fips of counties that already exist,
  - updates the count in the README table,
  - prints a list of the changes.

Then run:  python scripts/validate.py --fix
Uses only the Python standard library.
"""
import csv
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from validate import FILES, STATES  # noqa: E402

LEVELS = {
    "states": {"place": "state_name", "label": "State"},
    "counties": {"place": "county", "label": "County"},
    "cities": {"place": "city", "label": "City and town"},
}


def clean(nicknames):
    """Split, trim, remove duplicates and A/The duplicates. Return (kept, removed)."""
    out, seen, removed = [], set(), []
    for n in re.split(r"\s*;\s*", nicknames or ""):
        n = re.sub(r"\s+", " ", n).strip()
        if not n:
            continue
        if n.lower() in seen:
            removed.append((n, "duplicate"))
            continue
        seen.add(n.lower())
        out.append(n)
    low = {n.lower() for n in out}
    kept = []
    for n in out:
        if any((a + n).lower() in low for a in ("A ", "The ")):
            removed.append((n, "a longer version with 'A' or 'The' exists"))
        else:
            kept.append(n)
    return kept, removed


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    if len(args) != 2 or args[0] not in LEVELS:
        print(__doc__)
        sys.exit(2)
    level, src = args
    pc = LEVELS[level]["place"]
    fields = FILES[level + ".csv"]["columns"]
    path = os.path.join(DATA, level + ".csv")

    with open(path, encoding="utf-8", newline="") as f:
        old_rows = list(csv.DictReader(f))
    old_by_nick = {(r["state"], r[pc].lower(), r["nickname"].lower()): r for r in old_rows}
    old_place = {}
    for r in old_rows:
        old_place.setdefault((r["state"], r[pc].lower()), r)

    with open(src, encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        next(reader)  # header
        combined = [row for row in reader if row and row[0].strip()]

    new_rows, problems, auto_removed = [], [], []
    for row in combined:
        key = row[0].strip()
        nicks = row[1] if len(row) > 1 else ""
        state = key[:2].upper()
        name = STATES.get(state, "") if level == "states" else key[2:].strip()
        if state not in STATES:
            problems.append(f"{key}: unknown state code {state!r}")
            continue
        kept, removed = clean(nicks)
        for n, why in removed:
            auto_removed.append(f"{key}: removed {n!r} ({why})")
        if not kept:
            problems.append(f"{key}: no nicknames, so the place is not in the data")
        base = old_place.get((state, name.lower()))
        if level == "counties" and not base:
            problems.append(f"{key}: new county; add county_type and county_fips by hand")
        for n in kept:
            old = old_by_nick.get((state, name.lower(), n.lower()), {})
            r = {c: "" for c in fields}
            r.update({"state": state, pc: name, "nickname": n,
                      "source": old.get("source", ""), "notes": old.get("notes", "")})
            if level == "counties" and base:
                r["county_type"], r["county_fips"] = base["county_type"], base["county_fips"]
            new_rows.append(r)

    # ---- report
    def keyset(rows):
        return {(r["state"], r[pc], r["nickname"]) for r in rows}
    old_k, new_k = keyset(old_rows), keyset(new_rows)
    added = sorted(new_k - old_k)
    deleted = sorted(old_k - new_k)
    places_old = {(r["state"], r[pc]) for r in old_rows}
    places_new = {(r["state"], r[pc]) for r in new_rows}
    print(f"{level}: {len(old_rows)} -> {len(new_rows)} nicknames, "
          f"{len(places_old)} -> {len(places_new)} places")
    print(f"  added nicknames:   {len(added)}")
    print(f"  removed nicknames: {len(deleted)}")
    for s, p, n in added:
        print(f"    + {s} {p}: {n}")
    for s, p, n in deleted:
        print(f"    - {s} {p}: {n}")
    for line in auto_removed:
        print("  AUTO", line)
    for line in problems:
        print("  CHECK", line)

    if dry:
        print("Dry run: no files changed.")
        return

    new_rows.sort(key=lambda r: (r["state"].lower(), r[pc].lower(), r["nickname"].lower()))
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(new_rows)

    readme = os.path.join(ROOT, "README.md")
    if os.path.exists(readme):
        text = open(readme, encoding="utf-8").read()
        pattern = (r"(\| \[`data/" + level + r"\.csv`\]\(data/" + level + r"\.csv\) \| "
                   + re.escape(LEVELS[level]["label"]) + r" \| )[\d,]+ \| [\d,]+ \|")
        text2 = re.sub(pattern, lambda m: f"{m.group(1)}{len(places_new):,} | {len(new_rows):,} |", text)
        if text2 != text:
            open(readme, "w", encoding="utf-8").write(text2)
            print("README.md: counts updated")
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
