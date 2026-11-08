"""Tests for deck_shapes.py (SRHR map skill, phase d). A synthetic deck is built in the test as a zip
holding one slide XML; every name is invented, because this repository is public.

Run:  python test_deck_shapes.py
"""
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import deck_shapes as ds  # noqa: E402

NAMES = {"Xaland": "XA1"}


def sp(name, tip=None, text=None, fill="00313C"):
    link = f'<a:hlinkClick r:id="" tooltip="{tip}"/>' if tip is not None else ""
    body = f"<p:txBody><a:p><a:r><a:t>{text}</a:t></a:r></a:p></p:txBody>" if text is not None else ""
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="1" name="{name}">{link}</p:cNvPr><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:solidFill><a:srgbClr val="{fill}"/></a:solidFill></p:spPr>{body}</p:sp>')


TIP = "Xaland: 4 grant streams in 2026"
SLIDE = ("<p:sld><p:cSld><p:spTree>"
         + sp("Country: Xaland", TIP)
         + sp("Close-up: Xaland", TIP)
         + sp("Hover: Xaland", TIP)
         + '<p:grpSp><p:nvGrpSpPr><p:cNvPr id="9" name="Layer: not Class B"/></p:nvGrpSpPr>'
         + sp("Layer: not Class B | Xaland", TIP, fill="EEF0EE")
         + "</p:grpSp>"
         + sp("Label: Xaland", TIP, "4")
         + sp("Badge: Xaland", TIP, "2")
         + sp("Dot: Xaland | K1", TIP)
         + sp("Rate label: Xaland", TIP, "4.4")
         + sp("Matrix total: Xaland", None, "2")
         + sp("Matrix dot: Xaland | K1")
         + sp("Filter button: s1", None, "1 thing (3)")
         + sp("Legend text: full member", None, "Full member (5)")
         + sp("Legend text: close-up locator", None, "Dashed box")
         + sp("Title 1", None, "A title")
         + sp("Countryside", "decoy tip", "decoy")
         + "</p:spTree></p:cSld></p:sld>")


def build(tmp):
    p = Path(tmp) / "Map B - test.pptx"
    with zipfile.ZipFile(p, "w") as z:
        z.writestr("ppt/slides/slide1.xml", SLIDE)
    return p


def main():
    results = []

    def record(case, ok, detail=""):
        results.append(ok)
        print(f"{'ok  ' if ok else 'FAIL'} {case}" + (f": {detail}" if not ok else ""))

    with tempfile.TemporaryDirectory() as tmp:
        deck = build(tmp)
        rows = ds.inventory(deck, NAMES)
        kinds = {}
        for r in rows:
            kinds.setdefault(r["kind"], []).append(r)
        for k in ("tip", "label", "badge", "dot", "rate_label", "layer_member", "matrix_total", "matrix_dot",
                  "legend_count", "title", "fill"):
            record(f"kind_{k}_found", k in kinds, f"kinds {sorted(kinds)}")
        record("label_once", len(kinds.get("label", [])) == 1, kinds.get("label"))
        record("badge_once", len(kinds.get("badge", [])) == 1, kinds.get("badge"))
        tips = {r["shape_name"] for r in kinds.get("tip", [])}
        want_tips = {"Country: Xaland", "Close-up: Xaland", "Hover: Xaland", "Layer: not Class B | Xaland",
                     "Label: Xaland", "Badge: Xaland", "Dot: Xaland | K1", "Rate label: Xaland"}
        record("tip_carriers_all_found", tips == want_tips, f"got {sorted(tips)}")
        grouped = [r for r in rows if r["shape_name"] == "Layer: not Class B | Xaland"]
        record("grouped_copy_found_and_marked", bool(grouped) and all(r["in_group"] == "yes" for r in grouped),
               grouped)
        lm = kinds.get("layer_member", [{}])[0]
        record("layer_member_class", (lm.get("current"), lm.get("iso3_or_key")) == ("Class B", "XA1"), lm)
        record("decoy_not_listed", not any("Countryside" in r["shape_name"] for r in rows))
        record("legend_without_count_not_listed",
               not any(r["shape_name"] == "Legend text: close-up locator" for r in rows))
        lc = {r["shape_name"]: r["current"] for r in kinds.get("legend_count", [])}
        record("legend_counts_read", lc == {"Filter button: s1": "1 thing (3)",
                                            "Legend text: full member": "Full member (5)"}, lc)
        record("indicator_from_deck_letter",
               kinds["label"][0]["indicator"] == "ippf_grant_streams_count", kinds["label"][0])
        record("tip_current_text", kinds["tip"][0]["current"] == TIP, kinds["tip"][0])
        record("iso3_mapped", kinds["label"][0]["iso3_or_key"] == "XA1", kinds["label"][0])
        record("slide_and_deck_columns", (kinds["label"][0]["deck"], kinds["label"][0]["slide"]) == ("B", "slide1.xml"),
               kinds["label"][0])
        # cross-check against register_deck_check.deck_tips: nothing it reads may be missing here
        record("cross_check_clean", ds.cross_check(deck, rows) == [], ds.cross_check(deck, rows))
        record("cross_check_can_fail", ds.cross_check(deck, [r for r in rows if r["shape_name"] != "Country: Xaland"])
               == ["B slide1.xml Country: Xaland"])

    print(f"{sum(results)}/{len(results)} cases ok")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
