"""Write a colleague's answers into a new register edition, and approve it (SRHR map skill, phase c, steps 6-7).

apply() reads the answered review workbook and the run file the review step saved
(<map root>/review/run_<edition>.json), and writes <map root>/map_register/map_register_<edition>.csv:
  every row of the last edition (ticks kept, blank ma_code filled from config/ma_codes.csv), and
  for each change:  Correct    -> the new row, ticked by the reviewer on the answer date
                    Wrong      -> the corrected value, unticked, machine_check "colleague correction: second check"
                    Not sure / blank -> the new row, unticked
                    missing + Correct -> blank value, "no report <year>", ticked
  A business-plan focus change without a second reader stays unticked whatever the answer.
  A row from the Intelligence Tool snapshot keeps its value: "Wrong" unticks it and flags it for that tool's owner.

Safety: the last edition is never opened for writing. Before the new edition file is rewritten it is backed up
to map_register/_backup/; the rows are checked against the shared contract before and after writing, and a
failure restores the backup (or removes a file that did not exist before). Rows are replaced by their key, so
applying the same workbook twice gives the same file.

approve() refuses while any change is unresolved, otherwise writes map_register/approval_<edition>.json.
"""
import csv
import hashlib
import io
import json
import re
import shutil
import sys
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import compare_register as cr  # noqa: E402
import config_tables  # noqa: E402
import review_workbook as rw  # noqa: E402

CONTRACT = HERE.parent / "shared" / "srhr_data_contract.v1.json"
CORRECTION = "colleague correction: second check"
CONFIRMED = "colleague confirmed: no report"
SNAPSHOT_FLAG = "colleague flagged: ask the Intelligence Tool owner"
SNAPSHOT_TICK = "snapshot ba_tick"


@dataclass
class ApplyResult:
    written: int = 0
    ticked: int = 0
    unticked: int = 0
    problems: list = field(default_factory=list)


class ApproveRefused(Exception):
    """approve() found changes nobody has ticked yet; the message lists them."""


# ---------------------------------------------------------------- contract
def load_register_contract(path=CONTRACT):
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    t = dict(d["tables"]["map_register"])
    t["fields"] = [{**d.get("field_defaults", {}), **f} for f in t["fields"]]
    return t


def _type_ok(ftype, v):
    if v == "":
        return True
    if ftype == "int":
        return re.fullmatch(r"-?\d+", v) is not None
    if ftype == "date":
        try:
            return date.fromisoformat(v).isoformat() == v
        except ValueError:
            return False
    if ftype == "iso3":
        return re.fullmatch(r"[A-Z]{3}", v) is not None
    if ftype.startswith("enum:"):
        return v in ftype[5:].split("|")
    return True


def check_register(rows, contract):
    """Return a plain problem line per broken field or rule (fields and rules of the shared contract)."""
    probs = []
    for n, r in enumerate(rows, start=1):
        where = f"row {n} ({r.get('iso3', '')} {r.get('indicator_id', '')} {r.get('reference_year', '')})"
        for f in contract["fields"]:
            name, v = f["name"], str(r.get(f["name"], "") or "").strip()
            if f.get("required", True) and name not in r:
                probs.append(f"{where}: column {name} is missing")
            elif f.get("nonblank") and not v:
                probs.append(f"{where}: {name} is blank")
            elif not _type_ok(f["type"], v):
                probs.append(f"{where}: {name} '{v}' is not a valid {f['type']}")
        for rule in contract.get("rules", []):
            if rule["rule"] == "nonblank_unless_prefix":
                if not str(r.get(rule["prefix_field"], "")).startswith(rule["prefix"]) \
                        and not str(r.get(rule["field"], "")).strip():
                    probs.append(f"{where}: {rule['field']} is blank ({rule['why']})")
            elif rule["rule"] == "together":
                filled = [bool(str(r.get(x, "")).strip()) for x in rule["fields"]]
                if any(filled) and not all(filled):
                    probs.append(f"{where}: {' and '.join(rule['fields'])} must be filled together ({rule['why']})")
    return probs


# ---------------------------------------------------------------- files
def _reg(root):
    return Path(root) / "map_register"


def _edition_path(root, ed):
    return _reg(root) / f"map_register_{ed}.csv"


