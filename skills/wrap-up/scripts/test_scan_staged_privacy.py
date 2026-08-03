#!/usr/bin/env python3
"""Fixture-repo tests for the Gate 3 content scan.

These build throwaway git repos in a temp dir, stage real content, and assert on
what the scanner actually returns. The point of testing this way rather than
calling the validators directly is that the failure mode being guarded against
was never a maths error -- it was a scan that read filenames and therefore never
looked at the content at all. A test that only exercised valid_rrn() would have
passed against the broken gate.

All identifiers below are synthetic. They carry valid checksums so the scanner
has something real to match, but they belong to nobody.

Run: python scripts/test_scan_staged_privacy.py
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCANNER = os.path.join(HERE, "scan_staged_privacy.py")

# Synthetic, checksum-valid, belonging to no one.
FAKE_RRN = "93.05.18-223.61"
FAKE_IBAN = "BE68 5390 0754 7034"
FAKE_CNP = "1850730401233"


def run(cmd: list[str], cwd: str) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def make_repo(tmp: str, name: str, remote: str | None, gitignore: str | None) -> str:
    repo = os.path.join(tmp, name)
    os.makedirs(repo)
    run(["git", "init", "-q"], repo)
    run(["git", "config", "user.email", "test@example.invalid"], repo)
    run(["git", "config", "user.name", "Fixture"], repo)
    if gitignore is not None:
        with open(os.path.join(repo, ".gitignore"), "w", encoding="utf-8") as fh:
            fh.write(gitignore)
    if remote:
        run(["git", "remote", "add", "origin", remote], repo)
    return repo


def stage(repo: str, relpath: str, content: str) -> None:
    full = os.path.join(repo, relpath)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(content)
    run(["git", "add", "--", relpath], repo)


def scan(repo: str) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, SCANNER, "--repo", repo, "--json"],
        capture_output=True, text=True,
    )
    try:
        return proc.returncode, json.loads(proc.stdout)
    except json.JSONDecodeError:
        raise AssertionError(f"scanner emitted non-JSON:\n{proc.stdout}\n{proc.stderr}")


GITIGNORE = "*.local.*\n**/*private*\n__pycache__/\n"

results: list[tuple[bool, str]] = []


def check(condition: bool, label: str) -> None:
    results.append((bool(condition), label))


def main() -> int:
    tmp = tempfile.mkdtemp(prefix="gate3-fixture-")
    try:
        # --- 1. The 2026-07-03 scenario: ordinary filename, public remote -----
        repo = make_repo(tmp, "public-with-pii", "https://github.com/example/notes.git", GITIGNORE)
        stage(repo, "notes/meeting-notes.md",
              f"Buyer registration\n\nrijksregister {FAKE_RRN}\naccount {FAKE_IBAN}\n")
        code, out = scan(repo)
        check(code == 2, "public remote + personal data exits 2 (HOLD)")
        check(out["status"] == "HOLD", "status is HOLD")
        kinds = {f["kind"] for f in out["findings"]}
        check("RRN (Belgian)" in kinds, "Belgian rijksregister detected inside a .md file")
        check("IBAN" in kinds, "IBAN detected inside a .md file")
        # The scanner's output flows into the session transcript and from there
        # into handoff files, so a finding that quoted the number in full would
        # re-commit the harm it just prevented.
        serialised = json.dumps(out)
        bare_rrn = FAKE_RRN.replace(".", "").replace("-", "")
        check(bare_rrn not in serialised and FAKE_RRN not in serialised,
              "raw RRN never appears in output, punctuated or bare")
        check(FAKE_IBAN.replace(" ", "") not in serialised and FAKE_IBAN not in serialised,
              "raw IBAN never appears in output, spaced or bare")
        check("notes/meeting-notes.md" in out["unmarked_files"],
              "file flagged as breaking the .local convention")

        # --- 2. Clean session must not hold ----------------------------------
        repo = make_repo(tmp, "clean", "https://github.com/example/clean.git", GITIGNORE)
        stage(repo, "src/app.py",
              "TIMESTAMP = 1722688123456  # epoch ms\n"
              "ORDER_ID = 20240115001\nBATCH = 1234567890123\n")
        stage(repo, "docs/report.md", "We surveyed 1250 people across 11 countries.\n")
        code, out = scan(repo)
        check(code == 0, "clean repo exits 0")
        check(out["status"] == "clean", "clean repo reports clean")

        # --- 3. Same data, private/non-forge remote -> advisory, not HOLD -----
        repo = make_repo(tmp, "local-remote", "/srv/git/mirror.git", GITIGNORE)
        stage(repo, "notes/buyers.md", f"CNP {FAKE_CNP}\n")
        code, out = scan(repo)
        check(code == 1, "non-forge remote + personal data exits 1 (advisory)")
        check(out["status"] == "ADVISORY", "status is ADVISORY, commit not blocked")
        check(any(f["kind"].startswith("CNP") for f in out["findings"]), "CNP detected")

        # --- 4. The .local convention self-enforces upstream of the scanner --
        # A correctly-marked file matches the repo's own gitignore, so `git add`
        # refuses it and it never reaches staging. This is why the convention
        # check recommends the rename: renaming does not just label the file, it
        # removes it from the commit entirely.
        repo = make_repo(tmp, "marked", "https://github.com/example/marked.git", GITIGNORE)
        stage(repo, "data/buyers.local.md", f"CNP {FAKE_CNP}\n")
        code, out = scan(repo)
        check(code == 0, "a .local.-marked file is gitignored and never staged")

        # --- 5. Identity-scan images caught by name --------------------------
        repo = make_repo(tmp, "scans", "https://github.com/example/scans.git", GITIGNORE)
        stage(repo, "docs/identity-card-front.jpg", "notarealimage")
        code, out = scan(repo)
        check(any(f["kind"] == "identity-document scan" for f in out["findings"]),
              "identity-card image flagged by filename")

        # --- 6. Unstaged personal data is out of scope -----------------------
        repo = make_repo(tmp, "unstaged", "https://github.com/example/u.git", GITIGNORE)
        stage(repo, "README.md", "nothing here\n")
        with open(os.path.join(repo, "loose.md"), "w", encoding="utf-8") as fh:
            fh.write(f"IBAN {FAKE_IBAN}\n")  # written but never staged
        code, out = scan(repo)
        check(code == 0, "unstaged personal data does not trigger the gate")

    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    passed = sum(1 for ok, _ in results if ok)
    for ok, label in results:
        print(f"  {'PASS' if ok else 'FAIL'}  {label}")
    print(f"\n{passed}/{len(results)} checks passed")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
