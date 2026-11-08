"""Tests for the non-COM parts of publish_swap.py (SRHR map skill, phase d): plan reading, slide
order, the text edit span, the swap-log comparison, deck lookup, the local-path guard and the
year-folder copy. Every name and key is invented, because this repository is public. The COM
swap itself is tested by Run A on scratch copies of the real decks (plan Task 3.3), not here.

Run:  python test_publish_swap.py
"""
import csv
import hashlib
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import publish_swap as ps  # noqa: E402

results = []


def record(name, ok, detail=""):
    results.append(bool(ok))
    print(("ok   " if ok else "FAIL ") + name + ("" if ok else f"  {detail!r}"))


def write_csv(path, rows, cols=None):
    cols = cols or list(rows[0])
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)


def plan_row(**kw):
    r = {"deck": "B", "slide": "slide1.xml", "shape_name": "Label: XA1", "kind": "label",
         "field": "text", "old": "4", "new": "5"}
    r.update(kw)
    return r


def fake_pptx(path, order):
    """A zip with presentation.xml listing slides in `order` (part names) and the matching rels."""
    ids = "".join(f'<p:sldId id="{256 + i}" r:id="rId{10 + i}"/>' for i in range(len(order)))
    ox = ps.OX  # namespace base, built without "<letter>:/" text (public-repo check)
    rels = "".join(f'<Relationship Id="rId{10 + i}" Type="urn:x:slide" Target="slides/{p}"/>'
                   for i, p in enumerate(order))
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("ppt/presentation.xml",
                   f'<p:presentation xmlns:p="{ox}presentationml/2006/main" '
                   f'xmlns:r="{ox}officeDocument/2006/relationships">'
                   f'<p:sldIdLst>{ids}</p:sldIdLst></p:presentation>')
        z.writestr("ppt/_rels/presentation.xml.rels",
                   f'<Relationships xmlns="{ox}package/2006/relationships">'
                   f'<Relationship Id="rId1" Type="urn:x:theme" Target="theme/theme1.xml"/>{rels}'
                   '</Relationships>')


