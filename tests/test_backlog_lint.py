"""Contract tests for factory/scripts/backlog-lint."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "factory" / "scripts" / "backlog-lint"


def _write_story(backlog_dir: Path, story_id: str, body: str) -> Path:
    """Write one backlog story file under the provided backlog directory."""
    path = backlog_dir / f"{story_id}.md"
    path.write_text(body, encoding="utf-8")
    return path


def _run_backlog_lint(backlog_dir: Path) -> subprocess.CompletedProcess[str]:
    """Run backlog-lint against the provided backlog directory."""
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--backlog-dir", str(backlog_dir)],
        capture_output=True,
        text=True,
        check=False,
    )


def _base_story(
    *,
    risk_domains: str | None = None,
    strategy: str | None = None,
    quality_gates: str | None = None,
    notes: str | None = None,
    seam_outputs: str | None = None,
    impl_outputs: str | None = None,
    outputs: str = "[src/feature.py]",
) -> str:
    """Render a minimal valid story frontmatter body for backlog-lint tests."""
    lines = [
        "---",
        "id: ST-9999",
        "epic: Test Epic",
        "title: Test Story",
        "tier: economy",
        "status: pending",
        f"outputs: {outputs}",
    ]
    if risk_domains is not None:
        lines.append(f"risk_domains: {risk_domains}")
    if strategy is not None:
        lines.append(f"strategy: {strategy}")
    if quality_gates is not None:
        lines.append(f"quality-gates: {quality_gates}")
    if notes is not None:
        lines.append(f"notes: {notes}")
    if seam_outputs is not None:
        lines.append(f"seam_outputs: {seam_outputs}")
    if impl_outputs is not None:
        lines.append(f"impl_outputs: {impl_outputs}")
    lines.extend(["---", "", "# Test Story"])
    return "\n".join(lines)


def test_existing_story_without_new_fields_is_valid(tmp_path: Path) -> None:
    """Absent optional fields still passes backlog-lint."""
    backlog_dir = tmp_path / "backlog"
    backlog_dir.mkdir()
    _write_story(backlog_dir, "ST-9999", _base_story())

    result = _run_backlog_lint(backlog_dir)

    assert result.returncode == 0, result.stdout
    assert "error(s)" in result.stdout


def test_unknown_risk_domain_is_rejected(tmp_path: Path) -> None:
    """risk_domains uses a closed enum."""
    backlog_dir = tmp_path / "backlog"
    backlog_dir.mkdir()
    _write_story(
        backlog_dir,
        "ST-9999",
        _base_story(risk_domains="[securty]"),
    )

    result = _run_backlog_lint(backlog_dir)

    assert result.returncode == 1
    assert "risk_domains" in result.stdout
    assert "securty" in result.stdout


def test_unknown_strategy_is_rejected(tmp_path: Path) -> None:
    """strategy uses a closed enum."""
    backlog_dir = tmp_path / "backlog"
    backlog_dir.mkdir()
    _write_story(
        backlog_dir,
        "ST-9999",
        _base_story(strategy="seams"),
    )

    result = _run_backlog_lint(backlog_dir)

    assert result.returncode == 1
    assert "strategy" in result.stdout
    assert "seams" in result.stdout


def test_quality_gates_accepts_known_gate_names(tmp_path: Path) -> None:
    """quality_gates accepts the known semantic gate names."""
    backlog_dir = tmp_path / "backlog"
    backlog_dir.mkdir()
    _write_story(
        backlog_dir,
        "ST-9999",
        _base_story(
            quality_gates="[crap-score, mutation-analysis, dependency-check]",
        ),
    )

    result = _run_backlog_lint(backlog_dir)

    assert result.returncode == 0, result.stdout


def test_quality_gates_rejects_unknown_gate_names(tmp_path: Path) -> None:
    """quality_gates uses a closed gate set."""
    backlog_dir = tmp_path / "backlog"
    backlog_dir.mkdir()
    _write_story(
        backlog_dir,
        "ST-9999",
        _base_story(
            quality_gates="[crap-score, mutation-analysis, dependency-check, rainbow-gate]"
        ),
    )

    result = _run_backlog_lint(backlog_dir)

    assert result.returncode == 1
    assert "quality-gates" in result.stdout
    assert "rainbow-gate" in result.stdout


def test_quality_gates_subset_requires_justification_notes(tmp_path: Path) -> None:
    """Omitting a default gate requires a notes justification."""
    backlog_dir = tmp_path / "backlog"
    backlog_dir.mkdir()
    _write_story(
        backlog_dir,
        "ST-9999",
        _base_story(quality_gates="[crap-score, dependency-check]"),
    )

    result = _run_backlog_lint(backlog_dir)

    assert result.returncode == 1
    assert "notes" in result.stdout
    assert "mutation-analysis" in result.stdout


def test_quality_gates_subset_with_justification_notes_passes(tmp_path: Path) -> None:
    """A notes justification satisfies the omission requirement."""
    backlog_dir = tmp_path / "backlog"
    backlog_dir.mkdir()
    _write_story(
        backlog_dir,
        "ST-9999",
        _base_story(
            quality_gates="[crap-score, dependency-check]",
            notes="mutation-analysis excluded: no production code changes.",
        ),
    )

    result = _run_backlog_lint(backlog_dir)

    assert result.returncode == 0, result.stdout


def test_overlapping_seam_and_impl_outputs_are_rejected(tmp_path: Path) -> None:
    """seam_outputs and impl_outputs must be disjoint."""
    backlog_dir = tmp_path / "backlog"
    backlog_dir.mkdir()
    _write_story(
        backlog_dir,
        "ST-9999",
        _base_story(
            strategy="seams-first",
            seam_outputs="[tests/test_feature.py]",
            impl_outputs="[tests/test_feature.py, src/feature.py]",
            outputs="[tests/test_feature.py, src/feature.py]",
        ),
    )

    result = _run_backlog_lint(backlog_dir)

    assert result.returncode == 1
    assert "overlap" in result.stdout
    assert "tests/test_feature.py" in result.stdout


def test_seams_first_requires_union_equal_outputs(tmp_path: Path) -> None:
    """seams-first stories must partition outputs exactly."""
    backlog_dir = tmp_path / "backlog"
    backlog_dir.mkdir()
    _write_story(
        backlog_dir,
        "ST-9999",
        _base_story(
            strategy="seams-first",
            seam_outputs="[tests/test_feature.py]",
            impl_outputs="[src/feature.py]",
            outputs="[tests/test_feature.py, src/other.py]",
        ),
    )

    result = _run_backlog_lint(backlog_dir)

    assert result.returncode == 1
    assert "seams-first" in result.stdout
    assert "outputs" in result.stdout
