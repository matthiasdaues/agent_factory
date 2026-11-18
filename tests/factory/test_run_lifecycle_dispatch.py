"""dispatch commands of the run lifecycle (docs/spec/features/run-lifecycle.feature).

Each test builds its own git repository in tmp_path and runs dispatch as a
subprocess, the way the implementation agent does.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from conftest import SOURCE_SCRIPTS_DIR

DISPATCH = SOURCE_SCRIPTS_DIR / "dispatch"
STORY = """---
id: {id}
title: {id}
tier: economy
status: open
deps: []
touches: ["src/{id}.txt"]
outputs: ["src/{id}.txt"]
quality-gates: []
---
# {id}
"""


def _env() -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(
        GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
        GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t",
    )
    return env


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, env=_env(), check=True,
        capture_output=True, text=True,
    ).stdout.strip()


def _dispatch(cwd: Path, ledger: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(DISPATCH), "--ledger", str(ledger), *args],
        cwd=cwd, env=_env(), capture_output=True, text=True, check=False,
    )


def _write_passing_dependency_results(root: Path, story_id: str) -> None:
    """premerge-check requires a dependency-check result for every story (BR-066)."""
    report_dir = root / ".current-work" / "dependency-check"
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / f"{story_id}.json").write_text("[]\n")


def _snapshot(root: Path) -> dict[str, tuple[bytes, int]]:
    return {
        str(path.relative_to(root)): (path.read_bytes(), path.stat().st_mtime_ns)
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _install_copy(checkout: Path) -> Path:
    """Write an installed copy that differs from packages/factory."""
    installed = checkout / ".agent-factory" / "factory"
    (installed / "scripts").mkdir(parents=True)
    (installed / "scripts" / "tool").write_text("installed\n")
    (installed / "VERSION").write_text("0.1\n")
    return installed


@pytest.fixture()
def factory_repo(tmp_path: Path) -> dict[str, Path]:
    """A repository with packages/factory, an ignored installed copy, and
    story ST-0350 dispatched from feature branch feat/x."""
    repo = tmp_path / "repo"
    for folder in ("backlog", "config", "src", "packages/factory/scripts"):
        (repo / folder).mkdir(parents=True)
    _git(repo.parent, "init", "-q", "-b", "dev", str(repo))
    (repo / "backlog" / "ST-0350.md").write_text(STORY.format(id="ST-0350"))
    (repo / "config" / "project.json").write_text('{"test_command": "true"}')
    (repo / ".gitignore").write_text(".current-work/\n/.agent-factory/\n")
    (repo / "src" / ".keep").write_text("")
    (repo / "packages" / "factory" / "scripts" / "tool").write_text("source\n")
    (repo / "packages" / "factory" / "NEW").write_text("only in source\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "init")
    feature = repo / ".current-work" / "feat" / "x" / "inv"
    _git(repo, "worktree", "add", "-q", "-b", "feat/x", str(feature))
    ledger = repo / ".current-work" / "feat" / "x" / "dispatch-ledger.yaml"
    for root in (repo, feature):
        _write_passing_dependency_results(root, "ST-0350")
        _install_copy(root)
    base = _git(repo, "rev-parse", "HEAD")
    for args in (
        ("init", "--base", base, "--stories", "ST-0350", "--feature-branch", "feat/x", "--yes"),
        ("plan", "--backlog-dir", "backlog"),
        ("prepare-wave", "1"),
        ("mark-dispatching", "ST-0350"),
        ("mark-dispatched", "ST-0350"),
    ):
        result = _dispatch(repo, ledger, *args)
        assert result.returncode == 0, (args, result.stdout, result.stderr)
    story = repo / ".current-work" / "feat" / "x" / "story" / "ST-0350"
    return {"repo": repo, "feature": feature, "story": story, "ledger": ledger}


@pytest.mark.spec("RL-18-IT-01")
def test_RL_18_IT_01_merge_story_copies_nothing_into_the_installed_copy(factory_repo):
    """Scenario: merge-story copies nothing into the installed copy."""
    repo, feature, ledger = (
        factory_repo["repo"], factory_repo["feature"], factory_repo["ledger"],
    )
    story = factory_repo["story"]
    (story / "src" / "ST-0350.txt").write_text("work\n")
    _git(story, "add", "-A")
    _git(story, "commit", "-qm", "story work")
    sha = _git(story, "rev-parse", "HEAD")
    assert _dispatch(repo, ledger, "verify-story", "ST-0350", "--sha", sha).returncode == 0
    before = {
        root: _snapshot(root / ".agent-factory" / "factory") for root in (repo, feature)
    }

    result = _dispatch(feature, ledger, "merge-story", "ST-0350")

    assert result.returncode == 0, result.stdout + result.stderr
    assert _git(feature, "rev-parse", "HEAD^2") == sha
    for root in (repo, feature):
        assert _snapshot(root / ".agent-factory" / "factory") == before[root]
