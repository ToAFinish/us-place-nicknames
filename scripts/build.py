"""Make the download files in dist/ from the files in data/.

Usage:  python scripts/build.py

Output:
  dist/all_nicknames.csv   one file with all levels (state, county, city)
  dist/nicknames.json      the same data, grouped by state and place
  dist/state_nicknames_combined.csv    one row per state,  nicknames separated by "; "
  dist/county_nicknames_combined.csv   one row per county, nicknames separated by "; "
  dist/city_nicknames_combined.csv     one row per city,   nicknames separated by "; "
  dist/us-place-nicknames.zip   data/*.csv + the files above + README + LICENSE

Do not edit the files in dist/ by hand. Edit data/*.csv and run this script again.
Uses only the Python standard library.
"""
import csv
import json
import os
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
DIST = os.path.join(ROOT, "dist")


def read(name):
    with open(os.path.join(DATA, name), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    os.makedirs(DIST, exist_ok=True)
    states, counties, cities = read("states.csv"), read("counties.csv"), read("cities.csv")

    # ---- combined CSV
    combined = []
    for r in states:
        combined.append({"level": "state", "state": r["state"], "place": r["state_name"],
                         "county_fips": "", "nickname": r["nickname"],
                         "source": r["source"], "notes": r["notes"]})
    for r in counties:
        label = f"{r['county']} {r['county_type']}".strip()
        combined.append({"level": "county", "state": r["state"], "place": label,
                         "county_fips": r["county_fips"], "nickname": r["nickname"],
                         "source": r["source"], "notes": r["notes"]})
    for r in cities:
        combined.append({"level": "city", "state": r["state"], "place": r["city"],
                         "county_fips": "", "nickname": r["nickname"],
                         "source": r["source"], "notes": r["notes"]})
    cols = ["level", "state", "place", "county_fips", "nickname", "source", "notes"]
    with open(os.path.join(DIST, "all_nicknames.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(combined)

    # ---- nested JSON: {state: {name, nicknames, counties: {...}, cities: {...}}}
    out = {}

    def state_node(code):
        return out.setdefault(code, {"name": "", "nicknames": [], "counties": {}, "cities": {}})

    for r in states:
        node = state_node(r["state"])
        node["name"] = r["state_name"]
        node["nicknames"].append(r["nickname"])
    for r in counties:
        c = state_node(r["state"])["counties"].setdefault(
            r["county"], {"type": r["county_type"], "fips": r["county_fips"], "nicknames": []})
        c["nicknames"].append(r["nickname"])
    for r in cities:
        state_node(r["state"])["cities"].setdefault(r["city"], []).append(r["nickname"])
    with open(os.path.join(DIST, "nicknames.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1, sort_keys=True)

    # ---- combined files: one row per place, same layout as the original files
    def combined_file(name, header, rows, key):
        groups = {}
        for r in rows:
            groups.setdefault(key(r), []).append(r["nickname"])
        with open(os.path.join(DIST, name), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(header)
            for k in sorted(groups, key=lambda k: k.lower()):
                w.writerow([k, "; ".join(sorted(groups[k], key=str.lower))])
        return len(groups)

    combined_file("state_nicknames_combined.csv", ["State", "Nicknames"], states, lambda r: r["state"])
    combined_file("county_nicknames_combined.csv", ["Key", "Nicknames"], counties,
                  lambda r: r["state"] + r["county"])
    combined_file("city_nicknames_combined.csv", ["Key", "Nicknames"], cities,
                  lambda r: r["state"] + r["city"])

    # ---- ZIP
    zpath = os.path.join(DIST, "us-place-nicknames.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for name in ("states.csv", "counties.csv", "cities.csv"):
            z.write(os.path.join(DATA, name), f"us-place-nicknames/{name}")
        z.write(os.path.join(DIST, "all_nicknames.csv"), "us-place-nicknames/all_nicknames.csv")
        z.write(os.path.join(DIST, "nicknames.json"), "us-place-nicknames/nicknames.json")
        for name in ("state_nicknames_combined.csv", "county_nicknames_combined.csv",
                     "city_nicknames_combined.csv"):
            z.write(os.path.join(DIST, name), f"us-place-nicknames/combined/{name}")
        for extra in ("README.md", "LICENSE", "datapackage.json"):
            p = os.path.join(ROOT, extra)
            if os.path.exists(p):
                z.write(p, f"us-place-nicknames/{extra}")

    print(f"all_nicknames.csv: {len(combined)} rows")
    print(f"nicknames.json:    {len(out)} states")
    print(f"zip:               {os.path.getsize(zpath):,} bytes")


if __name__ == "__main__":
    main()
