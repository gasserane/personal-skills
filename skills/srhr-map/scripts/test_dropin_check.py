"""Planted-mismatch test for dropin_check.py (SRHR map skill, phase b).

Builds small synthetic files from each contract, so it never needs the organisation's data.
A planted case passes only if the checker reports exactly the expected number of problems.
The real-file run (Task 2 step 4 of the phase b plan) is the leg that meets real data.

The public-repository case needs a list of country names and reads it from the CSV named in
the SRHR_MASTER_COUNTRIES environment variable (column 'country'). Without it, the case is
reported as SKIPPED, never as passed.

Run:  python test_dropin_check.py
"""
import csv
import json
import os
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
SKILL = HERE.parent
sys.path.insert(0, str(HERE))
import dropin_check as dc  # noqa: E402

CONTRACTS = {p.stem.split(".")[0]: dc.load_contract(p) for p in sorted((SKILL / "contracts").glob("*.json"))}
YEAR = 2026


def spec_of(cid, role):
    return next(f for f in CONTRACTS[cid]["files"] if f["role"] == role)


def valid_row(spec, year):
    """One row that satisfies every machine-checked rule of a file spec."""
    row = {c: "x" for c in spec["required_columns"]}
    for r in spec.get("rules", []):
        if r["rule"] == "period_is_year":
            row[r["column"]] = str(year)
        elif r["rule"] == "ma_code_parses":
            row[r["column"]] = "Static Clinics (XX100-0000)"
        elif r["rule"] == "enum":
            row[r["column"]] = r["allowed"][0]
        elif r["rule"] == "values_in":
            row[r["column"]] = r["allowed"][0]
    return row


