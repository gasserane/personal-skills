"""Register-to-deck agreement check (SRHR map skill; spec section 8.5).

Every country ScreenTip on every view of decks A to D must equal what the map register says.
Map D trends are recomputed from the register's 2015 and 2024 rates, never read from a stored
row, so the check also proves the "computed at publish" rule. A withdrawn member must be absent
from the membership and funding maps and must carry the withdrawal sentence on the HIV map.

The decks are read as zip files and never opened in PowerPoint or saved. Stream labels come from a
crosswalk CSV (columns key,label, in legend order) kept with the register, because stream names
do not belong in this public repository.

Run:  python register_deck_check.py --register <csv> --decks <folder> --crosswalk <csv> --master <csv>
Exit 0 only when every tip on every view agrees with the register.
"""
import argparse
import csv
import html
import re
import sys
import zipfile
from pathlib import Path

TIP = re.compile(r'<p:cNvPr[^>]*name="Country: ([^"]+)"[^>]*>\s*<a:hlink\w+[^>]*tooltip="([^"]*)"')
B_TIP = re.compile(r": (\d+) grant streams? in (\d{4})$")
C_TIP = re.compile(r"^[^:]+: (.+?)\. (?:Grants \w+ to \w+ \d{4}: (.+?)|No grant stream \w+ to \w+ \d{4})\.(?: (.*))?$")
C_PARTNER = re.compile(r"Partner country on a joint (.+?) grant led by (.+?)\.")
D_RATE = re.compile(r"2024 rate:? (.+?)(?: per 100,000)?; trend:? (.+?)(?: since 2015)?[;.]")
D_FOCUS = re.compile(r"plan focus: (.+?);")
D_SERVICES = re.compile(r"HIV services 2025: (.+)$")
MAP_INDICATOR = {"A": "ippf_membership", "B": "ippf_grant_streams_count", "C": "ippf_funding_streams"}
D_INDICATORS = ("ecdc_hiv_diagnosis_rate", "ippf_bp_hiv_focus", "ippf_hiv_services")


def deck_tips(pptx: Path) -> list:
    """[(slide name, {country: tip})] for every slide that carries country ScreenTips."""
    out = []
    with zipfile.ZipFile(pptx) as z:
        names = sorted((n for n in z.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)),
                       key=lambda n: int(re.findall(r"\d+", n)[0]))
        for n in names:
            tips = {c: html.unescape(t) for c, t in TIP.findall(z.read(n).decode("utf-8"))}
            if tips:
                out.append((n.rsplit("/", 1)[-1], tips))
    return out


def _index(rows):
    by = {}
    for r in rows:
        by.setdefault(r["iso3"], {}).setdefault(r["indicator_id"], []).append(r)
    return by


def _one(by, iso3, indicator, year=None):
    rows = [r for r in by.get(iso3, {}).get(indicator, []) if year is None or r["reference_year"] == str(year)]
    return rows[0] if rows else None


def _trend(by, iso3):
    r15, r24 = _one(by, iso3, D_INDICATORS[0], 2015), _one(by, iso3, D_INDICATORS[0], 2024)
    if not (r15 and r24):
        return "no data"
    return f"{round((float(r24['value']) / float(r15['value']) - 1) * 100):+d}%"


