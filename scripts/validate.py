"""Check the data files. Runs automatically on each pull request.

Usage:  python scripts/validate.py          (check only)
        python scripts/validate.py --fix    (sort rows and remove extra spaces, then check)

Exit code 0 = no errors. Exit code 1 = errors (listed in the output).
Uses only the Python standard library.
"""
import csv
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

STATES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
    "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "DC": "District of Columbia",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois",
    "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana",
    "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan",
    "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri", "MT": "Montana",
    "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey",
    "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota",
    "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania",
    "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee",
    "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
    "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming", "PR": "Puerto Rico",
}
STATE_FIPS = {
    "AL": "01", "AK": "02", "AZ": "04", "AR": "05", "CA": "06", "CO": "08", "CT": "09",
    "DE": "10", "DC": "11", "FL": "12", "GA": "13", "HI": "15", "ID": "16", "IL": "17",
    "IN": "18", "IA": "19", "KS": "20", "KY": "21", "LA": "22", "ME": "23", "MD": "24",
    "MA": "25", "MI": "26", "MN": "27", "MS": "28", "MO": "29", "MT": "30", "NE": "31",
    "NV": "32", "NH": "33", "NJ": "34", "NM": "35", "NY": "36", "NC": "37", "ND": "38",
    "OH": "39", "OK": "40", "OR": "41", "PA": "42", "RI": "44", "SC": "45", "SD": "46",
    "TN": "47", "TX": "48", "UT": "49", "VT": "50", "VA": "51", "WA": "53", "WV": "54",
    "WI": "55", "WY": "56", "PR": "72",
}
COUNTY_TYPES = {"", "County", "Parish", "Borough", "City and Borough", "Census Area",
                "Municipality", "Independent City"}

FILES = {
    "states.csv": {
        "columns": ["state", "state_name", "nickname", "source", "notes"],
        "place": ["state"],
    },
    "counties.csv": {
        "columns": ["state", "county", "county_type", "county_fips", "nickname", "source", "notes"],
        "place": ["state", "county"],
    },
    "cities.csv": {
        "columns": ["state", "city", "nickname", "source", "notes"],
        "place": ["state", "city"],
    },
}


def sort_key(place_cols):
    return lambda r: tuple(r[c].lower() for c in place_cols) + (r["nickname"].lower(),)


def check_file(name, spec, fix):
    path = os.path.join(DATA, name)
    errors = []
    with open(path, newline="", encoding="utf-8") as f:
        text = f.read()
    if "\r" in text:
        if fix:
            text = text.replace("\r\n", "\n")
        else:
            errors.append(f"{name}: use LF line endings, not CRLF (run with --fix)")
    rows = list(csv.DictReader(text.splitlines()))
    header = text.splitlines()[0].split(",") if text else []
    if header != spec["columns"]:
        return [f"{name}: columns must be {','.join(spec['columns'])} (found {','.join(header)})"]

    if fix:
        for r in rows:
            for k in r:
                r[k] = re.sub(r"\s+", " ", (r[k] or "")).strip()
        rows.sort(key=sort_key(spec["place"]))
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=spec["columns"], lineterminator="\n")
            w.writeheader()
            w.writerows(rows)

    seen = set()
    prev = None
    for i, r in enumerate(rows, start=2):  # line 1 is the header
        where = f"{name} line {i}"
        if None in r or any(v is None for v in r.values()):
            errors.append(f"{where}: wrong number of fields (put quotes around a value with a comma)")
            continue
        for k, v in r.items():
            if v != v.strip() or "  " in v:
                errors.append(f"{where}: extra spaces in {k} (run with --fix)")
        if r["state"] not in STATES:
            errors.append(f"{where}: unknown state code {r['state']!r}")
        for c in spec["place"]:
            if not r[c]:
                errors.append(f"{where}: {c} is empty")
        nick = r["nickname"]
        if not nick:
            errors.append(f"{where}: nickname is empty")
        elif ";" in nick:
            errors.append(f"{where}: put each nickname on its own row (found ';')")
        if name == "states.csv" and r["state"] in STATES and r["state_name"] != STATES[r["state"]]:
            errors.append(f"{where}: state_name must be {STATES[r['state']]!r} for {r['state']}")
        if name == "counties.csv":
            if r["county_type"] not in COUNTY_TYPES:
                errors.append(f"{where}: county_type must be one of {sorted(COUNTY_TYPES - {''})}")
            fips = r["county_fips"]
            if fips and not re.fullmatch(r"\d{5}", fips):
                errors.append(f"{where}: county_fips must be 5 digits")
            elif fips and STATE_FIPS.get(r["state"]) != fips[:2]:
                errors.append(f"{where}: county_fips {fips} does not start with the FIPS code of {r['state']}")
        src = r["source"]
        if src and not (src.startswith(("http://", "https://")) or len(src) > 3):
            errors.append(f"{where}: source must be a URL or a short citation")
        key = tuple(r[c].lower() for c in spec["place"]) + (nick.lower(),)
        if key in seen:
            errors.append(f"{where}: duplicate nickname for this place")
        seen.add(key)
        k = sort_key(spec["place"])(r)
        if prev is not None and k < prev:
            errors.append(f"{where}: rows are not in sorted order (run with --fix)")
            prev = None  # report once per break
        else:
            prev = k
    print(f"{name}: {len(rows)} rows, {len(errors)} errors")
    return errors


def main():
    fix = "--fix" in sys.argv
    errors = []
    for name, spec in FILES.items():
        errors += check_file(name, spec, fix)
    for e in errors[:200]:
        print("ERROR:", e)
    if len(errors) > 200:
        print(f"... and {len(errors) - 200} more errors")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
