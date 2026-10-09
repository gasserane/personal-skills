import json

import publish
from helpers import make_skill, skill_text, synced_copy


def test_check_exit_codes(env, capsys):
    make_skill(env, "org", "good")
    assert publish.main(["check", "good"], env=env) == 0
    make_skill(env, "org", "bad", body="Spawn subagents.\n")
    assert publish.main(["check", "bad"], env=env) == 1
    assert "BLOCK agent-instruction" in capsys.readouterr().out


def test_verify_hook_prints_only_on_a_problem(env, capsys):
    make_skill(env, "account", "helper")
    assert publish.main(["verify", "--hook"], env=env) == 0
    assert json.loads(capsys.readouterr().out)["systemMessage"].startswith("⚠️")
    synced_copy(env, "org1_acc1", "helper", skill_text("helper"))
    assert publish.main(["verify", "--hook"], env=env) == 0
    assert capsys.readouterr().out == ""


def test_verify_exit_code_follows_the_active_account(env, capsys):
    make_skill(env, "account", "helper")
    assert publish.main(["verify", "helper"], env=env) == 1
    synced_copy(env, "org1_acc1", "helper", skill_text("helper"))
    assert publish.main(["verify", "helper"], env=env) == 0
    assert "match" in capsys.readouterr().out


def test_dupes_none(env, capsys):
    assert publish.main(["dupes"], env=env) == 0
    assert "dupes: none" in capsys.readouterr().out


def test_unknown_skill_is_a_clean_error(env, capsys):
    assert publish.main(["draft", "nope"], env=env) == 1
    assert "no skill 'nope'" in capsys.readouterr().err


def test_verify_hook_never_crashes_or_prints_when_env_fails(monkeypatch, capsys):
    def boom():
        raise RuntimeError("no env")
    monkeypatch.setattr(publish.Env, "default", staticmethod(boom))
    assert publish.main(["verify", "--hook"]) == 0
    captured = capsys.readouterr()
    assert captured.out == "" and captured.err == ""


def test_verify_hook_is_silent_even_if_the_check_raises(env, monkeypatch, capsys):
    monkeypatch.setattr(publish.synced, "freshness_message",
                        lambda e: (_ for _ in ()).throw(OSError("disk")))
    assert publish.main(["verify", "--hook"], env=env) == 0
    assert capsys.readouterr().out == ""
