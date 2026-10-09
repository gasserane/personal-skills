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
    assert any(c.startswith("Task.") and c.endswith(release.HARNESS_SUFFIX) for c in calls)
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


def test_both_arms_get_suffix_canary_does_not_with_before(env):
    _committed_skill_with_edit(env)
    calls = []
    release.compare(env, "toc-lite", runner=fake_runner(calls), rng=random.Random(1))
    assert calls[0] == "/publish-canary"
    arms = calls[1:]
    assert len(arms) == 2
    assert all(c.endswith("\n\n" + release.HARNESS_SUFFIX) for c in arms)
    assert arms[0].startswith("/toc-lite-before ") and arms[1].startswith("/toc-lite-draft ")


def test_first_version_arms_get_suffix(env):
    make_skill(env, "account", "helper")
    write(env.repo / "evals" / "helper" / "prompt.md", "Task.\n")
    calls = []
    release.compare(env, "helper", runner=fake_runner(calls), rng=random.Random(2))
    assert calls[0] == "/publish-canary"
    assert calls[1:] == ["Task.\n\n" + release.HARNESS_SUFFIX, "/helper-draft Task.\n\n" + release.HARNESS_SUFFIX]


def test_key_json_records_harness_suffix(env):
    _committed_skill_with_edit(env)
    run = release.compare(env, "toc-lite", runner=fake_runner([]), rng=random.Random(1))
    key = json.loads((run / "key.json").read_text(encoding="utf-8"))
    assert key["harness_suffix"] == release.HARNESS_SUFFIX


def test_run_claude_restricts_tools_and_resets_output_style(env, monkeypatch):
    seen = {}

    class Stub:
        returncode = 0
        stdout = "x"
        stderr = ""

    def fake_run(argv, **kw):
        seen["argv"] = argv
        return Stub()

    monkeypatch.setattr(release.subprocess, "run", fake_run)
    assert release.run_claude(env, "hi") == "x"
    argv = seen["argv"]
    assert argv[argv.index("--disallowedTools") + 1] == "Write,Edit,NotebookEdit"
    assert argv[argv.index("--allowedTools") + 1] == "Read,Grep,Glob"
    assert json.loads(argv[argv.index("--settings") + 1])["outputStyle"] == "default"


def test_harness_check_flags_insight_box():
    out = release.harness_check("clean text", "x\n\u2605 Insight \u2500\u2500\ny")
    assert "B.md" in out and "A.md" not in out
    assert "Read this before the blind read." in out


@pytest.mark.parametrize("path", [
    r"C:\Users\x\AppData\Local\Temp\claude\proj\sess\scratchpad\brief.md",
    "C:/Users/x/AppData/Local/Temp/claude/proj/sess/scratchpad/brief.md",
])
def test_harness_check_flags_scratchpad_file(path):
    out = release.harness_check(f"Saved to {path}", "clean")
    assert "A.md" in out and "B.md" not in out and "scratchpad" in out


def test_harness_check_clean_and_never_names_arms():
    assert release.harness_check("fine", "also fine") == "both outputs clean\n"
    flagged = release.harness_check("\u2605 Insight", "scratchpad/a.md")
    # the mandated note line ("Read this before the blind read.") legitimately holds the word before
    flagged = flagged.replace("Read this before the blind read.", "").lower()
    assert "draft" not in flagged and "before" not in flagged


def test_compare_writes_harness_check_file(env):
    _committed_skill_with_edit(env)
    run = release.compare(env, "toc-lite", runner=fake_runner([]), rng=random.Random(1))
    assert (run / "harness-check.md").read_text(encoding="utf-8") == "both outputs clean\n"


def _fill(run, preferred, colleague=None):
    write(run / "verdict.md", f"preferred: {preferred}\nreason: clearer steps\n")
    if colleague:
        write(run / "colleague.md", f"colleague-condition: {colleague}\nnote: works without the wiki\n")


def _compared(env, tier="org"):
    _committed_skill_with_edit(env, tier)
    run = release.compare(env, "toc-lite", runner=fake_runner([]), rng=random.Random(1))
    return run, json.loads((run / "key.json").read_text(encoding="utf-8"))


def test_publish_blocks_worse(env):
    run, key = _compared(env)
    _fill(run, key["before"], "pass")
    with pytest.raises(PublishError, match="worse"):
        release.publish(env, "toc-lite", "rewrite", "one text for all")


