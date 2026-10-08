import pytest

from helpers import git, write
from skillpub import gitops
from skillpub.paths import PublishError


def test_commit_refuses_files_staged_outside_paths(env):
    write(env.repo / "org" / "mine" / "SKILL.md", "a\n")
    write(env.repo / "secret.txt", "private\n")
    git(env.repo, "add", "secret.txt")
    before = git(env.repo, "rev-parse", "HEAD")
    with pytest.raises(PublishError, match="secret.txt"):
        gitops.commit_and_push(env, ["org/mine"], "x", push=False)
    assert git(env.repo, "rev-parse", "HEAD") == before


def test_commit_accepts_files_under_a_directory_path(env):
    write(env.repo / "org" / "mine" / "SKILL.md", "a\n")
    sha = gitops.commit_and_push(env, ["org/mine"], "x", push=False)
    assert sha == git(env.repo, "rev-parse", "HEAD").strip()


def test_commit_refuses_an_empty_index(env):
    with pytest.raises(PublishError, match="nothing staged"):
        gitops.commit_and_push(env, ["CHANGELOG.md"], "x", push=False)