def _editions(root):
    out = []
    for p in _reg(root).glob("map_register_*.csv"):
        m = re.fullmatch(r"map_register_(\d{4})", p.stem)
        if m:
            out.append(int(m.group(1)))
    return sorted(out)


def _read(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _csv_bytes(rows, fields):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k, "") for k in fields})
    return buf.getvalue().encode("utf-8")


def run_path(root, edition):
    return Path(root) / "review" / f"run_{edition}.json"


def save_run(root, edition, reporting_year, baseline_edition, changes):
    """Save what the review step found, so apply can rebuild every changed row (review/run_<edition>.json)."""
    p = run_path(root, edition)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"edition": int(edition), "reporting_year": int(reporting_year),
                             "baseline_edition": int(baseline_edition),
                             "saved_on": datetime.now().isoformat(timespec="seconds"),
                             "changes": [asdict(c) for c in changes]}, indent=1), encoding="utf-8")
    return p


def _clean(r):
    return {k: v for k, v in r.items() if not k.startswith("_")}


def _ticked(r):
    return bool(str(r.get("ticked_by", "")).strip())


# ---------------------------------------------------------------- apply
def _refusal(root, edition):
    others = [e for e in _editions(root) if e != int(edition)]
    if not others:
        return None, f"Refused: there is no register edition older than {edition} to build on."
    last = max(others)
    if int(edition) <= last:
        return None, (f"Refused: edition {edition} is not newer than the last register edition ({last}). "
                      "A refresh writes a new edition and never changes an existing one.")
    return last, None


def _row_for(c, a, header, codes_of):
    """Return the register row a change produces under answer a, or None when nothing is written."""
    old, new = c.get("old") or {}, c.get("new")
    when = header["date"]
    if c["kind"] == "missing":
        if a.choice not in (rw.CORRECT, rw.WRONG):
            return None
        row = dict(old, reference_year=str(c["reference_year"]), date_read=when, ticked_by="", tick_date="")
        if a.choice == rw.CORRECT:
            row.update(value="", value_display=f"no report {c['reference_year']}",
                       machine_check=f"{CONFIRMED} {c['reference_year']}",
                       ticked_by=header["reviewer"], tick_date=when)
        else:
            row.update(value=a.corrected_value, value_display=a.corrected_value, machine_check=CORRECTION)
    else:
        row = dict(new)
        snapshot = row.get("ticked_by") == SNAPSHOT_TICK
        second = str(row.get("_second_reader", "") or "").strip()
        if a.choice == rw.CORRECT and not (c["kind"] == "focus_change" and not second):
            row.update(ticked_by=header["reviewer"], tick_date=when)
        elif a.choice == rw.WRONG and snapshot:
            row.update(ticked_by="", tick_date="", machine_check=SNAPSHOT_FLAG)
        elif a.choice == rw.WRONG:
            row.update(value=a.corrected_value, value_display=a.corrected_value, machine_check=CORRECTION,
                       ticked_by="", tick_date="")
        elif not snapshot:
            row.update(ticked_by="", tick_date="")
    row = _clean(row)
    if not str(row.get("ma_code", "")).strip():
        row["ma_code"] = codes_of.get(row.get("iso3", ""), "")
    return row


