"""Contract tests for crap-score script threshold resolution.

Validates that:
- Threshold reads from testing.yaml gates.crap_score.threshold when present
- Threshold falls back to hardcoded 30 when testing.yaml has no gates section
- --threshold CLI flag overrides testing.yaml value
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _get_repo_root() -> Path:
    """Find the repository root by looking for factory directory."""
    current = Path.cwd()
    for _ in range(10):
        if (current / "factory").is_dir():
            return current
        current = current.parent
    raise RuntimeError("Could not find repository root")


REPO_ROOT = _get_repo_root()
CRAP_SCRIPT = REPO_ROOT / "factory" / "scripts" / "crap-score"


def test_crap_score_reads_threshold_from_testing_yaml(tmp_path: Path) -> None:
    """Threshold resolution reads from testing.yaml when gates.crap_score.threshold exists."""
    # Setup: Create a minimal testing.yaml with gates.crap_score.threshold
    charter_dir = tmp_path / "docs" / "charter"
    charter_dir.mkdir(parents=True)

    testing_yaml = charter_dir / "testing.yaml"
    testing_yaml.write_text(
        """---
gates:
  crap_score:
    enabled: true
    threshold: 8
  mutation_testing:
    enabled: false
""",
        encoding="utf-8",
    )

    # Create minimal Python source directory with a single function
    src_dir = tmp_path / "src"
    src_dir.mkdir()

    test_file = src_dir / "example.py"
    test_file.write_text(
        """def simple_func():
    return 42
""",
        encoding="utf-8",
    )

    # Create a minimal coverage.json that shows full coverage
    cov_json = tmp_path / "coverage.json"
    cov_json.write_text(
        """{
  "files": {
    "src/example.py": {
      "executed_lines": [2],
      "missing_lines": []
    }
  }
}""",
        encoding="utf-8",
    )

    # Run crap-score script pointing to the temp directory
    result = subprocess.run(
        [
            sys.executable,
            str(CRAP_SCRIPT),
            "--source-root",
            str(src_dir),
            "--coverage-json",
            str(cov_json),
        ],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
    )

    # Check stderr output for threshold resolution
    assert "threshold=8" in result.stderr, (
        f"Expected 'threshold=8' in output, got: {result.stderr}"
    )


def test_crap_score_falls_back_to_default_when_no_gates_section(tmp_path: Path) -> None:
    """Threshold falls back to hardcoded 30 when testing.yaml has no gates section."""
    # Setup: Create testing.yaml without gates section
    charter_dir = tmp_path / "docs" / "charter"
    charter_dir.mkdir(parents=True)

    testing_yaml = charter_dir / "testing.yaml"
    testing_yaml.write_text(
        """---
test_command: "pytest"
""",
        encoding="utf-8",
    )

    # Create minimal Python source directory
    src_dir = tmp_path / "src"
    src_dir.mkdir()

    test_file = src_dir / "example.py"
    test_file.write_text(
        """def simple_func():
    return 42
""",
        encoding="utf-8",
    )

    # Create minimal coverage.json
    cov_json = tmp_path / "coverage.json"
    cov_json.write_text(
        """{
  "files": {
    "src/example.py": {
      "executed_lines": [2],
      "missing_lines": []
    }
  }
}""",
        encoding="utf-8",
    )

    # Run crap-score script
    result = subprocess.run(
        [
            sys.executable,
            str(CRAP_SCRIPT),
            "--source-root",
            str(src_dir),
            "--coverage-json",
            str(cov_json),
        ],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
    )

    # Check stderr output for default threshold
    assert "threshold=30" in result.stderr, (
        f"Expected 'threshold=30' in output, got: {result.stderr}"
    )


def test_crap_score_cli_flag_overrides_testing_yaml(tmp_path: Path) -> None:
    """CLI --threshold flag overrides testing.yaml value."""
    # Setup: Create testing.yaml with gates.crap_score.threshold
    charter_dir = tmp_path / "docs" / "charter"
    charter_dir.mkdir(parents=True)

    testing_yaml = charter_dir / "testing.yaml"
    testing_yaml.write_text(
        """---
gates:
  crap_score:
    enabled: true
    threshold: 8
""",
        encoding="utf-8",
    )

    # Create minimal Python source directory
    src_dir = tmp_path / "src"
    src_dir.mkdir()

    test_file = src_dir / "example.py"
    test_file.write_text(
        """def simple_func():
    return 42
""",
        encoding="utf-8",
    )

    # Create minimal coverage.json
    cov_json = tmp_path / "coverage.json"
    cov_json.write_text(
        """{
  "files": {
    "src/example.py": {
      "executed_lines": [2],
      "missing_lines": []
    }
  }
}""",
        encoding="utf-8",
    )

    # Run crap-score with CLI --threshold flag
    result = subprocess.run(
        [
            sys.executable,
            str(CRAP_SCRIPT),
            "--source-root",
            str(src_dir),
            "--coverage-json",
            str(cov_json),
            "--threshold",
            "15.5",
        ],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
    )

    # Check stderr output for CLI-overridden threshold
    assert "threshold=15.5" in result.stderr, (
        f"Expected 'threshold=15.5' in output, got: {result.stderr}"
    )


def test_crap_score_threshold_does_not_leak_from_sibling_gate(tmp_path: Path) -> None:
    """FAGAN-0031: threshold search must be bounded to the crap_score section.

    When crap_score has no threshold but a sibling gate does, the function
    must return None so resolve_threshold falls back to the hardcoded default,
    not silently adopt the sibling's threshold."""
    charter_dir = tmp_path / "docs" / "charter"
    charter_dir.mkdir(parents=True)

    testing_yaml = charter_dir / "testing.yaml"
    testing_yaml.write_text(
        """---
gates:
  crap_score:
    enabled: true
  mutation_testing:
    enabled: false
    threshold: 50
""",
        encoding="utf-8",
    )

    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "example.py").write_text(
        "def simple_func():\n    return 42\n", encoding="utf-8"
    )

    cov_json = tmp_path / "coverage.json"
    cov_json.write_text(
        '{"files": {"src/example.py": {"executed_lines": [2], "missing_lines": []}}}',
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(CRAP_SCRIPT),
            "--source-root",
            str(src_dir),
            "--coverage-json",
            str(cov_json),
        ],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
    )

    # Must fall back to default 30, NOT pick up mutation_testing's 50
    assert "threshold=30" in result.stderr, (
        f"Expected 'threshold=30' (default fallback), got: {result.stderr}"
    )