def compare(m: str, register_rows: list, tips: dict, names: dict, crosswalk: list) -> list:
    """Problems for one map view: tips {country name: tip text}; names {country name: iso3}."""
    by = _index(register_rows)
    iso_name = {v: k for k, v in names.items()}
    label = dict(crosswalk)
    order = {k: i for i, (k, _) in enumerate(crosswalk)}
    problems = []

    def p(country, msg):
        problems.append(f"map {m} {country}: {msg}")

    if m in MAP_INDICATOR:
        in_reg = {iso: rows for iso, rows in by.items() if MAP_INDICATOR[m] in rows}
    else:
        in_reg = {iso: rows for iso, rows in by.items() if any(i in rows for i in D_INDICATORS)}
    for iso in sorted(in_reg):
        name = iso_name.get(iso, iso)
        status = in_reg[iso][next(i for i in in_reg[iso])][0]["member_status"]
        if m != "D" and status == "withdrawn":
            if name in tips:
                p(name, "withdrawn in the register but shown on the deck")
            continue
        if name not in tips:
            p(name, "in the register, missing on the deck")
    for name in sorted(tips):
        if names.get(name) not in in_reg:
            p(name, "on the deck, not in the register")

    for name, tip in sorted(tips.items()):
        iso = names.get(name)
        if iso not in in_reg:
            continue
        if m == "A":
            row = _one(by, iso, "ippf_membership")
            got = tip.split(": ", 1)[1] if ": " in tip else tip
            if got != row["value_display"]:
                p(name, f"membership deck {got!r}, register {row['value_display']!r}")
        elif m == "B":
            row = _one(by, iso, "ippf_grant_streams_count")
            mm = B_TIP.search(tip)
            if not mm:
                p(name, f"cannot read tip {tip!r}")
            elif (mm.group(1), mm.group(2)) != (row["value"], row["reference_year"]):
                p(name, f"grant streams deck {mm.group(1)} in {mm.group(2)}, "
                        f"register {row['value']} in {row['reference_year']}")
        elif m == "C":
            row = _one(by, iso, "ippf_funding_streams")
            mm = C_TIP.match(tip)
            if not mm:
                p(name, f"cannot read tip {tip!r}")
                continue
            if mm.group(1) != row["member_status"]:
                p(name, f"member status deck {mm.group(1)!r}, register {row['member_status']!r}")
            keys = [] if row["value_display"] == "none" else [k.strip() for k in row["value_display"].split(",")]
            unknown = [k for k in keys if k not in label]
            if unknown:
                p(name, f"streams {unknown} have no label in the crosswalk")
                continue
            want = ", ".join(label[k] for k in sorted(keys, key=order.get))
            if (mm.group(2) or "") != want:
                p(name, f"streams deck {mm.group(2) or 'none'!r}, register {want or 'none'!r}")
            deck_half = set(C_PARTNER.findall(mm.group(3) or ""))
            reg_half = set()
            for h in by.get(iso, {}).get("ippf_funding_streams_partner", []):
                lead = re.match(r".+? with (.+?) \(row", h["value_display"])
                reg_half.add((label.get(h["value"], h["value"]), lead.group(1) if lead else ""))
            if deck_half != reg_half:
                p(name, f"partner dots deck {sorted(deck_half)}, register {sorted(reg_half)}")
        else:
            rate = _one(by, iso, D_INDICATORS[0], 2024)
            want_rate, want_trend = (rate["value_display"] if rate else "no data"), _trend(by, iso)
            mm = D_RATE.search(tip)
            if not mm:
                p(name, f"cannot read tip {tip!r}")
                continue
            if mm.group(1) != want_rate:
                p(name, f"2024 rate deck {mm.group(1)!r}, register {want_rate!r}")
            if mm.group(2) != want_trend:
                p(name, f"trend deck {mm.group(2)!r}, recomputed from register {want_trend!r}")
            status = in_reg[iso][next(i for i in in_reg[iso])][0]["member_status"]
            if status == "withdrawn":
                if "withdrew" not in tip:
                    p(name, "withdrawn in the register but the tip lacks the withdrawal sentence")
                continue
            focus, services = _one(by, iso, "ippf_bp_hiv_focus"), _one(by, iso, "ippf_hiv_services")
            fm, sm = D_FOCUS.search(tip), D_SERVICES.search(tip)
            want_f = focus["value_display"] if focus else None
            if (fm.group(1) if fm else None) != want_f:
                p(name, f"plan focus deck {fm and fm.group(1)!r}, register {want_f!r}")
            want_s = services["value_display"].split(" (")[0] if services else None
            if (sm.group(1) if sm else None) != want_s:
                p(name, f"HIV services deck {sm and sm.group(1)!r}, register {want_s!r}")
    return problems


def _csv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--register", type=Path, required=True)
    ap.add_argument("--decks", type=Path, required=True)
    ap.add_argument("--crosswalk", type=Path, required=True)
    ap.add_argument("--master", type=Path, required=True)
    args = ap.parse_args(argv)
    rows = _csv(args.register)
    names = {r["country"]: r["iso3"] for r in _csv(args.master)}
    crosswalk = [(r["key"], r["label"]) for r in _csv(args.crosswalk)]
    total = 0
    for m in "ABCD":
        decks = sorted(args.decks.glob(f"Map {m} *.pptx"))
        if len(decks) != 1:
            print(f"FAIL map {m}: expected one deck 'Map {m} *.pptx', found {len(decks)}")
            total += 1
            continue
        views = deck_tips(decks[0])
        if not views:
            print(f"FAIL map {m}: no country ScreenTips in {decks[0].name}")
            total += 1
            continue
        for slide, tips in views:
            problems = compare(m, rows, tips, names, crosswalk)
            total += len(problems)
            print(f"{'ok  ' if not problems else 'FAIL'} map {m} {slide}: {len(tips)} tips, {len(problems)} problem(s)")
            for p in problems[:10]:
                print(f"     {p}")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
