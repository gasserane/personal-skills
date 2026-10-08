import json
import random
import zipfile
from datetime import date

import pytest

from helpers import git, make_skill, write
from skillpub import release
from skillpub.paths import PublishError


def test_draft_installs_user_invoked_copy_and_zip(env):
    make_skill(env, "org", "toc-lite")
    dest, zp = release.draft(env, "toc-lite")
    text = (dest / "SKILL.md").read_text(encoding="utf-8")
    assert "name: toc-lite-draft" in text and "disable-model-invocation: true" in text
    assert zipfile.ZipFile(zp).namelist() == ["toc-lite-draft/SKILL.md"]


def test_draft_keeps_reference_files_and_skips_pycache(env):
    d = make_skill(env, "org", "toc-lite")
    write(d / "references" / "steps.md", "Steps.\n")
    write(d / "__pycache__" / "x.pyc", "junk")
    _, zp = release.draft(env, "toc-lite")
    assert sorted(zipfile.ZipFile(zp).namelist()) == ["toc-lite-draft/SKILL.md", "toc-lite-draft/references/steps.md"]


def test_build_zip_refuses_name_mismatch(env):
    d = make_skill(env, "org", "toc-lite")
    with pytest.raises(PublishError, match="must equal"):
        release.build_zip(d, env.dist, "other")
