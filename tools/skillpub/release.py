"""draft, compare and publish (spec § 3.3 to § 3.5)."""
from __future__ import annotations

import hashlib
import json
import random
import re
import shutil
import subprocess
import zipfile
from datetime import date
from pathlib import Path
from typing import Callable

from .frontmatter import parse, set_field
from .gitops import commit_and_push, files_at, git, last_publish
from .lint import check_skill
from .paths import PORTABLE_FOLDERS, Env, PublishError, resolve, tier_of

SKIP_PARTS = {"__pycache__", ".DS_Store"}


def read_dir(skill_dir: Path) -> dict[str, bytes]:
    return {
        p.relative_to(skill_dir).as_posix(): p.read_bytes()
        for p in sorted(skill_dir.rglob("*"))
        if p.is_file() and not SKIP_PARTS & set(p.relative_to(skill_dir).parts)
    }


def tree_hash(files: dict[str, bytes]) -> str:
    """Content hash of a skill tree. Text files (no NUL byte, git's own heuristic) hash with
    CRLF read as LF, so a core.autocrlf checkout equals its committed blobs; binaries hash raw."""
    h = hashlib.sha256()
    for rel in sorted(files):
        data = files[rel]
        if b"\0" not in data:
            data = data.replace(b"\r\n", b"\n")
        h.update(rel.encode("utf-8") + b"\0" + data + b"\0")
    return h.hexdigest()


def install_variant(env: Env, files: dict[str, bytes], variant: str) -> Path:
    """Install files at ~/.claude/skills/<variant>/ as a user-invoked-only skill named <variant>.

    disable-model-invocation keeps the copy from firing on its own and competing with
    the live skill for the same trigger phrases (spec § 3.3).
    """
    dest = env.claude_skills / variant
    if dest.exists():
        shutil.rmtree(dest)
    for rel, data in files.items():
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    skill_md = dest / "SKILL.md"
    text = skill_md.read_bytes().decode("utf-8")
    text = set_field(set_field(text, "name", variant), "disable-model-invocation", "true")
    skill_md.write_bytes(text.encode("utf-8"))
    return dest


def build_zip(skill_dir: Path, dist: Path, zip_name: str) -> Path:
    """dist/<zip_name>.zip with <zip_name>/SKILL.md at the root (claude.ai upload format)."""
    name = parse((skill_dir / "SKILL.md").read_text(encoding="utf-8")).get("name")
    if name != zip_name:
        raise PublishError(f"zip folder '{zip_name}' must equal the skill name '{name}'")
    dist.mkdir(parents=True, exist_ok=True)
    out = dist / f"{zip_name}.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel, data in read_dir(skill_dir).items():
            zf.writestr(f"{zip_name}/{rel}", data)
    return out


def draft(env: Env, name: str) -> tuple[Path, Path]:
    src = resolve(env, name)
    dest = install_variant(env, read_dir(src), f"{name}-draft")
    return dest, build_zip(dest, env.dist, f"{name}-draft")


CANARY = "PUBLISH-CANARY-7Q4"
Runner = Callable[[Env, str], str]

VERDICT_TEMPLATE = (
    "# Read A.md and B.md before you open key.json.\n"
    "# preferred: A, B or same. reason: one line.\n"
    "preferred: \n"
    "reason: \n"
)
COLLEAGUE_TEMPLATE = (
    "# Colleague-condition test (spec section 4). Upload dist/{name}-draft.zip to claude.ai,\n"
    "# run evals/{name}/prompt.md in plain chat (no wiki, no /ann), then delete the draft upload.\n"
    "# colleague-condition: pass or fail. note: one line.\n"
    "colleague-condition: \n"
    "note: \n"
)


def run_claude(env: Env, prompt: str) -> str:
    """One headless run in the work folder with read-only tools, so the wiki is reachable (Ane's condition)."""
    exe = shutil.which("claude") or "claude"
    r = subprocess.run([exe, "-p", prompt, "--allowedTools", "Read,Grep,Glob"],
                       cwd=env.work_folder, capture_output=True, text=True, encoding="utf-8", timeout=1800)
    if r.returncode != 0:
        raise PublishError(f"claude -p failed ({r.returncode}): {r.stderr.strip()[-400:]}")
    return r.stdout


def canary(env: Env, runner: Runner) -> None:
    """Prove that headless slash invocation loads a skill before paying for two real runs."""
    files = {"SKILL.md": ("---\nname: publish-canary\n"
                          "description: Test fixture for publish.py compare. Never use it.\n---\n\n"
                          f"Reply with exactly this token and nothing else: {CANARY}\n").encode("utf-8")}
    dest = install_variant(env, files, "publish-canary")
    try:
        out = runner(env, "/publish-canary")
    finally:
        shutil.rmtree(dest, ignore_errors=True)
    if CANARY not in out:
        raise PublishError("canary failed: claude -p did not load a skill by its slash name, "
                           "so a compare would measure nothing")


