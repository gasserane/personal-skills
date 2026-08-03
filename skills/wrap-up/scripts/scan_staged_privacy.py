#!/usr/bin/env python3
"""Content-aware privacy scan over staged files, for wrap-up Gate 3.

The filename scan in Gate 3 reads names only. On 2026-07-03 six documents holding
two people's national-register numbers, identity-card numbers and an IBAN, plus
three identity-card scans, passed that scan in a repo pointed at a PUBLIC GitHub
remote. Every filename looked ordinary. Only manual judgement caught them.

This scanner reads staged *content* instead. It is built around one constraint:
a gate that cries wolf gets clicked through, so it must be precise rather than
eager. Two of the three number formats carry checksums and the third carries an
embedded birth date, so precision is available without guesswork:

  IBAN    mod-97 over the rearranged string must equal 1
  RRN     mod-97 over the first 9 digits must equal the last 2
  CNP     weighted control digit (key 279146358279) plus a valid birth date

A bare "13-digit run" regex would match every epoch-millisecond timestamp
written between 2001 and 2286, which is most machine-generated data Ane handles.
That version of this check would be noise.

Findings are always masked. Printing a full national-register number into the
session transcript would flow it into the handoff file and reproduce the exact
harm this gate exists to prevent.

Exit codes:
  0  clean
  1  advisory findings (report them, let the commit proceed)
  2  HOLD (a sensitive match AND a public-forge remote co-occur)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, asdict

# Forges that serve repositories to the open internet. The host being public is
# what raises a finding from advisory to HOLD -- see resolve_remote_exposure().
PUBLIC_FORGE_HOSTS = {
    "github.com", "gitlab.com", "bitbucket.org", "codeberg.org",
    "sourceforge.net", "gitee.com", "git.sr.ht",
}

# Length by country. IBAN length is fixed per country, so this is a strong
# structural filter before the checksum ever runs.
IBAN_LENGTHS = {
    "AD": 24, "AE": 23, "AT": 20, "BE": 16, "BG": 22, "CH": 21, "CY": 28,
    "CZ": 24, "DE": 22, "DK": 18, "EE": 20, "ES": 24, "FI": 18, "FR": 27,
    "GB": 22, "GR": 27, "HR": 21, "HU": 28, "IE": 22, "IS": 26, "IT": 27,
    "LI": 21, "LT": 20, "LU": 20, "LV": 21, "MC": 27, "MD": 24, "MT": 31,
    "NL": 18, "NO": 15, "PL": 28, "PT": 25, "RO": 24, "RS": 22, "SE": 24,
    "SI": 19, "SK": 24, "SM": 27, "TR": 26, "UA": 29,
}

CNP_KEY = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]

IBAN_RE = re.compile(r"\b([A-Z]{2}\d{2}[ ]?(?:[A-Z0-9]{4}[ ]?){2,7}[A-Z0-9]{1,4})\b")
CNP_RE = re.compile(r"(?<!\d)(\d{13})(?!\d)")
# Rijksregister is written both bare and punctuated: 85.07.30-033.28
RRN_RE = re.compile(r"(?<!\d)(\d{2}[.\-/ ]?\d{2}[.\-/ ]?\d{2}[.\-/ ]?\d{3}[.\-/ ]?\d{2})(?!\d)")

IDENTITY_IMAGE_RE = re.compile(
    r"(identit|\bid[-_ ]?card|carte[-_ ]?d|permis|passport|paspoort|pasaport|"
    r"rijksregister|\beid\b|buletin|kaart|scan)",
    re.IGNORECASE,
)
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".pdf", ".tif", ".tiff", ".heic", ".webp", ".bmp"}

# This scanner and its test carry the patterns as literals and test vectors, so
# they would flag themselves forever. Nothing else is excluded by type: the
# 2026-07-03 incident was six ordinary .md and .docx documents, so excluding
# documentation -- the obvious-looking optimisation -- would rebuild the very
# blind spot this scanner exists to close.
SELF_EXCLUDE_RE = re.compile(r"(^|/)(scan_staged_privacy|test_scan_staged_privacy)\.py$")

MAX_BYTES = 2_000_000  # beyond this a staged text file is almost certainly data export


@dataclass
class Finding:
    path: str
    line: int
    kind: str
    masked: str
    note: str = ""


def mask(value: str) -> str:
    """Show enough to locate the value in the file, never enough to use it."""
    digits = re.sub(r"\D", "", value)
    if len(digits) <= 4:
        return "*" * len(digits)
    return f"{value[:2]}{'*' * (len(digits) - 4)}{value[-2:]}"


# --- validators ------------------------------------------------------------

def valid_iban(candidate: str) -> bool:
    s = candidate.replace(" ", "").upper()
    if len(s) < 15 or len(s) > 34:
        return False
    expected = IBAN_LENGTHS.get(s[:2])
    if expected is not None and len(s) != expected:
        return False
    rearranged = s[4:] + s[:4]
    total = 0
    for ch in rearranged:
        if ch.isdigit():
            total = (total * 10 + int(ch)) % 97
        elif ch.isalpha():
            total = (total * 100 + (ord(ch) - 55)) % 97
        else:
            return False
    return total == 1


def valid_rrn(candidate: str) -> bool:
    """Belgian rijksregisternummer: mod-97 over the first 9 digits."""
    d = re.sub(r"\D", "", candidate)
    if len(d) != 11:
        return False
    yy, mm, dd = int(d[0:2]), int(d[2:4]), int(d[4:6])
    # bis-numbers add 20 or 40 to the month; month 0 is used when DOB is unknown
    if mm > 40:
        mm -= 40
    elif mm > 20:
        mm -= 20
    if mm > 12 or dd > 31:
        return False
    body, check = int(d[0:9]), int(d[9:11])
    # Born before 2000 checks the bare number; from 2000 a leading 2 is prepended.
    return (97 - (body % 97)) == check or (97 - (int("2" + d[0:9]) % 97)) == check


def valid_cnp(candidate: str) -> bool:
    """Romanian CNP: structural date + weighted control digit."""
    d = candidate
    if len(d) != 13 or not d.isdigit():
        return False
    if d[0] == "0":  # sex/century digit is 1-8 (9 = foreign resident)
        return False
    if int(d[0]) > 9:
        return False
    mm, dd = int(d[3:5]), int(d[5:7])
    if not (1 <= mm <= 12) or not (1 <= dd <= 31):
        return False
    county = int(d[7:9])
    if not (1 <= county <= 52):
        return False
    total = sum(int(d[i]) * CNP_KEY[i] for i in range(12))
    control = total % 11
    control = 1 if control == 10 else control
    return control == int(d[12])


# --- git plumbing ----------------------------------------------------------

def git(repo: str, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", repo, *args],
        capture_output=True, text=True, errors="replace",
    )
    return result.stdout if result.returncode == 0 else ""


def staged_files(repo: str) -> list[str]:
    out = git(repo, "diff", "--cached", "--name-only", "--diff-filter=ACMR")
    return [line for line in out.splitlines() if line.strip()]


def staged_content(repo: str, path: str) -> str | None:
    """Read the blob as staged, not as it sits in the working tree."""
    result = subprocess.run(
        ["git", "-C", repo, "show", f":{path}"],
        capture_output=True,
    )
    if result.returncode != 0:
        return None
    raw = result.stdout
    if len(raw) > MAX_BYTES or b"\x00" in raw[:8192]:
        return None  # binary or oversized; the filename checks still cover it
    return raw.decode("utf-8", errors="replace")


def resolve_remote_exposure(repo: str) -> tuple[bool, str]:
    """Is this repo pointed at a forge that serves code to the open internet?

    Deliberately called only after a finding exists, so a clean session never
    pays for the lookup. `gh` can tell us a GitHub repo is private, which
    downgrades HOLD to advisory; absent that answer we assume exposure, because
    the cost of a false HOLD is one question and the cost of a false all-clear
    is a national-register number on the public internet.
    """
    url = git(repo, "remote", "get-url", "origin").strip()
    if not url:
        return False, "no origin remote"
    host_match = re.search(r"(?:@|//)([^/:]+)", url)
    host = host_match.group(1).lower() if host_match else ""
    if host not in PUBLIC_FORGE_HOSTS:
        return False, f"origin host {host or 'unknown'} is not a public forge"
    probe = subprocess.run(
        ["gh", "repo", "view", "--json", "visibility", "-q", ".visibility"],
        capture_output=True, text=True, cwd=repo,
    )
    if probe.returncode == 0:
        visibility = probe.stdout.strip().upper()
        if visibility == "PRIVATE":
            return False, f"{host} repo reports visibility PRIVATE"
        return True, f"{host} repo reports visibility {visibility or 'UNKNOWN'}"
    return True, f"{host} is a public forge (visibility unverified)"


# --- checks ----------------------------------------------------------------

def scan_content(repo: str, paths: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    for path in paths:
        if SELF_EXCLUDE_RE.search(path.replace("\\", "/")):
            continue
        text = staged_content(repo, path)
        if text is None:
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            if len(line) > 4000:
                continue
            for match in IBAN_RE.finditer(line):
                if valid_iban(match.group(1)):
                    findings.append(Finding(path, lineno, "IBAN", mask(match.group(1)),
                                            "mod-97 checksum valid"))
            for match in CNP_RE.finditer(line):
                if valid_cnp(match.group(1)):
                    findings.append(Finding(path, lineno, "CNP (Romanian)", mask(match.group(1)),
                                            "control digit valid"))
            for match in RRN_RE.finditer(line):
                if valid_rrn(match.group(1)):
                    findings.append(Finding(path, lineno, "RRN (Belgian)", mask(match.group(1)),
                                            "mod-97 checksum valid"))
    return findings


def scan_image_names(paths: list[str]) -> list[Finding]:
    out = []
    for path in paths:
        ext = os.path.splitext(path)[1].lower()
        if ext in IMAGE_EXTS and IDENTITY_IMAGE_RE.search(os.path.basename(path)):
            out.append(Finding(path, 0, "identity-document scan", os.path.basename(path),
                               "filename suggests an identity document"))
    return out


def privacy_conventions(repo: str) -> list[str]:
    """Read the repo's own privacy convention out of .gitignore.

    Ane's repos mark sensitive files with a `.local.` infix or a `private`
    segment and gitignore that family. A file carrying personal data without the
    marker is not just a risk, it is a break in the convention the repo already
    declares -- which makes the rename the natural fix rather than a new rule.
    """
    path = os.path.join(repo, ".gitignore")
    if not os.path.isfile(path):
        return []
    conventions = []
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        for raw in handle:
            entry = raw.strip()
            if not entry or entry.startswith("#"):
                continue
            if ".local." in entry or "local.*" in entry or "private" in entry.lower():
                conventions.append(entry)
    return conventions


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="repository root (default: cwd)")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()

    repo = os.path.abspath(args.repo)
    paths = staged_files(repo)
    if not paths:
        if args.json:
            print(json.dumps({"status": "clean", "reason": "nothing staged"}))
        else:
            print("PRIVACY SCAN: nothing staged.")
        return 0

    findings = scan_content(repo, paths) + scan_image_names(paths)
    conventions = privacy_conventions(repo)

    unmarked = []
    if conventions:
        for finding in findings:
            base = os.path.basename(finding.path).lower()
            if ".local." not in base and "private" not in finding.path.lower():
                unmarked.append(finding.path)
    unmarked = sorted(set(unmarked))

    if not findings:
        if args.json:
            print(json.dumps({"status": "clean", "staged": len(paths)}))
        else:
            print(f"PRIVACY SCAN: {len(paths)} staged file(s), no personal-data patterns matched.")
        return 0

    public, reason = resolve_remote_exposure(repo)
    status = "HOLD" if public else "ADVISORY"

    if args.json:
        print(json.dumps({
            "status": status,
            "remote_public": public,
            "remote_reason": reason,
            "conventions": conventions,
            "unmarked_files": unmarked,
            "findings": [asdict(f) for f in findings],
        }, indent=2))
        return 2 if public else 1

    print(f"PRIVACY SCAN: {status} — {len(findings)} match(es) across {len(paths)} staged file(s)")
    print(f"  remote: {reason}")
    for finding in findings:
        where = f"{finding.path}:{finding.line}" if finding.line else finding.path
        print(f"  - {finding.kind}: {where}  [{finding.masked}]  ({finding.note})")
    if unmarked:
        print("  convention: this repo gitignores " + ", ".join(conventions))
        print("  these carry personal data but lack the marker:")
        for path in unmarked:
            print(f"    - {path}  → rename to *.local.* to have it ignored")
    if public:
        print("  A public-forge remote and personal data co-occur. Commit held for confirmation.")
    return 2 if public else 1


if __name__ == "__main__":
    sys.exit(main())
