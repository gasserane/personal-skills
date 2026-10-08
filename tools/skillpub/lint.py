"""Portability lint and the tier rule (spec § 3.2 tier rule, § 3.3 check)."""
from __future__ import annotations

import importlib.util
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from . import synced
from .frontmatter import parse
from .paths import PORTABLE_FOLDERS, Env, PublishError, all_skill_dirs, find_skill, tier_of

NAME_RE = re.compile(r"^[a-z0-9-]{1,64}$")
XML_RE = re.compile(r"<[^>\n]+>")
HARD_PATH_RE = re.compile(r"(?<![A-Za-z])[A-Za-z]:[/\\]|~/\.claude\b|\$\{[A-Z_]+_ROOT\}")
AGENT_RE = re.compile(
    r"\bsub-?agents?\b|\bAgent tool\b|\bTask tool\b|\bspawn\w*\s+(?:\w+\s+){0,3}agents?\b", re.I)
MCP_RE = re.compile(r"\bmcp__\w+|\bMCP server\b", re.I)
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"\+\d[\d\s().-]{7,}\d")
# Starting denylist (plan decision I): internal folder and file-name fragments that must
# never reach a public org/ or account/ skill. Extend it when a release finds a new one.
INTERNAL_TOKENS = ("agent-improvements/", "claude-ai-shareable-export", "5 JURNAL",
                   "OneDrive", "/handoffs/", ".local.")
HEADING_RE = re.compile(r"^(#{1,6})\s+\S")
IF_AVAILABLE_RE = re.compile(r"^#{1,6}\s+if available\b", re.I)
STOPWORDS = frozenset(
    "about also asks into like only such than that them then there these they this "
    "those used user uses when which with your from what skill skills".split())

Forbidden = tuple[list[tuple[str, str]], Callable[[str], bool]]


@dataclass(frozen=True)
class Finding:
    rule: str
    detail: str
    blocking: bool = True

    def __str__(self) -> str:
        return f"{'BLOCK' if self.blocking else 'WARN'} {self.rule}: {self.detail}"


def if_available_mask(lines: list[str]) -> list[bool]:
    """True for lines inside a section headed 'If available' (decision 6 wording)."""
    mask: list[bool] = []
    level: int | None = None
    for line in lines:
        m = HEADING_RE.match(line)
        if m:
            depth = len(m.group(1))
            if IF_AVAILABLE_RE.match(line):
                level = depth
                mask.append(True)
                continue
            if level is not None and depth <= level:
                level = None
        mask.append(level is not None)
    return mask