def apply(map_root, edition, workbook):
    """Write the answers of one review workbook into map_register_<edition>.csv; see the module docstring."""
    root, edition = Path(map_root), int(edition)
    res = ApplyResult()
    last, why = _refusal(root, edition)
    if why:
        res.problems.append(why)
        return res
    rp = run_path(root, edition)
    if not rp.exists():
        res.problems.append(f"Refused: {rp.name} is missing; run review for edition {edition} first.")
        return res
    run = json.loads(rp.read_text(encoding="utf-8"))
    if int(run["baseline_edition"]) != last:
        res.problems.append(f"Refused: the review compared with edition {run['baseline_edition']}, but the last "
                            f"edition is {last}. Run review again.")
        return res
    header, answers, read_problems = rw.read_answers(workbook)
    if not header["reviewer"]:
        res.problems.append("Refused: the Reviewer cell on 'How to use' is empty. Type your name and apply again.")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", header["date"] or ""):
        res.problems.append("Refused: the Date answered cell on 'How to use' is empty or not a date. "
                            "Type the date (dd.mm.yyyy) and apply again.")
    if res.problems:
        return res
    res.problems.extend(read_problems)

    _, codes = config_tables.load_config(root)
    codes_of = {}
    for code, iso3 in codes.items():
        codes_of.setdefault(iso3, []).append(code)
    codes_of = {k: ";".join(sorted(v)) for k, v in codes_of.items()}

    target = _edition_path(root, edition)
    contract = load_register_contract()
    fields = [f["name"] for f in contract["fields"]]
    rows = [dict(r) for r in _read(target if target.exists() else _edition_path(root, last))]
    for r in rows:
        if not str(r.get("ma_code", "")).strip():
            r["ma_code"] = codes_of.get(r.get("iso3", ""), "")
    at = {cr._key(r): i for i, r in enumerate(rows)}
    for c in run["changes"]:
        a = answers.get(c["change_id"], rw.Answer("", ""))
        row = _row_for(c, a, header, codes_of)
        if row is None:
            continue
        k = cr._key(row)
        prev = rows[at[k]] if k in at else None
        if not a.choice and prev is not None and _ticked(prev) and str(prev.get("value", "")) == str(row.get("value", "")):
            continue  # unanswered here, already confirmed by an earlier apply: keep that tick
        if prev is not None:
            rows[at[k]] = row
        else:
            at[k] = len(rows)
            rows.append(row)
        res.written += 1
        if _ticked(row):
            res.ticked += 1
        else:
            res.unticked += 1

    bad = check_register(rows, contract)
    if bad:
        res.problems.extend(["Nothing written: " + b for b in bad])
        return res
    backup = None
    if target.exists():
        bdir = _reg(root) / "_backup"
        bdir.mkdir(exist_ok=True)
        backup = bdir / f"map_register_{edition}.{datetime.now().strftime('%Y%m%d-%H%M%S-%f')}.csv"
        shutil.copy2(target, backup)
    target.write_bytes(_csv_bytes(rows, fields))
    bad = check_register(_read(target), contract)
    if bad:
        if backup:
            shutil.copy2(backup, target)
        else:
            target.unlink()
        res.problems.extend(["Write undone: " + b for b in bad])
    return res


# ---------------------------------------------------------------- approve
def unresolved(map_root, edition):
    """Change ids (with a short reason) that still need a person's tick in the edition file."""
    root = Path(map_root)
    run = json.loads(run_path(root, edition).read_text(encoding="utf-8"))
    path = _edition_path(root, edition)
    rows = {cr._key(r): r for r in _read(path)} if path.exists() else {}
    out = []
    for c in run["changes"]:
        if c["kind"] == "missing":
            r = rows.get((c["iso3"], c["indicator_id"], str(c["reference_year"])))
            old = c.get("old") or {}
            done = r is not None and _ticked(r) and (str(r.get("machine_check", "")).startswith(CONFIRMED)
                                                     or r.get("value") != old.get("value")
                                                     or r.get("reference_year") != old.get("reference_year"))
        else:
            r = rows.get(cr._key(c["new"]))
            done = r is not None and _ticked(r)
        if not done:
            out.append(f"{c['change_id']} ({c['kind']}: {c['iso3']} {c['indicator_id']} {c['reference_year']})")
    return out


def approve(map_root, edition, by):
    """Record the owner's approval of an edition; refuse while any change is unticked."""
    root, edition = Path(map_root), int(edition)
    if not str(by or "").strip():
        raise ApproveRefused("Not approved: give the approver's name (--by).")
    path = _edition_path(root, edition)
    if not path.exists():
        raise ApproveRefused(f"Not approved: {path.name} does not exist; run apply first.")
    left = unresolved(root, edition)
    if left:
        raise ApproveRefused(f"Not approved: {len(left)} change(s) still need a tick:\n  " + "\n  ".join(left))
    out = _reg(root) / f"approval_{edition}.json"
    out.write_text(json.dumps({"edition": edition, "approved_by": by.strip(),
                               "approved_on": date.today().isoformat(),
                               "register_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}, indent=1),
                   encoding="utf-8")
    return out
