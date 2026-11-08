"""Planted tests for publish_dataset.py (SRHR map skill, phase d, Power BI dataset).

Invented countries (XAA...), codes, sources and values only. Writes into a temporary folder. Run:
    python test_publish_dataset.py
"""
import csv
import io
import re
import sys
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from openpyxl import load_workbook

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import publish_dataset as pd_  # noqa: E402
import publish_workbook as pw  # noqa: E402

FAILS = []
TMP = Path(tempfile.mkdtemp(prefix="srhr_pd_"))
URL_A = "https" + "://example.org/source-a"  # concatenated: public_repo_clean flags drive-letter-like text
MA = "XA1"


def check(name, cond, detail=""):
    print(f"{'ok  ' if cond else 'FAIL'} {name}{'' if cond else ': ' + detail}")
    if not cond:
        FAILS.append(name)


def write_csv(path, fields, rows):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    return path


def row(iso3, ind, value, display, unit, year, src, by="", on=""):
    return {"iso3": iso3, "ma_code": MA, "member_status": "full", "topic": "HIV", "indicator_id": ind,
            "value": value, "value_display": display, "unit": unit, "reference_year": year, "source_id": src,
            "date_read": "", "machine_check": "pass", "ticked_by": by, "tick_date": on, "snapshot_tag": ""}


REG_ROWS = [
    row("XAB", "ecdc_hiv_diagnosis_rate", "3.1", "3.1", "per 100 000", "2023", "src_a", "Reviewer One", "2026-11-01"),
    row("XAA", "ippf_membership", "core", "Full member", "", "2025", "ippf_tracker", "Reviewer One", "2026-11-01"),
    row("XAA", "ippf_grant_streams_count", "12", "12", "grant streams", "2026", "src_b"),
]
REG = write_csv(TMP / "map_register_2031.csv", pw.REGISTER_FIELDS, REG_ROWS)
SRC = write_csv(TMP / "source_register.csv", ["source_id", "source", "publisher", "url"], [
    {"source_id": "src_a", "source": "Source A annual report", "publisher": "Agency A", "url": URL_A},
    {"source_id": "src_b", "source": "Source B table", "publisher": "Agency B", "url": ""}])
MASTER = write_csv(TMP / "master_countries.csv", ["country", "iso3"], [
    {"country": "Country A", "iso3": "XAA"}, {"country": "Country B", "iso3": "XAB"}])


def run(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = pd_.main(argv)
    return code, out.getvalue() + err.getvalue()


def args(out_dir):
    return ["--register", str(REG), "--sources", str(SRC), "--master", str(MASTER), "--out-dir", str(out_dir)]


def main():
    d = TMP / "publish" / "2031"
    code, msg = run(args(d))
    c, x = d / "powerbi_dataset_2031.csv", d / "powerbi_dataset_2031.xlsx"
    check("writes csv and xlsx, exit 0", code == 0 and c.exists() and x.exists(), f"code {code}: {msg}")
    if code != 0:
        print(f"{len(FAILS)} failure(s)")
        sys.exit(1)

    raw = c.read_bytes()
    check("csv starts with the UTF-8 BOM", raw.startswith(b"\xef\xbb\xbf"))
    with open(c, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    check("csv columns = DATASET_COLUMNS in order", rows[0] == pd_.DATASET_COLUMNS, str(rows[0]))
    check("one csv row per register row", len(rows) - 1 == len(REG_ROWS), str(len(rows) - 1))
    check("no MA code or MA column (country only)",
          MA not in raw.decode("utf-8-sig") and "ma_code" not in rows[0] and "member_status" not in rows[0])
    col = {h: i for i, h in enumerate(rows[0])}
    byk = {(r[col["iso3"]], r[col["indicator_id"]]): r for r in rows[1:]}
    rate = byk[("XAB", "ecdc_hiv_diagnosis_rate")]
    check("long format: edition, country name, plain indicator, source url",
          (rate[col["edition"]], rate[col["country"]], rate[col["source_url"]]) == ("2031", "Country B", URL_A)
          and rate[col["indicator"]].startswith(pw.PLAIN["ecdc_hiv_diagnosis_rate"]), str(rate))
    check("value_number set for a number, blank for a category",
          rate[col["value_number"]] == "3.1" and byk[("XAA", "ippf_membership")][col["value_number"]] == "")
    check("confirmed yes / not yet confirmed",
          rate[col["confirmed"]] == "yes"
          and byk[("XAA", "ippf_grant_streams_count")][col["confirmed"]] == pw.NOT_CONFIRMED)

    wb = load_workbook(x)
    ws = wb[pd_.DATA_SHEET]
    xrows = [["" if v is None else v for v in r] for r in ws.iter_rows(values_only=True)]
    check("xlsx header = csv header", xrows[0] == rows[0], str(xrows[0]))
    same = len(xrows) == len(rows)
    for cr_, xr in zip(rows[1:], xrows[1:]):
        for h, i in col.items():
            a, b = cr_[i], xr[i]
            ok = (float(a) == b) if (h == "value_number" and a != "") else (str(b) == a)
            same &= ok
    check("csv and xlsx hold identical values, cell by cell", same)
    check("value_number is a number in the xlsx", isinstance(xrows[1 + [r[col["iso3"]] for r in rows[1:]].index("XAB")]
                                                             [col["value_number"]], (int, float)))
    t = list(ws.tables.values())
    check("xlsx table ref covers every data row",
          bool(t) and int(re.search(r"(\d+)$", t[0].ref).group(1)) == len(rows), str([tt.ref for tt in t]))
    gl = " ".join(str(v) for r in wb["Glossary"].iter_rows(values_only=True) for v in r if v)
    check("Glossary explains every column", all(h in gl for h in pd_.DATASET_COLUMNS),
          str([h for h in pd_.DATASET_COLUMNS if h not in gl]))

    before = (c.read_bytes(), x.read_bytes())
    code, msg = run(args(d))
    check("existing targets: exit 2, names a file, files unchanged",
          code == 2 and c.name in msg and (c.read_bytes(), x.read_bytes()) == before, f"{code}: {msg}")
    d2 = TMP / "only_xlsx"
    d2.mkdir()
    (d2 / "powerbi_dataset_2031.xlsx").write_bytes(b"hand-made")
    code, msg = run(args(d2))
    check("one existing target is enough to refuse; the other is not written",
          code == 2 and "powerbi_dataset_2031.xlsx" in msg and not (d2 / "powerbi_dataset_2031.csv").exists(),
          f"{code}: {msg}")

    # race: files that appear after the early check and before the write are never overwritten
    d3_ = TMP / "race"
    real_rows = pd_.dataset_rows

    def planted(*a, **k):
        d3_.mkdir(parents=True, exist_ok=True)
        (d3_ / "powerbi_dataset_2031.csv").write_bytes(b"made by someone else")
        return real_rows(*a, **k)
    pd_.dataset_rows = planted
    try:
        code, msg = run(args(d3_))
    except Exception as e:  # noqa: BLE001 - the RED state is an uncaught error or an overwrite
        code, msg = "raised", repr(e)
    finally:
        pd_.dataset_rows = real_rows
    check("race: csv appearing after the check is kept, exit 2, xlsx not written",
          code == 2 and (d3_ / "powerbi_dataset_2031.csv").read_bytes() == b"made by someone else"
          and not (d3_ / "powerbi_dataset_2031.xlsx").exists(), f"{code}: {msg[-200:]}")

    print(f"{len(FAILS)} failure(s)")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
