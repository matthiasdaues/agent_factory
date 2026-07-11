"""Tests for `configure > model-matrix` (ST-0050).

Traces: UC-10, FR-R9, FR-K5, ADR-0017 point 5, ADR-0018 point 3,
cli_specification.md lines 166-179. Covers:
  - `show`: renders facts (adapter -> tier -> model) and policy
    (classification -> tier, phase -> tier, on_missing) as `display`
    content; degrades to a readable message (not a crash) on a missing or
    malformed matrix file.
  - `validate`: reuses `scripts/matrix-lint` (not a reimplementation) —
    one test runs the real script end to end, others inject `lint_fn` to
    isolate the pass/fail branches without a real subprocess.
  - `edit`: opens `$EDITOR` via an injected `run_fn`/`get_editor` seam
    (never a real subprocess in tests); reports a clear error when
    `$EDITOR` is unset instead of crashing; repopulates adapter
    dictionaries from the edited matrix on success; leaves dictionaries
    untouched when the editor exits non-zero or the edited file is invalid.
  - `populate_adapter_dictionaries_from_matrix`: the facts-to-dictionary
    population step, exercised against the real `TomlAdapterRegistry` and
    `FileModelMatrix` (not mocks, mirroring test_configure_defaults.py and
    test_cli_list.py), including the idempotency guarantee the story
    requires — running it twice produces the same dictionary state and
    raises nothing either time.
"""

from __future__ import annotations

import shutil
import sys
import textwrap
from pathlib import Path

import pytest

from orchestrator.adapters.adapter_registry import TomlAdapterRegistry
from orchestrator.adapters.model_matrix import FileModelMatrix
from orchestrator.cli import (
    build_configure_model_matrix_dispatch,
    populate_adapter_dictionaries_from_matrix,
)
from orchestrator.entities import MenuNode, MenuNodeType

_REPO_SCRIPTS = Path(__file__).resolve().parents[2] / "factory" / "scripts"


def _node(node_id: str, node_type: MenuNodeType = MenuNodeType.FUNCTION) -> MenuNode:
    return MenuNode(id=node_id, label=node_id, type=node_type)


def _orch_dir(tmp_path: Path) -> Path:
    return tmp_path / ".orchestrator"


def _write_matrix(path: Path, content: str) -> Path:
    path.write_text(textwrap.dedent(content), encoding="utf-8")
    return path


VALID_MATRIX = """\
[facts]
copilot.economy  = gpt-5.4-mini
copilot.standard = gpt-5.4
copilot.strong   = claude-opus-4-6
claude.economy   = claude-haiku-4-5
claude.standard  = claude-sonnet-4-5
claude.strong    = claude-opus-4-6
on_missing = auto
"""

# --- show: facts rendering, missing/malformed degrade gracefully -----------


class TestShow:
    def test_show_renders_facts(self, tmp_path: Path) -> None:
        matrix_path = _write_matrix(tmp_path / "model.conf", VALID_MATRIX)
        adapter_registry = TomlAdapterRegistry(_orch_dir(tmp_path))
        dispatch = build_configure_model_matrix_dispatch(matrix_path, adapter_registry)

        outcome = dispatch(_node("configure.model-matrix.show", MenuNodeType.DISPLAY))

        assert "copilot" in outcome.content
        assert "gpt-5.4-mini" in outcome.content
        assert "economy" in outcome.content
        assert "claude" in outcome.content
        assert "claude-sonnet-4-5" in outcome.content
        assert "on_missing = auto" in outcome.content

    def test_show_missing_file_reports_readable_message_not_a_crash(
        self, tmp_path: Path
    ) -> None:
        matrix_path = tmp_path / "model.conf"
        adapter_registry = TomlAdapterRegistry(_orch_dir(tmp_path))
        dispatch = build_configure_model_matrix_dispatch(matrix_path, adapter_registry)

        outcome = dispatch(_node("configure.model-matrix.show", MenuNodeType.DISPLAY))

        assert "not found" in outcome.content.lower()

    def test_show_malformed_file_reports_readable_message_not_a_crash(
        self, tmp_path: Path
    ) -> None:
        matrix_path = _write_matrix(
            tmp_path / "model.conf",
            "[facts]\ncopilot.economy = gpt-5.4-mini\n\n[bogus]\nx = 1\n",
        )
        adapter_registry = TomlAdapterRegistry(_orch_dir(tmp_path))
        dispatch = build_configure_model_matrix_dispatch(matrix_path, adapter_registry)

        outcome = dispatch(_node("configure.model-matrix.show", MenuNodeType.DISPLAY))

        assert "invalid" in outcome.content.lower()


# --- validate: reuses scripts/matrix-lint, does not reimplement it ----------


