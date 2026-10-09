from datetime import datetime, timedelta, timezone

from helpers import git, make_skill, skill_text, synced_copy, write
from skillpub import synced


def test_match_ignores_crlf_and_quoted_name(env):
    make_skill(env, "org", "toc-lite")
    text = skill_text("toc-lite").replace("name: toc-lite", 'name: "toc-lite"').replace("\n", "\r\n")
    synced_copy(env, "org1_acc1", "toc-lite", text)
    assert [r.status for r in synced.verify(env, "toc-lite")] == ["match"]


def test_mismatch_and_dash2_variant(env):
    make_skill(env, "org", "toc-lite")
    synced_copy(env, "org1_acc1", "toc-lite", skill_text("toc-lite", body="Old text.\n"))
    synced_copy(env, "org1_acc1", "toc-lite-2", skill_text("toc-lite-2"))
    row = synced.verify(env, "toc-lite")[0]
    assert row.status == "mismatch" and row.variants == ["toc-lite-2"]


def test_missing(env):
    make_skill(env, "org", "toc-lite")
    assert synced.verify(env, "toc-lite")[0].status == "missing"


def test_not_synced_yet_when_manifest_predates_publish(env):
    make_skill(env, "org", "toc-lite")
    git(env.repo, "add", "-A")
    git(env.repo, "commit", "-q", "-m", "publish(toc-lite): first")
    synced_copy(env, "org1_acc1", "toc-lite", skill_text("toc-lite", body="Old.\n"),
                updated="2000-01-01T00:00:00Z")
    assert synced.verify(env, "toc-lite")[0].status == "not-synced-yet"


def test_inactive_account_ignored_by_default(env):
    make_skill(env, "org", "toc-lite")
    synced_copy(env, "org1_acc1", "toc-lite", skill_text("toc-lite"))
    synced_copy(env, "old0_old0", "toc-lite", skill_text("toc-lite"))
    assert len(synced.verify(env, "toc-lite")) == 1
    assert synced.dupes(env) == []
    assert any(line.startswith("toc-lite: ") for line in synced.dupes(env, all_accounts=True))


def test_dupes_finds_local_against_account_and_dash2(env):
    write(env.claude_skills / "mel-discipline" / "SKILL.md", skill_text("mel-discipline"))
    synced_copy(env, "org1_acc1", "mel-discipline-2", skill_text("mel-discipline-2"))
    write(env.claude_skills / "pdf" / "SKILL.md", skill_text("pdf"))
    synced_copy(env, "org1_acc1", "pdf", skill_text("pdf"))
    lines = synced.dupes(env)
    assert any(line.startswith("pdf: local, account:org1_acc") for line in lines)
    assert any(line.startswith("mel-discipline-2 next to mel-discipline") for line in lines)


def test_no_active_account(env):
    env.claude_json.write_text("{}", encoding="utf-8")
    assert synced.active_account_dir(env) is None


def test_freshness_message_reports_then_clears(env):
    make_skill(env, "account", "helper")
    synced_copy(env, "org1_acc1", "helper", skill_text("helper", body="Old.\n"))
    assert "helper (mismatch)" in synced.freshness_message(env)
    synced_copy(env, "org1_acc1", "helper", skill_text("helper"))
    assert synced.freshness_message(env) is None


def test_freshness_quiet_within_an_hour_of_publish(env):
    make_skill(env, "account", "helper")
    git(env.repo, "add", "-A")
    git(env.repo, "commit", "-q", "-m", "publish(helper): first")
    assert synced.freshness_message(env) is None
    later = datetime.now(timezone.utc) + timedelta(hours=2)
    assert "helper (missing)" in synced.freshness_message(env, now=later)


def test_freshness_names_a_missing_active_account(env):
    make_skill(env, "account", "helper")
    env.claude_json.write_text("{}", encoding="utf-8")
    assert "no synced folder" in synced.freshness_message(env)


def test_dupes_ignores_an_identical_project_copy(env):
    write(env.claude_skills / "ann" / "SKILL.md", skill_text("ann"))
    write(env.work_folder / ".claude" / "skills" / "ann" / "SKILL.md", skill_text("ann").replace("\n", "\r\n"))
    assert synced.dupes(env) == []


def test_dupes_flags_a_differing_project_copy(env):
    write(env.claude_skills / "ann" / "SKILL.md", skill_text("ann"))
    write(env.work_folder / ".claude" / "skills" / "ann" / "SKILL.md", skill_text("ann", body="Edited.\n"))
    assert synced.dupes(env) == ["ann: local, project (project copy differs)"]


def test_naive_manifest_time_is_treated_as_utc(env):
    make_skill(env, "org", "toc-lite")
    git(env.repo, "add", "-A")
    git(env.repo, "commit", "-q", "-m", "publish(toc-lite): first")
    synced_copy(env, "org1_acc1", "toc-lite", skill_text("toc-lite", body="Old.\n"),
                updated="2000-01-01T00:00:00")  # no Z, no offset
    assert synced.verify(env, "toc-lite")[0].status == "not-synced-yet"
    assert synced._parse_time("2000-01-01T00:00:00").tzinfo is not None


def test_freshness_skips_a_skill_it_cannot_read(env):
    make_skill(env, "account", "helper")
    synced_copy(env, "org1_acc1", "helper", skill_text("helper", body="Old.\n"))
    make_skill(env, "org", "twin")
    make_skill(env, "account", "twin")  # same name in two folders: resolve() refuses
    (env.repo / "org" / "binary" ).mkdir()
    (env.repo / "org" / "binary" / "SKILL.md").write_bytes(b"\xff\xfe\x00bad")
    msg = synced.freshness_message(env)
    assert "helper (mismatch)" in msg
    assert "twin" not in msg and "binary" not in msg
