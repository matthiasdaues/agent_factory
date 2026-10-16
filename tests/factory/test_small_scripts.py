"""Regression tests for the small install, commit, and merge-config faults (ST-0307)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from conftest import REPO_ROOT, SOURCE_SCRIPTS_DIR, load_script


def _clean_env() -> dict[str, str]:
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True, capture_output=True, text=True, env=_clean_env(),
    ).stdout


def _init_factory(target: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SOURCE_SCRIPTS_DIR / "init-factory"),
         "--source", str(REPO_ROOT), "--target", str(target), *args],
        stdin=subprocess.DEVNULL, capture_output=True, text=True,
        env=_clean_env(), check=False,
    )


def _remove_factory(target: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SOURCE_SCRIPTS_DIR / "remove-factory"),
         "--target", str(target)],
        stdin=subprocess.DEVNULL, capture_output=True, text=True,
        env=_clean_env(), check=False,
    )


def _new_project(tmp_path: Path) -> Path:
    target = tmp_path / "project"
    target.mkdir()
    subprocess.run(["git", "init", "-q", str(target)], check=True, env=_clean_env())
    return target


# --- BUG-0080: commit-safe commits only what was staged ----------------------

# A hook that rewrites a staged file and fails, the way mdformat or ruff do.
REWRITING_HOOK = """#!/bin/sh
if grep -q raw staged.txt; then
  sed -i 's/raw/fixed/' staged.txt
  exit 1
fi
exit 0
"""


def _repo_with_rewriting_hook(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")
    (repo / "staged.txt").write_text("start\n")
    (repo / "wip.txt").write_text("start\n")
    _git(repo, "add", "staged.txt", "wip.txt")
    _git(repo, "commit", "-q", "-m", "initial")
    hook = repo / ".git" / "hooks" / "pre-commit"
    hook.write_text(REWRITING_HOOK)
    hook.chmod(0o755)
    return repo


def _commit_safe(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(SOURCE_SCRIPTS_DIR / "commit-safe"), *args],
        cwd=repo, capture_output=True, text=True, env=_clean_env(), check=False,
    )


def test_bug_0080_second_pass_leaves_unstaged_work_out_of_the_commit(tmp_path):
    repo = _repo_with_rewriting_hook(tmp_path)
    (repo / "staged.txt").write_text("raw\n")
    (repo / "wip.txt").write_text("work in progress\n")

    result = _commit_safe(repo, "-m", "fix: change staged (BUG-0080)", "staged.txt")

    assert result.returncode == 0, result.stderr
    assert _git(repo, "show", "--name-only", "--format=", "HEAD").split() == [
        "staged.txt"
    ]
    assert _git(repo, "show", "HEAD:staged.txt") == "fixed\n"
    assert _git(repo, "status", "--porcelain").splitlines() == [" M wip.txt"]


def test_bug_0080_message_flag_without_value_explains_itself(tmp_path):
    repo = _repo_with_rewriting_hook(tmp_path)

    result = _commit_safe(repo, "-m")

    assert result.returncode == 2
    assert "-m <message> is required" in result.stderr


# --- BUG-0081: merge-precommit-config adds no duplicate hooks ----------------

FACTORY_TEMPLATE = (
    REPO_ROOT / "packages/factory/config/pre-commit-config.yaml"
).read_text(encoding="utf-8")

PROJECT_WITH_OWN_MDFORMAT = """\
repos:
  - repo: local
    hooks:
      - id: mdformat
        name: mdformat
        entry: mdformat --wrap 80
        language: system
        types: [markdown]
