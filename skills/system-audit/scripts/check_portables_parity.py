"""Portables parity: every skill copy shipped outside Claude Code still matches its source.

A skill's `portables/` folder holds copies of its SKILL.md for surfaces that cannot
read the clone (claude.ai uploads, team releases). Nothing regenerates them, so they
drift silently when SKILL.md changes. Two rules:

  1. A zip under portables/ must carry a SKILL.md byte-identical to the source
     (CRLF folded to LF).
  2. A `portables/<name>-team/SKILL.md` may differ from the source only on lines that
     assume Ane's own setup (PERSONAL_RX). Any other source line missing from the
     team copy means a gate, rule or wording changed and the team copy was not updated.

Exit 0 = all in parity (or no portables); 1 = drift found, one line per finding.
Usage: python check_portables_parity.py [skills_root]   (default: this repo's skills/)
"""
import re
import sys
import zipfile
from pathlib import Path

# Lines in the source that the team copy is allowed to replace.
PERSONAL_RX = re.compile(r"\bAne\b|Ane's|CLAUDE\.md|^## Maintenance note|Tier register|she needs|portables/|/system-audit")


def norm(text: str) -> list[str]:
    return text.replace("\r\n", "\n").replace("\r", "\n").split("\n")


def check(skills_root: Path) -> list[str]:
    findings = []
    for src in sorted(skills_root.glob("*/SKILL.md")):
        port = src.parent / "portables"
        if not port.is_dir():
            continue
        source = norm(src.read_text(encoding="utf-8"))
        name = src.parent.name
        for z in sorted(port.glob("*.zip")):
            with zipfile.ZipFile(z) as zf:
                inner = [n for n in zf.namelist() if n.endswith("SKILL.md")]
                if not inner:
                    findings.append(f"{name}: {z.name} holds no SKILL.md")
                    continue
                if norm(zf.read(inner[0]).decode("utf-8")) != source:
                    findings.append(f"{name}: {z.name} is stale against SKILL.md (regenerate the zip)")
        for team in sorted(port.glob("*-team/SKILL.md")):
            team_lines = set(norm(team.read_text(encoding="utf-8")))
            for n, line in enumerate(source, 1):
                if line.strip() and line not in team_lines and not PERSONAL_RX.search(line):
                    findings.append(f"{name}: SKILL.md:{n} missing from {team.parent.name}/SKILL.md "
                                    f"(update the team copy, bump its version, re-ship): {line[:70]}")
    return findings


if __name__ == "__main__":
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2]
    found = check(root)
    for f in found:
        print("DRIFT", f)
    print(f"portables parity: {'FAIL' if found else 'PASS'} ({len(found)} finding(s)) under {root}")
    sys.exit(1 if found else 0)
