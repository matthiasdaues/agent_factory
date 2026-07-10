"""Tests for the `configure > cli-list` menu leaves (ST-0047).

Traces: UC-10 (Main Success Scenario steps 1-8, 23-24; extensions 4a, 4b,
8a, 8b, 24a), FR-R2, FR-R3, FR-R4, BR-042, BR-048. Covers
`build_cli_list_dispatch`'s three leaves (`auto-detect`, `add-adapter`,
`remove-adapter.{name}`) and `build_cli_list_remove_adapter_menu`'s
runtime-populated adapter list.

Exercises the concrete `TomlAdapterRegistry` against real temp-directory
files (not mocks), mirroring tests/test_configure_defaults.py's approach,
so BR-048's atomicity is observed end to end rather than assumed from a
mocked registry.
"""

from __future__ import annotations

import sys
from pathlib import Path

from orchestrator.adapters.adapter_detect import DetectedAdapter
from orchestrator.adapters.adapter_registry import TomlAdapterRegistry
from orchestrator.cli import (
    build_cli_list_dispatch,
    build_cli_list_remove_adapter_menu,
)
from orchestrator.entities import MenuNode, MenuNodeType


def _orch_dir(tmp_path: Path) -> Path:
    return tmp_path / ".orchestrator"


def _node(node_id: str, node_type: MenuNodeType = MenuNodeType.FUNCTION) -> MenuNode:
    return MenuNode(id=node_id, label=node_id, type=node_type)


# --- auto-detect: with/without candidates, already-registered, partial ------


class TestAutoDetect:
    def test_no_candidates_reports_no_change(self, tmp_path: Path, capsys) -> None:
        orch_dir = _orch_dir(tmp_path)
        adapter_registry = TomlAdapterRegistry(orch_dir)

        dispatch = build_cli_list_dispatch(adapter_registry, detect_fn=lambda: [])
        outcome = dispatch(_node("configure.cli-list.auto-detect"))

        assert outcome.long_running is False
        assert adapter_registry.list_adapters() == []
        assert not (orch_dir / "config.toml").exists()
        assert "no" in capsys.readouterr().out.lower()

    def test_new_candidate_is_atomically_registered(
        self, tmp_path: Path, capsys
    ) -> None:
        orch_dir = _orch_dir(tmp_path)
        adapter_registry = TomlAdapterRegistry(orch_dir)
        candidate = DetectedAdapter(name="copilot", binary_path=sys.executable)

        dispatch = build_cli_list_dispatch(
            adapter_registry, detect_fn=lambda: [candidate]
        )
        outcome = dispatch(_node("configure.cli-list.auto-detect"))

        assert outcome.long_running is False
        registered = adapter_registry.list_adapters()
        assert [entry.name for entry in registered] == ["copilot"]
        assert registered[0].binary_path == sys.executable
        assert "copilot" in capsys.readouterr().out

    def test_already_registered_candidate_is_not_reported_as_new(
        self, tmp_path: Path, capsys
    ) -> None:
        orch_dir = _orch_dir(tmp_path)
        adapter_registry = TomlAdapterRegistry(orch_dir)
        adapter_registry.register("copilot", sys.executable)
        candidate = DetectedAdapter(name="copilot", binary_path=sys.executable)

        dispatch = build_cli_list_dispatch(
            adapter_registry, detect_fn=lambda: [candidate]
        )
        outcome = dispatch(_node("configure.cli-list.auto-detect"))

        assert outcome.long_running is False
        assert [entry.name for entry in adapter_registry.list_adapters()] == ["copilot"]
        assert "no" in capsys.readouterr().out.lower()

    def test_one_new_one_conflicting_candidate_registers_the_new_one(
        self, tmp_path: Path, capsys
    ) -> None:
        """A candidate whose path collides with an already-registered
        adapter under another name fails register()'s own validation
        (BR-043) — extension 4b: skip it, record the reason, keep scanning;
        the other, unrelated candidate still gets registered."""
        orch_dir = _orch_dir(tmp_path)
        adapter_registry = TomlAdapterRegistry(orch_dir)
        adapter_registry.register("already-here", sys.executable)
        conflicting = DetectedAdapter(name="copilot", binary_path=sys.executable)
        new_one = DetectedAdapter(name="othercli", binary_path="/bin/cat")

        dispatch = build_cli_list_dispatch(
            adapter_registry, detect_fn=lambda: [conflicting, new_one]
        )
        outcome = dispatch(_node("configure.cli-list.auto-detect"))

        assert outcome.long_running is False
        names = {entry.name for entry in adapter_registry.list_adapters()}
        assert names == {"already-here", "othercli"}
        err = capsys.readouterr().err
        assert "copilot" in err


# --- add adapter: valid persist, duplicate-name/invalid-path rejection -----


