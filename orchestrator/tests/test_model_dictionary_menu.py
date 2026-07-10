"""Tests for the `configure > cli > {adapter}` menu leaves (ST-0048).

Traces: UC-10 (Main Success Scenario steps 9-22; extensions 11a, 13a, 20a,
22a), FR-R6, FR-R7, FR-R8, BR-045, BR-046, BR-047. Covers
`build_configure_cli_dispatch`'s four leaves (`list-models`, `auto-detect`,
`add-model`, `remove-model.{tier}`) and the runtime-populated submenu
builders (`build_configure_cli_menu`, `build_configure_cli_adapter_menu`,
`build_configure_cli_remove_model_menu`).

Exercises the concrete `TomlAdapterRegistry` against real temp-directory
files (not mocks), mirroring tests/test_cli_list.py's approach, so the
atomicity `TomlAdapterRegistry.set_model`/`remove_model` already guarantee
(ST-0046) is observed end to end rather than assumed from a mocked registry.
"""

from __future__ import annotations

import sys
from pathlib import Path

from orchestrator.adapters.adapter_registry import TomlAdapterRegistry
from orchestrator.cli import (
    build_configure_cli_adapter_menu,
    build_configure_cli_dispatch,
    build_configure_cli_menu,
    build_configure_cli_remove_model_menu,
)
from orchestrator.entities import MenuNode, MenuNodeType


def _orch_dir(tmp_path: Path) -> Path:
    return tmp_path / ".orchestrator"


def _node(node_id: str, node_type: MenuNodeType = MenuNodeType.FUNCTION) -> MenuNode:
    return MenuNode(id=node_id, label=node_id, type=node_type)


def _registry_with_copilot(tmp_path: Path) -> TomlAdapterRegistry:
    registry = TomlAdapterRegistry(_orch_dir(tmp_path))
    registry.register("copilot", sys.executable)
    return registry


# --- list models: table + coverage status -----------------------------------


class TestListModels:
    def test_empty_dictionary_reports_no_models_and_incomplete_coverage(
        self, tmp_path: Path
    ) -> None:
        registry = _registry_with_copilot(tmp_path)

        dispatch = build_configure_cli_dispatch(registry)
        outcome = dispatch(
            _node("configure.cli.copilot.list-models", MenuNodeType.DISPLAY)
        )

        assert "no models registered" in outcome.content
        assert "incomplete" in outcome.content
        assert "economy" in outcome.content and "standard" in outcome.content

    def test_partial_coverage_lists_mapped_tiers_and_reports_missing(
        self, tmp_path: Path
    ) -> None:
        registry = _registry_with_copilot(tmp_path)
        registry.set_model("copilot", "standard", "gpt-5.4")

        dispatch = build_configure_cli_dispatch(registry)
        outcome = dispatch(
            _node("configure.cli.copilot.list-models", MenuNodeType.DISPLAY)
        )

        assert "gpt-5.4" in outcome.content
        assert "standard" in outcome.content
        assert "incomplete" in outcome.content
        assert "economy" in outcome.content
        assert "strong" in outcome.content

    def test_complete_coverage_reports_complete(self, tmp_path: Path) -> None:
        registry = _registry_with_copilot(tmp_path)
        registry.set_model("copilot", "economy", "gpt-5-mini")
        registry.set_model("copilot", "standard", "gpt-5.4")
        registry.set_model("copilot", "strong", "gpt-5.4-strong")

        dispatch = build_configure_cli_dispatch(registry)
        outcome = dispatch(
            _node("configure.cli.copilot.list-models", MenuNodeType.DISPLAY)
        )

        assert "tier coverage: complete" in outcome.content
        assert "gpt-5-mini" in outcome.content
        assert "gpt-5.4" in outcome.content
        assert "gpt-5.4-strong" in outcome.content

    def test_unknown_adapter_reports_failure_without_crashing(
        self, tmp_path: Path
    ) -> None:
        registry = TomlAdapterRegistry(_orch_dir(tmp_path))

        dispatch = build_configure_cli_dispatch(registry)
        outcome = dispatch(
            _node("configure.cli.ghost.list-models", MenuNodeType.DISPLAY)
        )

        assert "not registered" in outcome.content


