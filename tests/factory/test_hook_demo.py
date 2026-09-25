"""Contract tests for ST-0289: gate demonstration before choosing hooks.

Owned contracts (EPIC 4 Ownership Resolution table,
docs/spec/value-first-onboarding-journey-qa-strategy.md):

  - VFO-07-IT-01 — Gate demonstration shows failure and success without
    target changes (`Scenario: Gate demonstration shows one
    failure-to-pass cycle`). Real filesystem and subprocess: `hook-demo`
    shells out to the real `mdformat` gate, the same one the
    `agent_factory_hook-mdformat` pre-commit hook runs.

Skipping the demonstration (`Scenario: Skipping the gate demonstration
preserves defaults`) is a session-level decision that lives outside this
script — the contract for this file is that `hook-demo` is never invoked
as a side effect of import, so skipping never creates a fixture.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from conftest import load_script

hd = load_script("hook-demo")


@pytest.fixture
def repo_root(tmp_path: Path) -> Path:
    return tmp_path


class TestCreateFixture:
    def test_writes_fixture_under_current_work_hook_demo(self, repo_root: Path):
        fixture = hd.create_fixture(repo_root)

        assert fixture == repo_root / ".current-work" / "hook-demo" / "demo-fixture.md"
        assert fixture.is_file()

    def test_fixture_contains_a_deliberate_formatting_error(self, repo_root: Path):
        fixture = hd.create_fixture(repo_root)

        content = fixture.read_text()
        assert "* " in content  # asterisk bullet, not the canonical dash

    def test_importing_the_module_creates_no_fixture(self, repo_root: Path):
        # The module was already imported (load_script, above) before this
        # test's tmp_path existed. Re-asserting here documents the contract:
        # nothing in this module runs at import time.
        assert not (repo_root / ".current-work").exists()


class TestGateFailsOnBrokenFixture:
    def test_check_fails_on_the_disposable_fixture(self, repo_root: Path):
        fixture = hd.create_fixture(repo_root)

        result = hd.run_gate_check(fixture)

        assert result.returncode != 0
        assert (result.stdout + result.stderr).strip() != ""

    def test_check_failure_names_the_fixture(self, repo_root: Path):
        fixture = hd.create_fixture(repo_root)

        result = hd.run_gate_check(fixture)

        assert str(fixture) in (result.stdout + result.stderr)


class TestCorrectFixture:
    def test_correction_rewrites_asterisk_bullets_to_dashes(self, repo_root: Path):
        fixture = hd.create_fixture(repo_root)

        hd.correct_fixture(fixture)

        content = fixture.read_text()
        assert "* deliberately" not in content
        assert "- deliberately" in content

    def test_check_passes_after_correction(self, repo_root: Path):
        fixture = hd.create_fixture(repo_root)
        hd.correct_fixture(fixture)

        result = hd.run_gate_check(fixture)

        assert result.returncode == 0


class TestRemoveFixtureDir:
    def test_removes_the_directory_and_verifies_absence(self, repo_root: Path):
        hd.create_fixture(repo_root)
        base_dir = hd.fixture_base_dir(repo_root)
        assert base_dir.exists()

        hd.remove_fixture_dir(base_dir)

        assert not base_dir.exists()

    def test_is_idempotent_on_an_already_removed_directory(self, repo_root: Path):
        base_dir = hd.fixture_base_dir(repo_root)
        assert not base_dir.exists()

        hd.remove_fixture_dir(base_dir)  # must not raise

        assert not base_dir.exists()


class TestRunDemonstration:
    """VFO-07-IT-01: one failure-to-pass cycle, target project unchanged."""

    def test_full_cycle_fails_then_passes_then_cleans_up(self, repo_root: Path):
        (repo_root / "untouched.txt").write_text("target project file\n")

        result = hd.run_demonstration(repo_root)

        assert result.failure_returncode != 0
        assert result.pass_returncode == 0
        assert result.cleaned_up is True

    def test_fixture_directory_is_gone_after_the_cycle(self, repo_root: Path):
        hd.run_demonstration(repo_root)

        assert not (repo_root / ".current-work" / "hook-demo").exists()

    def test_target_project_files_are_unchanged(self, repo_root: Path):
        target_file = repo_root / "README.md"
        target_file.write_text("# Target project\n")
        before = target_file.read_text()

        hd.run_demonstration(repo_root)

        assert target_file.read_text() == before

    def test_gate_unexpectedly_passing_on_the_broken_fixture_raises(
        self, repo_root: Path, monkeypatch: pytest.MonkeyPatch
    ):
        import subprocess

        def _always_pass(fixture, script_dir=hd.SCRIPT_DIR):
            return subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")

        monkeypatch.setattr(hd, "run_gate_check", _always_pass)

        with pytest.raises(hd.HookDemoError):
            hd.run_demonstration(repo_root)

        # cleanup still ran even though the gate behaved unexpectedly
        assert not (repo_root / ".current-work" / "hook-demo").exists()


class TestInterruptDuringDemonstration:
    """`hook-demo` removes the fixture on exit, even when interrupted."""

    def test_exception_during_the_gate_run_still_removes_the_fixture(
        self, repo_root: Path, monkeypatch: pytest.MonkeyPatch
    ):
        def _raise(*args, **kwargs):
            raise KeyboardInterrupt

        monkeypatch.setattr(hd, "run_gate_check", _raise)

        with pytest.raises(KeyboardInterrupt):
            hd.run_demonstration(repo_root)

        assert not (repo_root / ".current-work" / "hook-demo").exists()

    def test_exception_during_correction_still_removes_the_fixture(
        self, repo_root: Path, monkeypatch: pytest.MonkeyPatch
    ):
        def _raise(*args, **kwargs):
            raise OSError("simulated interruption")

        monkeypatch.setattr(hd, "correct_fixture", _raise)

        with pytest.raises(OSError):
            hd.run_demonstration(repo_root)

        assert not (repo_root / ".current-work" / "hook-demo").exists()


class TestMain:
    def test_main_returns_zero_on_a_clean_cycle(
        self, repo_root: Path, capsys: pytest.CaptureFixture
    ):
        exit_code = hd.main(["--repo-root", str(repo_root)])

        assert exit_code == 0
        out = capsys.readouterr().out
        assert "gate reports a failure, as expected" in out
        assert "gate passes on the corrected fixture" in out
        assert not (repo_root / ".current-work" / "hook-demo").exists()

    def test_main_returns_nonzero_when_the_gate_misbehaves(
        self, repo_root: Path, monkeypatch: pytest.MonkeyPatch
    ):
        import subprocess

        def _always_pass(fixture, script_dir=hd.SCRIPT_DIR):
            return subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")

        monkeypatch.setattr(hd, "run_gate_check", _always_pass)

        exit_code = hd.main(["--repo-root", str(repo_root)])

        assert exit_code == 1
