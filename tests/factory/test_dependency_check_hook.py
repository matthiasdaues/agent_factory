"""Integration tests for ST-0417: the `dependency-check` commit hook.

Owned rows of docs/spec/work/run-lifecycle-qa-strategy.md:

  - RL-10-IT-01 — a commit whose staged `.py` file breaks a rule fails in
    the hook, and git creates no commit.
  - RL-10-IT-02 — without `docs/spec/dependency-rules.dsl`, the hook prints
    the skip notice and passes, also without `uv` on PATH.
  - RL-10-IT-03 — the script called directly without the rules file exits 2.
  - RL-10-IT-04 — fitting a project without the rules file leaves the hook
    out of the generated configuration.

Each test builds its own repository in `tmp_path`. The hook runs through a
shell script in `.git/hooks/pre-commit` that holds the hook's entry, so the
tests need no `pre-commit install`. The rules file has one rule: `domain`
must not import `web`. The source root is the repository root, so `domain/`
and `web/` are top-level packages.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from conftest import REPO_ROOT

PRE_COMMIT_PATH = REPO_ROOT / "packages" / "factory" / "config" / "pre-commit-config.yaml"
METADATA_PATH = REPO_ROOT / "packages" / "factory" / "config" / "hook-metadata.yaml"
SCRIPTS = REPO_ROOT / "packages" / "factory" / "scripts"
HOOK_ID = "agent_factory_hook-dependency-check"
RULE = "domain must_not_depend_on web"
NOTICE = "dependency-check: no docs/spec/dependency-rules.dsl, skipped"


def hook_entry() -> str:
    hooks = {
        hook["id"]: hook
        for repo in yaml.safe_load(PRE_COMMIT_PATH.read_text(encoding="utf-8"))["repos"]
        for hook in repo["hooks"]
    }
    return hooks[HOOK_ID]["entry"].strip()


def git_env(path: str | None = None) -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "SKIP"))}
    env.update(
        GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
        GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t",
    )
    if path is not None:
        env["PATH"] = path
    return env


def run_git(project: Path, *args: str, path: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=project, env=git_env(path),
        capture_output=True, text=True, check=False,
    )


def make_project(tmp_path: Path, *, rules: bool) -> Path:
    """A repository with one commit, the hook installed, and the Factory's
    `dependency-check` script linked into `.agent-factory/`."""
    project = tmp_path / "project"
    project.mkdir()
    assert run_git(project, "init", "-q", "-b", "dev").returncode == 0
    (project / "README.md").write_text("init\n")
    run_git(project, "add", "README.md")
    assert run_git(project, "commit", "-qm", "init").returncode == 0

    if rules:
        dsl = project / "docs" / "spec" / "dependency-rules.dsl"
        dsl.parent.mkdir(parents=True)
        dsl.write_text(RULE + "\n")
    (project / "web").mkdir()
    (project / "web" / "__init__.py").write_text("")
    (project / "web" / "views.py").write_text("def render():\n    return 'ok'\n")

    scripts = project / ".agent-factory" / "factory" / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "dependency-check").symlink_to(SCRIPTS / "dependency-check")
    hook = project / ".git" / "hooks" / "pre-commit"
    hook.parent.mkdir(exist_ok=True)
    hook.write_text("#!/bin/sh\n" + hook_entry() + "\n")
    hook.chmod(0o755)
    return project


def stage_breaking_import(project: Path) -> None:
    (project / "domain").mkdir()
    (project / "domain" / "__init__.py").write_text("")
    (project / "domain" / "order.py").write_text("from web.views import render\n")
    run_git(project, "add", "domain", "web")


def path_without_uv(tmp_path: Path) -> str:
    """PATH with `git` and `sh` and none of the directories that hold `uv`."""
    keep = [
        entry for entry in os.environ.get("PATH", "").split(os.pathsep)
        if entry and not (Path(entry) / "uv").exists()
    ]
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for tool in ("git", "sh", "bash"):
        found = shutil.which(tool)
        if found:
            (bin_dir / tool).symlink_to(found)
    path = os.pathsep.join([str(bin_dir), *keep])
    assert shutil.which("uv", path=path) is None
    return path


def head(project: Path) -> str:
    return run_git(project, "rev-parse", "HEAD").stdout.strip()


@pytest.mark.spec("RL-10-IT-01")
@pytest.mark.skipif(shutil.which("uv") is None, reason="uv not installed")
def test_st_0417_commit_that_breaks_a_rule_fails_in_the_hook(tmp_path: Path):
    project = make_project(tmp_path, rules=True)
    before = head(project)
    stage_breaking_import(project)

    result = run_git(project, "commit", "-qm", "add order")

    output = result.stdout + result.stderr
    assert result.returncode == 1, output
    assert RULE in output
    assert "domain/order.py" in output
    assert head(project) == before


@pytest.mark.spec("RL-10-IT-01")
@pytest.mark.skipif(shutil.which("uv") is None, reason="uv not installed")
def test_st_0417_commit_that_keeps_the_rules_passes_the_hook(tmp_path: Path):
    project = make_project(tmp_path, rules=True)
    before = head(project)
    run_git(project, "add", "web")

    result = run_git(project, "commit", "-qm", "add web")

    assert result.returncode == 0, result.stdout + result.stderr
    assert head(project) != before


@pytest.mark.spec("RL-10-IT-02")
def test_st_0417_project_without_rules_skips_the_hook_without_uv(tmp_path: Path):
    project = make_project(tmp_path, rules=False)
    before = head(project)
    stage_breaking_import(project)

    result = run_git(project, "commit", "-qm", "add order", path=path_without_uv(tmp_path))

    output = result.stdout + result.stderr
    assert result.returncode == 0, output
    assert NOTICE in output
    assert head(project) != before


@pytest.mark.spec("RL-10-IT-03")
@pytest.mark.skipif(shutil.which("uv") is None, reason="uv not installed")
def test_st_0417_script_called_directly_without_rules_exits_2(tmp_path: Path):
    project = make_project(tmp_path, rules=False)

    result = subprocess.run(
        [str(SCRIPTS / "dependency-check")],
        cwd=project, capture_output=True, text=True, check=False,
    )

    assert result.returncode == 2, result.stdout + result.stderr
    assert "DSL file not found" in result.stderr


def fitting_template(repo_root: Path) -> str:
    result = subprocess.run(
        [
            sys.executable, str(SCRIPTS / "hook-subset"), "generate",
            "--pre-commit", str(PRE_COMMIT_PATH),
            "--metadata", str(METADATA_PATH),
            "--repo-root", str(repo_root),
        ],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout


@pytest.mark.spec("RL-10-IT-04")
def test_st_0417_fitting_leaves_the_hook_out_without_a_rules_file(tmp_path: Path):
    (tmp_path / "docs" / "spec").mkdir(parents=True)

    assert HOOK_ID not in fitting_template(tmp_path)

    (tmp_path / "docs" / "spec" / "dependency-rules.dsl").write_text(RULE + "\n")
    assert HOOK_ID in fitting_template(tmp_path)
