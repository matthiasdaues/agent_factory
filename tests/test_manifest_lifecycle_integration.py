"""Integration tests for the step manifest lifecycle (Layer 3e).

Covers manifest creation on prepare-wave/prepare-story, no-supersede
protection, removal on completion, per-worktree independence, and forced
recovery of a stale manifest via `dispatch clear-manifest --force`.
"""

from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

DISPATCH_SCRIPT = (
    Path(__file__).resolve().parent.parent / "factory" / "scripts" / "dispatch"
)
SCRIPT_DIR = Path(__file__).resolve().parent.parent / "factory" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))
dispatch_lib = importlib.import_module("dispatch_lib")

Ledger = dispatch_lib.Ledger
StoryEntry = dispatch_lib.StoryEntry
StoryState = dispatch_lib.StoryState
ManifestExistsError = dispatch_lib.ManifestExistsError
write_manifest = dispatch_lib.write_manifest
remove_manifest = dispatch_lib.remove_manifest
clear_manifest_force = dispatch_lib.clear_manifest_force
MANIFEST_FILENAME = dispatch_lib.MANIFEST_FILENAME


def _git_env(tmp_path: Path) -> dict[str, str]:
    """Return a git environment isolated from user-level configuration."""
    return {
        **os.environ,
        "GIT_CONFIG_NOSYSTEM": "1",
        "HOME": str(tmp_path),
    }