class TestValidate:
    def test_valid_matrix_reports_valid(self, tmp_path: Path, capsys) -> None:
        matrix_path = _write_matrix(tmp_path / "model.conf", VALID_MATRIX)
        adapter_registry = TomlAdapterRegistry(_orch_dir(tmp_path))
        dispatch = build_configure_model_matrix_dispatch(
            matrix_path, adapter_registry, lint_fn=lambda path: (0, "")
        )

        outcome = dispatch(_node("configure.model-matrix.validate"))

        assert outcome.long_running is False
        assert capsys.readouterr().out.strip() == "valid"

    def test_invalid_matrix_reports_errors(self, tmp_path: Path, capsys) -> None:
        matrix_path = _write_matrix(tmp_path / "model.conf", VALID_MATRIX)
        adapter_registry = TomlAdapterRegistry(_orch_dir(tmp_path))
        dispatch = build_configure_model_matrix_dispatch(
            matrix_path,
            adapter_registry,
            lint_fn=lambda path: (
                1,
                "[ERROR  ] MX-RESOLVE  tier 'strong' unresolved\n",
            ),
        )

        outcome = dispatch(_node("configure.model-matrix.validate"))

        assert outcome.long_running is False
        err = capsys.readouterr().err
        assert "MX-RESOLVE" in err

    def test_default_lint_fn_runs_the_real_matrix_lint_script(
        self, tmp_path: Path, capsys
    ) -> None:
        """FR-K5: the default `validate` wiring reuses the real
        `scripts/matrix-lint`, not a reimplementation of its checks."""
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir()
        shutil.copy2(_REPO_SCRIPTS / "matrix-lint", scripts_dir / "matrix-lint")
        matrix_path = _write_matrix(tmp_path / "model.conf", VALID_MATRIX)
        adapter_registry = TomlAdapterRegistry(_orch_dir(tmp_path))
        dispatch = build_configure_model_matrix_dispatch(matrix_path, adapter_registry)

        outcome = dispatch(_node("configure.model-matrix.validate"))

        assert outcome.long_running is False
        assert capsys.readouterr().out.strip() == "valid"

    def test_default_lint_fn_surfaces_real_errors(self, tmp_path: Path, capsys) -> None:
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir()
        shutil.copy2(_REPO_SCRIPTS / "matrix-lint", scripts_dir / "matrix-lint")
        # 'mega' is not a valid tier.
        matrix_path = _write_matrix(
            tmp_path / "model.conf",
            """\
            [facts]
            copilot.mega = gpt-5.4-mini
            on_missing = halt
            """,
        )
        adapter_registry = TomlAdapterRegistry(_orch_dir(tmp_path))
        dispatch = build_configure_model_matrix_dispatch(matrix_path, adapter_registry)

        outcome = dispatch(_node("configure.model-matrix.validate"))

        assert outcome.long_running is False
        err = capsys.readouterr().err
        assert "MX-TIER" in err


# --- edit: $EDITOR seam, unset-editor error, repopulation on success --------


class TestEdit:
    def test_unset_editor_reports_clear_error_and_does_not_crash(
        self, tmp_path: Path, capsys
    ) -> None:
        matrix_path = _write_matrix(tmp_path / "model.conf", VALID_MATRIX)
        adapter_registry = TomlAdapterRegistry(_orch_dir(tmp_path))
        dispatch = build_configure_model_matrix_dispatch(
            matrix_path,
            adapter_registry,
            run_fn=lambda cmd: (_ for _ in ()).throw(
                AssertionError("must not spawn an editor when $EDITOR is unset")
            ),
            get_editor=lambda: None,
        )

        outcome = dispatch(_node("configure.model-matrix.edit"))

        assert outcome.long_running is False
        err = capsys.readouterr().err
        assert "EDITOR" in err

    def test_successful_edit_repopulates_adapter_dictionaries(
        self, tmp_path: Path, capsys
    ) -> None:
        matrix_path = _write_matrix(
            tmp_path / "model.conf",
            """\
            [facts]
            copilot.economy = gpt-5.4-mini
            on_missing = auto
            """,
        )
        adapter_registry = TomlAdapterRegistry(_orch_dir(tmp_path))
        adapter_registry.register("copilot", sys.executable)

        def _fake_editor(cmd):
            # Simulates the operator saving a new tier mapping in $EDITOR.
            _write_matrix(
                matrix_path,
                """\
                [facts]
                copilot.economy = gpt-5.4-mini
                copilot.standard = gpt-5.4
                on_missing = auto
                """,
            )
            return 0

        dispatch = build_configure_model_matrix_dispatch(
            matrix_path,
            adapter_registry,
            run_fn=_fake_editor,
            get_editor=lambda: "vim",
        )

        outcome = dispatch(_node("configure.model-matrix.edit"))

        assert outcome.long_running is False
        assert adapter_registry.get_model("copilot", "economy") == "gpt-5.4-mini"
        assert adapter_registry.get_model("copilot", "standard") == "gpt-5.4"
        assert "repopulated" in capsys.readouterr().out.lower()

    def test_editor_nonzero_exit_leaves_dictionary_unchanged(
        self, tmp_path: Path, capsys
    ) -> None:
        matrix_path = _write_matrix(tmp_path / "model.conf", VALID_MATRIX)
        adapter_registry = TomlAdapterRegistry(_orch_dir(tmp_path))
        adapter_registry.register("copilot", sys.executable)

        dispatch = build_configure_model_matrix_dispatch(
            matrix_path,
            adapter_registry,
            run_fn=lambda cmd: 1,
            get_editor=lambda: "vim",
        )

        outcome = dispatch(_node("configure.model-matrix.edit"))

        assert outcome.long_running is False
        assert adapter_registry.get_model("copilot", "economy") is None
        err = capsys.readouterr().err
        assert "1" in err

    def test_edit_leaves_matrix_invalid_after_edit_does_not_crash_or_populate(
        self, tmp_path: Path, capsys
    ) -> None:
        matrix_path = _write_matrix(tmp_path / "model.conf", VALID_MATRIX)
        adapter_registry = TomlAdapterRegistry(_orch_dir(tmp_path))
        adapter_registry.register("copilot", sys.executable)

        def _break_the_file(cmd):
            matrix_path.write_text("not a valid matrix file at all\n", encoding="utf-8")
            return 0

        dispatch = build_configure_model_matrix_dispatch(
            matrix_path,
            adapter_registry,
            run_fn=_break_the_file,
            get_editor=lambda: "vim",
        )

        outcome = dispatch(_node("configure.model-matrix.edit"))

        assert outcome.long_running is False
        assert adapter_registry.get_model("copilot", "economy") is None
        assert "invalid" in capsys.readouterr().err.lower()

    def test_editor_command_passes_the_matrix_path(self, tmp_path: Path) -> None:
        matrix_path = _write_matrix(tmp_path / "model.conf", VALID_MATRIX)
        adapter_registry = TomlAdapterRegistry(_orch_dir(tmp_path))
        seen = []

        dispatch = build_configure_model_matrix_dispatch(
            matrix_path,
            adapter_registry,
            run_fn=lambda cmd: seen.append(cmd) or 0,
            get_editor=lambda: "nano",
        )

        dispatch(_node("configure.model-matrix.edit"))

        assert seen == [["nano", str(matrix_path)]]