class TestAddAdapter:
    def test_valid_add_persists_atomically(self, tmp_path: Path, capsys) -> None:
        orch_dir = _orch_dir(tmp_path)
        adapter_registry = TomlAdapterRegistry(orch_dir)
        assert not (orch_dir / "config.toml").exists()
        answers = iter(["copilot", sys.executable])

        dispatch = build_cli_list_dispatch(
            adapter_registry, input_fn=lambda prompt: next(answers)
        )
        outcome = dispatch(_node("configure.cli-list.add-adapter"))

        assert outcome.long_running is False
        assert (orch_dir / "config.toml").exists()
        registered = adapter_registry.list_adapters()
        assert [entry.name for entry in registered] == ["copilot"]
        assert "copilot" in capsys.readouterr().out

    def test_duplicate_name_rejected_with_no_state_change(
        self, tmp_path: Path, capsys
    ) -> None:
        orch_dir = _orch_dir(tmp_path)
        adapter_registry = TomlAdapterRegistry(orch_dir)
        adapter_registry.register("copilot", sys.executable)
        answers = iter(["copilot", "/bin/cat"])

        dispatch = build_cli_list_dispatch(
            adapter_registry, input_fn=lambda prompt: next(answers)
        )
        outcome = dispatch(_node("configure.cli-list.add-adapter"))

        assert outcome.long_running is False
        registered = adapter_registry.list_adapters()
        assert len(registered) == 1
        assert registered[0].binary_path == sys.executable
        err = capsys.readouterr().err
        assert "already registered" in err

    def test_invalid_binary_path_rejected_with_no_state_change(
        self, tmp_path: Path, capsys
    ) -> None:
        orch_dir = _orch_dir(tmp_path)
        adapter_registry = TomlAdapterRegistry(orch_dir)
        missing_path = str(tmp_path / "does-not-exist")
        answers = iter(["copilot", missing_path])

        dispatch = build_cli_list_dispatch(
            adapter_registry, input_fn=lambda prompt: next(answers)
        )
        outcome = dispatch(_node("configure.cli-list.add-adapter"))

        assert outcome.long_running is False
        assert adapter_registry.list_adapters() == []
        assert not (orch_dir / "config.toml").exists()
        err = capsys.readouterr().err
        assert "executable" in err


# --- remove adapter: menu shape + cascade removal ---------------------------


class TestRemoveAdapterMenu:
    def test_one_leaf_per_registered_adapter(self, tmp_path: Path) -> None:
        orch_dir = _orch_dir(tmp_path)
        adapter_registry = TomlAdapterRegistry(orch_dir)
        adapter_registry.register("copilot", sys.executable)
        adapter_registry.register("claude", "/bin/cat")

        menu = build_cli_list_remove_adapter_menu(adapter_registry)

        assert menu.id == "configure.cli-list.remove-adapter"
        assert menu.type == MenuNodeType.MENU
        assert sorted(child.label for child in menu.children) == ["claude", "copilot"]
        for child in menu.children:
            assert child.type == MenuNodeType.FUNCTION
            assert child.id == f"configure.cli-list.remove-adapter.{child.label}"

    def test_no_registered_adapters_yields_no_children(self, tmp_path: Path) -> None:
        orch_dir = _orch_dir(tmp_path)
        adapter_registry = TomlAdapterRegistry(orch_dir)

        menu = build_cli_list_remove_adapter_menu(adapter_registry)

        assert menu.children == []


class TestRemoveAdapterDispatch:
    def test_removes_adapter_and_its_model_dictionary(
        self, tmp_path: Path, capsys
    ) -> None:
        orch_dir = _orch_dir(tmp_path)
        adapter_registry = TomlAdapterRegistry(orch_dir)
        adapter_registry.register("copilot", sys.executable)
        adapter_registry.set_model("copilot", "standard", "gpt-5.4")

        dispatch = build_cli_list_dispatch(adapter_registry)
        outcome = dispatch(_node("configure.cli-list.remove-adapter.copilot"))

        assert outcome.long_running is False
        assert adapter_registry.list_adapters() == []
        config_text = (orch_dir / "config.toml").read_text(encoding="utf-8")
        assert "[models.copilot]" not in config_text
        assert "copilot" in capsys.readouterr().out

    def test_unknown_adapter_reports_failure_without_crashing(
        self, tmp_path: Path, capsys
    ) -> None:
        orch_dir = _orch_dir(tmp_path)
        adapter_registry = TomlAdapterRegistry(orch_dir)

        dispatch = build_cli_list_dispatch(adapter_registry)
        outcome = dispatch(_node("configure.cli-list.remove-adapter.ghost"))

        assert outcome.long_running is False
        assert "not registered" in capsys.readouterr().err
