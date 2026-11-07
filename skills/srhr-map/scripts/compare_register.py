"""What counts as a change between the last register edition and the proposed rows (refresh step 4).

compare() decides, row by row, what a person must look at; group_changes() folds those changes into
review lines short enough for one sitting (at most MAX_MUST lines on the "Must check" sheet).

Kinds:
  new           the key (country, indicator, year) is not in the last edition
  revised       the key is there with a different value (value only: display text is hand-written
                evidence a refresh cannot reproduce; funding streams compare the set of stream keys)
  missing       a country held a covered indicator in the last edition but has no row for the
                covered year in the new files
  focus_change  a business-plan HIV focus rating differs from the country's previous plan year
"""
import hashlib
from dataclasses import dataclass, field

BIG_CHANGE = 0.5
MAX_MUST = 30
FOCUS = "ippf_bp_hiv_focus"
STREAM_SETS = {"ippf_funding_streams"}
PARTNER = "ippf_funding_streams_partner"
SECOND_READER = "needs a second reader before it can be ticked"


@dataclass
class Change:
    change_id: str
    kind: str
    group: str
    iso3: str
    indicator_id: str
    reference_year: str
    old: dict = None
    new: dict = None
    guidance: str = ""
    link: str = ""


@dataclass
class Line:
    group: str
    change_ids: list = field(default_factory=list)
    title: str = ""
    guidance: str = ""
    link: str = ""
    sheet: str = "Must check"
    size: float = 0.0


def _key(r):
    k = (r["iso3"], r["indicator_id"], str(r["reference_year"]))
    return k + ((r["value"],) if r["indicator_id"] == PARTNER else ())


def _same(a, b):
    if a["indicator_id"] in STREAM_SETS:
        keys = lambda r: {x.strip() for x in r.get("value_display", "").split(",")} - {"", "none"}
        return keys(a) == keys(b)
    return str(a.get("value", "")).strip() == str(b.get("value", "")).strip()


def _id(kind, iso3, ind, year, value_key=""):
    return hashlib.sha1(f"{kind}|{iso3}|{ind}|{year}|{value_key}".encode("utf-8")).hexdigest()[:10]


def _float(v):
    try:
        return float(str(v).replace(",", ""))
    except (TypeError, ValueError):
        return None


def size_of(c: Change) -> float:
    """How far a value moved, as a share of the earlier value; inf when it cannot be measured."""
    if c.kind in ("missing", "focus_change"):
        return float("inf")
    if not c.old or not c.new:
        return 0.0
    a, b = _float(c.old.get("value")), _float(c.new.get("value"))
    if a is None or b is None:
        return float("inf") if c.old.get("value") != c.new.get("value") else 0.0
    if a == 0:
        return float("inf") if b != 0 else 0.0
    return abs(b - a) / abs(a)


def compare(baseline, proposed, covered):
    """covered = {indicator_id: {"year": str, "link": str}} for the indicators the new files cover."""
    base = {_key(b): b for b in baseline}
    earlier = {}  # (iso3, indicator) -> latest baseline row
    for b in baseline:
        k = (b["iso3"], b["indicator_id"])
        if k not in earlier or int(b["reference_year"]) > int(earlier[k]["reference_year"]):
            earlier[k] = b
    changes, seen = [], set()
    for n in proposed:
        k = _key(n)
        seen.add(k)
        iso3, ind, yr = k[0], k[1], k[2]
        link = n.get("_link") or covered.get(ind, {}).get("link", "")
        vkey = n["value"] if ind == PARTNER else ""
        if k in base:
            if not _same(base[k], n):
                changes.append(Change(_id("revised", iso3, ind, yr, vkey), "revised", f"{ind} {yr}", iso3, ind, yr,
                                      base[k], n, "The value at the link matches the new value.", link))
            continue
        prev = earlier.get((iso3, ind))
        if prev is not None and int(prev["reference_year"]) >= int(yr):
            prev = None  # an older year added late: nothing earlier to compare with
        if ind == FOCUS and prev is not None and prev["value"].strip() != n["value"].strip():
            guidance = "The business plan page at the link supports the new rating."
            if not (n.get("_second_reader") or "").strip():
                guidance += f" This rating {SECOND_READER}."
            changes.append(Change(_id("focus_change", iso3, ind, yr), "focus_change", f"{ind} {yr}", iso3, ind, yr,
                                  prev, n, guidance, link))
            continue
        changes.append(Change(_id("new", iso3, ind, yr, vkey), "new", f"{ind} {yr}", iso3, ind, yr, prev, n,
                              "The value at the link matches the new value.", link))
    held = {}
    for b in baseline:
        held.setdefault(b["indicator_id"], set()).add(b["iso3"])
    for ind, cov in covered.items():
        have = {k[0] for k in seen if k[1] == ind and k[2] == str(cov["year"])}
        for iso3 in sorted(held.get(ind, set()) - have):
            changes.append(Change(_id("missing", iso3, ind, cov["year"]), "missing", f"{ind} {cov['year']}", iso3,
                                  ind, str(cov["year"]), earlier.get((iso3, ind)), None,
                                  "The file at the link has no value for this country. Correct = it really "
                                  "reported nothing this year.", cov.get("link", "")))
    return changes


def _title(c: Change) -> str:
    old = (c.old or {}).get("value_display") or (c.old or {}).get("value") or "-"
    new = (c.new or {}).get("value_display") or (c.new or {}).get("value") or "-"
    what = f"{c.indicator_id} {c.reference_year}"
    return {"revised": f"{c.iso3}: {what} changed from {old} to {new}",
            "missing": f"{c.iso3}: no {what} value in the new files (last edition: {old})",
            "focus_change": f"{c.iso3}: business-plan HIV focus {c.reference_year} is {new} (previous plan: {old})",
            "new": f"{c.iso3}: {what} = {new} (earlier: {old})"}[c.kind]


def group_changes(changes):
    """Fold changes into review lines; the first MAX_MUST by priority go on 'Must check'."""
    lines, groups = [], {}
    for c in changes:
        snapshot = (c.new or {}).get("ticked_by") == "snapshot ba_tick"
        own = c.kind != "new" or size_of(c) > BIG_CHANGE and c.old is not None
        if own:
            lines.append(Line(c.group, [c.change_id], _title(c), c.guidance, c.link,
                              "Optional" if snapshot else "Must check", size_of(c)))
            continue
        g = groups.get((c.group, snapshot))
        if g is None:
            g = groups[(c.group, snapshot)] = Line(c.group, [], "", c.guidance, c.link,
                                                   "Optional" if snapshot else "Must check", 0.0)
            lines.append(g)
        g.change_ids.append(c.change_id)
        g.size = max(g.size, size_of(c))
    for g in groups.values():
        g.title = f"{len(g.change_ids)} new values: {g.group} (each within {int(BIG_CHANGE * 100)}% of its earlier value)"
    order = {"focus_change": 0, "missing": 1, "revised": 2, "new": 3}
    kind_of = {c.change_id: c.kind for c in changes}
    lines.sort(key=lambda l: (l.sheet != "Must check", order[kind_of[l.change_ids[0]]], -l.size))
    must = 0
    for l in lines:
        if l.sheet == "Must check":
            must += 1
            if must > MAX_MUST:
                l.sheet = "Optional"
    lines.sort(key=lambda l: (l.sheet != "Must check", -l.size if l.sheet == "Optional" else 0))
    return lines
