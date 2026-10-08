#!/usr/bin/env python3
"""Release pipeline for gasserane/personal-skills (skills-distribution spec § 3.3).

Commands: check, draft, compare, publish, verify, dupes, classify.
It never uploads: claude.ai upload stays a manual step, because no API exists.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from skillpub import lint, release, synced  # noqa: E402
from skillpub.paths import PORTABLE_FOLDERS, Env, PublishError, all_skill_dirs  # noqa: E402


def _cmd_check(env: Env, a) -> int:
    if not a.all and not a.name:
        raise PublishError("give a skill name or --all")
    names = [d.name for d in all_skill_dirs(env)] if a.all else [a.name]
    forbidden = lint.load_forbidden(env)
    blocked = False
    for n in dict.fromkeys(names):
        findings = lint.check_skill(env, n, forbidden)
        for f in findings:
            print(f"{n}: {f}")
        blocked = blocked or any(f.blocking for f in findings)
    print("check: FAIL" if blocked else "check: PASS")
    return 1 if blocked else 0


def _cmd_draft(env: Env, a) -> int:
    dest, zip_path = release.draft(env, a.name)
    print(f"Installed {dest}. Call /{a.name}-draft by name. Chat test zip: {zip_path}")
    return 0


def _cmd_compare(env: Env, a) -> int:
    run = release.compare(env, a.name, before=a.before)
    extra = " and colleague.md" if (run / "colleague.md").exists() else ""
    print(f"Blind outputs in {run}. Read A.md and B.md, fill in verdict.md{extra}, then run publish.")
    return 0


def _cmd_publish(env: Env, a) -> int:
    print(release.publish(env, a.name, a.what, a.why, trivial=a.trivial, push=not a.no_push))
    return 0


def _cmd_verify(env: Env, a) -> int:
    if a.hook:
        try:
            msg = synced.freshness_message(env)
        except Exception as exc:  # a hook must report, never crash
            msg = f"⚠️ Upload-freshness check failed: {exc}"
        if msg:
            print(json.dumps({"systemMessage": msg}))
        return 0
    if a.all:
        names = [d.name for d in all_skill_dirs(env, PORTABLE_FOLDERS)]
    elif a.name:
        names = [a.name]
    else:
        raise PublishError("give a skill name or --all")
    if synced.active_account_dir(env) is None and not a.all_accounts:
        raise PublishError("no synced folder for the signed-in claude.ai account under ~/.claude/skills/synced")
    bad = False
    for n in names:
        rows = synced.verify(env, n, all_accounts=a.all_accounts)
        for row in rows:
            print(f"{n}: {row}")
        bad = bad or any(r.active and r.status != "match" for r in rows)
    return 1 if bad else 0


def _cmd_dupes(env: Env, a) -> int:
    lines = synced.dupes(env, all_accounts=a.all_accounts)
    print("\n".join(lines) if lines else "dupes: none")
    return 1 if lines else 0


def _cmd_classify(env: Env, a) -> int:
    print(lint.format_classify(lint.classify(env)))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="publish.py", description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="portability lint")
    c.add_argument("name", nargs="?")
    c.add_argument("--all", action="store_true")
    c.set_defaults(fn=_cmd_check)
    c = sub.add_parser("draft", help="install <name>-draft and build its chat-test zip")
    c.add_argument("name")
    c.set_defaults(fn=_cmd_draft)
    c = sub.add_parser("compare", help="blind before/after run on evals/<name>/prompt.md")
    c.add_argument("name")
    c.add_argument("--before", help="revision to compare against (default: last publish, else HEAD)")
    c.set_defaults(fn=_cmd_compare)
    c = sub.add_parser("publish", help="gated release: CHANGELOG, zip, commit and push")
    c.add_argument("name")
    c.add_argument("--what", required=True)
    c.add_argument("--why", required=True)
    c.add_argument("--trivial", action="store_true", help="skip compare (refused for org/)")
    c.add_argument("--no-push", action="store_true")
    c.set_defaults(fn=_cmd_publish)
    c = sub.add_parser("verify", help="compare sources with synced claude.ai copies")
    c.add_argument("name", nargs="?")
    c.add_argument("--all", action="store_true")
    c.add_argument("--all-accounts", action="store_true")
    c.add_argument("--hook", action="store_true", help="SessionStart mode: systemMessage JSON or nothing")
    c.set_defaults(fn=_cmd_verify)
    c = sub.add_parser("dupes", help="names Claude Code would list twice")
    c.add_argument("--all-accounts", action="store_true")
    c.set_defaults(fn=_cmd_dupes)
    c = sub.add_parser("classify", help="tier-rule table for every skill in skills/")
    c.set_defaults(fn=_cmd_classify)
    return p


def main(argv: list[str] | None = None, env: Env | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:
        pass
    a = build_parser().parse_args(argv)
    env = env or Env.default()
    try:
        return a.fn(env, a)
    except PublishError as exc:
        print(f"publish.py: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
