"""claude.ai account sync on disk: ~/.claude/skills/synced/<org-id>_<account-id>/ (spec § 2)."""
from __future__ import annotations

import json
from pathlib import Path

from .paths import Env


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