def _before_files(env: Env, name: str, before: str | None) -> tuple[dict[str, bytes] | None, str]:
    if before:
        files = files_at(env, before, name)
        if files is None:
            raise PublishError(f"no '{name}' at revision {before}")
        return files, before
    published = last_publish(env, name)
    if published:
        rev = published[0]
    else:
        try:
            rev = git(env, "rev-parse", "HEAD").strip()
        except PublishError:  # a repo with no commits has nothing to compare against
            return None, "none"
    return files_at(env, rev, name), rev


def _new_run_dir(env: Env, name: str, day: date) -> Path:
    base = env.repo / "evals" / name / "runs"
    run, n = base / day.isoformat(), 2
    while run.exists():
        run, n = base / f"{day.isoformat()}-{n}", n + 1
    run.mkdir(parents=True)
    return run


def compare(env: Env, name: str, runner: Runner | None = None, day: date | None = None,
            rng: random.Random | None = None, before: str | None = None) -> Path:
    """Blind before/after run on the fixed prompt (spec § 3.5). Returns the run folder."""
    runner = runner or run_claude
    day = day or date.today()
    rng = rng or random.Random()
    src = resolve(env, name)
    prompt_file = env.repo / "evals" / name / "prompt.md"
    if not prompt_file.is_file():
        raise PublishError(f"write evals/{name}/prompt.md first: one realistic task, "
                           "never tuned to a version (spec 3.5)")
    prompt = prompt_file.read_text(encoding="utf-8").strip()
    draft_files = read_dir(src)
    before_files, before_rev = _before_files(env, name, before)
    if before_files is not None and tree_hash(before_files) == tree_hash(draft_files):
        raise PublishError(f"the draft equals {before_rev}; nothing to compare "
                           "(edit first, and commit nothing between the edit and publish)")
    canary(env, runner)
    install_variant(env, draft_files, f"{name}-draft")
    if before_files is None:
        before_rev = "none (bare model, first version)"
        out_before = runner(env, prompt)
    else:
        install_variant(env, before_files, f"{name}-before")
        out_before = runner(env, f"/{name}-before {prompt}")
    out_draft = runner(env, f"/{name}-draft {prompt}")
    run = _new_run_dir(env, name, day)
    draft_letter = rng.choice("AB")
    before_letter = "B" if draft_letter == "A" else "A"
    (run / f"{draft_letter}.md").write_text(out_draft, encoding="utf-8")
    (run / f"{before_letter}.md").write_text(out_before, encoding="utf-8")
    (run / "key.json").write_text(json.dumps({
        "draft": draft_letter, "before": before_letter, "before_rev": before_rev,
        "draft_sha256": tree_hash(draft_files)}, indent=2), encoding="utf-8")
    (run / "verdict.md").write_text(VERDICT_TEMPLATE, encoding="utf-8")
    if tier_of(src) == "org":
        (run / "colleague.md").write_text(COLLEAGUE_TEMPLATE.format(name=name), encoding="utf-8")
    return run


def latest_run(env: Env, name: str) -> Path | None:
    base = env.repo / "evals" / name / "runs"

    def order(p: Path) -> tuple[str, int]:
        m = re.match(r"^(\d{4}-\d{2}-\d{2})(?:-(\d+))?$", p.name)
        return (m.group(1), int(m.group(2) or 1)) if m else ("", 0)

    runs = [p for p in base.iterdir() if p.is_dir() and order(p)[0]] if base.is_dir() else []
    return max(runs, key=order) if runs else None


def read_verdict(run: Path) -> tuple[str, str]:
    """Map Ane's blind letter to better, same or worse through key.json (plan decision D)."""
    key = json.loads((run / "key.json").read_text(encoding="utf-8"))
    text = (run / "verdict.md").read_text(encoding="utf-8") if (run / "verdict.md").is_file() else ""
    m = re.search(r"^preferred:[ \t]*(A|B|same)[ \t]*$", text, re.M | re.I)
    if not m:
        raise PublishError(f"{run.name}/verdict.md is not filled in: "
                           "write 'preferred: A', 'preferred: B' or 'preferred: same'")
    reason = re.search(r"^reason:[ \t]*(\S.*)$", text, re.M)
    if not reason:
        raise PublishError(f"{run.name}/verdict.md needs one line of reasons after 'reason:'")
    choice = m.group(1)
    if choice.lower() == "same":
        return "same", reason.group(1).strip()
    return ("better" if choice.upper() == key["draft"] else "worse"), reason.group(1).strip()


