"""ToR docx builder scaffold — IPPF Visual Identity 2025.

Proven pattern from the AI-for-Research ToR v0.4-v0.7 generators (July 2026):
each ToR lives as a self-contained generator script next to its deliverable
(<project>/generators/gen_tor_vNN_docx.py), so the docx is always regenerable
from source and never dual-edited.

Usage by the tor-procurement skill (build mode):
1. Copy this file into the project's generators/ folder as gen_tor_v01_docx.py.
2. Keep the constants, helpers and TorBuilder unchanged.
3. Replace build_tor() with the real ToR body as linear builder calls,
   following the canonical section order in references/open-market-checklist.md.
4. Run it; the docx lands one level above the generators/ folder.

Self-contained on purpose: no ane_package import, so the generator runs on any
machine with python-docx. Brand constants mirror
ane_package.reporting.brand.IPPF_FORMAT_TEMPLATE — if the IPPF template
changes, update both.
"""

from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

# IPPF Visual Identity 2025 (mirrors ane_package.reporting.brand)
FONT = "Barlow Medium"
DREAM = RGBColor(0x00, 0x31, 0x3C)
FIRE_RED = RGBColor(0xEB, 0x33, 0x00)
DREAM_HEX = "00313C"

OUT_NAME = "2 ToR - [assignment] - v0.1 - DRAFT.docx"


def _shade(cell, hex_colour: str) -> None:
    """Fill a table cell (w:shd) with a solid colour."""
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), hex_colour)
    cell._tc.get_or_add_tcPr().append(shd)


def _cell_text(cell, text: str, bold: bool = False, white: bool = False,
               size: int = 10) -> None:
    cell.text = ""
    p = cell.paragraphs[0]
    run = p.add_run(text)
    run.font.name = FONT
    run.font.size = Pt(size)
    run.font.bold = bold
    if white:
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)


class TorBuilder:
    """Linear ToR document builder. One method call per block, top to bottom."""

    def __init__(self):
        self.doc = Document()
        for section in self.doc.sections:
            section.top_margin = Cm(2.0)
            section.bottom_margin = Cm(2.0)
            section.left_margin = Cm(2.2)
            section.right_margin = Cm(2.2)
        style = self.doc.styles["Normal"]
        style.font.name = FONT
        style.font.size = Pt(10.5)

    def title(self, text: str, subtitle: str = "") -> None:
        p = self.doc.add_paragraph()
        run = p.add_run(text)
        run.font.name = FONT
        run.font.size = Pt(20)
        run.font.bold = True
        run.font.color.rgb = DREAM
        if subtitle:
            p2 = self.doc.add_paragraph()
            r2 = p2.add_run(subtitle)
            r2.font.name = FONT
            r2.font.size = Pt(12)
            r2.font.color.rgb = FIRE_RED

    def h1(self, text: str) -> None:
        p = self.doc.add_paragraph()
        p.space_before = Pt(14)
        run = p.add_run(text)
        run.font.name = FONT
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = DREAM

    def h2(self, text: str) -> None:
        p = self.doc.add_paragraph()
        run = p.add_run(text)
        run.font.name = FONT
        run.font.size = Pt(12)
        run.font.bold = True
        run.font.color.rgb = FIRE_RED

    def para(self, text: str) -> None:
        p = self.doc.add_paragraph()
        run = p.add_run(text)
        run.font.name = FONT
        run.font.size = Pt(10.5)

    def lead(self, label: str, text: str) -> None:
        """Paragraph with a bold run-in lead: 'Label. Rest of sentence.'"""
        p = self.doc.add_paragraph()
        r1 = p.add_run(f"{label} ")
        r1.font.name = FONT
        r1.font.size = Pt(10.5)
        r1.font.bold = True
        r2 = p.add_run(text)
        r2.font.name = FONT
        r2.font.size = Pt(10.5)

    def bullets(self, items: list[str]) -> None:
        for item in items:
            p = self.doc.add_paragraph(style="List Bullet")
            run = p.add_run(item)
            run.font.name = FONT
            run.font.size = Pt(10.5)

    def numbered(self, items: list[str], bold_leads: bool = True) -> None:
        """Numbered list; with bold_leads, text before the first ':' is bolded."""
        for item in items:
            p = self.doc.add_paragraph(style="List Number")
            if bold_leads and ":" in item:
                head, _, tail = item.partition(":")
                r1 = p.add_run(f"{head}:")
                r1.font.name = FONT
                r1.font.size = Pt(10.5)
                r1.font.bold = True
                r2 = p.add_run(tail)
                r2.font.name = FONT
                r2.font.size = Pt(10.5)
            else:
                run = p.add_run(item)
                run.font.name = FONT
                run.font.size = Pt(10.5)

    def table(self, headers: list[str], rows: list[list[str]],
              widths: list[float] | None = None,
              header_fill: str = DREAM_HEX) -> None:
        t = self.doc.add_table(rows=1 + len(rows), cols=len(headers))
        t.style = "Table Grid"
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        for j, header in enumerate(headers):
            cell = t.rows[0].cells[j]
            _shade(cell, header_fill)
            _cell_text(cell, header, bold=True, white=True)
        for i, row in enumerate(rows, start=1):
            for j, value in enumerate(row):
                _cell_text(t.rows[i].cells[j], value)
        if widths:
            for j, width in enumerate(widths):
                for row in t.rows:
                    row.cells[j].width = Cm(width)

    def kv_table(self, rows: list[tuple[str, str]], key_width: float = 4.5,
                 val_width: float = 12.0) -> None:
        """Two-column key-value table (the 'At a glance' block)."""
        t = self.doc.add_table(rows=len(rows), cols=2)
        t.style = "Table Grid"
        for i, (key, value) in enumerate(rows):
            _shade(t.rows[i].cells[0], DREAM_HEX)
            _cell_text(t.rows[i].cells[0], key, bold=True, white=True)
            _cell_text(t.rows[i].cells[1], value)
            t.rows[i].cells[0].width = Cm(key_width)
            t.rows[i].cells[1].width = Cm(val_width)

    def save(self, out_path: Path | None = None) -> Path:
        out = out_path or Path(__file__).resolve().parent.parent / OUT_NAME
        self.doc.save(out)
        return out


def build_tor() -> Path:
    """REPLACE THIS BODY with the real ToR, section by section.

    Canonical order (see references/open-market-checklist.md):
    internal prep note, at-a-glance, how-to-apply, assignment in brief,
    sections 1-13, annexes.
    """
    b = TorBuilder()
    b.title("Terms of Reference — [assignment title]", "[commissioning unit] — DRAFT v0.1")
    b.h1("Internal preparation note — REMOVE BEFORE PUBLICATION")
    b.bullets(["[unresolved item 1]", "[unresolved item 2]"])
    b.h1("At a glance")
    b.kv_table([
        ("Assignment", "[title]"),
        ("Commissioned by", "[entity]"),
        ("Maximum budget", "EUR [X], inclusive of all fees, costs and any applicable VAT"),
        ("Level of effort", "Proposed by the consultant: days per deliverable"),
        ("Duration", "[start] to [end]"),
    ])
    b.h1("How to apply")
    b.para("[deadline, submit-to address, what to submit, Q&A dates, interview dates]")
    return b.save()


if __name__ == "__main__":
    print(build_tor())
