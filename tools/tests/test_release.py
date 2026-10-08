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


def fake_runner(calls):
    def run(env, prompt):
        calls.append(prompt)
        if prompt == "/publish-canary":
            return f"ok {release.CANARY}"
        return f"OUTPUT for {prompt.split()[0]}"
    return run


def _committed_skill_with_edit(env, tier="org"):
    d = make_skill(env, tier, "toc-lite", body="Version one.\n")
    write(env.repo / "evals" / "toc-lite" / "prompt.md", "Build a ToC for a youth SRHR project.\n")
    git(env.repo, "add", "-A")
    git(env.repo, "commit", "-q", "-m", "add toc-lite")
    p = d / "SKILL.md"
    write(p, p.read_text(encoding="utf-8").replace("Version one.", "Version two."))
    return d


def test_compare_writes_blind_pair_and_key(env):
    _committed_skill_with_edit(env)
    calls = []
    run = release.compare(env, "toc-lite", runner=fake_runner(calls), day=date(2026, 10, 9),
                          rng=random.Random(1))
    key = json.loads((run / "key.json").read_text(encoding="utf-8"))
    assert (run / f"{key['draft']}.md").read_text(encoding="utf-8").startswith("OUTPUT for /toc-lite-draft")
    assert (run / f"{key['before']}.md").read_text(encoding="utf-8").startswith("OUTPUT for /toc-lite-before")
    assert calls[0] == "/publish-canary"
    assert (run / "colleague.md").exists() and run.name == "2026-10-09"
    assert not (env.claude_skills / "publish-canary").exists()


def test_compare_stops_when_canary_fails(env):
    _committed_skill_with_edit(env)
    calls = []
    with pytest.raises(PublishError, match="canary failed"):
        release.compare(env, "toc-lite", runner=lambda e, p: calls.append(p) or "Unknown command")
    assert calls == ["/publish-canary"]


def test_compare_refuses_identical_draft(env):
    make_skill(env, "org", "toc-lite")
    write(env.repo / "evals" / "toc-lite" / "prompt.md", "Task.\n")
    git(env.repo, "add", "-A")
    git(env.repo, "commit", "-q", "-m", "add")
    with pytest.raises(PublishError, match="nothing to compare"):
        release.compare(env, "toc-lite", runner=fake_runner([]))


def test_compare_needs_a_prompt(env):
    make_skill(env, "org", "toc-lite")
    with pytest.raises(PublishError, match="prompt.md first"):
        release.compare(env, "toc-lite", runner=fake_runner([]))


def test_compare_first_version_uses_bare_model(env):
    make_skill(env, "account", "helper")
    write(env.repo / "evals" / "helper" / "prompt.md", "Task.\n")
    calls = []
    run = release.compare(env, "helper", runner=fake_runner(calls), rng=random.Random(2))
    assert "Task." in calls
    assert json.loads((run / "key.json").read_text(encoding="utf-8"))["before_rev"].startswith("none")
    assert not (run / "colleague.md").exists()


def test_second_run_same_day_gets_a_suffix(env):
    _committed_skill_with_edit(env)
    first = release.compare(env, "toc-lite", runner=fake_runner([]), day=date(2026, 10, 9))
    second = release.compare(env, "toc-lite", runner=fake_runner([]), day=date(2026, 10, 9))
    assert (first.name, second.name) == ("2026-10-09", "2026-10-09-2")


def test_compare_refuses_crlf_copy_of_committed_lf(env):
    d = make_skill(env, "org", "toc-lite")
    write(env.repo / "evals" / "toc-lite" / "prompt.md", "Task.\n")
    git(env.repo, "add", "-A")
    git(env.repo, "commit", "-q", "-m", "add")
    p = d / "SKILL.md"
    p.write_bytes(p.read_bytes().replace(b"\n", b"\r\n"))
    with pytest.raises(PublishError, match="nothing to compare"):
        release.compare(env, "toc-lite", runner=fake_runner([]))