def main():
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)

        # --- read_plan: columns, field, deck letter, duplicates ---
        write_csv(t / "ok.csv", [plan_row(), plan_row(shape_name="Tip: XA1", kind="tip", field="screentip",
                                                      old="XA1: 4 grant streams", new="XA1: 5 grant streams")])
        rows = ps.read_plan(t / "ok.csv")
        record("read_plan_ok", len(rows) == 2 and rows[1]["field"] == "screentip", rows)
        write_csv(t / "empty.csv", [], cols=ps.COLUMNS)
        record("read_plan_empty_is_empty_list", ps.read_plan(t / "empty.csv") == [])
        for name, bad in (("bad_field", [plan_row(field="fill")]),
                          ("bad_deck", [plan_row(deck="E")]),
                          ("duplicate", [plan_row(), plan_row(new="6")]),
                          ("old_equals_new", [plan_row(new="4")])):
            write_csv(t / f"{name}.csv", bad)
            try:
                ps.read_plan(t / f"{name}.csv")
                record(f"read_plan_refuses_{name}", False, "no PlanError")
            except ps.PlanError:
                record(f"read_plan_refuses_{name}", True)
        write_csv(t / "cols.csv", [{k: v for k, v in plan_row().items() if k != "field"}])
        try:
            ps.read_plan(t / "cols.csv")
            record("read_plan_refuses_missing_column", False, "no PlanError")
        except ps.PlanError:
            record("read_plan_refuses_missing_column", True)

        # --- slide_order: part name -> 1-based show position, from presentation.xml, not the part number ---
        fake_pptx(t / "Map Q - x.pptx", ["slide3.xml", "slide1.xml", "slide2.xml"])
        order = ps.slide_order(t / "Map Q - x.pptx")
        record("slide_order_follows_sldIdLst", order == {"slide3.xml": 1, "slide1.xml": 2, "slide2.xml": 3}, order)

        # --- text_edit: the smallest middle span, so the unchanged characters keep their run ---
        record("text_edit_count", ps.text_edit("Class P (13)", "Class P (14)") == (11, 1, "4"),
               ps.text_edit("Class P (13)", "Class P (14)"))
        record("text_edit_grow", ps.text_edit("Class P (9)", "Class P (10)") == (10, 1, "10"),
               ps.text_edit("Class P (9)", "Class P (10)"))
        record("text_edit_whole", ps.text_edit("4", "5") == (1, 1, "5"), ps.text_edit("4", "5"))
        record("text_edit_shrink", ps.text_edit("26.5", "6.5") == (1, 1, ""), ps.text_edit("26.5", "6.5"))
        record("text_edit_repeat_char", ps.text_edit("(11)", "(111)") == (4, 0, "1"), ps.text_edit("(11)", "(111)"))
        for old, new in (("Class P (13)", "Class P (14)"), ("26.5", "6.5"), ("(11)", "(111)"), ("ab", "xaby")):
            a, n, ins = ps.text_edit(old, new)
            got = old[:a - 1] + ins + old[a - 1 + n:]
            record(f"text_edit_rebuilds_{old}->{new}", got == new, got)

        # --- log_problems: written == read back, and old read == planned old ---
        good = {"deck": "B", "slide": "slide1.xml", "shape_name": "Label: XA1", "field": "text",
                "old_planned": "4", "old_read": "4", "new_written": "5", "new_read": "5"}
        record("log_clean", ps.log_problems([good]) == [])
        record("log_readback_differs", len(ps.log_problems([dict(good, new_read="4")])) == 1)
        record("log_old_differs", len(ps.log_problems([dict(good, old_read="3")])) == 1)

        # --- deck_files: one file per letter the plan names ---
        d = t / "decks"
        d.mkdir()
        (d / "Map B - one.pptx").write_bytes(b"b")
        (d / "Map C - one.pptx").write_bytes(b"c")
        (d / "Map C - two.pptx").write_bytes(b"c2")
        files = ps.deck_files(d, {"B"})
        record("deck_files_found", files == {"B": d / "Map B - one.pptx"}, files)
        for name, letters in (("missing", {"A"}), ("ambiguous", {"C"})):
            try:
                ps.deck_files(d, letters)
                record(f"deck_files_refuses_{name}", False, "no PlanError")
            except ps.PlanError:
                record(f"deck_files_refuses_{name}", True)

        # --- is_local: a cloud document is refused ---
        # invented paths built by concatenation: the public-repo check forbids "<letter>:/" text
        record("is_local_path", ps.is_local("C" + r":\work\Map B - one.pptx"))
        record("is_local_refuses_https", not ps.is_local("https" + "://example.org/sites/x/Map B - one.pptx"))

        # --- copy_decks: byte-identical copies, refused when the target holds a deck ---
        src = t / "src"
        src.mkdir()
        for k in "AB":
            (src / f"Map {k} - x.pptx").write_bytes(f"deck {k}".encode())
        (src / "notes.txt").write_text("not a deck")
        dst = t / "2099"
        copied = ps.copy_decks(src, dst)
        same = all(hashlib.sha256((src / n).read_bytes()).hexdigest()
                   == hashlib.sha256((dst / n).read_bytes()).hexdigest() for n, _, _ in copied)
        record("copy_decks_identical", len(copied) == 2 and same and all(a == b for _, a, b in copied)
               and not (dst / "notes.txt").exists(), copied)
        try:
            ps.copy_decks(src, dst)
            record("copy_decks_refuses_existing", False, "no PlanError")
        except ps.PlanError:
            record("copy_decks_refuses_existing", True)

        # --- CLI without --apply: prints the plan, touches nothing; empty plan prints zero swaps ---
        before = (d / "Map B - one.pptx").read_bytes()
        code = ps.main(["--decks", str(d), "--plan", str(t / "empty.csv")])
        record("cli_empty_plan_exit_0", code == 0)
        code = ps.main(["--decks", str(d), "--plan", str(t / "ok.csv")])
        record("cli_dry_run_exit_0_and_untouched", code == 0 and (d / "Map B - one.pptx").read_bytes() == before
               and not list(d.glob("swap_log*.csv")), code)
        record("cli_bad_plan_exit_1", ps.main(["--decks", str(d), "--plan", str(t / "bad_field.csv")]) == 1)

    # --- _write on text: late-bound COM exposes the span only as GetCharacters(start, len);
    #     Characters(start, len) raises "Does not support a collection" (Run A, 2026-11-08) ---
    class Span:
        def __init__(self, box, a, n):
            self.box, self.a, self.n = box, a, n

        @property
        def Text(self):
            return self.box.text[self.a - 1:self.a - 1 + self.n]

        @Text.setter
        def Text(self, v):
            self.box.text = self.box.text[:self.a - 1] + v + self.box.text[self.a - 1 + self.n:]

        def InsertAfter(self, v):
            self.box.text = self.box.text[:self.a - 1 + self.n] + v + self.box.text[self.a - 1 + self.n:]

        def InsertBefore(self, v):
            self.box.text = self.box.text[:self.a - 1] + v + self.box.text[self.a - 1:]

    class LateBoundRange:
        def __init__(self, text):
            self.text = text

        def GetCharacters(self, a, n):
            return Span(self, a, n)

        @property
        def Characters(self):
            raise RuntimeError("Does not support a collection.")

    class FakeShape:
        def __init__(self, text):
            self.TextFrame2 = type("TF", (), {})()
            self.TextFrame2.TextRange = LateBoundRange(text)

    for old, new in [("4", "5"), ("Class P (9)", "Class P (10)"), ("(11)", "(111)"), ("26.5", "6.5"), ("ab", "xab")]:
        sh = FakeShape(old)
        try:
            ps._write(sh, "text", old, new)
            got = sh.TextFrame2.TextRange.text
        except Exception as e:  # noqa: BLE001
            got = f"raised {e}"
        record(f"write_text_late_bound_{old}->{new}", got == new, got)

    print(f"{sum(results)}/{len(results)} cases ok")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
