"""Shipped text names the current layout and install record (BUG-0045, BUG-0046)."""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

import pytest

from conftest import REPO_ROOT

FACTORY = REPO_ROOT / "packages" / "factory"
SHIPPED_SUFFIXES = {".md", ".sh", ".ts", ".yaml", ".py", ".conf", ""}
# Lines that name the old layout on purpose, to recognise or migrate it.
LEGACY_ALLOWED = {
    ("scripts/init-factory", "``factory/config/``"),
    ("scripts/init-factory", "factory/config/AGENTS"),
    ("scripts/merge-precommit-config", '"factory/scripts/" in entry'),
}
OLD_LAYOUT = re.compile(r"(?<![\w./-])factory/(scripts|agents|skills|playbooks|rulebooks|config|docs)/")


def _shipped_files():
    for path in FACTORY.rglob("*"):
        if not path.is_file() or path.suffix not in SHIPPED_SUFFIXES:
            continue
        if "reports" in path.relative_to(FACTORY).parts or path.name == "CHANGELOG.md":
            continue  # historical records keep the paths of their time
        yield path


def test_no_shipped_text_names_the_old_factory_layout():
    """BUG-0045: the factory/ layout no longer exists."""
    hits = [
        f"{path.relative_to(REPO_ROOT)}:{n}"
        for path in _shipped_files()
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
        if OLD_LAYOUT.search(line)
        and not any(
            str(path.relative_to(FACTORY)) == name and marker in line
            for name, marker in LEGACY_ALLOWED
        )
    ]
    assert hits == []


def test_no_check_reads_the_old_install_record_name():
    """BUG-0046: the installer writes .agent-factory/install.json. Only
    migrate-layout may name the old file, because it renames it."""
    hits = [
        str(path.relative_to(REPO_ROOT))
        for path in FACTORY.rglob("*")
        if path.is_file()
        and path.suffix in {".sh", ".ts", ".py", ""}
        and path.name != "migrate-layout"
        and "factory-install.json" in path.read_text(encoding="utf-8", errors="ignore")
    ]
    assert hits == []


def _project(tmp_path: Path, recorded_hash: str | None) -> Path:
    project = tmp_path / "project"
    (project / "packages" / "factory").mkdir(parents=True)
    (project / "packages" / "factory" / "VERSION").write_text("1\n")
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    for args in (["init", "-q"], ["add", "-A"], ["commit", "-qm", "init"]):
        subprocess.run(["git", *args], cwd=project, env=env, check=True)
    if recorded_hash == "current":
        recorded_hash = subprocess.run(
            ["git", "rev-parse", "HEAD:packages/factory"], cwd=project, env=env,
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    (project / ".agent-factory").mkdir()
    (project / ".agent-factory" / "install.json").write_text(
        json.dumps({"factory_tree_hash": recorded_hash})
    )
    return project


@pytest.mark.parametrize(("recorded", "warns"), [("stale", True), ("current", False)])
def test_freshness_hook_reads_the_install_record(tmp_path, recorded, warns):
    """BUG-0046: the hook warns when the recorded tree hash is stale."""
    project = _project(tmp_path, recorded)
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(CLAUDE_PROJECT_DIR=str(project), SESSION_ID=f"test-{recorded}")

    result = subprocess.run(
        ["bash", str(FACTORY / "config" / "hooks" / "check-factory-freshness.sh")],
        input="{}", capture_output=True, text=True, env=env, check=False,
    )

    assert result.returncode == 0
    assert ("out of sync" in result.stderr) is warns
