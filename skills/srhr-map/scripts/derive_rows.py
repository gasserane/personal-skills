"""Turn checked drop-in files into proposed register rows (SRHR map skill, phase c, refresh step 3).

Folder layout under the map root (the organisation's storage, never this public repository):
  drop_in/<reporting year>/   dhis2/dataValueSets.csv, subgranting/<grant ledger>.xlsx,
                              business_plans/business_plan_focus_*.csv (a file directly in the year
                              folder is found too; the subfolder wins when both hold one)
  intelligence_tool/          track_b_proposed_<date>.csv (latest by name), master_countries.csv,
                              source_register.csv (optional, for links)
  config/                     streams.csv, ma_codes.csv (see config_tables.py)

DHIS2 and the Intelligence Tool snapshot are read at the reporting year; the grant ledger and the
business-plan coding sheet at the edition year (reporting year + 1 by default), because the register
holds funding and plan focus for the year the map is published.

Every proposed row has the register columns plus private keys (starting "_") that later steps use
and the register writer drops: _link (where a person can check the value), _second_reader.
"""
import csv
import re
from datetime import date
from pathlib import Path

import config_tables
import dropin_check as dc

FIELDS = ["iso3", "ma_code", "member_status", "topic", "indicator_id", "value", "value_display", "unit",
          "reference_year", "source_id", "date_read", "machine_check", "ticked_by", "tick_date", "snapshot_tag"]
CONTRACTS = Path(__file__).resolve().parent.parent / "contracts"
HIV_LABEL = "HIV and AIDS"
NOT_ON_MAP = "not on map"
TOPIC_OF = {"ippf_hiv_services": "HIV", "ippf_bp_hiv_focus": "HIV", "ippf_funding_streams": "funding",
            "ippf_grant_streams_count": "funding", "ippf_funding_streams_partner": "funding"}


class RefreshStop(Exception):
    """Refresh cannot go on; the message tells a colleague what to do."""


def _row(**kw):
    r = {f: "" for f in FIELDS}
    r["date_read"] = date.today().isoformat()
    r.update(kw)
    return r


def _num(text):
    n = float(str(text).replace(",", "").strip() or 0)
    return int(n) if n == int(n) else n


# ---------------------------------------------------------------- DHIS2 services
def from_dhis2(path, year, codes):
    """HIV service counts per country from dataValueSets.csv. codes = {ma_code: iso3} (ticked only)."""
    path = Path(path)
    spec = next(f for f in dc.load_contract(CONTRACTS / "ippf_dhis2_annual.v1.json")["files"]
                if f["role"] == "services")
    _, rows, _ = dc._read(path, spec, year)
    total, seen_codes, problems, unknown = {}, {}, [], set()
    for _, r in rows:
        code = dc.ma_code(r.get("orgunit", ""))
        if code is None:
            continue  # dropin_check reports it
        if code not in codes:
            if code not in unknown:
                unknown.add(code)
                problems.append(f"unknown organisation code '{code}' ({r.get('orgunit', '').strip()}): no ticked "
                                f"row in config\\ma_codes.csv; its services are not counted")
            continue
        iso3 = codes[code]
        seen_codes.setdefault(iso3, set()).add(code)
        total.setdefault(iso3, 0)
        de = r.get("dataelement", "")
        if HIV_LABEL in de and de.startswith(("SRV-", "REF-")):
            total[iso3] += _num(r.get("value", ""))
    out = [_row(iso3=iso3, ma_code=";".join(sorted(seen_codes[iso3])), topic="HIV",
                indicator_id="ippf_hiv_services", value=str(n), value_display=f"{n:,}",
                reference_year=str(year), source_id="ippf_dhis2_service_stats", machine_check="pass",
                _link=str(path))
           for iso3, n in sorted(total.items())]
    return out, problems


# ---------------------------------------------------------------- grant ledger
def _norm(text):
    t = str(text or "").split("\n")[0].lower()
    t = re.sub(r"\([^)]*\)", " ", t)
    t = re.sub(r"\b(19|20)\d{2}\b", " ", t)
    return " ".join(re.sub(r"[^a-z0-9]+", " ", t).split())


