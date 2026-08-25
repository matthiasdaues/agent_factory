'''Integration tests for dispatch verification immutability.'''

from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
from pathlib import Path

DISPATCH_SCRIPT = Path(__file__).resolve().parent.parent / "factory" / "scripts" / "dispatch"
SCRIPT_DIR = Path(__file__).resolve().parent.parent / "factory" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))
dispatch_lib = importlib.import_module("dispatch_lib")

Ledger = dispatch_lib.Ledger
StoryEntry = dispatch_lib.StoryEntry
StoryState = dispatch_lib.StoryState


def _git_env(tmp_path: Path) -> dict[str, str]:
    '''Return a git environment isolated from user-level configuration.'''
    return {
        **os.environ,
        "GIT_CONFIG_NOSYSTEM": "1",
        "HOME": str(tmp_path),
    }


def _run_dispatch(*args: str, cwd: Path, tmp_path: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    '''Invoke the dispatch CLI as a subprocess.'''
    return subprocess.run(
        [sys.executable, str(DISPATCH_SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=cwd,
        check=False,
        env=env or _git_env(tmp_path),
    )


def _git(repo: Path, tmp_path: Path, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    '''Run a git command inside the temporary repository.'''
    return subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        cwd=repo,
        check=False,
        env=env or _git_env(tmp_path),
    )


def _init_repo(tmp_path: Path, test_command: str = "true") -> Path:
    '''Create a minimal git repository for immutability integration tests.'''
    repo = tmp_path / "repo"
    repo.mkdir()

    env = _git_env(tmp_path)
    for args in (
        ("init", "--initial-branch=main"),
        ("config", "user.email", "test@test.com"),
        ("config", "user.name", "Test"),
    ):
        result = _git(repo, tmp_path, *args, env=env)
        assert result.returncode == 0, result.stderr

    (repo / "README.md").write_text("initial\n")
    config_dir = repo / "config"
    config_dir.mkdir()
    (config_dir / "project.json").write_text(
        json.dumps({"project_name": "test", "test_command": test_command})
    )

    result = _git(repo, tmp_path, "add", "-A", env=env)
    assert result.returncode == 0, result.stderr
    result = _git(repo, tmp_path, "commit", "-m", "initial", env=env)
    assert result.returncode == 0, result.stderr
    return repo


def _write_ledger(repo: Path, *entries: StoryEntry) -> Path:
    '''Persist a dispatch ledger containing the provided entries.'''
    ledger = Ledger()
    for entry in entries:
        ledger.stories[entry.id] = entry
    ledger_path = repo / ".agent-factory" / "dispatch-ledger.yaml"
    ledger.save(ledger_path)
    return ledger_path


def _load_ledger(repo: Path) -> Ledger:
    '''Load the repository's default dispatch ledger.'''
    return Ledger.load(repo / ".agent-factory" / "dispatch-ledger.yaml")


def _commit_on_story_branch(repo: Path, tmp_path: Path, branch: str, filename: str) -> str:
    '''Create a branch commit and return its SHA.'''
    _git(repo, tmp_path, "checkout", "-b", branch)
    (repo / filename).write_text("content\n")
    _git(repo, tmp_path, "add", "-A")
    _git(repo, tmp_path, "commit", "-m", f"commit on {branch}")
    sha = _git(repo, tmp_path, "rev-parse", "HEAD").stdout.strip()
    _git(repo, tmp_path, "checkout", "main")
    return sha


def _git_wrapper(tmp_path: Path) -> tuple[Path, Path, dict[str, str]]:
    '''Write a git proxy that records commands for later assertions.'''
    real_git = subprocess.run(["which", "git"], capture_output=True, text=True, check=True).stdout.strip()
    wrapper_dir = tmp_path / "bin"
    wrapper_dir.mkdir()
    log_path = tmp_path / "git-log.txt"
    wrapper_path = wrapper_dir / "git"
    wrapper_path.write_text(
        f'''#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from pathlib import Path

REAL_GIT = {real_git!r}
LOG_PATH = Path({str(log_path)!r})
args = sys.argv[1:]
with LOG_PATH.open("a", encoding="utf-8") as fh:
    fh.write("git " + " ".join(args) + "\\n")
os.execv(REAL_GIT, [REAL_GIT, *args])
''',
        encoding="utf-8",
    )
    wrapper_path.chmod(0o755)
    env = _git_env(tmp_path)
    env["PATH"] = f"{wrapper_dir}:{env['PATH']}"
    return log_path, wrapper_dir, env


def test_verify_story_preserves_git_status_porcelain(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    sha = _commit_on_story_branch(repo, tmp_path, "story/ST-001", "feature.txt")
    _write_ledger(
        repo,
        StoryEntry(id="ST-001", status=StoryState.DISPATCHED, branch="story/ST-001"),
    )
    before_status = _git(repo, tmp_path, "status", "--porcelain").stdout

    result = _run_dispatch(
        "verify-story", "ST-001", "--sha", sha, cwd=repo, tmp_path=tmp_path
    )

    assert result.returncode == 0, result.stderr
    after_status = _git(repo, tmp_path, "status", "--porcelain").stdout
    assert after_status == before_status


def test_verify_story_preserves_working_tree_contents(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    sha = _commit_on_story_branch(repo, tmp_path, "story/ST-001", "feature.txt")
    _write_ledger(
        repo,
        StoryEntry(id="ST-001", status=StoryState.DISPATCHED, branch="story/ST-001"),
    )
    branch_before = _git(repo, tmp_path, "rev-parse", "--abbrev-ref", "HEAD").stdout
    head_before = _git(repo, tmp_path, "rev-parse", "HEAD").stdout
    readme_before = (repo / "README.md").read_text()

    result = _run_dispatch(
        "verify-story", "ST-001", "--sha", sha, cwd=repo, tmp_path=tmp_path
    )

    assert result.returncode == 0, result.stderr
    branch_after = _git(repo, tmp_path, "rev-parse", "--abbrev-ref", "HEAD").stdout
    head_after = _git(repo, tmp_path, "rev-parse", "HEAD").stdout
    readme_after = (repo / "README.md").read_text()
    assert branch_after == branch_before
    assert head_after == head_before
    assert readme_after == readme_before
    assert not (repo / "feature.txt").exists()


def test_merge_story_premerge_check_does_not_use_mutating_git_commands(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path, test_command="true")
    log_path, _, env = _git_wrapper(tmp_path)

    backlog_dir = repo / "backlog"
    backlog_dir.mkdir(exist_ok=True)
    story_path = backlog_dir / "ST-002.md"
    story_path.write_text("---\nid: ST-002\nstatus: dispatched\noutputs:\n  - src/foo.py\n---\n# ST-002\n")
    _git(repo, tmp_path, "add", "--", "backlog/ST-002.md", env=_git_env(tmp_path))
    _git(repo, tmp_path, "commit", "-m", "backlog: add ST-002", env=_git_env(tmp_path))
    _git(repo, tmp_path, "branch", "story/ST-002", "HEAD", env=_git_env(tmp_path))
    _git(repo, tmp_path, "checkout", "story/ST-002", env=_git_env(tmp_path))
    (repo / "src").mkdir()
    (repo / "src" / "foo.py").write_text("print('hi')\n")
    _git(repo, tmp_path, "add", "-A", env=_git_env(tmp_path))
    _git(repo, tmp_path, "commit", "-m", "feat: ST-002", env=_git_env(tmp_path))
    _git(repo, tmp_path, "checkout", "main", env=_git_env(tmp_path))
    worktree = repo / ".agent-factory" / "worktrees" / "story-ST-002"
    _git(repo, tmp_path, "worktree", "add", str(worktree), "story/ST-002", env=_git_env(tmp_path))
    _write_ledger(
        repo,
        StoryEntry(
            id="ST-002",
            wave=1,
            status=StoryState.DISPATCHED,
            branch="story/ST-002",
            worktree=str(worktree),
            feature_branch="main",
        ),
    )
    before_index = _git(repo, tmp_path, "ls-files", "--stage").stdout

    result = _run_dispatch("merge-story", "ST-002", "--dry-run", cwd=repo, tmp_path=tmp_path, env=env)

    assert result.returncode == 0, result.stderr
    after_index = _git(repo, tmp_path, "ls-files", "--stage").stdout
    assert after_index == before_index

    log_lines = log_path.read_text().splitlines()
    forbidden = {"git add", "git checkout", "git reset"}
    assert all(not any(line.startswith(prefix) for prefix in forbidden) for line in log_lines)



def test_escalate_does_not_mutate_git_state(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path, test_command="true")
    env = _git_env(tmp_path)
    log_path, _, wrapped_env = _git_wrapper(tmp_path)

    backlog_dir = repo / "backlog"
    backlog_dir.mkdir(exist_ok=True)
    (backlog_dir / "ST-001.md").write_text(
        "---\n"
        "id: ST-001\n"
        "tier: economy\n"
        "status: failed\n"
        "outputs:\n"
        "  - src/foo.py\n"
        "---\n"
        "# ST-001\n"
    )
    _git(repo, tmp_path, "add", "-A", env=env)
    _git(repo, tmp_path, "commit", "-m", "add backlog story", env=env)
    base_sha = _git(repo, tmp_path, "rev-parse", "HEAD", env=env).stdout.strip()

    (repo / "src").mkdir(exist_ok=True)
    story_sha = _commit_on_story_branch(repo, tmp_path, "story/ST-001", "src/foo.py")
    worktree = repo / ".agent-factory" / "worktrees" / "story-ST-001"
    _git(repo, tmp_path, "worktree", "add", str(worktree), "story/ST-001", env=env)
    _write_ledger(
        repo,
        StoryEntry(
            id="ST-001",
            wave=1,
            status=StoryState.FAILED,
            branch="story/ST-001",
            worktree=str(worktree),
            base_sha=base_sha,
            tier="economy",
            attempts=[
                {
                    "session": "impl",
                    "tier": "economy",
                    "failure_class": "acceptance_unmet",
                    "evidence": "docs/findings/IMPL-0001.md",
                    "commit_sha": story_sha,
                    "normalized_total": 11,
                }
            ],
        ),
    )
    before_status = _git(repo, tmp_path, "status", "--porcelain", env=env).stdout

    result = _run_dispatch("escalate", "ST-001", cwd=repo, tmp_path=tmp_path, env=wrapped_env)

    assert result.returncode == 0, result.stderr
    after_status = _git(repo, tmp_path, "status", "--porcelain", env=env).stdout
    assert after_status == before_status
    log_lines = log_path.read_text().splitlines()
    forbidden_prefixes = ("git add ", "git commit ", "git reset ", "git checkout ", "git merge ", "git branch -d ", "git worktree remove")
    assert all(not any(line.startswith(prefix) for prefix in forbidden_prefixes) for line in log_lines)
