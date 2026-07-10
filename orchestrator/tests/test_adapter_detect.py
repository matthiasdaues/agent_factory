"""Tests for adapter auto-detection (ST-0047, UC-10 step 4, FR-R2, BR-042).

Pure unit tests for `adapter_detect.py` in isolation — no `AdapterRegistry`
involved (that composition is exercised end to end in
`tests/test_cli_list.py`'s `TestAutoDetect`). `probe_binary` is checked
against real filesystem fixtures (an executable file, a non-executable
file, a missing path); `detect_candidates` is checked with a stubbed
`which_fn` so results don't depend on what's actually installed on the
machine running the suite.
"""

from __future__ import annotations

import os
import stat
from pathlib import Path

from orchestrator.adapters.adapter_detect import (
    KNOWN_ADAPTER_BINARIES,
    DetectedAdapter,
    detect_candidates,
    probe_binary,
)


class TestProbeBinary:
    def test_executable_file_passes(self, tmp_path: Path) -> None:
        binary = tmp_path / "copilot"
        binary.write_text("#!/bin/sh\necho hi\n")
        binary.chmod(binary.stat().st_mode | stat.S_IEXEC)

        assert probe_binary(str(binary)) is True

    def test_non_executable_file_fails(self, tmp_path: Path) -> None:
        binary = tmp_path / "copilot"
        binary.write_text("not executable")
        binary.chmod(0o644)

        assert probe_binary(str(binary)) is False

    def test_missing_path_fails(self, tmp_path: Path) -> None:
        missing = tmp_path / "does-not-exist"

        assert probe_binary(str(missing)) is False

    def test_directory_fails(self, tmp_path: Path) -> None:
        directory = tmp_path / "adir"
        directory.mkdir()
        os.chmod(directory, 0o755)

        assert probe_binary(str(directory)) is False


class TestKnownAdapterBinaries:
    def test_copilot_is_the_seeded_known_binary(self) -> None:
        """This codebase ships exactly one concrete CLIAdapter today
        (CopilotAdapter, adapters/copilot.py) — see ST-0047.md's Analysis
        for why the allowlist starts here and only here."""
        assert KNOWN_ADAPTER_BINARIES == ("copilot",)


class TestDetectCandidates:
    def test_no_candidates_on_path_yields_empty_list(self) -> None:
        result = detect_candidates(which_fn=lambda name: None)

        assert result == []

    def test_known_binary_found_and_executable_is_a_candidate(
        self, tmp_path: Path
    ) -> None:
        binary = tmp_path / "copilot"
        binary.write_text("#!/bin/sh\n")
        binary.chmod(binary.stat().st_mode | stat.S_IEXEC)

        result = detect_candidates(which_fn=lambda name: str(binary))

        assert result == [DetectedAdapter(name="copilot", binary_path=str(binary))]

    def test_found_but_not_executable_is_not_a_candidate(self, tmp_path: Path) -> None:
        """The probe re-validates a `which_fn` hit — a stale/broken PATH
        entry never becomes a candidate just because it resolved."""
        binary = tmp_path / "copilot"
        binary.write_text("not executable")
        binary.chmod(0o644)

        result = detect_candidates(which_fn=lambda name: str(binary))

        assert result == []

    def test_only_scans_known_names(self, tmp_path: Path) -> None:
        """A `which_fn` that resolves anything is still constrained to the
        known-binary-name allowlist — auto-detect never scans arbitrary
        PATH entries."""
        seen_names = []

        def which_fn(name: str) -> str | None:
            seen_names.append(name)
            return None

        detect_candidates(
            known_names=("copilot", "hypothetical-other-cli"), which_fn=which_fn
        )

        assert seen_names == ["copilot", "hypothetical-other-cli"]