def read_colleague(run: Path) -> str:
    text = (run / "colleague.md").read_text(encoding="utf-8") if (run / "colleague.md").is_file() else ""
    m = re.search(r"^colleague-condition:[ \t]*(pass|fail)[ \t]*$", text, re.M | re.I)
    if not m:
        raise PublishError(f"{run.name}/colleague.md is not filled in: "
                           "the colleague-condition test is mandatory for org/")
    if m.group(1).lower() != "pass":
        raise PublishError("colleague-condition test failed: the release is blocked")
    note = re.search(r"^note:[ \t]*(\S.*)$", text, re.M)
    return note.group(1).strip() if note else ""


def changelog_add(env: Env, day: date, name: str, what: str, why: str, verdict_line: str) -> None:
    path = env.repo / "CHANGELOG.md"
    text = path.read_text(encoding="utf-8", newline="")
    nl = "\r\n" if "\r\n" in text else "\n"
    entry = (f"## [{day.isoformat()}] — publish: {name}\n\n**Skills affected:** {name}\n\n### {name}\n"
             f"- **What changed:** {what}\n- **Why:** {why}\n- **Before/after verdict:** {verdict_line}\n\n"
             ).replace("\n", nl)
    if entry in text:
        return
    idx = text.find(nl + "## [")
    text = text + nl + entry if idx < 0 else text[: idx + len(nl)] + entry + text[idx + len(nl):]
    path.write_text(text, encoding="utf-8", newline="")


def publish(env: Env, name: str, what: str, why: str, trivial: bool = False,
            push: bool = True, day: date | None = None) -> str:
    day = day or date.today()
    if not what.strip() or not why.strip():
        raise PublishError("--what and --why are required: the CHANGELOG records both")
    src = resolve(env, name)
    tier = tier_of(src)
    blocking = [f for f in check_skill(env, name) if f.blocking and f.rule != "installed-locally"]
    if blocking:
        raise PublishError("check failed:\n" + "\n".join(str(f) for f in blocking))
    colleague = ""
    if tier not in PORTABLE_FOLDERS:
        verdict_line = "Tier B (Code-only): no compare"
    elif trivial:
        if tier == "org":
            raise PublishError("--trivial is refused for org/: the before/after verdict and the "
                               "colleague-condition test are mandatory for every org/ publish "
                               "(decisions file, Spec review)")
        verdict_line = "trivial, no compare"
    else:
        run = latest_run(env, name)
        if run is None:
            raise PublishError(f"run compare first: python tools/publish.py compare {name}")
        key = json.loads((run / "key.json").read_text(encoding="utf-8"))
        if key["draft_sha256"] != tree_hash(read_dir(src)):
            raise PublishError(f"{name} changed after the compare run {run.name}; run compare again")
        verdict, reason = read_verdict(run)
        if verdict == "worse":
            raise PublishError(f"verdict is 'worse' ({reason}): the release is blocked (decision 6)")
        if tier == "org":
            colleague = read_colleague(run)
        verdict_line = f"{verdict}: {reason} (run {run.name})"
    for variant in (f"{name}-draft", f"{name}-before"):
        shutil.rmtree(env.claude_skills / variant, ignore_errors=True)
    steps: list[str] = []
    if tier in PORTABLE_FOLDERS:
        zip_path = build_zip(src, env.dist, name)
        steps.append(f"claude.ai > Customize > Skills: delete the old '{name}' (open it, switch it off, "
                     f"... > Delete), then + > Create skill > Upload a skill > {zip_path}. "
                     "A shared skill is edited in place instead (spec 3.4 step 6).")
        if tier == "org":
            note = env.dist / f"{name}-review-note.md"
            note.write_text(f"# Review note: {name} ({day.isoformat()})\n\n- What changed: {what}\n"
                            f"- Why: {why}\n- Before/after verdict: {verdict_line}\n"
                            f"- Colleague-condition test: pass. {colleague}\n- Upload: {zip_path.name}\n",
                            encoding="utf-8")
            steps.append(f"Review note: {note}")
        if (env.claude_skills / name / "SKILL.md").is_file():
            steps.append("After the upload syncs and verify says match: "
                         f"npx skills remove {name} --global --agent claude-code -y")
        steps.append(f"Next session: python tools/publish.py verify {name}")
    else:
        steps.append("The SessionStart installer picks it up in the next session.")
    changelog_path = env.repo / "CHANGELOG.md"
    changelog_before = changelog_path.read_bytes()
    head_before = git(env, "rev-parse", "HEAD").strip()
    changelog_add(env, day, name, what, why, verdict_line)
    paths = [src.relative_to(env.repo).as_posix(), "CHANGELOG.md"]
    if (env.repo / "evals" / name).is_dir():
        paths.append(f"evals/{name}")
    try:
        sha = commit_and_push(env, paths, f"publish({name}): {what}", push=push)
    except PublishError:
        if git(env, "rev-parse", "HEAD").strip() == head_before:
            changelog_path.write_bytes(changelog_before)
        raise
    return f"Published {name} at {sha[:8]}.\n" + "\n".join(f"- {s}" for s in steps)