# --- add model: fresh tier, replace-with-confirm, invalid tier --------------


class TestAddModel:
    def test_fresh_tier_persists_atomically(self, tmp_path: Path, capsys) -> None:
        registry = _registry_with_copilot(tmp_path)
        answers = iter(["gpt-5.4-mini", "economy"])

        dispatch = build_configure_cli_dispatch(
            registry, input_fn=lambda prompt: next(answers)
        )
        outcome = dispatch(_node("configure.cli.copilot.add-model"))

        assert outcome.long_running is False
        assert registry.get_model("copilot", "economy") == "gpt-5.4-mini"
        assert "gpt-5.4-mini" in capsys.readouterr().out

    def test_replace_with_confirmation_accepted_overwrites(
        self, tmp_path: Path, capsys
    ) -> None:
        registry = _registry_with_copilot(tmp_path)
        registry.set_model("copilot", "economy", "old-model")
        answers = iter(["new-model", "economy", "y"])

        dispatch = build_configure_cli_dispatch(
            registry, input_fn=lambda prompt: next(answers)
        )
        outcome = dispatch(_node("configure.cli.copilot.add-model"))

        assert outcome.long_running is False
        assert registry.get_model("copilot", "economy") == "new-model"
        assert "new-model" in capsys.readouterr().out

    def test_replace_with_confirmation_declined_leaves_dictionary_unchanged(
        self, tmp_path: Path, capsys
    ) -> None:
        registry = _registry_with_copilot(tmp_path)
        registry.set_model("copilot", "economy", "old-model")
        answers = iter(["new-model", "economy", "n"])

        dispatch = build_configure_cli_dispatch(
            registry, input_fn=lambda prompt: next(answers)
        )
        outcome = dispatch(_node("configure.cli.copilot.add-model"))

        assert outcome.long_running is False
        assert registry.get_model("copilot", "economy") == "old-model"
        assert "declined" in capsys.readouterr().out.lower()

    def test_invalid_tier_rejected_with_no_state_change(
        self, tmp_path: Path, capsys
    ) -> None:
        registry = _registry_with_copilot(tmp_path)
        answers = iter(["gpt-5.4-mini", "bogus-tier"])

        dispatch = build_configure_cli_dispatch(
            registry, input_fn=lambda prompt: next(answers)
        )
        outcome = dispatch(_node("configure.cli.copilot.add-model"))

        assert outcome.long_running is False
        assert registry.list_models("copilot") == []
        err = capsys.readouterr().err
        assert "tier" in err.lower()

    def test_unknown_adapter_reports_failure_without_crashing(
        self, tmp_path: Path, capsys
    ) -> None:
        registry = TomlAdapterRegistry(_orch_dir(tmp_path))
        answers = iter(["gpt-5.4-mini", "economy"])

        dispatch = build_configure_cli_dispatch(
            registry, input_fn=lambda prompt: next(answers)
        )
        outcome = dispatch(_node("configure.cli.ghost.add-model"))

        assert outcome.long_running is False
        assert "not registered" in capsys.readouterr().err


# --- remove model: menu shape, dispatch removal, coverage warning -----------


class TestRemoveModelMenu:
    def test_one_leaf_per_mapped_tier(self, tmp_path: Path) -> None:
        registry = _registry_with_copilot(tmp_path)
        registry.set_model("copilot", "economy", "gpt-5-mini")
        registry.set_model("copilot", "strong", "gpt-5.4-strong")

        menu = build_configure_cli_remove_model_menu(registry, "copilot")

        assert menu.id == "configure.cli.copilot.remove-model"
        assert menu.type == MenuNodeType.MENU
        assert sorted(child.id for child in menu.children) == [
            "configure.cli.copilot.remove-model.economy",
            "configure.cli.copilot.remove-model.strong",
        ]
        labels = {child.label for child in menu.children}
        assert labels == {"gpt-5-mini [economy]", "gpt-5.4-strong [strong]"}
        for child in menu.children:
            assert child.type == MenuNodeType.FUNCTION

    def test_no_mapped_tiers_yields_no_children(self, tmp_path: Path) -> None:
        registry = _registry_with_copilot(tmp_path)

        menu = build_configure_cli_remove_model_menu(registry, "copilot")

        assert menu.children == []


