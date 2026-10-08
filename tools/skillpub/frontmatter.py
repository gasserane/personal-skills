"""Read and set SKILL.md frontmatter without disturbing any other byte."""
from __future__ import annotations

import re

import yaml

from .paths import PublishError

FM_RE = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", re.S)


def split(text: str) -> tuple[str, str]:
    m = FM_RE.match(text)
    if not m:
        raise PublishError("SKILL.md has no frontmatter block between --- lines")
    return m.group(1), text[m.end():]


def parse(text: str) -> dict:
    block, _ = split(text)
    try:
        data = yaml.safe_load(block) or {}
    except yaml.YAMLError as exc:
        raise PublishError(f"frontmatter is not valid YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise PublishError("frontmatter is not a key: value mapping")
    return data


def set_field(text: str, key: str, value: str) -> str:
    """Replace the single-line `key:` entry, or append it. Keeps CRLF when the file uses it."""
    m = FM_RE.match(text)
    if not m:
        raise PublishError("SKILL.md has no frontmatter block between --- lines")
    nl = "\r\n" if "\r\n" in text[: m.end()] else "\n"
    lines = m.group(1).split(nl)
    new_line = f"{key}: {value}"
    key_re = re.compile(rf"{re.escape(key)}\s*:")
    for i, line in enumerate(lines):
        if key_re.match(line):
            lines[i] = new_line
            break
    else:
        lines.append(new_line)
    return text[: m.start(1)] + nl.join(lines) + text[m.end(1):]
