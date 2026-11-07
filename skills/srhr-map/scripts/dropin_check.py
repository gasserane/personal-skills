"""Check a file a colleague drops in against its data contract (SRHR map skill, phase b).

Each contract in ../contracts/ names, per file role: the file name pattern, the format, the sheet
(xlsx), the header row, the required columns and the rules. This script reports every mismatch as
"<file>:<line N|header>: <problem>", the same shape as the shared schema check.

Rules with "rule": "documented" are method notes for people and later phases; they are never
checked here, and the script says how many it skipped.

Run:  python dropin_check.py <contract.json> <role> <file> --year <YYYY>
Exit 0 only when the file matches its contract.
"""
import argparse
import csv
import fnmatch
import json
import re
import sys
from pathlib import Path

KNOWN_RULES = {"period_is_year", "ma_code_parses", "values_in", "enum", "nonblank", "nonblank_unless",
               "documented"}
# The organisation code closes the org unit: "(XX123-0000)", "Channels (123)", "XX123-0000",
# "<name> (XX) (123)"; a sub-unit adds one letter (123A).
MA_CODE = re.compile(r"(?:\(|\b)(?:[A-Z]{2})?(\d{3}[A-Z]?)(?:-\d{4})?\)?\s*$")


def ma_code(orgunit: str):
    """The organisation code at the end of a DHIS2 org unit, or None."""
    m = MA_CODE.search(orgunit or "")
    return m.group(1) if m else None


def load_contract(path: Path) -> dict:
    contract = json.loads(Path(path).read_text(encoding="utf-8"))
    for key in ("contract_id", "version", "files"):
        if key not in contract:
            raise ValueError(f"{path}: contract lacks {key!r}")
    for spec in contract["files"]:
        if spec.get("format") not in ("csv", "xlsx"):
            raise ValueError(f"{path}: role {spec.get('role')} has unknown format {spec.get('format')!r}")
        if spec["format"] == "xlsx" and not spec.get("sheet"):
            raise ValueError(f"{path}: role {spec['role']} is xlsx but names no sheet")
        cols = set(spec.get("required_columns", []))
        for rule in spec.get("rules", []):
            if rule.get("rule") not in KNOWN_RULES:
                raise ValueError(f"{path}: role {spec['role']} has unknown rule {rule.get('rule')!r}")
            used = [rule[k] for k in ("column", "when_column", "other") if k in rule]
            if any(u not in cols for u in used):
                raise ValueError(f"{path}: role {spec['role']} rule {rule['rule']!r} names a column "
                                 f"that is not required")
    return contract


def _read(path: Path, spec: dict, year: int):
    """Return (header, rows, problem). rows = list of (line number, {column: text})."""
    hr = spec["header_row"]
    if spec["format"] == "csv":
        with open(path, encoding="utf-8-sig", newline="") as f:
            rd = csv.reader(f)
            header, rows = None, []
            for rec in rd:
                if rd.line_num < hr:
                    continue
                if header is None:
                    header = [c.strip() for c in rec]
                    continue
                rows.append((rd.line_num, dict(zip(header, rec))))
        return header or [], rows, None
    import openpyxl  # only needed for xlsx drop-ins
    sheet = spec["sheet"].format(year=year)
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        if sheet not in wb.sheetnames:
            return [], [], f"{path.name}:header: sheet '{sheet}' not found"
        it = wb[sheet].iter_rows(min_row=hr, values_only=True)
        first = next(it, None) or ()
        header = ["" if c is None else str(c).strip() for c in first]
        rows = [(hr + i, {h: ("" if v is None else str(v)) for h, v in zip(header, r)})
                for i, r in enumerate(it, 1)]
        return header, rows, None
    finally:
        wb.close()


def _row_problem(rule: dict, row: dict, year: int):
    col = rule.get("column")
    v = (row.get(col) or "").strip() if col else ""
    kind = rule["rule"]
    if kind == "period_is_year" and v != str(year):
        return f"{col} is {v!r}, expected {year}"
    if kind == "ma_code_parses" and ma_code(v) is None:
        return f"{col} {v!r} has no organisation code at its end"
    if kind == "enum" and v not in rule["allowed"]:
        return f"{col} {v!r} is not one of {rule['allowed']}"
    if kind == "nonblank" and not v:
        return f"{col} is blank"
    if kind == "nonblank_unless" and not v and (row.get(rule["other"]) or "").strip() != rule["value"]:
        return f"{col} is blank while {rule['other']} is not {rule['value']!r}"
    if kind == "values_in":
        when = row.get(rule["when_column"]) or ""
        if when.startswith(tuple(rule["when_prefix"])) and rule.get("except_containing", "\0") not in when:
            if (row.get(col) or "") not in rule["allowed"]:
                return f"{col} {row.get(col)!r} for {when!r} is not one of {rule['allowed']}"
    return None


def check_file(contract: dict, role: str, path: Path, year: int) -> list:
    path = Path(path)
    spec = next((f for f in contract["files"] if f["role"] == role), None)
    if spec is None:
        return [f"{path.name}:header: contract {contract['contract_id']} has no role {role!r}"]
    problems = []
    pattern = spec["pattern"].format(year=year)
    if not fnmatch.fnmatch(path.name, pattern):
        problems.append(f"{path.name}:header: file name does not match {pattern!r}")
    header, rows, problem = _read(path, spec, year)
    if problem:
        return problems + [problem]
    required = spec["required_columns"]
    missing = [c for c in required if c not in header]
    if len(missing) == len(required):
        return problems + [f"{path.name}:header: row {spec['header_row']} holds none of the required "
                           f"columns (header row moved?)"]
    problems += [f"{path.name}:header: missing column {c!r}" for c in missing]
    if missing:
        return problems
    checked = [r for r in spec.get("rules", []) if r["rule"] != "documented"]
    for line, row in rows:
        if not any((v or "").strip() for v in row.values()):
            continue
        for rule in checked:
            msg = _row_problem(rule, row, year)
            if msg:
                problems.append(f"{path.name}:line {line}: {msg}")
    return problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("contract", type=Path)
    ap.add_argument("role")
    ap.add_argument("file", type=Path)
    ap.add_argument("--year", type=int, required=True)
    args = ap.parse_args(argv)
    contract = load_contract(args.contract)
    problems = check_file(contract, args.role, args.file, args.year)
    spec = next((f for f in contract["files"] if f["role"] == args.role), {})
    notes = sum(1 for r in spec.get("rules", []) if r["rule"] == "documented")
    print(f"{'ok  ' if not problems else 'FAIL'} {contract['contract_id']}/{args.role}: "
          f"{len(problems)} problem(s); {notes} documented rule(s) not machine-checked")
    for p in problems[:20]:
        print(f"     {p}")
    if len(problems) > 20:
        print(f"     ... {len(problems) - 20} more")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
