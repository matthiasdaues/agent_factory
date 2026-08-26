"""Integration tests for dispatch interruption safety."""

from __future__ import annotations

import importlib
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

DISPATCH_SCRIPT = (
    Path(__file__).resolve().parent.parent / "factory" / "scripts" / "dispatch"
)
SCRIPT_DIR = Path(__file__).resolve().parent.parent / "factory" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))
dispatch_lib = importlib.import_module("dispatch_lib")

Ledger = dispatch_lib.Ledger
StoryEntry = dispatch_lib.StoryEntry
StoryState = dispatch_lib.StoryState


def _git_env(tmp_path: Path) -> dict[str, str]:
    """Return a git environment isolated from user-level configuration."""
    return {
        **os.environ,
        "GIT_CONFIG_NOSYSTEM": "1",
        "HOME": str(tmp_path),
    }


def _run_dispatch(
    *args: str, cwd: Path, tmp_path: Path, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    """Invoke the dispatch CLI as a subprocess."""
    return subprocess.run(
        [sys.executable, str(DISPATCH_SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=cwd,
        check=False,
        env=env or _git_env(tmp_path),
    )


def _spawn_dispatch(
    *args: str, cwd: Path, tmp_path: Path, env: dict[str, str] | None = None
) -> subprocess.Popen[str]:
    """Start a dispatch CLI subprocess for interruption tests."""
    return subprocess.Popen(
        [sys.executable, str(DISPATCH_SCRIPT), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=cwd,
        env=env or _git_env(tmp_path),
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
    """Create a minimal git repository for interruption integration tests."""
    repo = tmp_path / "repo"
    repo.mkdir()

    for args in (
        ("init", "--initial-branch=main"),
        ("config", "user.email", "test@test.com"),
        ("config", "user.name", "Test"),
    ):
        result = _git(repo, tmp_path, *args)
        assert result.returncode == 0, result.stderr

    config_dir = repo / "config"
    config_dir.mkdir()
    (config_dir / "project.json").write_text(
        json.dumps({"project_name": "test", "test_command": test_command})
    )

    backlog_dir = repo / "backlog"
    backlog_dir.mkdir()

    result = _git(repo, tmp_path, "add", "-A")
    assert result.returncode == 0, result.stderr
    result = _git(repo, tmp_path, "commit", "-m", "initial")
    assert result.returncode == 0, result.stderr
    return repo


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


def _write_git_wrapper(
    tmp_path: Path,
    *,
    sleep_match: list[str] | None = None,
    sleep_seconds: float = 5.0,
) -> tuple[Path, Path, Path, dict[str, str]]:
    """Write a git proxy that logs commands and can pause on a chosen call."""
    real_git = subprocess.run(
        ["which", "git"], capture_output=True, text=True, check=True
    ).stdout.strip()
    wrapper_dir = tmp_path / "bin"
    wrapper_dir.mkdir()
    log_path = tmp_path / "git-log.txt"
    marker_path = tmp_path / "git-sleeping.marker"
    wrapper_path = wrapper_dir / "git"
    wrapper_path.write_text(
        f"""#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

REAL_GIT = {real_git!r}
LOG_PATH = Path({str(log_path)!r})
MARKER_PATH = Path({str(marker_path)!r})
SLEEP_MATCH = json.loads(os.environ.get("GIT_WRAPPER_SLEEP_MATCH", "null"))
SLEEP_SECONDS = float(os.environ.get("GIT_WRAPPER_SLEEP_SECONDS", "0"))
args = sys.argv[1:]
with LOG_PATH.open("a", encoding="utf-8") as fh:
    fh.write("git " + " ".join(args) + "\\n")
if SLEEP_MATCH is not None and args == SLEEP_MATCH:
    MARKER_PATH.write_text("sleeping\\n", encoding="utf-8")
    time.sleep(SLEEP_SECONDS)
os.execv(REAL_GIT, [REAL_GIT, *args])
""",
        encoding="utf-8",
    )
    wrapper_path.chmod(0o755)
    env = _git_env(tmp_path)
    env["PATH"] = f"{wrapper_dir}:{env['PATH']}"
    if sleep_match is not None:
        env["GIT_WRAPPER_SLEEP_MATCH"] = json.dumps(sleep_match)
        env["GIT_WRAPPER_SLEEP_SECONDS"] = str(sleep_seconds)
    return wrapper_dir, log_path, marker_path, env


def test_prepare_wave_runs_from_scratch_when_nothing_was_written(
    tmp_path: Path,
) -> None:
    repo = _init_repo(tmp_path)
    _write_ledger(repo, StoryEntry(id="ST-001", wave=1, status=StoryState.PENDING))
    conflicting = _git(repo, tmp_path, "branch", "story/ST-001", "HEAD")
    assert conflicting.returncode == 0, conflicting.stderr

    first = _run_dispatch("prepare-wave", "1", cwd=repo, tmp_path=tmp_path)
    assert first.returncode == 1

    before = (repo / ".agent-factory" / "dispatch-ledger.yaml").read_text()
    assert _load_ledger(repo).stories["ST-001"].status == StoryState.PENDING

    delete_branch = _git(repo, tmp_path, "branch", "-D", "story/ST-001")
    assert delete_branch.returncode == 0, delete_branch.stderr

    second = _run_dispatch("prepare-wave", "1", cwd=repo, tmp_path=tmp_path)
    assert second.returncode == 0, second.stderr
    after = (repo / ".agent-factory" / "dispatch-ledger.yaml").read_text()
    assert after != before
    assert _load_ledger(repo).stories["ST-001"].status == StoryState.PREPARED


def test_prepare_wave_resumes_after_partial_ledger_write(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _write_ledger(
        repo,
        StoryEntry(id="ST-001", wave=1, status=StoryState.PENDING),
        StoryEntry(id="ST-002", wave=1, status=StoryState.PENDING),
    )
    conflicting = _git(repo, tmp_path, "branch", "story/ST-002", "HEAD")
    assert conflicting.returncode == 0, conflicting.stderr

    first = _run_dispatch("prepare-wave", "1", cwd=repo, tmp_path=tmp_path)
    assert first.returncode == 1

    ledger = _load_ledger(repo)
    assert ledger.stories["ST-001"].status == StoryState.PREPARED
    assert ledger.stories["ST-002"].status == StoryState.PENDING

    delete_branch = _git(repo, tmp_path, "branch", "-D", "story/ST-002")
    assert delete_branch.returncode == 0, delete_branch.stderr

    second = _run_dispatch("prepare-wave", "1", cwd=repo, tmp_path=tmp_path)
    assert second.returncode == 0, second.stderr

    resumed = _load_ledger(repo)
    assert resumed.stories["ST-001"].status == StoryState.PREPARED
    assert resumed.stories["ST-002"].status == StoryState.PREPARED


def test_merge_story_reuses_existing_merge_commit_after_interruption(
    tmp_path: Path,
) -> None:
    repo = _init_repo(tmp_path, test_command=str(tmp_path / "run-suite.sh"))
    suite = tmp_path / "run-suite.sh"
    suite.write_text(
        "#!/usr/bin/env sh\nset -eu\nprintf 'ran\\n' > .agent-factory/test-suite-ran\n"
    )
    suite.chmod(0o755)
    story_path = repo / "backlog" / "ST-777.md"
    story_path.write_text(
        "---\nid: ST-777\nstatus: dispatched\nquality-gates: []\noutputs:\n  - src/foo.py\n---\n# ST-777\n"
    )
    _git(repo, tmp_path, "add", "--", "backlog/ST-777.md")
    _git(repo, tmp_path, "commit", "-m", "backlog: add ST-777")
    _git(repo, tmp_path, "branch", "story/ST-777", "HEAD")
    _git(repo, tmp_path, "checkout", "story/ST-777")
    (repo / "src").mkdir()
    (repo / "src" / "foo.py").write_text("print('hi')\n")
    _git(repo, tmp_path, "add", "-A")
    _git(repo, tmp_path, "commit", "-m", "feat: ST-777")
    _git(repo, tmp_path, "checkout", "main")
    worktree = repo / ".agent-factory" / "worktrees" / "story-ST-777"
    _git(repo, tmp_path, "worktree", "add", str(worktree), "story/ST-777")
    _write_ledger(
        repo,
        StoryEntry(
            id="ST-777",
            wave=1,
            status=StoryState.DISPATCHED,
            branch="story/ST-777",
            worktree=str(worktree),
            feature_branch="main",
        ),
    )

    result = _run_dispatch("merge-story", "ST-777", cwd=repo, tmp_path=tmp_path)
    assert result.returncode == 0, result.stderr

    assert (repo / ".agent-factory" / "test-suite-ran").exists()
    ledger = _load_ledger(repo)
    assert ledger.stories["ST-777"].status == StoryState.DONE
    assert ledger.stories["ST-777"].commit_sha


def test_prepare_wave_stops_at_safe_point_after_first_story(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _write_ledger(
        repo,
        StoryEntry(id="ST-001", wave=1, status=StoryState.PENDING),
        StoryEntry(id="ST-002", wave=1, status=StoryState.PENDING),
    )
    _, _, marker_path, env = _write_git_wrapper(
        tmp_path,
        sleep_match=["branch", "story/ST-002", "HEAD"],
        sleep_seconds=10.0,
    )

    proc = _spawn_dispatch("prepare-wave", "1", cwd=repo, tmp_path=tmp_path, env=env)
    for _ in range(200):
        if marker_path.exists():
            break
        if proc.poll() is not None:
            break
        time.sleep(0.05)
    assert marker_path.exists()

    proc.send_signal(signal.SIGINT)
    proc.communicate(timeout=20)
    assert proc.returncode not in {0, None}

    ledger = _load_ledger(repo)
    assert ledger.stories["ST-001"].status == StoryState.PREPARED
    assert ledger.stories["ST-002"].status == StoryState.PENDING

    rerun = _run_dispatch("prepare-wave", "1", cwd=repo, tmp_path=tmp_path)
    assert rerun.returncode == 0, rerun.stderr
    rerun_ledger = _load_ledger(repo)
    assert rerun_ledger.stories["ST-001"].status == StoryState.PREPARED
    assert rerun_ledger.stories["ST-002"].status == StoryState.PREPARED


def test_prepare_wave_exits_immediately_when_signal_is_already_aborted(
    tmp_path: Path,
) -> None:
    repo = _init_repo(tmp_path)
    _write_ledger(repo, StoryEntry(id="ST-001", wave=1, status=StoryState.PENDING))
    _, _, _, env = _write_git_wrapper(
        tmp_path,
        sleep_match=["branch", "story/ST-001", "HEAD"],
        sleep_seconds=10.0,
    )
    before = (repo / ".agent-factory" / "dispatch-ledger.yaml").read_text()

    proc = _spawn_dispatch("prepare-wave", "1", cwd=repo, tmp_path=tmp_path, env=env)
    proc.send_signal(signal.SIGINT)
    proc.communicate(timeout=20)
    assert proc.returncode not in {0, None}

    after = (repo / ".agent-factory" / "dispatch-ledger.yaml").read_text()
    assert after == before
    ledger = _load_ledger(repo)
    assert ledger.stories["ST-001"].status == StoryState.PENDING