class TestRemoveModelDispatch:
    def test_removes_mapping(self, tmp_path: Path, capsys) -> None:
        registry = _registry_with_copilot(tmp_path)
        registry.set_model("copilot", "economy", "gpt-5-mini")
        registry.set_model("copilot", "standard", "gpt-5.4")
        registry.set_model("copilot", "strong", "gpt-5.4-strong")

        dispatch = build_configure_cli_dispatch(registry)
        outcome = dispatch(_node("configure.cli.copilot.remove-model.economy"))

        assert outcome.long_running is False
        assert registry.get_model("copilot", "economy") is None
        assert "copilot" in capsys.readouterr().out

    def test_removing_last_model_for_a_tier_warns_about_incomplete_coverage(
        self, tmp_path: Path, capsys
    ) -> None:
        """BR-046, UC-10 extension 22a: the removal always persists; a
        warning follows naming the now-missing tier."""
        registry = _registry_with_copilot(tmp_path)
        registry.set_model("copilot", "economy", "gpt-5-mini")
        registry.set_model("copilot", "standard", "gpt-5.4")
        registry.set_model("copilot", "strong", "gpt-5.4-strong")

        dispatch = build_configure_cli_dispatch(registry)
        outcome = dispatch(_node("configure.cli.copilot.remove-model.strong"))

        assert outcome.long_running is False
        assert registry.get_model("copilot", "strong") is None
        err = capsys.readouterr().err
        assert "incomplete" in err
        assert "strong" in err

    def test_removing_an_already_unmapped_tier_is_idempotent_and_still_warns(
        self, tmp_path: Path, capsys
    ) -> None:
        """`remove_model` is idempotent (ST-0046); removing a tier that was
        never mapped still leaves the dictionary incomplete (it always was),
        so the same warning applies — no crash, no spurious "removed"
        claim about a mapping that never existed."""
        registry = _registry_with_copilot(tmp_path)
        registry.set_model("copilot", "standard", "gpt-5.4")

        dispatch = build_configure_cli_dispatch(registry)
        outcome = dispatch(_node("configure.cli.copilot.remove-model.economy"))

        assert outcome.long_running is False
        assert registry.get_model("copilot", "economy") is None
        err = capsys.readouterr().err
        assert "incomplete" in err

    def test_unknown_adapter_reports_failure_without_crashing(
        self, tmp_path: Path, capsys
    ) -> None:
        registry = TomlAdapterRegistry(_orch_dir(tmp_path))

        dispatch = build_configure_cli_dispatch(registry)
        outcome = dispatch(_node("configure.cli.ghost.remove-model.economy"))

        assert outcome.long_running is False
        assert "not registered" in capsys.readouterr().err


# --- auto-detect: unsupported default, injected-supported, cancel -----------


