"""Planted tests for derive_rows.py (SRHR map skill, phase c).

Synthetic drop-ins with invented codes, countries and streams only (this repository is public).
Run:  python test_derive_rows.py
"""
import csv
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import derive_rows as dr  # noqa: E402

FAILS = []
YEAR, EDITION = 2025, 2026
STREAMS = [
    {"key": "Stream A", "label": "Alpha fund", "group": "G1", "colour": "111111", "ledger_names": "Alpha grant"},
    {"key": "Stream B", "label": "Beta fund", "group": "G2", "colour": "222222", "ledger_names": ""},
    {"key": "Stream Z", "label": "Zeta fund", "group": "not on map", "colour": "", "ledger_names": ""},
]
COUNTRIES = {"country a": "XAA", "country b": "XBB", "country c": "XCC", "xaa": "XAA", "xbb": "XBB", "xcc": "XCC"}
PROJECT_COLS = ["Funding source", "Country", "grant status", "PO number", "other countries", "topic", "amount",
                "signed agreement", "start date", "end project", "Reporting deadline", "Status",
                "Report received", "Comment"]


def check(name, cond, detail=""):
    print(f"{'ok  ' if cond else 'FAIL'} {name}{'' if cond else ': ' + detail}")
    if not cond:
        FAILS.append(name)


