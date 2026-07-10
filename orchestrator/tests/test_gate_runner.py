import subprocess
from pathlib import Path
from unittest.mock import patch

from orchestrator.adapters.gate_runner import WorkingTreeGate
from orchestrator.entities import GateResult


def _completed_process(
    cmd: list[str], stdout: str = "", stderr: str = "", returncode: int = 0
) -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(
        args=cmd, returncode=returncode, stdout=stdout, stderr=stderr
    )


class TestWorkingTreeGateVerify:
    def test_exit_zero_and_clean_tree_passes(self):
        gate = WorkingTreeGate(Path("/repo"))

        with patch(
            "orchestrator.adapters.gate_runner.subprocess.run",
            return_value=_completed_process(["git", "status", "--porcelain"]),
        ) as run:
            result = gate.verify(Path("/repo"), exit_code=0)

        assert result == GateResult(
            passed=True, errored=False, hook="working-tree", error_count=0
        )
        run.assert_called_once_with(
            ["git", "status", "--porcelain"],
            cwd=Path("/repo"),
            capture_output=True,
            text=True,
        )

    def test_exit_zero_and_dirty_tree_is_confabulation(self):
        gate = WorkingTreeGate(Path("/repo"))

        with patch(
            "orchestrator.adapters.gate_runner.subprocess.run",
            return_value=_completed_process(
                ["git", "status", "--porcelain"],
                stdout=" M alpha.py\n?? beta.py\n",
            ),
        ):
            result = gate.verify(Path("/repo"), exit_code=0)

        assert result == GateResult(
            passed=False,
            errored=True,
            hook="confabulation",
            error_count=2,
            output="exit 0 but uncommitted changes: alpha.py, beta.py",
        )

    def test_nonzero_and_dirty_tree_fails_without_erroring(self):
        gate = WorkingTreeGate(Path("/repo"))

        with patch(
            "orchestrator.adapters.gate_runner.subprocess.run",
            return_value=_completed_process(
                ["git", "status", "--porcelain"],
                stdout=" M alpha.py\n?? beta.py\n",
            ),
        ):
            result = gate.verify(Path("/repo"), exit_code=1)

        assert result == GateResult(
            passed=False,
            errored=False,
            hook="working-tree",
            error_count=2,
            output="alpha.py, beta.py",
        )

    def test_nonzero_and_clean_tree_fails(self):
        gate = WorkingTreeGate(Path("/repo"))

        with patch(
            "orchestrator.adapters.gate_runner.subprocess.run",
            return_value=_completed_process(["git", "status", "--porcelain"]),
        ):
            result = gate.verify(Path("/repo"), exit_code=1)

        assert result == GateResult(
            passed=False,
            errored=False,
            hook="working-tree",
            error_count=0,
        )


class TestWorkingTreeGateArtifactsChanged:
    def test_artifacts_changed_detects_tracked_changes(self, tmp_path):
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "prd.md").write_text("# PRD\n")

        gate = WorkingTreeGate(tmp_path)

        def fake_run(cmd, cwd, capture_output, text):
            if cmd[:4] == ["git", "diff", "--name-only", "HEAD"]:
                return _completed_process(cmd, stdout="docs/prd.md\n")
            if cmd[:2] == ["git", "ls-files"]:
                return _completed_process(cmd)
            raise AssertionError(f"unexpected command: {cmd}")

        with patch(
            "orchestrator.adapters.gate_runner.subprocess.run", side_effect=fake_run
        ):
            assert gate.artifacts_changed(["docs/*.md"]) is True

    def test_artifacts_changed_detects_untracked_changes(self, tmp_path):
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "notes.md").write_text("# Notes\n")

        gate = WorkingTreeGate(tmp_path)

        def fake_run(cmd, cwd, capture_output, text):
            if cmd[:4] == ["git", "diff", "--name-only", "HEAD"]:
                return _completed_process(cmd)
            if cmd[:2] == ["git", "ls-files"]:
                return _completed_process(cmd, stdout="docs/notes.md\n")
            raise AssertionError(f"unexpected command: {cmd}")

        with patch(
            "orchestrator.adapters.gate_runner.subprocess.run", side_effect=fake_run
        ):
            assert gate.artifacts_changed(["docs/*.md"]) is True

    def test_artifacts_changed_ignores_unmatched_patterns(self, tmp_path):
        gate = WorkingTreeGate(tmp_path)

        with patch("orchestrator.adapters.gate_runner.subprocess.run") as run:
            assert gate.artifacts_changed(["docs/*.md"]) is False

        run.assert_not_called()


class TestWorkingTreeGateCleanTree:
    def test_clean_tree_runs_checkout_and_clean(self):
        gate = WorkingTreeGate(Path("/repo"))
        calls = []

        def fake_run(cmd, cwd, capture_output, check):
            calls.append(cmd)
            return _completed_process(cmd)

        with patch(
            "orchestrator.adapters.gate_runner.subprocess.run", side_effect=fake_run
        ):
            gate.clean_tree(Path("/repo"))

        assert calls == [
            ["git", "checkout", "."],
            ["git", "clean", "-fd"],
        ]


class TestWorkingTreeGateGitFailure:
    def test_verify_returns_errored_on_git_status_failure(self):
        gate = WorkingTreeGate(Path("/repo"))

        with patch(
            "orchestrator.adapters.gate_runner.subprocess.run",
            return_value=_completed_process(
                ["git", "status", "--porcelain"],
                returncode=128,
                stderr="fatal: not a git repository",
            ),
        ):
            result = gate.verify(Path("/repo"), exit_code=0)

        assert result.errored is True
        assert result.passed is False
        assert result.hook == "git-error"
        assert "not a git repository" in result.output
