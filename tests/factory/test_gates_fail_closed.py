"""Gates fail closed (BUG-0039, BUG-0040, BUG-0041)."""

from __future__ import annotations

import os
import shlex
import subprocess
from pathlib import Path

import pytest
import yaml

from conftest import REPO_ROOT, SOURCE_SCRIPTS_DIR

CONSUMER_CONFIG = REPO_ROOT / "packages" / "factory" / "config" / "pre-commit-config.yaml"
SOURCE_CONFIG = REPO_ROOT / ".pre-commit-config.yaml"


def _env() -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(
        GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
        GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t",
    )
    return env


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd, cwd=cwd, env=_env(), capture_output=True, text=True, check=False
    )


def _no_frontmatter_stories(backlog: Path, count: int) -> None:
    backlog.mkdir(parents=True)
    for n in range(1, count + 1):
        (backlog / f"ST-{n:04d}.md").write_text("no frontmatter\n")


def test_backlog_lint_exits_1_at_256_errors(tmp_path):
    """BUG-0039: 256 errors no longer wrap around to exit code 0."""
    _no_frontmatter_stories(tmp_path / "backlog", 256)

    result = _run(
        [str(SOURCE_SCRIPTS_DIR / "backlog-lint"), "--backlog-dir", "backlog"], tmp_path
    )

    assert "256 error(s)" in result.stdout + result.stderr
    assert result.returncode == 1


def test_spec_lint_exits_1_not_the_error_count(tmp_path):
    """BUG-0039: two errors exit 1, not 2, the code for usage errors."""
    spec = tmp_path / "docs" / "spec"
    spec.mkdir(parents=True)
    (spec / "a.md").write_text("# Spec\n\nSee BR-901 and BR-902.\n")

    result = _run([str(SOURCE_SCRIPTS_DIR / "spec-lint")], tmp_path)

    assert "2 error(s)" in result.stdout + result.stderr
    assert result.returncode == 1


def _hooks(config: Path) -> list[dict]:
    data = yaml.safe_load(config.read_text())
    return [hook for repo in data["repos"] for hook in repo.get("hooks", [])]


def test_source_hooks_run_the_source_scripts():
    """BUG-0040: the source repository's own hooks never call the installed
    copy, so they work in worktrees and check the code being changed.
    matrix-lint is left to BUG-0029."""
    offenders = [
        hook["id"]
        for hook in _hooks(SOURCE_CONFIG)
        if not hook["id"].startswith("agent_factory_hook-")
        and hook["id"] != "matrix-lint"
        and ".agent-factory/factory/scripts/" in hook.get("entry", "")
    ]
    assert offenders == []


def _consumer_command(hook_id: str) -> list[str]:
    hook = next(h for h in _hooks(CONSUMER_CONFIG) if h["id"] == hook_id)
    return shlex.split(hook["entry"])


@pytest.fixture()
def project_with_worktree(tmp_path: Path) -> dict[str, Path]:
    """A project with an installed link-check stub and a linked worktree."""
    project = tmp_path / "project"
    project.mkdir()
    _run(["git", "init", "-q", "-b", "dev"], project)
    (project / ".gitignore").write_text(".agent-factory/\n.current-work/\n")
    (project / "README.md").write_text("# Readme\n")
    _run(["git", "add", "-A"], project)
    _run(["git", "commit", "-qm", "init"], project)
    marker = tmp_path / "link-check-ran"
    stub = project / ".agent-factory" / "factory" / "scripts" / "link-check"
    stub.parent.mkdir(parents=True)
    stub.write_text(f'#!/bin/sh\necho "$@" > "{marker}"\n')
    stub.chmod(0o755)
    worktree = project / ".current-work" / "feat"
    result = _run(["git", "worktree", "add", "-q", "-b", "feat", str(worktree)], project)
    assert result.returncode == 0, result.stderr
    return {"project": project, "worktree": worktree, "marker": marker, "stub": stub}


def test_consumer_gate_runs_in_a_linked_worktree(project_with_worktree):
    """BUG-0041: a consumer hook run from a linked worktree finds the main
    checkout's .agent-factory/ and runs the gate."""
    worktree, marker = project_with_worktree["worktree"], project_with_worktree["marker"]

    result = _run(_consumer_command("agent_factory_hook-link-check") + ["README.md"], worktree)

    assert result.returncode == 0, result.stderr
    assert marker.read_text().strip() == "README.md"


def test_consumer_gate_skips_without_any_factory(project_with_worktree):
    """BUG-0041: without .agent-factory/ anywhere, the hook still lets a
    teammate commit."""
    project = project_with_worktree["project"]
    project_with_worktree["stub"].unlink()
    (project / ".agent-factory" / "factory" / "scripts").rmdir()
    (project / ".agent-factory" / "factory").rmdir()
    (project / ".agent-factory").rmdir()

    result = _run(
        _consumer_command("agent_factory_hook-link-check") + ["README.md"],
        project_with_worktree["worktree"],
    )

    assert result.returncode == 0
    assert not project_with_worktree["marker"].exists()