def make(tmp, name, spec, year, rows=None, header=None, sheet=None, header_row=None):
    """Write a synthetic drop-in file for a spec; returns its path."""
    header = header if header is not None else list(spec["required_columns"])
    rows = rows if rows is not None else [valid_row(spec, year)]
    header_row = header_row or spec["header_row"]
    path = Path(tmp) / name
    if spec["format"] == "csv":
        with open(path, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            for _ in range(header_row - 1):
                w.writerow([])
            w.writerow(header)
            for r in rows:
                w.writerow([r.get(c, "") for c in header])
    else:
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = sheet or spec["sheet"].format(year=year)
        for i, c in enumerate(header, 1):
            ws.cell(row=header_row, column=i, value=c)
        for j, r in enumerate(rows, header_row + 1):
            for i, c in enumerate(header, 1):
                ws.cell(row=j, column=i, value=r.get(c, ""))
        wb.save(path)
    return path


def main():
    results, skipped = [], []

    def record(case, ok, detail):
        results.append(ok)
        print(f"{'ok  ' if ok else 'FAIL'} {case}: {detail}")

    def expect(case, contract, role, path, year, n, must_contain=None):
        got = dc.check_file(contract, role, path, year)
        ok = len(got) == n and (must_contain is None or (got and must_contain in got[0]))
        record(case, ok, f"problems {got}")

    with tempfile.TemporaryDirectory() as tmp:
        # --- clean: one synthetic file per role must pass ---
        for cid, contract in CONTRACTS.items():
            for spec in contract["files"]:
                name = (spec["pattern"].replace("*", "sample"))
                p = make(tmp, f"clean_{spec['role']}_{name}", spec, YEAR)
                p2 = p.with_name(name)
                p.replace(p2)
                expect(f"clean_{cid}_{spec['role']}", contract, spec["role"], p2, YEAR, 0)

        sub = CONTRACTS["ippf_subgranting"]
        spec = spec_of("ippf_subgranting", "ledger_projects")
        header = [c for c in spec["required_columns"] if c != "amount"]
        p = make(tmp, "missing.xlsx", spec, YEAR, header=header)
        expect("missing_column", sub, "ledger_projects", p, YEAR, 1, "amount")

        p = make(tmp, "sheet.xlsx", spec, YEAR, sheet=f"projects {YEAR - 1}")
        expect("wrong_sheet", sub, "ledger_projects", p, YEAR, 1, "sheet")

        p = make(tmp, "shifted.xlsx", spec, YEAR, header_row=spec["header_row"] + 1)
        expect("header_row_shifted", sub, "ledger_projects", p, YEAR, 1, "header")

        dh = CONTRACTS["ippf_dhis2_annual"]
        spec = spec_of("ippf_dhis2_annual", "services")
        row = valid_row(spec, YEAR)
        p = make(tmp, "dataValueSets.csv", spec, YEAR, rows=[valid_row(spec, YEAR), dict(row, period=str(YEAR - 1))])
        expect("period_wrong", dh, "services", p, YEAR, 1, "line 3")

        p = make(tmp, "dataValueSets.csv", spec, YEAR, rows=[dict(row, orgunit="Head office")])
        expect("orgunit_unparsed", dh, "services", p, YEAR, 1, "line 2")

        for text, code in (("Digital/Virtual DV523-0000", "523"), ("Static Clinics (CL542-0000)", "542"),
                           ("Channels (510)", "510"), ("Some Name (DE) (510)", "510"),
                           ("Static Clinics (CL503A-0000)", "503A"), ("Head office", None)):
            record(f"ma_code {text!r}", dc.ma_code(text) == code, f"got {dc.ma_code(text)!r}, want {code!r}")

        spec = spec_of("ippf_dhis2_annual", "global_indicators")
        row = valid_row(spec, YEAR)
        p = make(tmp, "globalindicators.csv", spec, YEAR,
                 rows=[dict(row, dataelement="Marginalised - People living with HIV", value="12")])
        expect("tickbox_count_fails", dh, "global_indicators", p, YEAR, 1, "line 2")
        p = make(tmp, "globalindicators.csv", spec, YEAR,
                 rows=[dict(row, dataelement="EG - please specify 1", value="free text, with a comma\nand a newline"),
                       dict(row, dataelement="EG - Does your organisation have joint programmes", value="false")])
        expect("free_text_and_false_ok", dh, "global_indicators", p, YEAR, 0)

        bp = CONTRACTS["ippf_business_plan_focus"]
        spec = spec_of("ippf_business_plan_focus", "coding_sheet")
        row = valid_row(spec, YEAR)
        p = make(tmp, "business_plan_focus_x.csv", spec, YEAR, rows=[dict(row, focus="very high")])
        expect("focus_not_in_enum", bp, "coding_sheet", p, YEAR, 1, "focus")
        p = make(tmp, "business_plan_focus_x.csv", spec, YEAR, rows=[dict(row, focus="high", plan_page="")])
        expect("rating_without_page", bp, "coding_sheet", p, YEAR, 1, "plan_page")
        p = make(tmp, "business_plan_focus_x.csv", spec, YEAR, rows=[dict(row, focus="not assessed", plan_page="")])
        expect("not_assessed_without_page_ok", bp, "coding_sheet", p, YEAR, 0)

        p = make(tmp, "wrong_name.csv", spec, YEAR)
        expect("file_name_not_matching", bp, "coding_sheet", p, YEAR, 1, "name")

        bad = json.loads(json.dumps(bp))
        bad["files"][0]["rules"].append({"rule": "enumm", "column": "focus"})
        bad_path = Path(tmp) / "bad.json"
        bad_path.write_text(json.dumps(bad), encoding="utf-8")
        try:
            dc.load_contract(bad_path)
            record("unknown_rule_refused", False, "loaded without error")
        except ValueError as e:
            record("unknown_rule_refused", True, str(e)[:80])

    # --- the public repository holds no country name, currency or local path ---
    master = os.environ.get("SRHR_MASTER_COUNTRIES")
    if not master or not Path(master).exists():
        skipped.append("public_repo_clean")
        print("SKIP public_repo_clean: SRHR_MASTER_COUNTRIES not set")
    else:
        with open(master, encoding="utf-8", newline="") as f:
            names = [r["country"] for r in csv.DictReader(f) if r.get("country")]
        pats = [re.compile(r"\b" + re.escape(n) + r"\b") for n in names]
        pats += [re.compile(r"\bUSD\b"), re.compile(r"\bEUR\b"), re.compile(r"[A-Za-z]:[\\/]")]
        hits = []
        for path in SKILL.rglob("*"):
            if path.is_file() and path.suffix in (".md", ".json", ".py", ".csv", ".txt"):
                text = path.read_text(encoding="utf-8", errors="replace")
                hits += [f"{path.relative_to(SKILL)}: {p.pattern}" for p in pats if p.search(text)]
        record("public_repo_clean", not hits, f"hits {hits[:5]}")

    print(f"{sum(results)}/{len(results)} cases ok" + (f", {len(skipped)} skipped" if skipped else ""))
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