def _matcher(streams):
    names = {}
    for s in streams:
        for n in [s["key"], s.get("label", "")] + (s.get("ledger_names") or "").split(";"):
            if _norm(n):
                names.setdefault(_norm(n), s)
    return lambda text: names.get(_norm(text))


def _country(countries, name):
    """The ledger may name the organisation after the country: 'Country (Org)'."""
    text = str(name or "").strip().lower()
    return countries.get(text) or countries.get(re.sub(r"\s*\([^)]*\)\s*$", "", text))


def from_ledger(path, edition, streams, countries):
    """Funding rows from the grant ledger. countries = {name, iso2 or iso3 lowercased: iso3}."""
    path = Path(path)
    contract = dc.load_contract(CONTRACTS / "ippf_subgranting.v1.json")
    spec = {f["role"]: f for f in contract["files"]}
    match, order = _matcher(streams), {s["key"]: i for i, s in enumerate(streams)}
    problems, said = [], set()

    def key_of(text):
        s = match(text)
        if s is None:
            shown = str(text).split("\n")[0].strip()
            if shown not in said:
                said.add(shown)
                problems.append(f"stream '{shown}' has no row in config\\streams.csv")
            return None
        return None if s["group"] == NOT_ON_MAP else s["key"]

    def iso_of(name, where):
        iso = _country(countries, name)
        if iso is None and str(name).strip().lower() not in ("", "n/a") and (name, where) not in said:
            said.add((name, where))
            problems.append(f"country '{str(name).strip()}' ({where}) has no row in master_countries.csv; not mapped")
        return iso

    # overview: which streams each country holds this edition year
    _, ov_rows, err = dc._read(path, spec["ledger_overview"], edition)
    if err:
        return [], [err]
    held_ov, lead_name = {}, {}
    for _, r in ov_rows:
        iso = iso_of(r.get("Country"), "overview sheet") if (r.get("Country") or "").strip() else None
        if iso is None:
            continue
        held = held_ov.setdefault(iso, set())
        for col, v in r.items():
            if re.search(rf"\b{edition}\b", col) and str(v).strip():
                k = key_of(col)
                if k:
                    held.add(k)
    # projects: one row per grant, Funding source written once per block
    _, pr_rows, err = dc._read(path, spec["ledger_projects"], edition)
    if err:
        return [], problems + [err]
    full, partners, source = {iso: set() for iso in held_ov}, [], ""
    for _, r in pr_rows:
        if (r.get("Funding source") or "").strip():
            source = r["Funding source"]
        if not (r.get("Country") or "").strip() or "cancel" in (r.get("grant status") or "").lower():
            continue
        if not source.strip():
            continue
        iso = iso_of(r["Country"], f"projects {edition}")
        k = key_of(source)
        if iso is None or k is None:
            continue
        full.setdefault(iso, set()).add(k)
        lead_name[iso] = r["Country"].strip()
        cell = (r.get("other countries") or "").strip()
        for p in ([] if cell.lower() in ("", "n/a") else re.split(r"[,;]| and ", cell)):
            if p.strip():
                piso = iso_of(p, f"partner of {r['Country'].strip()}")
                if piso:
                    partners.append((piso, k, lead_name[iso]))
    link = f"{path}#'projects {edition}'"
    out = []
    for iso in sorted(full):
        keys = sorted(full[iso])
        out.append(_row(iso3=iso, topic="funding", indicator_id="ippf_funding_streams", value=str(len(keys)),
                        value_display=", ".join(keys) or "none", reference_year=str(edition),
                        source_id="ippf_grant_overview", machine_check="pass", _link=link))
    for iso in sorted(held_ov):
        keys = sorted(held_ov[iso], key=order.get)
        labels = [next(s["label"] for s in streams if s["key"] == k) for k in keys]
        out.append(_row(iso3=iso, topic="funding", indicator_id="ippf_grant_streams_count", value=str(len(keys)),
                        value_display=f"{len(keys)} ({', '.join(labels) or 'none'})", reference_year=str(edition),
                        source_id="ippf_grant_overview", machine_check="pass",
                        _link=f"{path}#'Grant and project overview'"))
    done = set()
    for piso, k, lead in partners:
        if k in full.get(piso, set()) or (piso, k) in done:
            continue
        done.add((piso, k))
        out.append(_row(iso3=piso, topic="funding", indicator_id="ippf_funding_streams_partner", value=k,
                        value_display=f"{k} with {lead}", reference_year=str(edition),
                        source_id="ippf_grant_overview", machine_check="pass", _link=link))
    return out, problems


