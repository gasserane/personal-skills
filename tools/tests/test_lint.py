import pytest

from helpers import make_skill, skill_text, write
from skillpub import lint
from skillpub.paths import Env, PublishError


def rules(findings, blocking=True):
    return {f.rule for f in findings if f.blocking == blocking}


def test_portable_skill_passes(env):
    make_skill(env, "org", "toc-lite", body="Build a theory of change step by step.\n")
    assert rules(lint.check_skill(env, "toc-lite")) == set()


def test_agent_instruction_fails(env):
    make_skill(env, "org", "toc-lite", body="Spawn three specialist subagents to review.\n")
    assert "agent-instruction" in rules(lint.check_skill(env, "toc-lite"))


def test_local_path_fails_outside_if_available(env):
    make_skill(env, "org", "toc-lite", body="Read C:/Users/x/wiki/page.md first.\n")
    assert "hard-path" in rules(lint.check_skill(env, "toc-lite"))


def test_local_path_allowed_inside_if_available(env):
    make_skill(env, "org", "toc-lite", body=(
        "Main steps.\n\n## If available\n\nRead ${MEL_WIKI_ROOT}/wiki/x.md.\n\n## Output\n\nA table.\n"))
    assert "hard-path" not in rules(lint.check_skill(env, "toc-lite"))


def test_path_after_the_if_available_section_fails(env):
    make_skill(env, "org", "toc-lite", body=(
        "## If available\n\nUse the wiki.\n\n## Output\n\nSave to ~/.claude/out.md\n"))
    assert "hard-path" in rules(lint.check_skill(env, "toc-lite"))


def test_url_is_not_a_drive_path(env):
    make_skill(env, "org", "toc-lite", body="See https://example.org/guide.\n")
    assert "hard-path" not in rules(lint.check_skill(env, "toc-lite"))


def test_duplicated_name_fails(env):
    make_skill(env, "org", "toc-lite")
    make_skill(env, "skills", "toc-lite")
    assert "one-folder" in rules(lint.check_skill(env, "toc-lite"))


def test_folder_name_mismatch_fails(env):
    write(env.repo / "org" / "toc-lite" / "SKILL.md", skill_text("toc-other"))
    assert "folder-name" in rules(lint.check_skill(env, "toc-lite"))


def test_scripts_folder_contact_and_internal_names_fail(env):
    d = make_skill(env, "account", "helper", body="Mail someone@example.org. See agent-improvements/x.md.\n")
    write(d / "scripts" / "run.py", "print(1)\n")
    assert {"scripts-folder", "contact-detail", "internal-name"} <= rules(lint.check_skill(env, "helper"))


def test_forbidden_citation_fails_unless_hedged(env):
    make_skill(env, "org", "srhr", body="Use the G-L 15-component package.\nThe 15-component count is wrong.\n")
    found = [f for f in lint.check_skill(env, "srhr") if f.rule == "forbidden-citation"]
    assert len(found) == 1 and found[0].detail.startswith("SKILL.md:6 ")


def test_name_rules(env):
    write(env.repo / "org" / "Claude-Thing" / "SKILL.md", skill_text("Claude-Thing", description="x" * 1025))
    assert {"name-format", "description-length"} <= rules(lint.check_skill(env, "Claude-Thing"))


def test_reserved_word_in_name(env):
    make_skill(env, "org", "claude-helper")
    assert "name-reserved" in rules(lint.check_skill(env, "claude-helper"))


def test_installed_locally_reported(env):
    make_skill(env, "org", "toc-lite")
    write(env.claude_skills / "toc-lite" / "SKILL.md", skill_text("toc-lite"))
    found = lint.check_skill(env, "toc-lite")
    assert "installed-locally" in rules(found, blocking=False)
    assert "installed-locally" not in rules(found)


def test_tier_b_frontmatter_problems_only_warn(env):
    write(env.repo / "skills" / "big" / "SKILL.md", skill_text("big", description="x" * 1100))
    found = lint.check_skill(env, "big")
    assert rules(found) == set() and "description-length" in rules(found, blocking=False)


def test_trigger_overlap_warns_and_never_blocks(env):
    make_skill(env, "account", "lit-helper",
               description='Use when the user says "help me research this topic" or similar.')
    write(env.claude_skills / "literature" / "SKILL.md",
          skill_text("literature", description='Search papers when asked to "help me research this topic".'))
    found = lint.check_skill(env, "lit-helper")
    assert "trigger-overlap" in rules(found, blocking=False) and rules(found) == set()


def test_malformed_frontmatter_reported_not_raised(env):
    write(env.repo / "org" / "broken" / "SKILL.md", "No frontmatter block here.\n")
    assert "frontmatter" in rules(lint.check_skill(env, "broken"))


def test_missing_citation_rules_is_an_error(env, tmp_path):
    make_skill(env, "org", "toc-lite")
    broken = Env(env.repo, env.claude_skills, env.claude_json, tmp_path / "nowhere")
    with pytest.raises(PublishError, match="forbidden-citation list not found"):
        lint.check_skill(broken, "toc-lite")


def test_classify_tier_rule(env):
    make_skill(env, "skills", "orchestrator", body="Spawn the specialist subagents.\n")
    make_skill(env, "skills", "plain", body="Write the brief.\n")
    make_skill(env, "skills", "caller", body="First run /orchestrator, then format.\n")
    make_skill(env, "skills", "caller2", body="Run /caller.\n")
    make_skill(env, "skills", "soft", body="Main steps.\n\n## If available\n\nRun /orchestrator.\n")
    d = make_skill(env, "skills", "scripted")
    write(d / "scripts" / "x.py", "")
    rows = {r.name: r for r in lint.classify(env)}
    assert rows["orchestrator"].tier == "B"
    assert rows["plain"].tier == "portable"
    assert rows["caller"].tier == "B" and "/orchestrator" in rows["caller"].reasons
    assert rows["caller2"].tier == "B"
    assert rows["soft"].tier == "portable"
    assert rows["scripted"].tier == "B"
    assert "| plain |" in lint.format_classify(list(rows.values()))


def test_classify_ignores_the_description(env):
    make_skill(env, "skills", "orchestrator", body="Spawn the specialist subagents.\n")
    make_skill(env, "skills", "negated", description="Not for /orchestrator.", body="Write the brief.\n")
    rows = {r.name: r for r in lint.classify(env)}
    assert rows["negated"].tier == "portable"
    assert rows["orchestrator"].tier == "B"