def write_csv(path, header, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    return path


def dhis2_file(folder, rows):
    return write_csv(Path(folder) / "dataValueSets.csv",
                     ["dataelement", "period", "orgunit", "categoryoptioncombo", "value"], rows)


def ledger_file(folder, projects, overview_cols, overview):
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"projects {EDITION}"
    ws.append([])
    ws.append(PROJECT_COLS)
    for p in projects:
        ws.append([p.get(c, "") for c in PROJECT_COLS])
    ov = wb.create_sheet("Grant and project overview")
    ov.append([])
    ov.append([None, "Country", "membership status", "region", "Name / acronym"] + overview_cols)  # real sheet: column B
    for row in overview:
        ov.append(row)
    path = Path(folder) / "ledger.xlsx"
    wb.save(path)
    return path


def test_hiv_services_sum():
    with tempfile.TemporaryDirectory() as tmp:
        p = dhis2_file(tmp, [
            ["SRV-HIV and AIDS - counselling", "2025", "Org One (XA901-0000)", "0 - 24", "3"],
            ["REF-HIV and AIDS - testing", "2025", "Org One (XA901-0000)", "25+", "4"],
            ["Notes-HIV and AIDS - remark", "2025", "Org One (XA901-0000)", "0 - 24", "50"],
            ["SRV-Contraception - pill", "2025", "Org One (XA901-0000)", "0 - 24", "9"],
            ["SRV-Contraception - pill", "2025", "Org Two (XB902-0000)", "0 - 24", "9"],
        ])
        rows, problems = dr.from_dhis2(p, YEAR, {"901": "XAA", "902": "XBB"})
        got = {r["iso3"]: r["value"] for r in rows}
        check("HIV services: SRV + REF summed, Notes- and other topics skipped", got.get("XAA") == "7", str(got))
        check("org reporting no HIV row gets 0, not absent", got.get("XBB") == "0", str(got))
        check("services rows carry indicator and source", all(
            r["indicator_id"] == "ippf_hiv_services" and r["source_id"] == "ippf_dhis2_service_stats"
            for r in rows), str(rows))
        check("no problems on a clean file", problems == [], str(problems))


def test_two_codes_one_country_summed():
    with tempfile.TemporaryDirectory() as tmp:
        p = dhis2_file(tmp, [
            ["SRV-HIV and AIDS - a", "2025", "Org One (XA901-0000)", "0 - 24", "2"],
            ["SRV-HIV and AIDS - a", "2025", "Org One digital XA901A-0000", "0 - 24", "5"],
        ])
        rows, _ = dr.from_dhis2(p, YEAR, {"901": "XAA", "901A": "XAA"})
        check("main code + sub-unit summed per country", [(r["iso3"], r["value"], r["ma_code"]) for r in rows]
              == [("XAA", "7", "901;901A")], str(rows))


def test_unknown_org_code_is_problem():
    with tempfile.TemporaryDirectory() as tmp:
        p = dhis2_file(tmp, [
            ["SRV-HIV and AIDS - a", "2025", "Org One (XA901-0000)", "0 - 24", "2"],
            ["SRV-HIV and AIDS - a", "2025", "Org New (XC903A-0000)", "0 - 24", "8"],
            ["REF-HIV and AIDS - b", "2025", "Org New (XC903A-0000)", "0 - 24", "1"],
        ])
        rows, problems = dr.from_dhis2(p, YEAR, {"901": "XAA"})
        check("unknown organisation code becomes one problem line",
              len(problems) == 1 and "unknown organisation code '903A'" in problems[0], str(problems))
        check("unknown code's services are not given to any country",
              [r["value"] for r in rows] == ["2"], str(rows))


def test_partner_half_dot_suppressed_by_full():
    with tempfile.TemporaryDirectory() as tmp:
        p = ledger_file(tmp, [
            {"Funding source": "Alpha grant 2026\nStream 1", "Country": "Country A", "other countries": "Country B, Country C"},
            {"Funding source": "", "Country": "Country B", "other countries": "n/a"},  # forward-filled: Alpha
            {"Funding source": "Beta fund", "Country": "Country C", "other countries": ""},
        ], ["Alpha fund 2026", "Beta fund (2025-2026)", "Beta fund 2024"],
            [[None, "Country A", "MA", "EU", "A", "x", "", "x"], [None, "Country B", "MA", "EU", "B", "", "", ""]])
        rows, problems = dr.from_ledger(p, EDITION, STREAMS, COUNTRIES)
        partner = sorted((r["iso3"], r["value"]) for r in rows if r["indicator_id"] == "ippf_funding_streams_partner")
        check("partner half dot only where the country lacks that stream fully", partner == [("XCC", "Stream A")],
              str(partner))
        full = {r["iso3"]: (r["value"], r["value_display"]) for r in rows if r["indicator_id"] == "ippf_funding_streams"}
        check("forward-filled funding source gives Country B the stream", full.get("XBB") == ("1", "Stream A"), str(full))
        check("project country outside the overview still gets its row", full.get("XCC") == ("1", "Stream B"), str(full))
        count = {r["iso3"]: r["value"] for r in rows if r["indicator_id"] == "ippf_grant_streams_count"}
        check("overview count uses edition-year columns only", count == {"XAA": "1", "XBB": "0"}, str(count))
        check("clean ledger has no problems", problems == [], str(problems))


def test_country_with_org_in_brackets():
    with tempfile.TemporaryDirectory() as tmp:
        p = ledger_file(tmp, [{"Funding source": "Beta fund", "Country": "Country A (Org One) "}], [],
                        [[None, "Country A", "MA", "EU", "A"]])
        rows, problems = dr.from_ledger(p, EDITION, STREAMS, COUNTRIES)
        full = {r["iso3"]: r["value_display"] for r in rows if r["indicator_id"] == "ippf_funding_streams"}
        check("'Country (Org)' resolves to the country", full == {"XAA": "Stream B"} and problems == [],
              f"{full} {problems}")


def test_unknown_stream_is_problem():
    with tempfile.TemporaryDirectory() as tmp:
        p = ledger_file(tmp, [
            {"Funding source": "Gamma pooled fund\nStream 2", "Country": "Country A"},
            {"Funding source": "Zeta fund", "Country": "Country A"},
        ], [], [[None, "Country A", "MA", "EU", "A"]])
        rows, problems = dr.from_ledger(p, EDITION, STREAMS, COUNTRIES)
        check("unknown funding source is a problem in the plan's words",
              problems == ["stream 'Gamma pooled fund' has no row in config\\streams.csv"], str(problems))
        full = [r for r in rows if r["indicator_id"] == "ippf_funding_streams"]
        check("'not on map' stream is absorbed, not counted", [(r["value"], r["value_display"]) for r in full]
              == [("0", "none")], str(full))


def snapshot_file(folder, date, rows):
    return write_csv(Path(folder) / f"track_b_proposed_{date}.csv",
                     ["iso3", "indicator_id", "year", "value", "value_display", "feed", "code", "retrieved_on",
                      "source_ref", "ba_tick", "machine_check", "note"], rows)


def test_snapshot_unticked_rows_skipped():
    with tempfile.TemporaryDirectory() as tmp:
        p = snapshot_file(tmp, "2026-10-25", [
            ["XAA", "rate_x", "2024", "4.4", "4.4", "F", "C", "2026-10-25", "ref", "yes", "pass", ""],
            ["XBB", "rate_x", "2024", "2.2", "2.2", "F", "C", "2026-10-25", "ref", "", "pass", ""],
            ["XCC", "rate_x", "2024", "1.1", "1.1", "F", "C", "2026-10-25", "ref", "yes", "flag: fill", ""],
        ])
        rows = dr.from_snapshot(p, YEAR)
        check("only ticked rows with machine_check pass are used", [r["iso3"] for r in rows] == ["XAA"], str(rows))
        check("snapshot tag copied, upstream tick carried with the upstream ticker's name (minor)",
              rows and rows[0]["snapshot_tag"] == "Snapshot 2026-10-25"
              and rows[0]["ticked_by"] == "snapshot ba_tick: yes", str(rows))


def test_unknown_code_with_country_prefix_reaches_that_country():
    """I2: an unticked code whose prefix names a country is carried to that country's change."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "drop_in" / str(YEAR)).mkdir(parents=True)
        (root / "config").mkdir()
        (root / "intelligence_tool").mkdir()
        write_csv(root / "config" / "streams.csv", ["key", "label", "group", "colour"], [["Stream A", "Alpha", "G", "1"]])
        write_csv(root / "config" / "ma_codes.csv", ["ma_code", "iso3", "org_name", "ticked_by", "tick_date"],
                  [["901", "XAA", "Org One", "R", "2026-11-08"]])
        write_csv(root / "intelligence_tool" / "master_countries.csv", ["country", "iso3", "iso2"],
                  [["Country A", "XAA", "XA"]])
        # The two letters before a code name a service channel (clinic, outreach ...), never a country:
        # 'XA' below equals the master iso2 on purpose, and must NOT attach 777 to XAA.
        dhis2_file(root / "drop_in" / str(YEAR), [
            ["SRV-HIV and AIDS - a", "2025", "Org One (XA901-0000)", "0 - 24", "5"],
            ["SRV-HIV and AIDS - a", "2025", "Static Clinics (QQ901B-0000)", "0 - 24", "4"],
            ["SRV-HIV and AIDS - a", "2025", "Static Clinics (XA777-0000)", "0 - 24", "4"]])
        rows, problems, covered = dr.derive(root, YEAR, "HIV", [])
        check("I2: unticked letter sub-unit carried to the country of its ticked main code; channel letters ignored",
              covered.get("ippf_hiv_services", {}).get("unknown_codes") == {"XAA": ["901B"]}, str(covered))
        check("I2: both unknown codes still listed as notes",
              sum("unknown organisation code" in p for p in problems) == 2, str(problems))


def test_non_numeric_dhis2_value_is_problem():
    """I6 (re-graded minor): a non-numeric value is a problem line, never a stack trace."""
    with tempfile.TemporaryDirectory() as tmp:
        p = dhis2_file(tmp, [["SRV-HIV and AIDS - a", "2025", "Org One (XA901-0000)", "0 - 24", "n/a"],
                             ["SRV-HIV and AIDS - a", "2025", "Org One (XA901-0000)", "0 - 24", "3"]])
        try:
            rows, problems = dr.from_dhis2(p, YEAR, {"901": "XAA"})
            ok = [r["value"] for r in rows] == ["3"] and any("n/a" in x for x in problems)
        except Exception as e:  # noqa: BLE001
            ok, rows, problems = False, [], [f"{type(e).__name__}: {e}"]
        check("I6: non-numeric value skipped with a problem line", ok, f"{rows} {problems}")


def test_find_dropin_skips_lock_files_and_picks_newest():
    """I6: Excel's '~$' lock file is never picked; minor: the newest file by date wins, not by name."""
    import os
    import time
    with tempfile.TemporaryDirectory() as tmp:
        sub = Path(tmp) / "subgranting"
        sub.mkdir()
        old, new = sub / "z_ledger_old.xlsx", sub / "a_ledger_new.xlsx"
        old.write_bytes(b"x")
        new.write_bytes(b"x")
        t = time.time()
        os.utime(old, (t - 3600, t - 3600))
        os.utime(new, (t - 60, t - 60))
        (sub / "~$a_ledger_new.xlsx").write_bytes(b"lock")
        got = dr.find_dropin(Path(tmp), "ippf_subgranting.v1.json", "*.xlsx")
        check("I6/minor: lock file skipped, newest by date picked", got == new, str(got))


def test_partner_country_name_with_and():
    """minor: a country name holding ' and ' stays one partner."""
    with tempfile.TemporaryDirectory() as tmp:
        countries = dict(COUNTRIES, **{"land and sea": "XLS"})
        p = ledger_file(tmp, [{"Funding source": "Beta fund", "Country": "Country A",
                               "other countries": "Land and Sea, Country B and Country C"}], [],
                        [[None, "Country A", "MA", "EU", "A"]])
        rows, problems = dr.from_ledger(p, EDITION, STREAMS, countries)
        partner = sorted(r["iso3"] for r in rows if r["indicator_id"] == "ippf_funding_streams_partner")
        check("minor: 'Land and Sea' one partner; 'Country B and Country C' still split",
              partner == ["XBB", "XCC", "XLS"] and problems == [], f"{partner} {problems}")


def test_snapshot_too_old_stops():
    with tempfile.TemporaryDirectory() as tmp:
        p = snapshot_file(tmp, "2025-03-01", [])
        try:
            dr.from_snapshot(p, 2026)
            check("snapshot older than the reporting year stops refresh", False, "no stop")
        except dr.RefreshStop as e:
            check("snapshot older than the reporting year stops refresh",
                  "Snapshot 2025-03-01 is older than reporting year 2026" in str(e), str(e))


def test_coding_sheet_rows():
    with tempfile.TemporaryDirectory() as tmp:
        p = write_csv(Path(tmp) / "business_plan_focus_x.csv",
                      ["iso3", "ma_code", "plan_year", "focus", "plan_page", "reader", "second_reader", "note"],
                      [["XAA", "901", "2026", "high", "12", "Reader One", "", ""],
                       ["XBB", "902", "2026", "moderate", "3", "Reader One", "Reader Two", ""]])
        rows = dr.from_coding_sheet(p, EDITION)
        mc = [r["machine_check"] for r in rows]
        check("focus machine_check names page and readers",
              mc == ["plan page 12; reader Reader One", "plan page 3; reader Reader One, second Reader Two"], str(mc))
        check("focus rows sit at the plan year", {r["reference_year"] for r in rows} == {"2026"}, str(rows))


def test_derive_reads_drop_in_folder():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "drop_in" / str(YEAR)).mkdir(parents=True)
        (root / "config").mkdir()
        (root / "intelligence_tool").mkdir()
        write_csv(root / "config" / "streams.csv", ["key", "label", "group", "colour"], [["Stream A", "Alpha", "G", "1"]])
        write_csv(root / "config" / "ma_codes.csv", ["ma_code", "iso3", "org_name", "ticked_by", "tick_date"],
                  [["901", "XAA", "Org One", "R", "2026-11-08"]])
        write_csv(root / "intelligence_tool" / "master_countries.csv", ["country", "iso3", "iso2"], [["Country A", "XAA", "XA"]])
        dhis2_file(root / "drop_in" / str(YEAR), [["SRV-HIV and AIDS - a", "2025", "Org One (XA901-0000)", "0 - 24", "5"]])
        baseline = [{"iso3": "XAA", "indicator_id": "ippf_hiv_services", "member_status": "full member",
                     "unit": "services", "topic": "HIV", "source_id": "ippf_dhis2_service_stats", "reference_year": "2024"}]
        rows, problems, covered = dr.derive(root, YEAR, "HIV", baseline)
        svc = [r for r in rows if r["indicator_id"] == "ippf_hiv_services"]
        check("derive finds dataValueSets.csv in drop_in/<year>", [r["value"] for r in svc] == ["5"], str(rows))
        check("member_status and unit come from the baseline",
              svc and svc[0]["member_status"] == "full member" and svc[0]["unit"] == "services", str(svc))
        check("covered names the services indicator at the reporting year",
              covered.get("ippf_hiv_services", {}).get("year") == "2025", str(covered))
        check("missing coding sheet is a problem, not covered",
              any("business_plan_focus" in p for p in problems) and "ippf_bp_hiv_focus" not in covered, str(problems))
        check("every row has all register columns", all(set(dr.FIELDS) <= set(r) for r in rows), str(rows))


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
            except Exception as e:
                check(name, False, f"{type(e).__name__}: {e}")
    print(f"\n{'PASS' if not FAILS else 'FAIL'}: {len(FAILS)} failing check(s)")
    sys.exit(1 if FAILS else 0)