def load_forbidden(env: Env) -> Forbidden:
    path = env.work_folder / "ane_package" / "citation_rules.py"
    if not path.is_file():
        raise PublishError(f"forbidden-citation list not found at {path}; set WORK_FOLDER_ROOT")
    spec = importlib.util.spec_from_file_location("_citation_rules", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return list(mod.FORBIDDEN_PATTERNS), mod.line_has_hedge


def frontmatter_findings(skill_dir: Path) -> list[Finding]:
    try:
        data = parse((skill_dir / "SKILL.md").read_text(encoding="utf-8"))
    except PublishError as exc:
        return [Finding("frontmatter", str(exc))]
    out: list[Finding] = []
    name, desc = data.get("name"), data.get("description")
    if not isinstance(name, str) or not NAME_RE.match(name):
        out.append(Finding("name-format", f"name {name!r}: 1-64 lowercase letters, numbers, hyphens"))
    elif "anthropic" in name or "claude" in name:
        out.append(Finding("name-reserved", f"name {name!r} contains 'anthropic' or 'claude'"))
    if isinstance(name, str) and name != skill_dir.name:
        out.append(Finding("folder-name", f"folder '{skill_dir.name}' differs from name '{name}'; upload fails"))
    if not isinstance(desc, str) or not desc.strip():
        out.append(Finding("description-empty", "description is missing or empty"))
    elif len(desc) > 1024:
        out.append(Finding("description-length", f"description has {len(desc)} characters; the limit is 1,024"))
    for key, val in (("name", name), ("description", desc)):
        if isinstance(val, str) and XML_RE.search(val):
            out.append(Finding("xml-tag", f"{key} contains {XML_RE.search(val).group(0)!r}"))
    return out


def portability_findings(env: Env, skill_dir: Path, forbidden: Forbidden | None = None) -> list[Finding]:
    """Rules for org/ and account/ skills: they must run in plain claude.ai chat."""
    patterns, hedged = forbidden if forbidden is not None else load_forbidden(env)
    out: list[Finding] = []
    if (skill_dir / "scripts").is_dir():
        out.append(Finding("scripts-folder", "ships a scripts/ folder; chat cannot run bundled scripts"))
    for md in sorted(skill_dir.rglob("*.md")):
        rel = md.relative_to(skill_dir).as_posix()
        lines = md.read_text(encoding="utf-8").splitlines()
        for i, (line, inside) in enumerate(zip(lines, if_available_mask(lines)), 1):
            where = f"{rel}:{i}"
            if not inside and HARD_PATH_RE.search(line):
                out.append(Finding("hard-path", f"{where} local path outside an 'If available' section"))
            if AGENT_RE.search(line):
                out.append(Finding("agent-instruction", f"{where} subagent or Agent-tool instruction"))
            if EMAIL_RE.search(line) or PHONE_RE.search(line):
                out.append(Finding("contact-detail", f"{where} e-mail address or phone number"))
            for token in INTERNAL_TOKENS:
                if token in line:
                    out.append(Finding("internal-name", f"{where} internal name '{token}'"))
            for pattern, reason in patterns:
                if re.search(pattern, line, re.I) and not hedged(line):
                    out.append(Finding("forbidden-citation", f"{where} {reason}"))
    return out


def one_folder_findings(env: Env, name: str) -> list[Finding]:
    found = find_skill(env, name)
    if len(found) > 1:
        return [Finding("one-folder", f"'{name}' exists in {', '.join(tier_of(p) for p in found)}")]
    return []


def installed_findings(env: Env, name: str) -> list[Finding]:
    """An org/ or account/ skill must not also be installed locally (outside synced/).

    A warning, not a block (plan decision C): check reports the leftover copy and
    publish does not stop on it.
    """
    if (env.claude_skills / name / "SKILL.md").is_file():
        return [Finding("installed-locally", f"~/.claude/skills/{name} exists; after the upload syncs, "
                        f"run: npx skills remove {name} --global --agent claude-code -y",
                        blocking=False)]
    return []


def _words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z]{4,}", text.lower()) if w not in STOPWORDS}


def _quoted(text: str) -> set[str]:
    return {q.strip().lower() for q in re.findall(r"[\"“]([^\"”]{6,80})[\"”]", text)}


def overlap_warnings(env: Env, skill_dir: Path) -> list[Finding]:
    """Warn, never block, when another visible skill shares trigger phrases."""
    desc = str(parse((skill_dir / "SKILL.md").read_text(encoding="utf-8")).get("description", ""))
    mine_w, mine_q = _words(desc), _quoted(desc)
    own = {skill_dir.name, f"{skill_dir.name}-draft", f"{skill_dir.name}-before"}
    out: list[Finding] = []
    for where, other in synced.visible_skill_dirs(env):
        if other.name in own:
            continue
        try:
            odesc = str(parse((other / "SKILL.md").read_text(encoding="utf-8")).get("description", ""))
        except (PublishError, OSError, UnicodeDecodeError):
            continue
        shared = mine_q & _quoted(odesc)
        other_w = _words(odesc)
        union = mine_w | other_w
        jaccard = len(mine_w & other_w) / len(union) if union else 0.0
        if shared or jaccard >= 0.3:
            why = f"shared phrase {sorted(shared)[0]!r}" if shared else f"word overlap {jaccard:.2f}"
            out.append(Finding("trigger-overlap", f"{other.name} ({where}): {why}", blocking=False))
    return out


def check_skill(env: Env, name: str, forbidden: Forbidden | None = None) -> list[Finding]:
    found = find_skill(env, name)
    if not found:
        raise PublishError(f"no skill '{name}' in skills/, org/ or account/")
    out = one_folder_findings(env, name)
    for skill_dir in found:
        if tier_of(skill_dir) in PORTABLE_FOLDERS:
            out += frontmatter_findings(skill_dir)
            out += portability_findings(env, skill_dir, forbidden)
            out += installed_findings(env, name)
            out += overlap_warnings(env, skill_dir)
        else:
            out += [Finding(f.rule, f.detail, blocking=False) for f in frontmatter_findings(skill_dir)]
    return out