"""


def test_bug_0081_repeated_merges_and_update_keep_one_copy_of_each_hook():
    mpc = load_script("merge-precommit-config")

    text = mpc.merge(PROJECT_WITH_OWN_MDFORMAT, FACTORY_TEMPLATE)
    again = mpc.merge(text, FACTORY_TEMPLATE)
    text = again if again is not None else text
    text = mpc.merge(text, FACTORY_TEMPLATE, update=True)

    assert again is None
    assert text.count("id: agent_factory_hook-link-check") == 1
    assert "id: agent_factory_hook-mdformat" not in text
    assert text.count("id: mdformat\n") == 1


# --- BUG-0091: spec-lint reads docs/spec/todo.md -----------------------------


def test_bug_0091_todo_check_reads_todo_md(tmp_path):
    spec_lint = load_script("spec-lint")
    (tmp_path / "todo.md").write_text("- [ ] Decide the retry policy\n")

    findings = spec_lint.check_todos(tmp_path, gate=True)

    assert len(findings) == 1
    assert findings[0].artifact == "docs/spec/todo.md"
    assert "1 unresolved todo item(s)" in findings[0].message


# --- BUG-0079: install faults outside remove-factory -------------------------


def test_bug_0079_codex_added_after_claude_restores_project_hooks_json(tmp_path):
    target = _new_project(tmp_path)
    (target / ".codex").mkdir()
    original = '{\n    "hooks": {\n        "Stop": []\n    }\n}\n'
    (target / ".codex/hooks.json").write_text(original)

    first = _init_factory(target, "--cli", "claude", "--project-name", "demo")
    assert first.returncode == 0, first.stderr
    second = _init_factory(target, "--cli", "claude", "codex")
    assert second.returncode == 0, second.stderr
    assert (target / ".codex/hooks.json").read_text() != original

    removed = _remove_factory(target)

    assert removed.returncode == 0, removed.stderr
    assert (target / ".codex/hooks.json").read_text() == original


def test_bug_0079_local_update_keeps_installer_records(tmp_path, monkeypatch):
    uf = load_script("update-factory")
    target = tmp_path / "target"
    factory = target / ".agent-factory" / "factory"
    (factory / "scripts").mkdir(parents=True)
    (factory / "scripts" / "step-guard").write_text("pass\n")
    uf._write_checksums(target, factory)
    source = tmp_path / "source"
    (source / "packages" / "factory").mkdir(parents=True)
    (source / "packages" / "factory" / "VERSION").write_text("1.1.0\n")
    manifest_path = target / uf.MANIFEST_PATH
    manifest_path.write_text(json.dumps({
        "version": 2,
        "factory_version": "1.0.0",
        "source_selector": "local",
        "factory_source": str(source),
        "resolved_source": "https://example.com/releases/1.0.0/",
        "archive_sha256": "abc123",
        "orientation": {},
    }))

    def _init_rewrites_manifest(src, tgt):
        # init-factory's write_manifest writes a fixed set of keys.
        (tgt / uf.MANIFEST_PATH).write_text(json.dumps({
            "version": 1, "factory_version": "1.0.0", "orientation": {},
            "factory_source": str(src),
        }))
        return 0

    monkeypatch.setattr(uf, "get_update_consent", lambda *a, **kw: True)
    monkeypatch.setattr(uf, "_run_init", _init_rewrites_manifest)

    assert uf.main(["--target", str(target)]) == 0

    manifest = json.loads(manifest_path.read_text())
    assert manifest["version"] == 2
    assert manifest["resolved_source"] == "https://example.com/releases/1.0.0/"
    assert manifest["archive_sha256"] == "abc123"
    assert manifest["factory_version"] == "1.1.0"


def test_bug_0079_migrate_layout_dry_run_reads_the_old_manifest(tmp_path, capsys):
    migrate = load_script("migrate-layout")
    (tmp_path / "factory").mkdir()
    (tmp_path / ".agent-factory").mkdir()
    old_manifest = tmp_path / ".agent-factory/factory-install.json"
    old_manifest.write_text(json.dumps({"remove_paths": ["factory"]}))

    assert migrate.main(["--dry-run", str(tmp_path)]) == 0

    out = capsys.readouterr().out
    assert "install.json not found" not in out
    assert "MANIFEST remove_paths: factory → .agent-factory/factory" in out
    assert json.loads(old_manifest.read_text()) == {"remove_paths": ["factory"]}
    assert (tmp_path / "factory").is_dir()


# --- BUG-0075: init-factory records the .claude/hooks/ it creates -------------


def test_bug_0075_removal_leaves_no_claude_hooks_dir_the_install_created(tmp_path):
    target = _new_project(tmp_path)
    (target / ".claude").mkdir()
    (target / ".claude/CLAUDE.md").write_text("# Project rules\n")

    installed = _init_factory(target, "--cli", "claude", "--project-name", "demo")
    assert installed.returncode == 0, installed.stderr
    manifest = json.loads((target / ".agent-factory/install.json").read_text())
    assert ".claude/hooks" in manifest["remove_paths"]

    removed = _remove_factory(target)

    assert removed.returncode == 0, removed.stderr
    assert not (target / ".claude/hooks").exists()
    assert (target / ".claude/CLAUDE.md").read_text().endswith("# Project rules\n")


def test_bug_0075_keeps_claude_hooks_dir_the_project_already_had(tmp_path):
    target = _new_project(tmp_path)
    (target / ".claude/hooks").mkdir(parents=True)

    installed = _init_factory(target, "--cli", "claude", "--project-name", "demo")
    assert installed.returncode == 0, installed.stderr
    manifest = json.loads((target / ".agent-factory/install.json").read_text())
    assert ".claude/hooks" not in manifest["remove_paths"]

    removed = _remove_factory(target)

    assert removed.returncode == 0, removed.stderr
    assert (target / ".claude/hooks").is_dir()


def test_bug_0075_removal_keeps_a_project_file_in_the_claude_hooks_dir(tmp_path):
    target = _new_project(tmp_path)
    (target / ".claude").mkdir()
    (target / ".claude/CLAUDE.md").write_text("# Project rules\n")
    installed = _init_factory(target, "--cli", "claude", "--project-name", "demo")
    assert installed.returncode == 0, installed.stderr
    own_hook = target / ".claude/hooks/my-hook.sh"
    own_hook.write_text("#!/bin/sh\nexit 0\n")

    removed = _remove_factory(target)

    assert removed.returncode == 0, removed.stderr
    assert own_hook.read_text() == "#!/bin/sh\nexit 0\n"
    assert [p.name for p in (target / ".claude/hooks").iterdir()] == ["my-hook.sh"]