# ---------------------------------------------------------------- business-plan coding sheet
def from_coding_sheet(path, edition):
    path = Path(path)
    out = []
    with open(path, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            if not (r.get("iso3") or "").strip():
                continue
            second = (r.get("second_reader") or "").strip()
            check = f"plan page {(r.get('plan_page') or '').strip() or 'not cited'}; reader {r['reader'].strip()}"
            if second:
                check += f", second {second}"
            out.append(_row(iso3=r["iso3"].strip(), ma_code=(r.get("ma_code") or "").strip(), topic="HIV",
                            indicator_id="ippf_bp_hiv_focus", value=r["focus"].strip(),
                            value_display=r["focus"].strip(), reference_year=r["plan_year"].strip(),
                            source_id="ippf_business_plan_focus", machine_check=check,
                            _second_reader=second, _link=str(path)))
    return out


# ---------------------------------------------------------------- Intelligence Tool snapshot
def from_snapshot(path, reporting_year):
    """Public-context rows the Intelligence Tool owner ticked and its machine check passed."""
    path = Path(path)
    m = re.search(r"(\d{4})-\d{2}-\d{2}", path.stem)
    if not m:
        raise RefreshStop(f"{path.name}: the snapshot file name carries no date; ask the Intelligence Tool owner.")
    tag = f"Snapshot {m.group(0)}"
    if int(m.group(1)) < int(reporting_year):
        raise RefreshStop(f"freshness result {tag} is older than reporting year {reporting_year}; "
                          "ask the Intelligence Tool owner for a new run")
    out = []
    with open(path, encoding="utf-8-sig", newline="") as f:
        for s in csv.DictReader(f):
            if not (s.get("ba_tick") or "").strip() or s.get("machine_check") != "pass":
                continue
            out.append(_row(iso3=s["iso3"], indicator_id=s["indicator_id"], value=s["value"],
                            value_display=s["value_display"], reference_year=s["year"],
                            date_read=s["retrieved_on"], machine_check="pass", ticked_by="snapshot ba_tick",
                            tick_date=s["retrieved_on"], snapshot_tag=tag, _link=str(path)))
    return out


# ---------------------------------------------------------------- derive
def _one(folder, pattern):
    hits = sorted(Path(folder).glob(pattern))
    return hits[-1] if hits else None


SUBFOLDER = {"ippf_dhis2_annual.v1.json": "dhis2", "ippf_subgranting.v1.json": "subgranting",
             "ippf_business_plan_focus.v1.json": "business_plans"}


def find_dropin(drop, contract_file, pattern):
    """The newest file matching pattern in drop/<role subfolder>/, else directly in drop/."""
    return _one(Path(drop) / SUBFOLDER[contract_file], pattern) or _one(drop, pattern)


def _countries(path):
    out = {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            for k in ("country", "iso2", "iso3"):
                if (r.get(k) or "").strip():
                    out[r[k].strip().lower()] = r["iso3"].strip()
    return out


def derive(map_root, year, topic, baseline, edition=None):
    """Return (proposed rows, problems, covered). covered = {indicator_id: {"year", "link"}}.

    topic = "HIV", "funding" or None (all). baseline = the previous register edition's rows.
    """
    root, year = Path(map_root), int(year)
    edition = int(edition or year + 1)
    drop, it = root / "drop_in" / str(year), root / "intelligence_tool"
    streams, codes = config_tables.load_config(root)
    rows, problems, covered = [], [], {}

    def want(ind):
        return topic is None or TOPIC_OF.get(ind) == topic

    def checked(contract_file, role, pattern, yr):
        c = dc.load_contract(CONTRACTS / contract_file)
        p = find_dropin(drop, contract_file, pattern)
        if p is None:
            problems.append(f"no file matching '{pattern}' in drop_in\\{year}\\{SUBFOLDER[contract_file]}; "
                            f"{role} not refreshed")
            return None
        bad = dc.check_file(c, role, p, yr)
        problems.extend(bad)
        return None if bad else p

    def cover(new, ind, yr):
        rows.extend(new)
        covered[ind] = {"year": str(yr), "link": new[0]["_link"] if new else ""}

    if want("ippf_hiv_services"):
        p = checked("ippf_dhis2_annual.v1.json", "services", "dataValueSets.csv", year)
        if p:
            new, pr = from_dhis2(p, year, codes)
            problems.extend(pr)
            cover(new, "ippf_hiv_services", year)
    if want("ippf_funding_streams"):
        p = checked("ippf_subgranting.v1.json", "ledger_projects", "*.xlsx", edition)
        mc = it / "master_countries.csv"
        if p and not mc.exists():
            problems.append("intelligence_tool\\master_countries.csv is missing; funding not refreshed")
        elif p and not dc.check_file(dc.load_contract(CONTRACTS / "ippf_subgranting.v1.json"),
                                     "ledger_overview", p, edition):
            new, pr = from_ledger(p, edition, streams, _countries(mc))
            problems.extend(pr)
            for ind in ("ippf_funding_streams", "ippf_grant_streams_count", "ippf_funding_streams_partner"):
                cover([r for r in new if r["indicator_id"] == ind], ind, edition)
    if want("ippf_bp_hiv_focus"):
        p = checked("ippf_business_plan_focus.v1.json", "coding_sheet", "business_plan_focus_*.csv", edition)
        if p:
            cover(from_coding_sheet(p, edition), "ippf_bp_hiv_focus", edition)
    public = {b["indicator_id"] for b in baseline
              if not b.get("source_id", "").startswith("ippf_") and (topic is None or b.get("topic") == topic)}
    if public:
        snap = _one(it, "track_b_proposed_*.csv")
        if snap is None:
            problems.append("no Intelligence Tool snapshot (track_b_proposed_*.csv) in intelligence_tool; "
                            "public context not refreshed")
        else:
            latest = {}
            for b in baseline:
                if b["indicator_id"] in public:
                    latest[b["indicator_id"]] = max(latest.get(b["indicator_id"], 0), int(b["reference_year"]))
            years = {(b["indicator_id"], b["reference_year"]) for b in baseline if b["indicator_id"] in public}
            new = [s for s in from_snapshot(snap, year) if s["indicator_id"] in public
                   and ((s["indicator_id"], s["reference_year"]) in years
                        or int(s["reference_year"]) > latest[s["indicator_id"]])]
            src = {b["indicator_id"]: b["source_id"] for b in baseline if b["indicator_id"] in public}
            for s in new:
                s["source_id"] = src[s["indicator_id"]]
            for ind in sorted(public):
                mine = [s for s in new if s["indicator_id"] == ind]
                if mine:
                    cover(mine, ind, max(s["reference_year"] for s in mine))
    # fill what the source files do not hold, from the baseline and the ticked code table
    status, unit, topic_of = {}, {}, {}
    for b in baseline:
        if b.get("member_status"):
            status[b["iso3"]] = b["member_status"]
        if b.get("unit"):
            unit.setdefault(b["indicator_id"], b["unit"])
        topic_of.setdefault(b["indicator_id"], b.get("topic", ""))
    by_iso = {}
    for code, iso in codes.items():
        by_iso.setdefault(iso, []).append(code)
    for r in rows:
        r["member_status"] = r["member_status"] or status.get(r["iso3"], "")
        r["unit"] = r["unit"] or unit.get(r["indicator_id"], "")
        r["topic"] = r["topic"] or topic_of.get(r["indicator_id"], "")
        r["ma_code"] = r["ma_code"] or ";".join(sorted(by_iso.get(r["iso3"], [])))
    return rows, problems, covered
