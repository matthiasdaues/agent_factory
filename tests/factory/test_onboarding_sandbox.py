"""Contract tests for ST-0291/ST-0292: isolated first-task sandbox
lifecycle.

Owned contracts (EPIC 5 Ownership Resolution table,
docs/spec/value-first-onboarding-journey-qa-strategy.md):

  - VFO-08-IT-01 — Repository state selects a detached worktree or a plain
    sandbox (`Scenario: Repository with a commit uses a detached
    worktree`, `Scenario: Repository without a commit uses a plain
    sandbox`). The plain-sandbox path is ST-0292's ownership.
  - VFO-08-IT-02 — Active-working-tree changes never enter the sandbox
    (`Scenario: Repository with a commit uses a detached worktree`).
  - VFO-08-IT-03 — Discard, retention, and production handoff apply only
    the selected outcome (`Scenario: Newcomer retains selected reference
    artifacts`, `Scenario: Newcomer discards the first task`,
    `Scenario: Newcomer begins real work explicitly`) — for both the
    detached-worktree sandbox (ST-0291) and the plain sandbox (ST-0292).

The dynamic, end-to-end first-task preview (VFO-08-AC-01) and the
ten-minute/five-decision journey bound are acceptance-level contracts owned
by `tests/factory/test_onboarding_journey.py`, currently blocked on the
acceptance-test harness gap recorded in the QA strategy's Gap Findings.
This file does not attempt to measure them — it checks the static content
contract instead: Virgil's "## First task" section states the preview
fields, the approval/outcome behavior, and the documented time bound
(same pattern as `TestFirstSessionInsightSection` in
`test_value_first_routing.py` for VFO-06-AC-01).
"""

from __future__ import annotations

import subprocess
import sys
import uuid
from pathlib import Path

import pytest

PACKAGES_DIR = Path(__file__).resolve().parents[2] / "packages" / "factory"
if str(PACKAGES_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGES_DIR))

from engine.onboarding_sandbox import (  # noqa: E402
    DEFAULT_SANDBOX_BASE,
    SandboxError,
    create_sandbox,
    discard_sandbox,
    request_production_handoff,
    retain_artifacts,
)
from engine.workstream import load_workstream  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
VIRGIL_PATH = REPO_ROOT / "packages" / "factory" / "agents" / "virgil.md"
FIRST_TASK_HEADING = "## First task"
FITTING_HEADING = "## Fitting"


def _run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=True
    )


