"""Git calls for publish.py. Every call runs in the personal-skills clone."""
from __future__ import annotations

import subprocess
from datetime import datetime

from .paths import TIER_FOLDERS, Env, PublishError


def git(env: Env, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(env.repo), *args],
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        raise PublishError(f"git {' '.join(args)} failed: {r.stderr.strip()[-400:]}")
    return r.stdout


def last_publish(env: Env, name: str) -> tuple[str, datetime] | None:
    """The newest commit made by `publish` for this skill (subject `publish(<name>): ...`)."""
    out = git(env, "log", "-1", "--basic-regexp", "--format=%H %cI", f"--grep=^publish({name}):").strip()
    if not out:
        return None
    sha, stamp = out.split(" ", 1)
    return sha, datetime.fromisoformat(stamp)


def files_at(env: Env, rev: str, name: str) -> dict[str, bytes] | None:
    """The skill's files at a revision, from whichever tier folder held it then."""
    for tier in TIER_FOLDERS:
        paths = [p for p in git(env, "ls-tree", "-r", "--name-only", rev, "--", f"{tier}/{name}").split("\n") if p]
        if not paths:
            continue
        prefix = f"{tier}/{name}/"
        out: dict[str, bytes] = {}
        for p in paths:
            r = subprocess.run(["git", "-C", str(env.repo), "show", f"{rev}:{p}"], capture_output=True)
            if r.returncode != 0:
                raise PublishError(f"git show {rev}:{p} failed")
            out[p[len(prefix):]] = r.stdout
        return out
    return None


def commit_and_push(env: Env, paths: list[str], message: str, push: bool = True) -> str:
    """Add, commit and push in one process: OneDrive can revert a file between tool calls."""
    git(env, "add", "-A", "--", *paths)
    staged = [s for s in git(env, "diff", "--cached", "--name-only", "-z").split("\0") if s]
    if not staged:
        raise PublishError("nothing staged: OneDrive may have reverted the files; inspect them on disk, not the index")
    roots = [p.replace("\\", "/").rstrip("/") for p in paths]
    stray = [s for s in staged if not any(s == r or s.startswith(r + "/") for r in roots)]
    if stray:
        raise PublishError("files already staged outside this publish would be committed and pushed: "
                           + ", ".join(stray) + "; unstage them with `git restore --staged <file>` and run again")
    git(env, "commit", "-q", "-m", message)
    if push:
        git(env, "push", "-q")
    return git(env, "rev-parse", "HEAD").strip()