def _run_dispatch(*args: str, cwd: Path, tmp_path: Path) -> subprocess.CompletedProcess[str]:
    """Invoke the dispatch CLI as a subprocess."""
    return subprocess.run(
        [sys.executable, str(DISPATCH_SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=cwd,
        check=False,
        env=_git_env(tmp_path),
    )


def _git(repo: Path, tmp_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Run a git command inside the temporary repository."""
    return subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        cwd=repo,
        check=False,
        env=_git_env(tmp_path),
    )


def _init_repo(tmp_path: Path) -> Path:
    """Create a minimal git repository for manifest lifecycle tests."""
    repo = tmp_path / "repo"
    repo.mkdir()

    for args in (
        ("init", "--initial-branch=main"),
        ("config", "user.email", "test@test.com"),
        ("config", "user.name", "Test"),
        ("config", "core.hooksPath", "/dev/null"),
    ):
        result = _git(repo, tmp_path, *args)
        assert result.returncode == 0, result.stderr

    config_dir = repo / "config"
    config_dir.mkdir()
    (config_dir / "project.json").write_text(
        json.dumps({"project_name": "test", "test_command": "echo ok"})
    )

    result = _git(repo, tmp_path, "add", "-A")
    assert result.returncode == 0, result.stderr
    result = _git(repo, tmp_path, "commit", "--no-verify", "-m", "initial")
    assert result.returncode == 0, result.stderr
    return repo


def _write_backlog_story(
    repo: Path,
    story_id: str,
    *,
    deps: list[str] | None = None,
    traces: list[str] | None = None,
    outputs: list[str] | None = None,
) -> None:
    """Write a minimal backlog story file with the given frontmatter."""
    backlog_dir = repo / "backlog"
    backlog_dir.mkdir(exist_ok=True)
    deps = deps or []
    traces = traces or []
    outputs = outputs or []

    def _yaml_list(items: list[str]) -> str:
        if not items:
            return "[]"
        return "\n" + "\n".join(f'  - "{i}"' for i in items)

    text = (
        "---\n"
        f"id: {story_id}\n"
        f"deps: {_yaml_list(deps)}\n"
        f"traces: {_yaml_list(traces)}\n"
        f"outputs: {_yaml_list(outputs)}\n"
        "---\n\n"
        f"# {story_id}\n"
    )
    (backlog_dir / f"{story_id}.md").write_text(text)


def _write_ledger(repo: Path, *entries: StoryEntry) -> Path:
    """Persist a dispatch ledger containing the provided entries."""
    ledger = Ledger()
    for entry in entries:
        ledger.stories[entry.id] = entry
    ledger_path = repo / ".agent-factory" / "dispatch-ledger.yaml"
    ledger.save(ledger_path)
    return ledger_path


def _load_ledger(repo: Path) -> Ledger:
    """Load the repository's default dispatch ledger."""
    return Ledger.load(repo / ".agent-factory" / "dispatch-ledger.yaml")


def _worktree_path(repo: Path, story_id: str) -> Path:
    """Return the expected worktree path for one story branch."""
    return repo / ".agent-factory" / "worktrees" / f"story-{story_id}"


def _manifest_path(worktree: Path, feature_branch: str, story_branch: str) -> Path:
    """Return the expected manifest path for one worktree/story branch."""
    return worktree / ".current_work" / feature_branch / story_branch / MANIFEST_FILENAME


def test_prepare_wave_writes_manifest(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _write_backlog_story(
        repo,
        "ST-001",
        traces=["Feature: Widget"],
        outputs=["src/widget.py"],
    )
    _write_ledger(repo, StoryEntry(id="ST-001", wave=1, status=StoryState.PENDING))

    result = _run_dispatch("prepare-wave", "1", cwd=repo, tmp_path=tmp_path)
    assert result.returncode == 0, result.stderr

    worktree = _worktree_path(repo, "ST-001")
    manifest_path = _manifest_path(worktree, "main", "story/ST-001")
    assert manifest_path.exists()

    manifest = yaml.safe_load(manifest_path.read_text())
    assert manifest["schema_version"] == 1
    assert manifest["step"] == "implement"
    assert manifest["playbook"] == "developer"
    assert manifest["phase"] == "red-green"
    assert manifest["outputs"] == ["src/widget.py"]
    assert "Feature: Widget" in manifest["inputs"]
    assert manifest["max_input_tokens"] == 100_000

    ledger = _load_ledger(repo)
    assert ledger.stories["ST-001"].feature_branch == "main"


def test_prepare_story_writes_manifest(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    merge_sha = _git(repo, tmp_path, "rev-parse", "HEAD").stdout.strip()
    _write_backlog_story(repo, "ST-006", outputs=["src/foo.py"])
    _write_ledger(
        repo,
        StoryEntry(id="ST-005", wave=1, status=StoryState.DONE, commit_sha=merge_sha),
        StoryEntry(id="ST-006", wave=1, status=StoryState.PENDING, deps=["ST-005"]),
    )

    result = _run_dispatch("prepare-story", "ST-006", cwd=repo, tmp_path=tmp_path)
    assert result.returncode == 0, result.stderr

    worktree = _worktree_path(repo, "ST-006")
    manifest_path = _manifest_path(worktree, "main", "story/ST-006")
    assert manifest_path.exists()

    manifest = yaml.safe_load(manifest_path.read_text())
    assert manifest["schema_version"] == 1
    assert manifest["outputs"] == ["src/foo.py"]

def test_playbook_step_declaration_writes_manifest(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    worktree = repo / "worktree-ST-777"
    branch = "story/ST-777"
    _git(repo, tmp_path, "branch", branch, "HEAD")
    _git(repo, tmp_path, "worktree", "add", str(worktree), branch)

    playbook = repo / "factory" / "playbooks" / "feature-addition.md"
    playbook.parent.mkdir(parents=True, exist_ok=True)
    playbook.write_text(
        "---\n"
        "title: Feature Addition Playbook\n"
        "category: orchestration\n"
        "type: runbook\n"
        "scenario: feature-addition\n"
        "version: 1.2.0\n"
        "steps:\n"
        "  - name: implement-stories\n"
        "    inputs:\n"
        "      - 'docs/proposals/**/*.md'\n"
        "    outputs:\n"
        "      - 'factory/**/*.py'\n"
        "      - 'tests/**/*.py'\n"
        "    max_input_tokens: 64000\n"
        "---\n\n"
        "# Feature Addition Playbook\n"
    )

    step_decl = dispatch_lib.load_playbook_step_declaration(playbook, "implement-stories")
    assert step_decl is not None

    story_meta = {
        "deps": ["ST-001"],
        "traces": ["Feature: Widget"],
        "outputs": ["src/ignored.py"],
        "max_input_tokens": 100_000,
    }
    write_manifest(worktree, "main", branch, story_meta, step_declaration=step_decl)

    manifest_path = _manifest_path(worktree, "main", branch)
    manifest = yaml.safe_load(manifest_path.read_text())
    assert manifest["inputs"] == ["docs/proposals/**/*.md"]
    assert manifest["outputs"] == ["factory/**/*.py", "tests/**/*.py"]
    assert manifest["max_input_tokens"] == 64_000


def test_no_supersede_blocks_second_write(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    worktree = repo / "worktree-ST-999"
    branch = "story/ST-999"
    _git(repo, tmp_path, "branch", branch, "HEAD")
    _git(repo, tmp_path, "worktree", "add", str(worktree), branch)

    story_meta = {"deps": [], "traces": [], "outputs": ["src/x.py"]}
    write_manifest(worktree, "main", branch, story_meta)

    with pytest.raises(ManifestExistsError):
        write_manifest(worktree, "main", branch, story_meta)


def test_manifest_removed_on_completion(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _write_backlog_story(repo, "ST-001", outputs=["src/widget.py"])
    _write_ledger(repo, StoryEntry(id="ST-001", wave=1, status=StoryState.PENDING))

    result = _run_dispatch("prepare-wave", "1", cwd=repo, tmp_path=tmp_path)
    assert result.returncode == 0, result.stderr

    worktree = _worktree_path(repo, "ST-001")
    manifest_path = _manifest_path(worktree, "main", "story/ST-001")
    assert manifest_path.exists()

    dispatching = _run_dispatch("mark-dispatching", "ST-001", cwd=repo, tmp_path=tmp_path)
    assert dispatching.returncode == 0, dispatching.stderr
    dispatched = _run_dispatch("mark-dispatched", "ST-001", cwd=repo, tmp_path=tmp_path)
    assert dispatched.returncode == 0, dispatched.stderr

    done = _run_dispatch("mark-done", "ST-001", cwd=repo, tmp_path=tmp_path)
    assert done.returncode == 0, done.stderr

    assert not manifest_path.exists()

    ledger = _load_ledger(repo)
    assert ledger.stories["ST-001"].status == StoryState.DONE


def test_clear_manifest_force_removes_stale(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _write_backlog_story(repo, "ST-001", outputs=["src/widget.py"])
    _write_ledger(repo, StoryEntry(id="ST-001", wave=1, status=StoryState.PENDING))

    result = _run_dispatch("prepare-wave", "1", cwd=repo, tmp_path=tmp_path)
    assert result.returncode == 0, result.stderr

    worktree = _worktree_path(repo, "ST-001")
    manifest_path = _manifest_path(worktree, "main", "story/ST-001")
    assert manifest_path.exists()

    cleared = _run_dispatch(
        "clear-manifest", "--force", "--worktree", str(worktree), cwd=repo, tmp_path=tmp_path
    )
    assert cleared.returncode == 0, cleared.stderr
    assert "warning" in cleared.stderr.lower()
    assert not manifest_path.exists()

    ledger = _load_ledger(repo)
    recoveries = ledger.stories["ST-001"].manifest_recoveries
    assert len(recoveries) == 1
    assert recoveries[0]["existed"] is True


def test_clear_manifest_without_force_rejected(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _write_backlog_story(repo, "ST-001", outputs=["src/widget.py"])
    _write_ledger(repo, StoryEntry(id="ST-001", wave=1, status=StoryState.PENDING))

    result = _run_dispatch("prepare-wave", "1", cwd=repo, tmp_path=tmp_path)
    assert result.returncode == 0, result.stderr

    worktree = _worktree_path(repo, "ST-001")
    manifest_path = _manifest_path(worktree, "main", "story/ST-001")

    cleared = _run_dispatch(
        "clear-manifest", "--worktree", str(worktree), cwd=repo, tmp_path=tmp_path
    )
    assert cleared.returncode != 0
    assert manifest_path.exists()


def test_independent_worktree_manifests(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _write_backlog_story(repo, "ST-001", outputs=["src/a.py"])
    _write_backlog_story(repo, "ST-002", outputs=["src/b.py"])
    _write_ledger(
        repo,
        StoryEntry(id="ST-001", wave=1, status=StoryState.PENDING),
        StoryEntry(id="ST-002", wave=1, status=StoryState.PENDING),
    )

    result = _run_dispatch("prepare-wave", "1", cwd=repo, tmp_path=tmp_path)
    assert result.returncode == 0, result.stderr

    worktree_1 = _worktree_path(repo, "ST-001")
    worktree_2 = _worktree_path(repo, "ST-002")
    manifest_1 = _manifest_path(worktree_1, "main", "story/ST-001")
    manifest_2 = _manifest_path(worktree_2, "main", "story/ST-002")
    assert manifest_1.exists()
    assert manifest_2.exists()

    for cmd in ("mark-dispatching", "mark-dispatched", "mark-done"):
        outcome = _run_dispatch(cmd, "ST-001", cwd=repo, tmp_path=tmp_path)
        assert outcome.returncode == 0, outcome.stderr

    assert not manifest_1.exists()
    assert manifest_2.exists()

    manifest = yaml.safe_load(manifest_2.read_text())
    assert manifest["outputs"] == ["src/b.py"]