class TestAutoDetect:
    def test_default_discover_fn_reports_unsupported_and_changes_nothing(
        self, tmp_path: Path, capsys
    ) -> None:
        registry = _registry_with_copilot(tmp_path)

        dispatch = build_configure_cli_dispatch(registry)
        outcome = dispatch(_node("configure.cli.copilot.auto-detect"))

        assert outcome.long_running is False
        assert registry.list_models("copilot") == []
        assert "unsupported" in capsys.readouterr().out.lower()

    def test_supported_discovery_with_confirmation_registers_mappings(
        self, tmp_path: Path, capsys
    ) -> None:
        registry = _registry_with_copilot(tmp_path)
        answers = iter(["economy", "strong", "y"])

        dispatch = build_configure_cli_dispatch(
            registry,
            input_fn=lambda prompt: next(answers),
            discover_fn=lambda adapter: ["gpt-5-mini", "gpt-5.4-strong"],
        )
        outcome = dispatch(_node("configure.cli.copilot.auto-detect"))

        assert outcome.long_running is False
        assert registry.get_model("copilot", "economy") == "gpt-5-mini"
        assert registry.get_model("copilot", "strong") == "gpt-5.4-strong"
        assert "2" in capsys.readouterr().out

    def test_supported_discovery_declined_confirmation_changes_nothing(
        self, tmp_path: Path, capsys
    ) -> None:
        registry = _registry_with_copilot(tmp_path)
        answers = iter(["economy", "n"])

        dispatch = build_configure_cli_dispatch(
            registry,
            input_fn=lambda prompt: next(answers),
            discover_fn=lambda adapter: ["gpt-5-mini"],
        )
        outcome = dispatch(_node("configure.cli.copilot.auto-detect"))

        assert outcome.long_running is False
        assert registry.list_models("copilot") == []
        assert "cancelled" in capsys.readouterr().out.lower()

    def test_supported_discovery_with_no_tiers_selected_changes_nothing(
        self, tmp_path: Path, capsys
    ) -> None:
        registry = _registry_with_copilot(tmp_path)
        answers = iter([""])  # blank = skip the one discovered model

        dispatch = build_configure_cli_dispatch(
            registry,
            input_fn=lambda prompt: next(answers),
            discover_fn=lambda adapter: ["gpt-5-mini"],
        )
        outcome = dispatch(_node("configure.cli.copilot.auto-detect"))

        assert outcome.long_running is False
        assert registry.list_models("copilot") == []

    def test_supported_discovery_with_zero_models_reports_and_changes_nothing(
        self, tmp_path: Path, capsys
    ) -> None:
        registry = _registry_with_copilot(tmp_path)

        dispatch = build_configure_cli_dispatch(
            registry, discover_fn=lambda adapter: []
        )
        outcome = dispatch(_node("configure.cli.copilot.auto-detect"))

        assert outcome.long_running is False
        assert registry.list_models("copilot") == []
        assert "no available models" in capsys.readouterr().out.lower()


# --- runtime-populated submenu builders --------------------------------------


class TestBuildConfigureCliMenu:
    def test_one_menu_child_per_registered_adapter(self, tmp_path: Path) -> None:
        registry = _registry_with_copilot(tmp_path)
        registry.register("claude", "/bin/cat")

        menu = build_configure_cli_menu(registry)

        assert menu.id == "configure.cli"
        assert menu.type == MenuNodeType.MENU
        assert sorted(child.label for child in menu.children) == ["claude", "copilot"]
        for child in menu.children:
            assert child.type == MenuNodeType.MENU
            assert child.id == f"configure.cli.{child.label}"

    def test_no_registered_adapters_yields_no_children(self, tmp_path: Path) -> None:
        registry = TomlAdapterRegistry(_orch_dir(tmp_path))

        menu = build_configure_cli_menu(registry)

        assert menu.children == []


class TestBuildConfigureCliAdapterMenu:
    def test_four_children_in_spec_order(self, tmp_path: Path) -> None:
        registry = _registry_with_copilot(tmp_path)

        menu = build_configure_cli_adapter_menu(registry, "copilot")

        assert [child.id for child in menu.children] == [
            "configure.cli.copilot.list-models",
            "configure.cli.copilot.auto-detect",
            "configure.cli.copilot.add-model",
            "configure.cli.copilot.remove-model",
        ]
        assert [child.label for child in menu.children] == [
            "list models",
            "auto-detect",
            "add model",
            "remove model",
        ]

    def test_leaf_types_match_spec(self, tmp_path: Path) -> None:
        registry = _registry_with_copilot(tmp_path)

        menu = build_configure_cli_adapter_menu(registry, "copilot")
        by_id = {child.id: child for child in menu.children}

        assert by_id["configure.cli.copilot.list-models"].type == MenuNodeType.DISPLAY
        assert by_id["configure.cli.copilot.auto-detect"].type == MenuNodeType.FUNCTION
        assert by_id["configure.cli.copilot.add-model"].type == MenuNodeType.FUNCTION
        assert by_id["configure.cli.copilot.remove-model"].type == MenuNodeType.MENU