def test_publish_blocks_stale_verdict(env):
    run, key = _compared(env)
    _fill(run, key["draft"], "pass")
    p = env.repo / "org" / "toc-lite" / "SKILL.md"
    write(p, p.read_text(encoding="utf-8") + "One more line.\n")
    with pytest.raises(PublishError, match="changed after the compare run"):
        release.publish(env, "toc-lite", "rewrite", "why")


def test_publish_blocks_unfilled_verdict(env):
    _compared(env)
    with pytest.raises(PublishError, match="not filled in"):
        release.publish(env, "toc-lite", "rewrite", "why")


def test_publish_org_needs_colleague_test(env):
    run, _ = _compared(env)
    _fill(run, "same")
    with pytest.raises(PublishError, match="colleague-condition"):
        release.publish(env, "toc-lite", "rewrite", "why")


def test_publish_org_blocks_failed_colleague_test(env):
    run, key = _compared(env)
    _fill(run, key["draft"], "fail")
    with pytest.raises(PublishError, match="colleague-condition test failed"):
        release.publish(env, "toc-lite", "rewrite", "why")


def test_publish_org_refuses_trivial(env):
    _committed_skill_with_edit(env)
    with pytest.raises(PublishError, match="refused for org/"):
        release.publish(env, "toc-lite", "typo", "typo", trivial=True)


def test_publish_account_trivial_records_the_skip(env):
    make_skill(env, "account", "helper")
    release.publish(env, "helper", "narrow description", "trigger collision", trivial=True, push=False)
    assert "trivial, no compare" in (env.repo / "CHANGELOG.md").read_text(encoding="utf-8")


def test_publish_success_commits_pushes_and_logs(env):
    run, key = _compared(env)
    _fill(run, key["draft"], "pass")
    msg = release.publish(env, "toc-lite", "rewrite to one text", "decision 6", day=date(2026, 10, 9))
    assert git(env.repo, "log", "-1", "--format=%s").strip() == "publish(toc-lite): rewrite to one text"
    assert git(env.repo, "rev-parse", "HEAD") == git(env.repo, "rev-parse", "origin/main")
    changelog = (env.repo / "CHANGELOG.md").read_text(encoding="utf-8")
    assert changelog.index("publish: toc-lite") < changelog.index("old entry")
    assert "better: clearer steps" in changelog
    assert (env.dist / "toc-lite.zip").exists() and (env.dist / "toc-lite-review-note.md").exists()
    assert not (env.claude_skills / "toc-lite-draft").exists()
    assert not (env.claude_skills / "toc-lite-before").exists()
    assert "Upload a skill" in msg


def test_publish_requires_what_and_why(env):
    make_skill(env, "skills", "code-only")
    with pytest.raises(PublishError, match="--what and --why"):
        release.publish(env, "code-only", "", "why")


def test_commit_and_push_refuses_an_empty_commit(env):
    from skillpub.gitops import commit_and_push
    with pytest.raises(PublishError, match="nothing staged"):
        commit_and_push(env, ["CHANGELOG.md"], "noop", push=False)


def test_changelog_add_is_idempotent(env):
    day = date(2026, 10, 9)
    release.changelog_add(env, day, "toc-lite", "rewrite", "why", "better: clearer")
    release.changelog_add(env, day, "toc-lite", "rewrite", "why", "better: clearer")
    assert (env.repo / "CHANGELOG.md").read_text(encoding="utf-8").count("publish: toc-lite") == 1


def test_publish_rerun_after_refused_commit_writes_one_entry(env):
    run, key = _compared(env)
    _fill(run, key["draft"], "pass")
    day = date(2026, 10, 9)
    write(env.repo / "stray.txt", "stray\n")
    git(env.repo, "add", "stray.txt")
    with pytest.raises(PublishError, match="outside this publish"):
        release.publish(env, "toc-lite", "rewrite", "why", day=day)
    assert "publish: toc-lite" not in (env.repo / "CHANGELOG.md").read_text(encoding="utf-8")
    git(env.repo, "restore", "--staged", "stray.txt")
    release.publish(env, "toc-lite", "rewrite", "why", day=day)
    assert (env.repo / "CHANGELOG.md").read_text(encoding="utf-8").count("publish: toc-lite") == 1
