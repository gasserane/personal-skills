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

Safety: the last edition is never opened for writing, and neither is an approved edition or an edition
file apply did not create (review/applied_<edition>.json records that apply made it, and which row each
change wrote). The workbook carries the fingerprint of the review run it came from; a workbook whose run
was replaced by a later review is refused, so a tick never lands on a value nobody saw. Run files are one
per topic, so a --topic review leaves the other topic's run alone. Rows are checked against the shared
contract before writing, the file must keep every row of the last edition, and the write goes through a
temporary file swapped in at the end (the previous file is backed up to map_register/_backup/ first).
A row a person already ticked keeps its tick when an answer would give it the same value.

approve() refuses while any change is unresolved, otherwise writes map_register/approval_<edition>.json.
"""
import csv
import hashlib
import io
import json
import os
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
from derive_rows import TOPIC_OF  # noqa: E402
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


def run_path(root, edition, topic=None):
    """review/run_<edition>.json for a full review, review/run_<edition>_<topic>.json for a --topic review."""
    return Path(root) / "review" / (f"run_{edition}.json" if not topic else f"run_{edition}_{topic}.json")


def run_digest(edition, baseline_edition, changes):
    """Fingerprint of everything a review proposed; the workbook carries it so apply can match the two."""
    blob = json.dumps({"edition": int(edition), "baseline_edition": int(baseline_edition), "changes": changes},
                      sort_keys=True, default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def save_run(root, edition, reporting_year, baseline_edition, changes, topic=None):
    """Save what the review step found, so apply can rebuild every changed row; one file per topic."""
    p = run_path(root, edition, topic)
    p.parent.mkdir(parents=True, exist_ok=True)
    ch = [asdict(c) for c in changes]
    p.write_text(json.dumps({"edition": int(edition), "reporting_year": int(reporting_year),
                             "baseline_edition": int(baseline_edition), "topic": topic or "",
                             "saved_on": datetime.now().isoformat(timespec="microseconds"),
                             "digest": run_digest(edition, baseline_edition, ch),
                             "changes": ch}, indent=1), encoding="utf-8")
    return p


def _clean(r):
    return {k: v for k, v in r.items() if not k.startswith("_")}


def _ticked(r):
    return bool(str(r.get("ticked_by", "")).strip())


def _snapshot_ticked(r):
    return str(r.get("ticked_by", "")).startswith(SNAPSHOT_TICK)


# ---------------------------------------------------------------- runs
def _runs(root, edition):
    """Every review run file of this edition (full and per topic), newest first."""
    out = []
    for p in (Path(root) / "review").glob(f"run_{edition}*.json"):
        if not re.fullmatch(rf"run_{edition}(_[A-Za-z]+)?", p.stem):
            continue
        try:
            r = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        r["_path"] = str(p)
        out.append(r)
    return sorted(out, key=lambda r: r.get("saved_on", ""), reverse=True)


def _topics(run):
    return {run["topic"]} if run.get("topic") else {"HIV", "funding"}


def _topic_of(c):
    r = c.get("new") or c.get("old") or {}
    return r.get("topic") or TOPIC_OF.get(c.get("indicator_id", ""), "")


def effective_changes(root, edition):
    """[(run, change)] that stand now: a change is dropped when a newer run reviewed its topic again."""
    covered, out = set(), []
    for run in _runs(root, edition):
        out += [(run, c) for c in run["changes"] if _topic_of(c) not in covered]
        covered |= _topics(run)
    return out


# ---------------------------------------------------------------- apply
def _approval_path(root, edition):
    return _reg(root) / f"approval_{edition}.json"


def applied_path(root, edition):
    """review/applied_<edition>.json: apply created the edition file, and which row each change wrote."""
    return Path(root) / "review" / f"applied_{edition}.json"


def _refusal(root, edition):
    if _approval_path(root, edition).exists():
        return None, (f"Refused: edition {edition} is approved ({_approval_path(root, edition).name}). "
                      "A refresh never changes an approved edition; build the next edition instead.")
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
        snapshot = _snapshot_ticked(row)
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


def _write_atomic(path, data):
    """Write to a temporary file beside path, then swap it in; an interrupted write leaves path as it was."""
    tmp = path.with_name(path.name + ".tmp")
    try:
        tmp.write_bytes(data)
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()


def apply(map_root, edition, workbook):
    """Write the answers of one review workbook into map_register_<edition>.csv; see the module docstring."""
    res = ApplyResult()
    try:
        _apply(Path(map_root), int(edition), Path(workbook), res)
    except config_tables.ConfigError as e:
        res.problems.append(f"Stopped: {e}")
    except PermissionError as e:
        res.problems.append(f"Stopped: {Path(e.filename or 'a file').name} is open or locked. Close it (Excel?) "
                            "and apply again. Nothing was changed.")
    except OSError as e:
        res.problems.append(f"Stopped: a file could not be read or written ({e}). Nothing was changed.")
    return res


def _apply(root, edition, workbook, res):
    last, why = _refusal(root, edition)
    if why:
        res.problems.append(why)
        return
    try:
        header, answers, read_problems = rw.read_answers(workbook)
    except Exception as e:  # noqa: BLE001 - a missing, mistyped or non-xlsx file: one plain line
        res.problems.append(f"Refused: {workbook.name} cannot be read as an answered review workbook "
                            f"({type(e).__name__}). Give the .xlsx the review step wrote.")
        return
    if not header.get("run_digest") or not header.get("ids"):
        res.problems.append("Refused: the workbook's hidden id list is gone, so its answers cannot be matched "
                            "to the review. Run review again and answer the new workbook.")
        return
    runs = _runs(root, edition)
    run = next((r for r in runs if r.get("digest") == header["run_digest"]), None)
    if run is None:
        newest = sorted((root / "review").glob(f"review_{edition}_*.xlsx"))
        res.problems.append("Refused: this workbook comes from an earlier review whose results have been "
                            "replaced, so a tick could land on a value nobody saw. Answer the newest workbook"
                            + (f" ({newest[-1].name})." if newest else "; run review again."))
        return
    if int(run["baseline_edition"]) != last:
        res.problems.append(f"Refused: the review compared with edition {run['baseline_edition']}, but the last "
                            f"edition is {last}. Run review again.")
        return
    run_ids = [c["change_id"] for c in run["changes"]]
    only_book = [i for i in header["ids"] if i not in run_ids]
    only_run = [i for i in run_ids if i not in header["ids"]]
    if only_book or only_run:
        res.problems.append("Refused: the workbook's hidden id list does not match its review run "
                            f"(only in the workbook: {', '.join(only_book) or 'none'}; only in the run: "
                            f"{', '.join(only_run) or 'none'}). Run review again.")
        return
    if not header["reviewer"]:
        res.problems.append("Refused: the Reviewer cell on 'How to use' is empty. Type your name and apply again.")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", header["date"] or ""):
        res.problems.append("Refused: the Date answered cell on 'How to use' is empty or not a date. "
                            "Type the date (dd.mm.yyyy) and apply again.")
    if res.problems:
        return
    res.problems.extend(read_problems)
    gone = set().union(*[_topics(r) for r in runs if r.get("saved_on", "") > run.get("saved_on", "")])
    changes = [c for c in run["changes"] if _topic_of(c) not in gone]
    if len(changes) < len(run["changes"]):
        res.problems.append(f"{len(run['changes']) - len(changes)} change(s) skipped: a newer review of "
                            f"{', '.join(sorted(gone))} replaced them. Answer that review's workbook.")

    _, codes = config_tables.load_config(root)
    codes_of = {}
    for code, iso3 in codes.items():
        codes_of.setdefault(iso3, []).append(code)
    codes_of = {k: ";".join(sorted(v)) for k, v in codes_of.items()}

    target, ap = _edition_path(root, edition), applied_path(root, edition)
    contract = load_register_contract()
    fields = [f["name"] for f in contract["fields"]]
    base_keys = [cr._key(r) for r in _read(_edition_path(root, last))]
    if target.exists():
        log = json.loads(ap.read_text(encoding="utf-8")) if ap.exists() else {}
        if not log.get("created_by_apply"):
            res.problems.append(f"Refused: {target.name} exists but apply did not create it (no review\\{ap.name}). "
                                "A refresh never rewrites an edition it did not write. Move that file away, or ask "
                                "the map owner.")
            return
        rows = [dict(r) for r in _read(target)]
        have = {cr._key(r) for r in rows}
        lost = [k for k in base_keys if k not in have]
        if lost:
            res.problems.append(f"Refused: {target.name} lacks {len(lost)} row(s) of edition {last} (first: "
                                f"{' '.join(map(str, lost[0]))}). Restore it from map_register\\_backup, or move it "
                                "away and apply every answered workbook again.")
            return
    else:
        rows = [dict(r) for r in _read(_edition_path(root, last))]
        log = {"edition": edition, "created_by_apply": True,
               "created_on": datetime.now().isoformat(timespec="seconds"), "rows": {}}
    for r in rows:
        if not str(r.get("ma_code", "")).strip():
            r["ma_code"] = codes_of.get(r.get("iso3", ""), "")
    at = {cr._key(r): i for i, r in enumerate(rows)}
    drop = set()
    for c in changes:
        a = answers.get(c["change_id"], rw.Answer("", ""))
        row = _row_for(c, a, header, codes_of)
        if row is None:
            continue
        k = cr._key(row)
        earlier = log["rows"].get(c["change_id"])
        log["rows"][c["change_id"]] = {"key": list(k), "digest": run["digest"]}
        if earlier and tuple(earlier["key"]) != k and tuple(earlier["key"]) in at:
            j = at[tuple(earlier["key"])]  # this change wrote another row before (e.g. an earlier 'Wrong')
            if not _ticked(rows[j]) and tuple(earlier["key"]) not in base_keys:
                drop.add(j)
        prev = rows[at[k]] if k in at else None
        if prev is not None and _ticked(prev) and str(prev.get("value", "")) == str(row.get("value", "")) \
                and (not a.choice or not _snapshot_ticked(prev)):
            continue  # same value already ticked (by an earlier apply or by hand): keep that tick
        if prev is not None:
            rows[at[k]] = row
            drop.discard(at[k])
        else:
            at[k] = len(rows)
            rows.append(row)
        res.written += 1
        if _ticked(row):
            res.ticked += 1
        else:
            res.unticked += 1
    rows = [r for i, r in enumerate(rows) if i not in drop]

    have = {cr._key(r) for r in rows}
    bad = [f"row {' '.join(map(str, k))} of edition {last} would be lost" for k in base_keys if k not in have]
    bad += check_register(rows, contract)
    if bad:
        res.problems.extend(["Nothing written: " + b for b in bad])
        return
    data = _csv_bytes(rows, fields)
    tmp = target.with_name(target.name + ".check.tmp")
    try:
        tmp.write_bytes(data)
        bad = check_register(_read(tmp), contract)
    finally:
        if tmp.exists():
            tmp.unlink()
    if bad:
        res.problems.extend(["Nothing written: " + b for b in bad])
        return
    if target.exists():
        bdir = _reg(root) / "_backup"
        bdir.mkdir(exist_ok=True)
        shutil.copy2(target, bdir / f"map_register_{edition}.{datetime.now().strftime('%Y%m%d-%H%M%S-%f')}.csv")
    ap.parent.mkdir(parents=True, exist_ok=True)
    _write_atomic(target, data)
    _write_atomic(ap, json.dumps(log, indent=1).encode("utf-8"))


# ---------------------------------------------------------------- approve
def unresolved(map_root, edition):
    """Change ids (with a short reason) that still need a person's tick in the edition file."""
    root = Path(map_root)
    path = _edition_path(root, edition)
    rows = {cr._key(r): r for r in _read(path)} if path.exists() else {}
    ap = applied_path(root, edition)
    log = json.loads(ap.read_text(encoding="utf-8")) if ap.exists() else {"rows": {}}
    out = []
    for run, c in effective_changes(root, edition):
        ent = log["rows"].get(c["change_id"])
        key = tuple(ent["key"]) if ent and ent.get("digest") == run.get("digest") else None
        if key is None and c["kind"] != "missing":
            key = cr._key(c["new"])
        r = rows.get(key) if key else None
        if not (r is not None and _ticked(r)):
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
    if not _runs(root, edition):
        raise ApproveRefused(f"Not approved: no review run for edition {edition} is saved in the review folder.")
    left = unresolved(root, edition)
    if left:
        raise ApproveRefused(f"Not approved: {len(left)} change(s) still need a tick." + "\n  " + "\n  ".join(left))
    out = _approval_path(root, edition)
    out.write_text(json.dumps({"edition": edition, "approved_by": by.strip(),
                               "approved_on": date.today().isoformat(),
                               "register_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}, indent=1),
                   encoding="utf-8")
    return out
