"""claude.ai account sync on disk: ~/.claude/skills/synced/<org-id>_<account-id>/ (spec § 2)."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .gitops import last_publish
from .paths import PORTABLE_FOLDERS, Env, all_skill_dirs, resolve


def active_account_dir(env: Env) -> Path | None:
    """The synced folder of the account Claude Code is signed in to (~/.claude.json oauthAccount).

    Other folders under synced/ belong to accounts used earlier. Claude Code does not
    load them: on 2026-10-08 the session listed the active account's mel-discipline-2
    and not the old account's mel-discipline.
    """
    try:
        data = json.loads(env.claude_json.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    acct = data.get("oauthAccount") or {}
    org, user = acct.get("organizationUuid"), acct.get("accountUuid")
    if not org or not user:
        return None
    d = env.synced_root / f"{org}_{user}"
    return d if d.is_dir() else None


def account_dirs(env: Env) -> list[Path]:
    if not env.synced_root.is_dir():
        return []
    return sorted(p for p in env.synced_root.iterdir() if p.is_dir())


def _scan(root: Path) -> list[Path]:
    return sorted(p.parent for p in root.glob("*/SKILL.md")) if root.is_dir() else []


def visible_skill_dirs(env: Env, all_accounts: bool = False) -> list[tuple[str, Path]]:
    """(location, folder) for every skill Claude Code can list: local, project, account."""
    out = [("local", d) for d in _scan(env.claude_skills)]
    out += [("project", d) for d in _scan(env.work_folder / ".claude" / "skills")]
    active = active_account_dir(env)
    for acct in account_dirs(env):
        if all_accounts or acct == active:
            label = f"account:{acct.name[:8]}" + ("" if acct == active else " (inactive)")
            out += [(label, d) for d in _scan(acct)]
    return out


VARIANT_RE = re.compile(r"^(?P<base>.+)-(?P<n>\d+)$")
NAME_LINE_RE = re.compile(r"^name:[ \t]*[\"']?([a-z0-9-]+)[\"']?[ \t]*$", re.M)


def read_manifest(account_dir: Path) -> dict[str, str]:
    try:
        data = json.loads((account_dir / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return {s.get("name", ""): s.get("updatedAt", "") for s in data.get("skills", [])}


def normalise(text: str) -> str:
    """Ignore line endings, trailing newlines, and claude.ai quoting the name line."""
    text = text.replace("\r\n", "\n").rstrip("\n")
    return NAME_LINE_RE.sub(lambda m: f"name: {m.group(1)}", text, count=1)


@dataclass
class VerifyRow:
    account: str
    active: bool
    status: str
    variants: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        extra = f"  duplicate variants: {', '.join(self.variants)}" if self.variants else ""
        return f"{self.account} ({'active' if self.active else 'inactive'}): {self.status}{extra}"


def _parse_time(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def verify_account(source_text: str, name: str, acct: Path, active: bool,
                   published_at: datetime | None) -> VerifyRow:
    variants = sorted(p.name for p in acct.glob(f"{name}-*")
                      if (m := VARIANT_RE.match(p.name)) and m["base"] == name)
    copy = acct / name / "SKILL.md"
    if not copy.is_file():
        return VerifyRow(acct.name[:8], active, "missing", variants)
    if normalise(copy.read_text(encoding="utf-8")) == normalise(source_text):
        return VerifyRow(acct.name[:8], active, "match", variants)
    synced_at = _parse_time(read_manifest(acct).get(name, ""))
    if published_at and synced_at and synced_at < published_at:
        return VerifyRow(acct.name[:8], active, "not-synced-yet", variants)
    return VerifyRow(acct.name[:8], active, "mismatch", variants)


def verify(env: Env, name: str, all_accounts: bool = False) -> list[VerifyRow]:
    source = (resolve(env, name) / "SKILL.md").read_text(encoding="utf-8")
    published = last_publish(env, name)
    published_at = published[1] if published else None
    active = active_account_dir(env)
    return [verify_account(source, name, acct, acct == active, published_at)
            for acct in account_dirs(env) if all_accounts or acct == active]


def _same_skill_text(a: Path, b: Path) -> bool:
    try:
        return (normalise((a / "SKILL.md").read_text(encoding="utf-8"))
                == normalise((b / "SKILL.md").read_text(encoding="utf-8")))
    except OSError:
        return False


def dupes(env: Env, all_accounts: bool = False) -> list[str]:
    """Names Claude Code would list twice, including <name> against claude.ai's <name>-2."""
    found: dict[str, list[tuple[str, Path]]] = {}
    for where, d in visible_skill_dirs(env, all_accounts):
        found.setdefault(d.name, []).append((where, d))
    seen: dict[str, list[str]] = {}
    differs: set[str] = set()
    for n, entries in found.items():
        where = [w for w, _ in entries]
        if "local" in where and "project" in where:
            local = next(d for w, d in entries if w == "local")
            project = next(d for w, d in entries if w == "project")
            if _same_skill_text(local, project):
                entries = [e for e in entries if e[0] != "project"]  # a mirror, not a second skill
            else:
                differs.add(n)
        seen[n] = [w for w, _ in entries]
    lines = []
    for n, w in sorted(seen.items()):
        if len(w) > 1:
            lines.append(f"{n}: {', '.join(w)}" + (" (project copy differs)" if n in differs else ""))
    for n in sorted(seen):
        m = VARIANT_RE.match(n)
        if m and m["base"] in seen:
            lines.append(f"{n} next to {m['base']}: claude.ai renamed a same-name upload")
    return lines


def freshness_message(env: Env, now: datetime | None = None) -> str | None:
    """SessionStart warning when an org/ or account/ source differs from its synced copy."""
    names = [d.name for d in all_skill_dirs(env, PORTABLE_FOLDERS)]
    if not names:
        return None
    if active_account_dir(env) is None:
        return ("⚠️ Upload-freshness check: no synced folder for the signed-in claude.ai account "
                "under ~/.claude/skills/synced, so org/ and account/ skills cannot be checked.")
    now = now or datetime.now(timezone.utc)
    stale = []
    for n in names:
        row = verify(env, n)[0]
        if row.status == "match":
            continue
        published = last_publish(env, n)
        if published and now - published[1] < timedelta(hours=1):
            continue  # account sync runs about every 10 minutes (fact 2)
        stale.append(f"{n} ({row.status})")
    if not stale:
        return None
    return ("⚠️ claude.ai copies differ from personal-skills: " + ", ".join(stale)
            + ". Upload dist/<name>.zip (delete the old copy first), then run: python tools/publish.py verify <name>")
