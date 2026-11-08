"""Regression tests for BUG-0111: factory hooks passed silently when
`.agent-factory/` was missing.

A clone marks that it installed the factory with the local git config key
`agent-factory.installed`. Without the key, a colleague who never
installed the factory commits untouched. With the key, a missing factory
folder fails the hook with a message that names the way out.
"""

from __future__ import annotations

import shlex
import subprocess
from pathlib import Path

import pytest
import yaml
from conftest import REPO_ROOT, load_script

inf = load_script("init-factory")
rf = load_script("remove-factory")

TEMPLATE = REPO_ROOT / "packages" / "factory" / "config" / "pre-commit-config.yaml"
REPO_CONFIG = REPO_ROOT / ".pre-commit-config.yaml"
GUIDE = REPO_ROOT / "packages" / "factory" / "docs" / "factory-guide.md"

def _factory_entries(path: Path) -> list[tuple[str, str]]:
    """(hook id, entry) for every agent_factory_hook-* hook in `path`,
    read as YAML, so a folded entry (BUG-0113) counts as its value."""
    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    return [
        (hook["id"], hook["entry"])
        for repo in config["repos"]
        for hook in repo.get("hooks", [])
        if hook["id"].startswith("agent_factory_hook-")
    ]


TEMPLATE_ENTRIES = _factory_entries(TEMPLATE)


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


@pytest.fixture
def bare_clone(tmp_path: Path) -> Path:
    """A git repository with no `.agent-factory/` anywhere."""
    repo = tmp_path / "project"
    repo.mkdir()
    _git(repo, "init", "-q")
    return repo


def _run_entry(entry: str, repo: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        shlex.split(entry), cwd=repo, capture_output=True, text=True, check=False,
    )


def test_template_has_every_factory_hook():
    assert len(TEMPLATE_ENTRIES) == 11


@pytest.mark.parametrize("hook_id,entry", TEMPLATE_ENTRIES, ids=[i for i, _ in TEMPLATE_ENTRIES])
def test_clone_without_factory_passes_silently(hook_id, entry, bare_clone):
    result = _run_entry(entry, bare_clone)

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""


@pytest.mark.parametrize("hook_id,entry", TEMPLATE_ENTRIES, ids=[i for i, _ in TEMPLATE_ENTRIES])
def test_installed_clone_with_missing_factory_fails(hook_id, entry, bare_clone):
    _git(bare_clone, "config", "--local", "agent-factory.installed", "true")

    result = _run_entry(entry, bare_clone)

    # pre-commit prints `- hook id: <id>` above a failing hook's output,
    # so the message names the variable, not the id.
    assert result.returncode == 1
    assert ".agent-factory/ missing" in result.stderr
    assert "update-factory" in result.stderr
    assert "SKIP=<hook id>" in result.stderr


@pytest.mark.parametrize("hook_id,entry", TEMPLATE_ENTRIES, ids=[i for i, _ in TEMPLATE_ENTRIES])
def test_key_set_to_false_counts_as_not_installed(hook_id, entry, bare_clone):
    _git(bare_clone, "config", "--local", "agent-factory.installed", "false")

    result = _run_entry(entry, bare_clone)

    assert result.returncode == 0
    assert result.stderr == ""


def test_repo_config_factory_block_matches_template():
    """This repo's own factory block carries the same entries, so a
    refresh by update-factory (BUG-0110) changes none of them."""
    assert _factory_entries(REPO_CONFIG) == TEMPLATE_ENTRIES


def test_guide_documents_the_key():
    text = GUIDE.read_text(encoding="utf-8")
    assert "agent-factory.installed" in text
    assert "[ -d \"$AF\" ] || exit 0" not in text


class TestInitMarksClone:
    def test_sets_the_key(self, bare_clone):
        report: list[str] = []

        inf.mark_clone_installed(bare_clone, report)

        out = subprocess.run(
            ["git", "config", "--local", "--get", "agent-factory.installed"],
            cwd=bare_clone, capture_output=True, text=True, check=True,
        )
        assert out.stdout.strip() == "true"

    def test_no_git_repository_is_reported_not_raised(self, tmp_path):
        report: list[str] = []

        inf.mark_clone_installed(tmp_path, report)

        assert any("agent-factory.installed" in line for line in report)


class TestRemoveUnmarksClone:
    def test_unsets_the_key(self, bare_clone):
        _git(bare_clone, "config", "--local", "agent-factory.installed", "true")

        rf.unmark_clone_installed(bare_clone)

        out = subprocess.run(
            ["git", "config", "--local", "--get", "agent-factory.installed"],
            cwd=bare_clone, capture_output=True, text=True, check=False,
        )
        assert out.returncode == 1

    def test_unset_key_is_not_an_error(self, bare_clone):
        rf.unmark_clone_installed(bare_clone)


# ---------------------------------------------------------------------------
# BUG-0113: the generated block passes yamllint and still runs from a
# linked worktree
# ---------------------------------------------------------------------------

mpc = load_script("merge-precommit-config")

STALE_CONFIG = """\
---
repos:
  - repo: local
    hooks:
      - id: agent_factory_hook-backlog-lint
        name: "agent_factory: backlog-lint"
        entry: bash -c '[ -d factory ] || exit 0; exec factory/scripts/backlog-lint' --
        language: system
        args: [--exclude, "ST-*-details.md"]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
"""


def _yamllint_default(path: Path) -> subprocess.CompletedProcess:
    import sys

    return subprocess.run(
        [sys.executable, "-m", "yamllint", "--strict", "-d", "default", str(path)],
        capture_output=True, text=True, check=False,
    )


def test_refreshed_config_passes_yamllint_defaults(tmp_path):
    template = TEMPLATE.read_text(encoding="utf-8")
    config = tmp_path / ".pre-commit-config.yaml"
    config.write_text(mpc.merge(STALE_CONFIG, template, update=True), encoding="utf-8")

    result = _yamllint_default(config)

    assert result.returncode == 0, result.stdout


def test_fresh_config_passes_yamllint_defaults(tmp_path):
    config = tmp_path / ".pre-commit-config.yaml"
    config.write_text(inf._fresh_precommit_text(TEMPLATE), encoding="utf-8")

    result = _yamllint_default(config)

    assert result.returncode == 0, result.stdout


def _gate_names() -> set[str]:
    import re

    return {
        m.group(1)
        for _, entry in TEMPLATE_ENTRIES
        for m in re.finditer(r'factory/scripts/([\w-]+)', entry)
    }


@pytest.mark.parametrize("hook_id,entry", TEMPLATE_ENTRIES, ids=[i for i, _ in TEMPLATE_ENTRIES])
def test_hook_runs_the_gate_from_a_linked_worktree(hook_id, entry, tmp_path):
    """`.agent-factory/` exists only in the main checkout; the hook finds
    it through the git common directory and runs the gate."""
    main = tmp_path / "main"
    main.mkdir()
    _git(main, "init", "-q")
    _git(main, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "base")
    scripts = main / ".agent-factory" / "factory" / "scripts"
    scripts.mkdir(parents=True)
    for name in _gate_names():
        stub = scripts / name
        stub.write_text('#!/bin/sh\necho "ran $(basename "$0")"\n', encoding="utf-8")
        stub.chmod(0o755)
    worktree = tmp_path / "story"
    _git(main, "worktree", "add", "-q", "-b", "story", str(worktree))
    _git(main, "config", "--local", "agent-factory.installed", "true")

    result = _run_entry(entry, worktree)

    assert result.returncode == 0, result.stderr
    assert "ran " in result.stdout
