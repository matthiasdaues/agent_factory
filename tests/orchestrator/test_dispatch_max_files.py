"""Tests for premerge-check --max-files scaling in dispatch (ST-0160).

Covers `dispatch merge-story`'s per-story --max-files scaling (derived from
the story's declared `outputs` list length) and the `dispatch
suggest-merge-args` subcommand, which sums declared output counts across the
whole ledger to recommend a --max-files value for the final feature-to-dev
merge.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
DISPATCH_SCRIPT = _ROOT / "factory" / "scripts" / "dispatch"
SCRIPT_DIR = _ROOT / "factory" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import importlib

dispatch_lib = importlib.import_module("dispatch_lib")

Ledger = dispatch_lib.Ledger
StoryEntry = dispatch_lib.StoryEntry
StoryState = dispatch_lib.StoryState


def _git_env(tmp_path: Path) -> dict[str, str]:
    """Return a git environment isolated from user-level configuration."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", HOME=str(tmp_path))
    return env


def _run_dispatch(
    *args: str, cwd: Path, tmp_path: Path
) -> subprocess.CompletedProcess[str]:
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


def _init_repo(tmp_path: Path, test_command: str = "true") -> Path:
    """Create a minimal git repository with a passing test_command."""
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
        json.dumps({"project_name": "test", "test_command": test_command})
    )

    (repo / "backlog").mkdir()

    result = _git(repo, tmp_path, "add", "-A")
    assert result.returncode == 0, result.stderr
    result = _git(repo, tmp_path, "commit", "--no-verify", "-m", "initial")
    assert result.returncode == 0, result.stderr
    return repo


def _write_story_file(repo: Path, story_id: str, outputs: list[str]) -> None:
    """Write a minimal backlog story file declaring the given outputs."""
    outputs_yaml = "\n".join(f'  - "{o}"' for o in outputs)
    text = (
        "---\n"
        f"id: {story_id}\n"
        "status: dispatched\n"
        "quality-gates: []\n"
        "outputs:\n"
        f"{outputs_yaml}\n"
        "---\n\n"
        f"# {story_id}\n"
    )
    (repo / "backlog" / f"{story_id}.md").write_text(text)


def _commit_story_file(repo: Path, tmp_path: Path, story_id: str) -> None:
    """Commit the story's backlog file to the current branch (main)."""
    result = _git(repo, tmp_path, "add", "--", f"backlog/{story_id}.md")
    assert result.returncode == 0, result.stderr
    result = _git(
        repo, tmp_path, "commit", "--no-verify", "-m", f"backlog: add {story_id}"
    )
    assert result.returncode == 0, result.stderr


def _write_ledger(repo: Path, *entries: StoryEntry) -> Path:
    """Persist a dispatch ledger containing the provided entries."""
    ledger = Ledger()
    for entry in entries:
        ledger.stories[entry.id] = entry
    ledger_path = repo / ".current-work" / "dispatch-ledger.yaml"
    ledger.save(ledger_path)
    return ledger_path


def _make_story_branch_with_files(
    repo: Path, tmp_path: Path, story_id: str, filenames: list[str]
) -> None:
    """Create a story branch off HEAD with one commit adding *filenames*."""
    branch = f"story/{story_id}"
    result = _git(repo, tmp_path, "branch", branch, "HEAD")
    assert result.returncode == 0, result.stderr
    result = _git(repo, tmp_path, "checkout", branch)
    assert result.returncode == 0, result.stderr
    for filename in filenames:
        path = repo / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("print('hi')\n")
    result = _git(repo, tmp_path, "add", "-A")
    assert result.returncode == 0, result.stderr
    result = _git(repo, tmp_path, "commit", "--no-verify", "-m", f"feat: {story_id}")
    assert result.returncode == 0, result.stderr
    result = _git(repo, tmp_path, "checkout", "main")
    assert result.returncode == 0, result.stderr


def _make_story_worktree(repo: Path, tmp_path: Path, story_id: str) -> Path:
    """Register a worktree for the story branch, as prepare-story would."""
    worktree = repo / ".current-work" / "worktrees" / f"story-{story_id}"
    result = _git(repo, tmp_path, "worktree", "add", str(worktree), f"story/{story_id}")
    assert result.returncode == 0, result.stderr
    return worktree


