"""Where publish.py reads and writes. Tests build an Env on tmp_path.

Spec: agent-improvements/skills-distribution-spec.md in anework-package, § 3.2 and § 3.3.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

TIER_FOLDERS = ("skills", "org", "account")
PORTABLE_FOLDERS = ("org", "account")
DEFAULT_WORK_FOLDER = "C:/Users/AGasser/OneDrive/5 ANE CLAUDE work folder"


class PublishError(Exception):
    """A refusal the user must act on. The CLI prints it and exits 1."""


@dataclass(frozen=True)
class Env:
    repo: Path           # the personal-skills clone
    claude_skills: Path  # ~/.claude/skills
    claude_json: Path    # ~/.claude.json: names the signed-in claude.ai account
    work_folder: Path    # anework-package: compare runs here; citation rules live here

    @classmethod
    def default(cls) -> "Env":
        home = Path.home()
        return cls(
            repo=Path(__file__).resolve().parents[2],
            claude_skills=Path(os.environ.get("PUBLISH_CLAUDE_SKILLS", str(home / ".claude" / "skills"))),
            claude_json=Path(os.environ.get("PUBLISH_CLAUDE_JSON", str(home / ".claude.json"))),
            work_folder=Path(os.environ.get("WORK_FOLDER_ROOT", DEFAULT_WORK_FOLDER)),
        )

    @property
    def synced_root(self) -> Path:
        return self.claude_skills / "synced"

    @property
    def dist(self) -> Path:
        return self.repo / "dist"


def find_skill(env: Env, name: str) -> list[Path]:
    """Every tier folder holding <name>/SKILL.md. More than one breaks the one-folder rule."""
    return [env.repo / t / name for t in TIER_FOLDERS if (env.repo / t / name / "SKILL.md").is_file()]


def resolve(env: Env, name: str) -> Path:
    found = find_skill(env, name)
    if not found:
        raise PublishError(f"no skill '{name}' in skills/, org/ or account/")
    if len(found) > 1:
        where = ", ".join(p.parent.name for p in found)
        raise PublishError(f"'{name}' exists in more than one folder ({where}); keep exactly one")
    return found[0]


def tier_of(skill_dir: Path) -> str:
    return skill_dir.parent.name


def all_skill_dirs(env: Env, tiers: tuple[str, ...] = TIER_FOLDERS) -> list[Path]:
    return [p.parent for t in tiers for p in sorted((env.repo / t).glob("*/SKILL.md"))]
