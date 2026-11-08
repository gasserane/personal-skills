"""Values computed from the map register at publish time (SRHR map skill, phase d; spec section 8.4).

No number is typed into a deck, a title or a legend: legend counts are register rows per class,
trends come from the 2015 and 2024 rates, and title strings come from templates that hold no digit.
The deck planner (publish_plan.py) and the later outputs call these same functions, so every output
shows the same number.

Classes per map:
  A  the membership value_display (one class per country)
  B  b_class(grant stream count): "0 grant streams" .. "3 grant streams", then one top class
  C  every crosswalk label the country holds (several per country); partner rows count as "half";
     the membership legend counts member_status
Withdrawn members never count on maps A to C.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import register_deck_check as rdc  # noqa: E402

TOP_CLASS = 4
COUNT_TAIL = re.compile(r"\s*\((\d+)(?: \+ (\d+) half)?\)$")
MARK = "●"


def b_class(n: int) -> str:
    if n >= TOP_CLASS:
        return f"{TOP_CLASS}+ grant streams"
    return f"{n} grant stream{'' if n == 1 else 's'}"


def _active(rows, indicator):
    return [r for r in rows if r["indicator_id"] == indicator and r["member_status"] != "withdrawn"]


def stream_keys(value_display: str) -> list:
    return [] if value_display in ("", "none") else [k.strip() for k in value_display.split(",")]


def country_classes(m: str, rows: list, crosswalk: list) -> dict:
    """{iso3: set of class labels} for map A, B or C (active members only)."""
    out = {}
    if m == "A":
        for r in _active(rows, "ippf_membership"):
            out.setdefault(r["iso3"], set()).add(r["value_display"])
    elif m == "B":
        for r in _active(rows, "ippf_grant_streams_count"):
            out.setdefault(r["iso3"], set()).add(b_class(int(r["value"])))
    elif m == "C":
        label = dict(crosswalk)
        for r in _active(rows, "ippf_funding_streams"):
            out.setdefault(r["iso3"], set()).update(label.get(k, k) for k in stream_keys(r["value_display"]))
    return out


def partner_keys(rows: list) -> dict:
    """{iso3: set of stream keys held as partner (half)} for active members."""
    out = {}
    for r in _active(rows, "ippf_funding_streams_partner"):
        out.setdefault(r["iso3"], set()).add(r["value"])
    return out


def class_counts(m: str, rows: list, crosswalk: list) -> dict:
    """{class: (n, half)}. A and B key by class label; C keys streams by crosswalk key and adds one
    entry per member_status for the membership legend."""
    counts = {}
    if m in ("A", "B"):
        for classes in country_classes(m, rows, crosswalk).values():
            for c in classes:
                n, h = counts.get(c, (0, 0))
                counts[c] = (n + 1, h)
        return counts
    if m != "C":
        return counts
    for r in _active(rows, "ippf_funding_streams"):
        for k in stream_keys(r["value_display"]):
            n, h = counts.get(k, (0, 0))
            counts[k] = (n + 1, h)
        n, h = counts.get(r["member_status"], (0, 0))
        counts[r["member_status"]] = (n + 1, h)
    for keys in partner_keys(rows).values():
        for k in keys:
            n, h = counts.get(k, (0, 0))
            counts[k] = (n, h + 1)
    return counts


def legend_label(text: str) -> str:
    """The class label of a legend or filter-button text: the count and the dot mark removed."""
    return COUNT_TAIL.sub("", text).lstrip(MARK).strip()


def legend_text(old: str, n: int, half: int = 0) -> str:
    """The legend text with only its trailing count replaced."""
    m = COUNT_TAIL.search(old)
    if not m:
        raise ValueError(f"legend text {old!r} holds no count")
    tail = f"({n} + {half} half)" if half else f"({n})"
    return old[:m.start()] + old[m.start():m.end()].replace(m.group(0).strip(), tail)


def trend(rows: list, iso3: str) -> str:
    return rdc._trend(rdc._index(rows), iso3)


def render(template: str, **values) -> str:
    """A title or subtitle from a template; a typed digit in the template is refused (spec 8.4)."""
    if re.search(r"\d", template):
        raise ValueError(f"template {template!r} holds a typed number; compute it from the register")
    return template.format(**values)