def test_single_story_merge_uses_default_max_files(tmp_path: Path) -> None:
    """A story with a single declared output scales to 20 (max(20, 1*2)),
    i.e. the pre-existing premerge-check default is preserved end to end."""
    repo = _init_repo(tmp_path)
    _write_story_file(repo, "ST-901", outputs=["src/foo.py"])
    _commit_story_file(repo, tmp_path, "ST-901")
    _make_story_branch_with_files(repo, tmp_path, "ST-901", ["src/foo.py"])
    worktree = _make_story_worktree(repo, tmp_path, "ST-901")
    _write_ledger(
        repo,
        StoryEntry(
            id="ST-901",
            wave=1,
            status=StoryState.DISPATCHED,
            branch="story/ST-901",
            worktree=str(worktree),
            feature_branch="main",
        ),
    )

    result = _run_dispatch("merge-story", "ST-901", cwd=repo, tmp_path=tmp_path)

    assert result.returncode == 0, result.stderr
    assert "(limit 20)" in result.stdout


def test_multi_output_story_merge_scales_max_files(tmp_path: Path) -> None:
    """A story declaring 15 outputs scales to max(20, 15*2) = 30, so a
    26-file diff (over the default 20, under the scaled 30) still merges."""
    repo = _init_repo(tmp_path)
    # 15 declared outputs, all the same broad glob — the *count* drives
    # scaling, not the breadth of any one pattern.
    _write_story_file(repo, "ST-902", outputs=["src/*.py"] * 15)
    _commit_story_file(repo, tmp_path, "ST-902")
    filenames = [f"src/f{i:03d}.py" for i in range(26)]
    _make_story_branch_with_files(repo, tmp_path, "ST-902", filenames)
    worktree = _make_story_worktree(repo, tmp_path, "ST-902")
    _write_ledger(
        repo,
        StoryEntry(
            id="ST-902",
            wave=1,
            status=StoryState.DISPATCHED,
            branch="story/ST-902",
            worktree=str(worktree),
            feature_branch="main",
        ),
    )

    result = _run_dispatch("merge-story", "ST-902", cwd=repo, tmp_path=tmp_path)

    assert result.returncode == 0, result.stderr
    assert "26 files changed (limit 30)" in result.stdout

    ledger = Ledger.load(repo / ".current-work" / "dispatch-ledger.yaml")
    assert ledger.stories["ST-902"].status == StoryState.DONE


def test_suggest_merge_args_sums_outputs_across_ledger(tmp_path: Path) -> None:
    """suggest-merge-args reads every story in the ledger and recommends
    --max-files as the sum of their declared output counts."""
    repo = _init_repo(tmp_path)
    _write_story_file(repo, "ST-903", outputs=[f"src/a{i}.py" for i in range(12)])
    _commit_story_file(repo, tmp_path, "ST-903")
    _write_story_file(repo, "ST-904", outputs=[f"src/b{i}.py" for i in range(15)])
    _commit_story_file(repo, tmp_path, "ST-904")
    _write_ledger(
        repo,
        StoryEntry(id="ST-903", wave=1, status=StoryState.DONE),
        StoryEntry(id="ST-904", wave=1, status=StoryState.DONE),
    )

    result = _run_dispatch("suggest-merge-args", cwd=repo, tmp_path=tmp_path)

    assert result.returncode == 0, result.stderr
    assert "--max-files 27" in result.stdout


def test_suggest_merge_args_defaults_to_20_with_no_scaling_information(
    tmp_path: Path,
) -> None:
    """With no stories in the ledger (or none declaring outputs), the
    recommendation falls back to premerge-check's own default of 20."""
    repo = _init_repo(tmp_path)
    _write_ledger(repo)

    result = _run_dispatch("suggest-merge-args", cwd=repo, tmp_path=tmp_path)

    assert result.returncode == 0, result.stderr
    assert "--max-files 20" in result.stdout
