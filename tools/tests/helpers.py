import json
import subprocess
from pathlib import Path

from skillpub.paths import Env


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(cwd), *args], check=True,
                          capture_output=True, text=True).stdout


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="")
    return path


def skill_text(name: str, body: str = "Do the task.\n", description: str | None = None,
               extra: str = "") -> str:
    desc = description if description is not None else f"Test skill {name} for a fixture task."
    return f"---\nname: {name}\ndescription: {desc}\n{extra}---\n\n{body}"


def make_skill(env: Env, tier: str, name: str, **kw) -> Path:
    write(env.repo / tier / name / "SKILL.md", skill_text(name, **kw))
    return env.repo / tier / name


def build_env(tmp: Path) -> Env:
    repo, remote = tmp / "repo", tmp / "remote.git"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(remote)], check=True)
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "test@example.invalid")
    git(repo, "config", "user.name", "Test")
    git(repo, "config", "core.autocrlf", "false")
    write(repo / "CHANGELOG.md", "# Changelog — test\n\nIntro.\n\n## [2026-01-01] — old entry\n\nOld.\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "init")
    git(repo, "remote", "add", "origin", str(remote))
    git(repo, "push", "-q", "-u", "origin", "main")
    skills = tmp / "claude_skills"
    (skills / "synced" / "org1_acc1").mkdir(parents=True)
    claude_json = write(tmp / "claude.json", json.dumps(
        {"oauthAccount": {"organizationUuid": "org1", "accountUuid": "acc1"}}))
    work = tmp / "work"
    write(work / "ane_package" / "citation_rules.py",
          'FORBIDDEN_PATTERNS = [(r"15[-\\s]component", "G-L 15-component")]\n\n'
          'def line_has_hedge(line):\n    return "wrong" in line.lower()\n')
    return Env(repo=repo, claude_skills=skills, claude_json=claude_json, work_folder=work)


def synced_copy(env: Env, account: str, name: str, text: str,
                updated: str = "2026-10-08T10:00:00Z") -> Path:
    acct = env.synced_root / account
    write(acct / name / "SKILL.md", text)
    mf = acct / "manifest.json"
    data = json.loads(mf.read_text(encoding="utf-8")) if mf.exists() else {"lastUpdated": 0, "skills": []}
    data["skills"] = [s for s in data["skills"] if s["name"] != name] + [
        {"skillId": name, "name": name, "description": "", "source": "plugin", "updatedAt": updated}]
    write(mf, json.dumps(data))
    return acct / name
