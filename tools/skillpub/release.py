"""draft, compare and publish (spec § 3.3 to § 3.5)."""
from __future__ import annotations

import hashlib
import shutil
import zipfile
from pathlib import Path

from .frontmatter import parse, set_field
from .paths import Env, PublishError, resolve

SKIP_PARTS = {"__pycache__", ".DS_Store"}


def read_dir(skill_dir: Path) -> dict[str, bytes]:
    return {
        p.relative_to(skill_dir).as_posix(): p.read_bytes()
        for p in sorted(skill_dir.rglob("*"))
        if p.is_file() and not SKIP_PARTS & set(p.relative_to(skill_dir).parts)
    }


def tree_hash(files: dict[str, bytes]) -> str:
    h = hashlib.sha256()
    for rel in sorted(files):
        h.update(rel.encode("utf-8") + b"\0" + files[rel] + b"\0")
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