def _init_repo(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", str(path)], capture_output=True, check=True)
    _run_git(["config", "user.email", "test@test"], path)
    _run_git(["config", "user.name", "Test"], path)


def _commit(path: Path, name: str = "README.md", content: str = "init\n") -> None:
    (path / name).write_text(content)
    _run_git(["add", "."], path)
    _run_git(["commit", "-m", f"add {name}", "--no-verify"], path)


@pytest.fixture()
def repo(tmp_path) -> Path:
    repo_path = tmp_path / "repo"
    _init_repo(repo_path)
    _commit(repo_path)
    return repo_path


@pytest.fixture()
def repo_without_head(tmp_path) -> Path:
    repo_path = tmp_path / "no-head-repo"
    _init_repo(repo_path)
    return repo_path


class TestCreateSandboxDetachedWorktree:
    """VFO-08-IT-01: a repository with HEAD gets a detached worktree under
    .current-work/onboarding-spike/<uuid4>/, no new branch, no new commit."""

    def test_creates_detached_worktree_under_default_base(self, repo: Path) -> None:
        sandbox = create_sandbox(repo)

        assert sandbox.exists()
        assert sandbox.parent == repo / DEFAULT_SANDBOX_BASE

    def test_session_id_is_a_uuid4_string(self, repo: Path) -> None:
        sandbox = create_sandbox(repo)

        parsed = uuid.UUID(sandbox.name)
        assert parsed.version == 4

    def test_creates_no_branch(self, repo: Path) -> None:
        before = _run_git(["branch", "--list"], repo).stdout
        create_sandbox(repo)
        after = _run_git(["branch", "--list"], repo).stdout

        assert before == after

    def test_creates_no_commit(self, repo: Path) -> None:
        before = _run_git(["log", "--oneline"], repo).stdout
        create_sandbox(repo)
        after = _run_git(["log", "--oneline"], repo).stdout

        assert before == after

    def test_worktree_is_registered_as_detached(self, repo: Path) -> None:
        sandbox = create_sandbox(repo)

        listing = _run_git(["worktree", "list"], repo).stdout
        assert str(sandbox) in listing
        assert "(detached HEAD)" in listing



class TestUncommittedChangesExcluded:
    """VFO-08-IT-02: active-working-tree changes never enter the sandbox."""

    def test_untracked_file_absent_from_sandbox(self, repo: Path) -> None:
        (repo / "scratch.txt").write_text("not committed\n")

        sandbox = create_sandbox(repo)

        assert not (sandbox / "scratch.txt").exists()

    def test_uncommitted_modification_absent_from_sandbox(self, repo: Path) -> None:
        (repo / "README.md").write_text("modified but not committed\n")

        sandbox = create_sandbox(repo)

        assert (sandbox / "README.md").read_text() == "init\n"


class TestDiscardSandbox:
    """VFO-08-IT-03: discard removes the worktree and verifies removal."""

    def test_discard_removes_sandbox_directory(self, repo: Path) -> None:
        sandbox = create_sandbox(repo)

        discard_sandbox(repo, sandbox)

        assert not sandbox.exists()

    def test_discard_removes_sandbox_from_worktree_list(self, repo: Path) -> None:
        sandbox = create_sandbox(repo)

        discard_sandbox(repo, sandbox)

        listing = _run_git(["worktree", "list"], repo).stdout
        assert str(sandbox) not in listing

    def test_discard_removes_a_dirty_sandbox(self, repo: Path) -> None:
        # The poc-spike playbook writes new, uncommitted files inside the
        # sandbox — discard must still succeed.
        sandbox = create_sandbox(repo)
        (sandbox / "spike-output.txt").write_text("result\n")

        discard_sandbox(repo, sandbox)

        assert not sandbox.exists()


class TestRetainSelectedArtifacts:
    """VFO-08-IT-03: retention copies only confirmed artifacts to
    docs/spikes/<name>/ and removes the sandbox afterwards."""

    def test_retains_only_confirmed_artifact(self, repo: Path) -> None:
        sandbox = create_sandbox(repo)
        (sandbox / "keep.txt").write_text("keep me\n")
        (sandbox / "skip.txt").write_text("discard me\n")

        target = retain_artifacts(
            repo, sandbox, artifact_names=["keep.txt"], retain_name="my-spike"
        )

        assert target == repo / "docs" / "spikes" / "my-spike"
        assert (target / "keep.txt").read_text() == "keep me\n"
        assert not (target / "skip.txt").exists()

    def test_retention_removes_the_sandbox(self, repo: Path) -> None:
        sandbox = create_sandbox(repo)
        (sandbox / "keep.txt").write_text("keep me\n")

        retain_artifacts(
            repo, sandbox, artifact_names=["keep.txt"], retain_name="my-spike"
        )

        assert not sandbox.exists()

    def test_empty_selection_raises_and_does_not_touch_sandbox(
        self, repo: Path
    ) -> None:
        sandbox = create_sandbox(repo)

        with pytest.raises(SandboxError):
            retain_artifacts(repo, sandbox, artifact_names=[], retain_name="my-spike")

        assert sandbox.exists()
        assert not (repo / "docs" / "spikes").exists()

    def test_missing_artifact_raises(self, repo: Path) -> None:
        sandbox = create_sandbox(repo)

        with pytest.raises(SandboxError):
            retain_artifacts(
                repo,
                sandbox,
                artifact_names=["nope.txt"],
                retain_name="my-spike",
            )


class TestProductionHandoff:
    """VFO-08-IT-03: production handoff delegates to the existing
    workstream mechanism and never promotes the sandbox itself."""

    def test_create_new_workstream_delegates_without_touching_sandbox(
        self, repo: Path
    ) -> None:
        sandbox = create_sandbox(repo)
        ws_base = repo / ".agent-factory" / "workstreams"

        request_production_handoff(
            create_new=True,
            workstream_id="first-real-feature",
            topic="First real feature",
            origin_ref=None,
            base_dir=ws_base,
        )

        data = load_workstream("first-real-feature", base_dir=ws_base)
        assert data["workstream_id"] == "first-real-feature"

        # The sandbox is untouched — still present, still a detached
        # worktree, never converted into the new workstream.
        assert sandbox.exists()
        listing = _run_git(["worktree", "list"], repo).stdout
        assert str(sandbox) in listing

    def test_select_existing_workstream_delegates_without_touching_sandbox(
        self, repo: Path
    ) -> None:
        sandbox = create_sandbox(repo)
        ws_base = repo / ".agent-factory" / "workstreams"
        request_production_handoff(
            create_new=True,
            workstream_id="existing-stream",
            topic="Existing",
            origin_ref=None,
            base_dir=ws_base,
        )

        data = request_production_handoff(
            create_new=False, workstream_id="existing-stream", base_dir=ws_base
        )

        assert data["workstream_id"] == "existing-stream"
        assert sandbox.exists()


class TestCreatePlainSandboxNoHead:
    """VFO-08-IT-01 (ST-0292): a repository without HEAD gets a plain
    directory under .current-work/onboarding-spike/<uuid4>/, and no
    `git worktree add` is attempted."""

    def test_creates_plain_directory_under_default_base(
        self, repo_without_head: Path
    ) -> None:
        sandbox = create_sandbox(repo_without_head)

        assert sandbox.exists()
        assert sandbox.is_dir()
        assert sandbox.parent == repo_without_head / DEFAULT_SANDBOX_BASE

    def test_session_id_is_a_uuid4_string(self, repo_without_head: Path) -> None:
        sandbox = create_sandbox(repo_without_head)

        parsed = uuid.UUID(sandbox.name)
        assert parsed.version == 4

    def test_does_not_raise(self, repo_without_head: Path) -> None:
        # Previously (ST-0291) create_sandbox raised SandboxError here; this
        # story replaces that with the plain-directory path.
        create_sandbox(repo_without_head)

    def test_no_worktree_is_registered(self, repo_without_head: Path) -> None:
        sandbox = create_sandbox(repo_without_head)

        listing = _run_git(["worktree", "list"], repo_without_head).stdout
        assert str(sandbox) not in listing

    def test_sandbox_has_no_dot_git(self, repo_without_head: Path) -> None:
        # `git worktree add` would leave a `.git` file at the sandbox root;
        # a plain `os.makedirs` directory has none.
        sandbox = create_sandbox(repo_without_head)

        assert not (sandbox / ".git").exists()


class TestDiscardPlainSandbox:
    """VFO-08-IT-03 (ST-0292): discard removes the plain sandbox with
    shutil.rmtree and verifies removal, reusing the worktree case's
    verification step."""

    def test_discard_removes_sandbox_directory(
        self, repo_without_head: Path
    ) -> None:
        sandbox = create_sandbox(repo_without_head)

        discard_sandbox(repo_without_head, sandbox)

        assert not sandbox.exists()

    def test_discard_removes_a_dirty_sandbox(self, repo_without_head: Path) -> None:
        sandbox = create_sandbox(repo_without_head)
        (sandbox / "spike-output.txt").write_text("result\n")

        discard_sandbox(repo_without_head, sandbox)

        assert not sandbox.exists()


class TestRetainSelectedArtifactsPlainSandbox:
    """VFO-08-IT-03 (ST-0292): retention behaves identically to the
    worktree case for a plain sandbox."""

    def test_retains_only_confirmed_artifact(self, repo_without_head: Path) -> None:
        sandbox = create_sandbox(repo_without_head)
        (sandbox / "keep.txt").write_text("keep me\n")
        (sandbox / "skip.txt").write_text("discard me\n")

        target = retain_artifacts(
            repo_without_head,
            sandbox,
            artifact_names=["keep.txt"],
            retain_name="my-spike",
        )

        assert target == repo_without_head / "docs" / "spikes" / "my-spike"
        assert (target / "keep.txt").read_text() == "keep me\n"
        assert not (target / "skip.txt").exists()
        assert not sandbox.exists()


class TestProductionHandoffPlainSandbox:
    """VFO-08-IT-03 (ST-0292): production handoff delegates without
    touching or promoting the plain sandbox."""

    def test_create_new_workstream_delegates_without_touching_sandbox(
        self, repo_without_head: Path
    ) -> None:
        sandbox = create_sandbox(repo_without_head)
        ws_base = repo_without_head / ".agent-factory" / "workstreams"

        request_production_handoff(
            create_new=True,
            workstream_id="first-real-feature",
            topic="First real feature",
            origin_ref=None,
            base_dir=ws_base,
        )

        data = load_workstream("first-real-feature", base_dir=ws_base)
        assert data["workstream_id"] == "first-real-feature"

        # The sandbox is untouched — still present, still a plain
        # directory, never converted into the new workstream.
        assert sandbox.exists()


class TestFirstTaskPreviewDocumented:
    """Static content contract for the first-task preview and outcome
    selection (VFO-08-AC-01's documented content; the dynamic scenario is
    owned by the blocked test_onboarding_journey.py)."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.content = VIRGIL_PATH.read_text(encoding="utf-8")
        start = self.content.index(FIRST_TASK_HEADING)
        end = self.content.index(FITTING_HEADING, start)
        self.section = self.content[start:end]

    def test_section_exists_before_fitting(self) -> None:
        assert FIRST_TASK_HEADING in self.content
        assert self.content.index(FIRST_TASK_HEADING) < self.content.index(
            FITTING_HEADING
        )

    def test_preview_fields_named(self) -> None:
        for field in (
            "Goal",
            "Expected duration",
            "Expected artifacts",
            "Required decisions",
            "Cleanup method",
        ):
            assert field in self.section

    def test_expected_duration_is_the_fixed_estimate(self) -> None:
        assert "approximately 5" in self.section
        assert "10 minutes" in self.section

    def test_blank_or_declined_approval_creates_no_sandbox(self) -> None:
        assert "blank or declined approval creates no sandbox" in self.section.lower()

    def test_sandbox_path_and_session_id_documented(self) -> None:
        assert ".current-work/onboarding-spike/<uuid4>/" in self.section
        assert "uuid.uuid4()" in self.section

    def test_no_branch_or_commit_and_no_uncommitted_leakage(self) -> None:
        assert "no branch and no commit" in self.section
        assert "uncommitted changes" in self.section

    def test_three_outcomes_documented(self) -> None:
        discard_idx = self.section.index("Discard")
        retain_idx = self.section.index("Retain")
        handoff_idx = self.section.index("Production handoff")
        assert discard_idx < retain_idx < handoff_idx

    def test_retention_targets_docs_spikes(self) -> None:
        assert "docs/spikes/<name>/" in self.section

    def test_production_handoff_does_not_promote_sandbox(self) -> None:
        assert "never promoted to production work" in self.section

    def test_time_and_decision_bounds_documented(self) -> None:
        assert "ten minutes" in self.section
        assert "five user decisions" in self.section
