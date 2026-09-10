"""Public CLI contracts for serial, human-reviewed implementation dispatch."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
import yaml

DISPATCH = (
    Path(__file__).resolve().parents[2]
    / "packages"
    / "factory"
    / "scripts"
    / "dispatch"
)


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


@pytest.fixture()
def review_repo(tmp_path: Path) -> Path:
    git(tmp_path, "init", "-b", "dev")
    git(tmp_path, "config", "user.email", "review@example.test")
    git(tmp_path, "config", "user.name", "Review Test")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "testing.yaml").write_text(
        'test_all: "true"\n', encoding="utf-8"
    )
    (tmp_path / ".gitignore").write_text("/.current-work/\n", encoding="utf-8")
    (tmp_path / "backlog").mkdir()
    (tmp_path / "backlog" / "ST-9000.md").write_text(
        "---\n"
        "id: ST-9000\n"
        "status: pending\n"
        "tier: economy\n"
        "outputs: [src/]\n"
        "---\n",
        encoding="utf-8",
    )
    git(tmp_path, "add", ".gitignore", "docs/testing.yaml", "backlog/ST-9000.md")
    git(tmp_path, "commit", "-m", "chore: initialize review fixture")
    return tmp_path


def run_dispatch(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(DISPATCH), *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )


def test_init_review_creates_primary_checkout_branch_and_review_ledger(review_repo):
    base_sha = git(review_repo, "rev-parse", "HEAD")

    result = run_dispatch(
        review_repo,
        "init-review",
        "--base",
        "dev",
        "--feature-branch",
        "feature/review-flow",
        "--stories",
        "ST-9000",
    )

    assert result.returncode == 0, result.stderr
    assert git(review_repo, "branch", "--show-current") == "feature/review-flow"
    ledger_path = (
        review_repo
        / ".current-work"
        / "feature"
        / "review-flow"
        / "dispatch-ledger.yaml"
    )
    ledger = yaml.safe_load(ledger_path.read_text(encoding="utf-8"))
    assert ledger["mode"] == "review"
    assert ledger["branch_root"] == base_sha
    assert ledger["branch_head"] == base_sha


def test_init_review_checks_cleanliness_before_branch_mutation(review_repo):
    (review_repo / "uncommitted.txt").write_text("dirty\n", encoding="utf-8")

    result = run_dispatch(
        review_repo,
        "init-review",
        "--base",
        "dev",
        "--feature-branch",
        "feature/review-flow",
        "--stories",
        "ST-9000",
    )

    assert result.returncode == 1
    assert git(review_repo, "branch", "--show-current") == "dev"
    assert "pre-dispatch check failed" in result.stderr


def test_review_dispatch_blocks_contaminated_checkout(review_repo):
    initialized = run_dispatch(
        review_repo,
        "init-review",
        "--base",
        "dev",
        "--feature-branch",
        "feature/review-flow",
        "--stories",
        "ST-9000",
    )
    assert initialized.returncode == 0, initialized.stderr
    (review_repo / "unrelated.txt").write_text("contamination\n", encoding="utf-8")

    result = run_dispatch(review_repo, "review-dispatch", "ST-9000")

    assert result.returncode == 1
    assert "clean worktree and index" in result.stderr
    ledger_path = (
        review_repo
        / ".current-work"
        / "feature"
        / "review-flow"
        / "dispatch-ledger.yaml"
    )
    ledger = yaml.safe_load(ledger_path.read_text(encoding="utf-8"))
    assert ledger["stories"]["ST-9000"]["status"] == "pending"


def test_review_dispatch_records_dispatching_state_and_manifest(review_repo):
    initialized = run_dispatch(
        review_repo,
        "init-review",
        "--base",
        "dev",
        "--feature-branch",
        "feature/review-flow",
        "--stories",
        "ST-9000",
    )
    assert initialized.returncode == 0, initialized.stderr

    result = run_dispatch(review_repo, "review-dispatch", "ST-9000")

    assert result.returncode == 0, result.stderr
    ledger_path = (
        review_repo
        / ".current-work"
        / "feature"
        / "review-flow"
        / "dispatch-ledger.yaml"
    )
    ledger = yaml.safe_load(ledger_path.read_text(encoding="utf-8"))
    assert ledger["stories"]["ST-9000"]["status"] == "dispatching"
    manifest = (
        review_repo
        / ".current-work"
        / "feature"
        / "review-flow"
        / "review"
        / "ST-9000"
        / "current-step.yml"
    )
    assert manifest.exists()
    manifest_data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
    assert manifest_data["outputs"] == ["src/"]


def test_review_accept_verifies_human_commit_and_advances_ledger(review_repo):
    initialized = run_dispatch(
        review_repo,
        "init-review",
        "--base",
        "dev",
        "--feature-branch",
        "feature/review-flow",
        "--stories",
        "ST-9000",
    )
    assert initialized.returncode == 0, initialized.stderr
    prepared = run_dispatch(review_repo, "review-dispatch", "ST-9000")
    assert prepared.returncode == 0, prepared.stderr
    dispatched = run_dispatch(review_repo, "mark-dispatched", "ST-9000")
    assert dispatched.returncode == 0, dispatched.stderr

    (review_repo / "src").mkdir()
    (review_repo / "src" / "feature.py").write_text("VALUE = 1\n", encoding="utf-8")
    story_path = review_repo / "backlog" / "ST-9000.md"
    story_path.write_text(
        story_path.read_text(encoding="utf-8").replace(
            "status: pending", "status: done"
        ),
        encoding="utf-8",
    )
    git(review_repo, "add", "src/feature.py", "backlog/ST-9000.md")
    git(review_repo, "commit", "-m", "feat: deliver review flow (ST-9000)")
    commit_sha = git(review_repo, "rev-parse", "HEAD")

    result = run_dispatch(
        review_repo, "review-accept", "ST-9000", "--sha", commit_sha
    )

    assert result.returncode == 0, result.stderr
    ledger_path = (
        review_repo
        / ".current-work"
        / "feature"
        / "review-flow"
        / "dispatch-ledger.yaml"
    )
    ledger = yaml.safe_load(ledger_path.read_text(encoding="utf-8"))
    assert ledger["stories"]["ST-9000"]["status"] == "done"
    assert ledger["stories"]["ST-9000"]["commit_sha"] == commit_sha
    assert ledger["branch_head"] == commit_sha
    manifest = (
        review_repo
        / ".current-work"
        / "feature"
        / "review-flow"
        / "review"
        / "ST-9000"
        / "current-step.yml"
    )
    assert not manifest.exists()


def test_review_accept_rejects_commit_without_atomic_done_status(review_repo):
    initialized = run_dispatch(
        review_repo,
        "init-review",
        "--base",
        "dev",
        "--feature-branch",
        "feature/review-flow",
        "--stories",
        "ST-9000",
    )
    assert initialized.returncode == 0, initialized.stderr
    assert run_dispatch(review_repo, "review-dispatch", "ST-9000").returncode == 0
    assert run_dispatch(review_repo, "mark-dispatched", "ST-9000").returncode == 0
    (review_repo / "src").mkdir()
    (review_repo / "src" / "feature.py").write_text("VALUE = 1\n", encoding="utf-8")
    git(review_repo, "add", "src/feature.py")
    git(review_repo, "commit", "-m", "feat: incomplete review (ST-9000)")
    commit_sha = git(review_repo, "rev-parse", "HEAD")

    result = run_dispatch(
        review_repo, "review-accept", "ST-9000", "--sha", commit_sha
    )

    assert result.returncode == 1
    assert "must set status: done" in result.stderr


def test_review_accept_rejects_out_of_scope_commit(review_repo):
    initialized = run_dispatch(
        review_repo,
        "init-review",
        "--base",
        "dev",
        "--feature-branch",
        "feature/review-flow",
        "--stories",
        "ST-9000",
    )
    assert initialized.returncode == 0, initialized.stderr
    assert run_dispatch(review_repo, "review-dispatch", "ST-9000").returncode == 0
    assert run_dispatch(review_repo, "mark-dispatched", "ST-9000").returncode == 0
    story_path = review_repo / "backlog" / "ST-9000.md"
    story_path.write_text(
        story_path.read_text(encoding="utf-8").replace(
            "status: pending", "status: done"
        ),
        encoding="utf-8",
    )
    (review_repo / "outside.txt").write_text("scope leak\n", encoding="utf-8")
    git(review_repo, "add", "backlog/ST-9000.md", "outside.txt")
    git(review_repo, "commit", "-m", "feat: leak scope (ST-9000)")
    commit_sha = git(review_repo, "rev-parse", "HEAD")

    result = run_dispatch(
        review_repo, "review-accept", "ST-9000", "--sha", commit_sha
    )

    assert result.returncode == 1
    assert "out-of-scope files: outside.txt" in result.stderr


def test_review_ledger_cannot_enter_autonomous_prepare_path(review_repo):
    initialized = run_dispatch(
        review_repo,
        "init-review",
        "--base",
        "dev",
        "--feature-branch",
        "feature/review-flow",
        "--stories",
        "ST-9000",
    )
    assert initialized.returncode == 0, initialized.stderr

    result = run_dispatch(review_repo, "prepare-wave", "1")

    assert result.returncode == 1
    assert "requires an autonomous-mode ledger" in result.stderr


def test_review_close_records_terminal_dispatch(review_repo):
    initialized = run_dispatch(
        review_repo,
        "init-review",
        "--base",
        "dev",
        "--feature-branch",
        "feature/review-flow",
        "--stories",
        "ST-9000",
    )
    assert initialized.returncode == 0, initialized.stderr
    ledger_path = (
        review_repo
        / ".current-work"
        / "feature"
        / "review-flow"
        / "dispatch-ledger.yaml"
    )
    ledger = yaml.safe_load(ledger_path.read_text(encoding="utf-8"))
    ledger["stories"]["ST-9000"]["status"] = "done"
    ledger_path.write_text(yaml.safe_dump(ledger, sort_keys=False), encoding="utf-8")

    result = run_dispatch(review_repo, "review-close")

    assert result.returncode == 0, result.stderr
    closed_ledger = yaml.safe_load(ledger_path.read_text(encoding="utf-8"))
    assert closed_ledger["closed"] is True


def test_review_close_blocks_non_terminal_dispatch(review_repo):
    initialized = run_dispatch(
        review_repo,
        "init-review",
        "--base",
        "dev",
        "--feature-branch",
        "feature/review-flow",
        "--stories",
        "ST-9000",
    )
    assert initialized.returncode == 0, initialized.stderr

    result = run_dispatch(review_repo, "review-close")

    assert result.returncode == 1
    assert "non-terminal stories: ST-9000" in result.stderr
