"""Read the two config tables the refresh mode needs (SRHR map skill, phase c).

Both live in the organisation's storage under <map root>/config/, never in this public repository:
  streams.csv   key,label,group,colour      the stream crosswalk (ledger key -> legend label)
  ma_codes.csv  ma_code,iso3,org_name,ticked_by,tick_date
                only rows a person ticked are used to join a DHIS2 organisation code to a country.
"""
import csv
from pathlib import Path


class ConfigError(Exception):
    """A config table is missing or inconsistent; the message is written for a colleague."""


def _read(path: Path, columns: list) -> list:
    if not path.exists():
        raise ConfigError(f"The config file {path.name} is missing from the config folder ({path.parent}). "
                          "Ask the map owner to add it.")
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if rows and any(c not in rows[0] for c in columns):
        raise ConfigError(f"{path.name} lacks one of the columns {columns}.")
    return rows


def load_config(map_root: Path):
    """Return (streams in legend order, {ma_code: iso3} for ticked rows only)."""
    cfg = Path(map_root) / "config"
    streams = _read(cfg / "streams.csv", ["key", "label", "group", "colour"])
    seen = set()
    for s in streams:
        if s["key"] in seen:
            raise ConfigError(f"streams.csv lists the stream key '{s['key']}' twice.")
        seen.add(s["key"])
    codes, all_codes = {}, set()
    for r in _read(cfg / "ma_codes.csv", ["ma_code", "iso3", "org_name", "ticked_by", "tick_date"]):
        code = r["ma_code"].strip()
        if code in all_codes:
            raise ConfigError(f"ma_codes.csv lists the organisation code '{code}' twice.")
        all_codes.add(code)
        if not r["ticked_by"].strip():
            continue
        if not r["iso3"].strip():
            raise ConfigError(f"ma_codes.csv: code '{code}' is ticked but has no country (iso3).")
        codes[code] = r["iso3"].strip()
    return streams, codes
