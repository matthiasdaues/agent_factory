"""Onboarding sandbox — isolated first-task lifecycle (ST-0291, ST-0292).

Creates a sandbox for the poc-spike playbook, then applies exactly one
newcomer-chosen outcome: discard, retain selected artifacts, or hand off to
a normal production workstream. The sandbox creates no branch and no
commit; production handoff delegates to the existing `engine.workstream`
mechanism rather than reimplementing it.

A repository with a current HEAD gets a detached worktree from that
commit (ST-0291). A repository without HEAD (a bare `git init`, no commits
yet) gets a plain directory instead — no `git worktree add` is attempted
(ST-0292). Both are addressed at the same path,
`.current-work/onboarding-spike/<uuid4>/`, and both flow through the same
discard/retain/handoff outcome logic: `discard_sandbox` tells them apart by
the presence of the `.git` file `git worktree add` leaves at the sandbox
root, which a plain `os.makedirs` directory never has.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import uuid
from pathlib import Path

from engine.workstream import create_workstream, load_workstream

DEFAULT_SANDBOX_BASE = ".current-work/onboarding-spike"
DEFAULT_SPIKES_BASE = "docs/spikes"
DEFAULT_WORKSTREAM_BASE = ".agent-factory/workstreams"


class SandboxError(Exception):
    pass


def _run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True
    )


def create_sandbox(
    repo_root: str | Path, base_dir: str | Path = DEFAULT_SANDBOX_BASE
) -> Path:
    """Create the first-task sandbox at <repo_root>/<base_dir>/<uuid4>/.

    A repository with a current HEAD gets a detached worktree from that
    commit. A repository without HEAD (exit code 128 from
    `git rev-parse --verify HEAD`, e.g. a bare `git init`) gets a plain
    directory instead — no `git worktree add` is attempted. Raises
    SandboxError when `git worktree add` fails.
    """
    repo_root = Path(repo_root)
    session_id = str(uuid.uuid4())
    sandbox_path = repo_root / base_dir / session_id

    head_check = _run_git(["rev-parse", "--verify", "HEAD"], repo_root)
    if head_check.returncode != 0:
        os.makedirs(sandbox_path)
        return sandbox_path

    sandbox_path.parent.mkdir(parents=True, exist_ok=True)

    result = _run_git(
        ["worktree", "add", "--detach", str(sandbox_path), "HEAD"], repo_root
    )
    if result.returncode != 0:
        raise SandboxError(f"git worktree add failed: {result.stderr.strip()}")

    return sandbox_path


def discard_sandbox(repo_root: str | Path, sandbox_path: str | Path) -> None:
    """Remove the sandbox and verify the path no longer exists.

    A worktree sandbox is removed with `git worktree remove --force` (the
    poc-spike playbook typically leaves uncommitted output files inside it,
    and discard must still succeed). A plain sandbox — detected by the
    absence of the `.git` file `git worktree add` leaves at the sandbox
    root — is removed with `shutil.rmtree` instead.
    """
    repo_root = Path(repo_root)
    sandbox_path = Path(sandbox_path)

    if (sandbox_path / ".git").exists():
        result = _run_git(
            ["worktree", "remove", "--force", str(sandbox_path)], repo_root
        )
        if result.returncode != 0:
            raise SandboxError(
                f"git worktree remove failed: {result.stderr.strip()}"
            )
    else:
        shutil.rmtree(sandbox_path)

    if sandbox_path.exists():
        raise SandboxError(
            f"sandbox path still exists after removal: {sandbox_path}"
        )


def retain_artifacts(
    repo_root: str | Path,
    sandbox_path: str | Path,
    artifact_names: list[str],
    retain_name: str,
    spikes_base: str | Path = DEFAULT_SPIKES_BASE,
) -> Path:
    """Copy only the separately confirmed artifacts to
    <repo_root>/<spikes_base>/<retain_name>/, then discard the sandbox.

    Raises SandboxError, and leaves the sandbox untouched, when no
    artifacts are confirmed (retention not separately confirmed copies
    nothing) or when a named artifact does not exist in the sandbox.
    """
    if not artifact_names:
        raise SandboxError("no artifacts confirmed for retention")

    repo_root = Path(repo_root)
    sandbox_path = Path(sandbox_path)
    target_dir = repo_root / spikes_base / retain_name

    for name in artifact_names:
        source = sandbox_path / name
        if not source.exists():
            raise SandboxError(f"artifact not found in sandbox: {name}")

    target_dir.mkdir(parents=True, exist_ok=True)
    for name in artifact_names:
        source = sandbox_path / name
        dest = target_dir / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, dest)
        else:
            shutil.copy2(source, dest)

    discard_sandbox(repo_root, sandbox_path)
    return target_dir


def request_production_handoff(
    *,
    create_new: bool,
    workstream_id: str,
    topic: str | None = None,
    origin_ref: str | None = None,
    base_dir: str | Path = DEFAULT_WORKSTREAM_BASE,
) -> dict:
    """Delegate to the existing workstream mechanism without reimplementing
    it. Never touches the sandbox — the sandbox is not promoted to
    production work by either path.
    """
    if create_new:
        create_workstream(workstream_id, topic, origin_ref, base_dir=base_dir)
    return load_workstream(workstream_id, base_dir=base_dir)