# --- populate_adapter_dictionaries_from_matrix: idempotency (story's core --
# acceptance criterion) --------------------------------------------------


class TestPopulateAdapterDictionariesFromMatrix:
    def test_populates_only_registered_clis_present_in_facts(
        self, tmp_path: Path
    ) -> None:
        matrix_path = _write_matrix(tmp_path / "model.conf", VALID_MATRIX)
        matrix = FileModelMatrix(matrix_path)
        adapter_registry = TomlAdapterRegistry(_orch_dir(tmp_path))
        adapter_registry.register("copilot", sys.executable)
        # 'claude' has facts but is not registered — must be skipped, not error.

        populate_adapter_dictionaries_from_matrix(matrix, adapter_registry)

        assert adapter_registry.get_model("copilot", "economy") == "gpt-5.4-mini"
        assert adapter_registry.get_model("copilot", "standard") == "gpt-5.4"
        assert adapter_registry.get_model("copilot", "strong") == "claude-opus-4-6"
        with pytest.raises(KeyError):
            adapter_registry.get_model("claude", "standard")

    def test_running_twice_is_idempotent(self, tmp_path: Path) -> None:
        """Story's explicit acceptance criterion: running the population
        step twice produces the same dictionary state, with no duplicate
        errors either time."""
        matrix_path = _write_matrix(tmp_path / "model.conf", VALID_MATRIX)
        matrix = FileModelMatrix(matrix_path)
        adapter_registry = TomlAdapterRegistry(_orch_dir(tmp_path))
        adapter_registry.register("copilot", sys.executable)
        adapter_registry.register("claude", "/bin/cat")

        populate_adapter_dictionaries_from_matrix(matrix, adapter_registry)
        first_copilot = sorted(adapter_registry.list_models("copilot"))
        first_claude = sorted(adapter_registry.list_models("claude"))

        # Re-running must not raise (e.g. a "duplicate mapping" error) and
        # must reproduce the identical dictionary state.
        populate_adapter_dictionaries_from_matrix(matrix, adapter_registry)
        second_copilot = sorted(adapter_registry.list_models("copilot"))
        second_claude = sorted(adapter_registry.list_models("claude"))

        assert (
            first_copilot
            == second_copilot
            == [
                ("economy", "gpt-5.4-mini"),
                ("standard", "gpt-5.4"),
                ("strong", "claude-opus-4-6"),
            ]
        )
        assert (
            first_claude
            == second_claude
            == [
                ("economy", "claude-haiku-4-5"),
                ("standard", "claude-sonnet-4-5"),
                ("strong", "claude-opus-4-6"),
            ]
        )

    def test_no_registered_adapters_matches_facts_is_a_no_op(
        self, tmp_path: Path
    ) -> None:
        matrix_path = _write_matrix(tmp_path / "model.conf", VALID_MATRIX)
        matrix = FileModelMatrix(matrix_path)
        adapter_registry = TomlAdapterRegistry(_orch_dir(tmp_path))

        populate_adapter_dictionaries_from_matrix(matrix, adapter_registry)  # no raise

        assert adapter_registry.list_adapters() == []
