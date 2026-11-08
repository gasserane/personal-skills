"""Write the summary web map for donors and partners (SRHR map skill, phase e).

One self-contained page with a computed headline ("N of the M countries of the WHO European Region")
and three maps: membership (A), funding in three bands (F) and new HIV diagnoses (D). It holds no
stream name, member association name or ma_code, and no hover text from a deck ScreenTip: every
string comes from the templates in this file and the register values. Geometry, the embedded d3 and
the page frame are reused from publish_webmap.py. Exit 1 = input error, exit 2 = the target exists.
"""
import csv
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import computed  # noqa: E402
from publish_workbook import Stop  # noqa: E402

HEADLINE = "IPPF member associations and partners work in {n} of the {m} countries of the WHO European Region"
DEFINITION = ("\"Work in\" means an IPPF member association or partner organisation is based in the country. "
              "It does not mean service coverage.")


# --- the WHO list and the headline -----------------------------------------------------------------------

def load_who(path) -> set:
    """Upper-cased iso3 codes of the WHO European Region member states (config/who_europe.csv).
    A file saved by Excel (byte-order mark, blank rows, lower case) loads the same as a clean one."""
    try:
        with open(path, encoding="utf-8-sig", newline="") as f:
            rd = csv.DictReader(f)
            rd.fieldnames = [c.strip() for c in (rd.fieldnames or [])]
            if "iso3" not in rd.fieldnames:
                raise Stop(1, f"stop: {Path(path).name} has no iso3 column")
            out = {(r.get("iso3") or "").strip().upper() for r in rd}
    except OSError as e:
        raise Stop(1, f"stop: cannot read the WHO European Region list: {e}")
    out.discard("")
    if not out:
        raise Stop(1, f"stop: {Path(path).name} lists no country; the headline cannot be computed")
    return out


def headline(rows: list, who: set) -> dict:
    """{"n", "m", "outside"}: n = countries coloured on map A (active members), m = WHO member states,
    outside = counted countries missing from the WHO list (the build refuses when there is any)."""
    counted = computed.member_status_classes(rows)
    return {"n": len(counted), "m": len(who), "outside": sorted(i for i in counted if i not in who)}


def region_notes(master_rows: list, who: set, drawn: set, counted: set) -> list:
    """Build notes, empty when the master list, the WHO list and the geometry agree."""
    master = {r["iso3"] for r in master_rows}
    notes = []
    if master - who:
        notes.append("note: master countries not on the WHO European Region list: " + ", ".join(sorted(master - who)))
    if who - master:
        notes.append("note: WHO European Region countries not in the master list: " + ", ".join(sorted(who - master)))
    undrawn = sorted(counted - drawn)
    if undrawn:
        notes.append("note: counted in the headline but no map geometry, so not drawn: " + ", ".join(undrawn))
    return notes
