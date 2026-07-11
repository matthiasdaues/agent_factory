from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from orchestrator.adapters.model_matrix import FileModelMatrix
from orchestrator.ports import ModelMatrix


VALID_MATRIX = """\
# Model config — operator-curated artifact (ADR-0020, ADR-0021)

[facts]
copilot.economy  = gpt-5.4-mini
copilot.standard = gpt-5.4
copilot.strong   = claude-opus-4-6
claude.standard  = claude-sonnet-4-5
on_missing = auto
"""


DEFAULT_ON_MISSING_MATRIX = """\
[facts]
copilot.economy = gpt-5.4-mini
"""


def _write_matrix(tmp_path: Path, content: str) -> Path:
    matrix_path = tmp_path / "model.conf"
    matrix_path.write_text(textwrap.dedent(content), encoding="utf-8")
    return matrix_path


def test_parse_valid_matrix_file(tmp_path: Path):
    matrix = FileModelMatrix(_write_matrix(tmp_path, VALID_MATRIX))

    assert isinstance(matrix, ModelMatrix)
    assert matrix.facts == {
        "copilot.economy": "gpt-5.4-mini",
        "copilot.standard": "gpt-5.4",
        "copilot.strong": "claude-opus-4-6",
        "claude.standard": "claude-sonnet-4-5",
        "on_missing": "auto",
    }


def test_get_model_returns_configured_model(tmp_path: Path):
    matrix = FileModelMatrix(_write_matrix(tmp_path, VALID_MATRIX))

    assert matrix.get_model("copilot", "strong") == "claude-opus-4-6"


def test_get_model_returns_none_for_unknown_cli_or_tier(tmp_path: Path):
    matrix = FileModelMatrix(_write_matrix(tmp_path, VALID_MATRIX))

    assert matrix.get_model("claude", "economy") is None
    assert matrix.get_model("unknown", "strong") is None


def test_get_on_missing_returns_configured_value(tmp_path: Path):
    matrix = FileModelMatrix(_write_matrix(tmp_path, VALID_MATRIX))

    assert matrix.get_on_missing() == "auto"


def test_get_on_missing_defaults_to_halt(tmp_path: Path):
    matrix = FileModelMatrix(_write_matrix(tmp_path, DEFAULT_ON_MISSING_MATRIX))

    assert matrix.get_on_missing() == "halt"


def test_configured_clis_returns_unique_cli_names(tmp_path: Path):
    matrix = FileModelMatrix(_write_matrix(tmp_path, VALID_MATRIX))

    assert matrix.configured_clis() == ["claude", "copilot"]


def test_configured_clis_excludes_on_missing(tmp_path: Path):
    matrix = FileModelMatrix(_write_matrix(tmp_path, DEFAULT_ON_MISSING_MATRIX))

    assert matrix.configured_clis() == ["copilot"]


def test_missing_file_raises_file_not_found_error(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        FileModelMatrix(tmp_path / "missing.conf")


def test_invalid_on_missing_policy_raises_value_error(tmp_path: Path):
    matrix_path = _write_matrix(
        tmp_path,
        """\
        [facts]
        copilot.economy = gpt-5.4-mini
        on_missing = maybe
        """,
    )

    with pytest.raises(ValueError, match="invalid on_missing policy"):
        FileModelMatrix(matrix_path)


def test_unknown_section_raises_value_error(tmp_path: Path):
    matrix_path = _write_matrix(
        tmp_path,
        """\
        [policy]
        class.trivial = economy
        """,
    )

    with pytest.raises(ValueError, match="unknown section"):
        FileModelMatrix(matrix_path)
