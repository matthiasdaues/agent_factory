"""Tests for the `configure > defaults` menu leaves (ST-0044).

Traces: UC-09, FR-Q4, BR-037, BR-038, BR-039, BR-041,
cli_specification.md §Configure. Covers `build_configure_defaults_dispatch`'s
four leaves (`adapter.{name}`, `timeout`, `cap`, `auto-approve`) — valid
persist, invalid-value rejection leaving the prior value unchanged,
first-persist file creation, and malformed-config-file refusal — plus
`build_configure_defaults_adapter_menu`'s runtime-populated adapter list
with the current default marked is_default (★).

Exercises the concrete `TomlConfigStore`/`TomlAdapterRegistry` adapters
against real temp-directory files (not mocks), mirroring
tests/test_toml_config_store.py's approach, so BR-038's atomic-write
guarantee is observed end to end rather than assumed from a mocked store.
"""

from __future__ import annotations

import sys
from pathlib import Path

from orchestrator.adapters.adapter_registry import TomlAdapterRegistry
from orchestrator.adapters.config_store import TomlConfigStore
from orchestrator.cli import (
    build_configure_defaults_adapter_menu,
    build_configure_defaults_dispatch,
)
from orchestrator.entities import Config, MenuNode, MenuNodeType


def _orch_dir(tmp_path: Path) -> Path:
    return tmp_path / ".orchestrator"


def _node(node_id: str, node_type: MenuNodeType = MenuNodeType.FUNCTION) -> MenuNode:
    return MenuNode(id=node_id, label=node_id, type=node_type)


def _register(
    adapter_registry: TomlAdapterRegistry, name: str, binary_path: str | None = None
) -> None:
    """Register `name` with a real, guaranteed-executable path.

    `binary_path` defaults to `sys.executable`; pass a distinct path (e.g.
    `/bin/cat`) when registering a second adapter in the same test — the
    registry rejects registering the same binary path under two names
    (BR-043).
    """
    adapter_registry.register(name, binary_path or sys.executable)


# --- timeout: valid persist, invalid rejection, first-persist creation -----


class TestTimeoutLeaf:
    def test_valid_timeout_persists_and_creates_file_on_first_persist(
        self, tmp_path: Path, capsys
    ) -> None:
        orch_dir = _orch_dir(tmp_path)
        config_store = TomlConfigStore(orch_dir)
        adapter_registry = TomlAdapterRegistry(orch_dir)
        assert not (orch_dir / "config.toml").exists()

        dispatch = build_configure_defaults_dispatch(
            config_store, adapter_registry, input_fn=lambda prompt: "900"
        )
        outcome = dispatch(_node("configure.defaults.timeout"))

        assert outcome.long_running is False
        assert (orch_dir / "config.toml").exists()
        assert config_store.load() == Config(timeout=900)
        assert "900" in capsys.readouterr().out

    def test_invalid_timeout_rejected_and_prior_value_unchanged(
        self, tmp_path: Path, capsys
    ) -> None:
        orch_dir = _orch_dir(tmp_path)
        config_store = TomlConfigStore(orch_dir)
        adapter_registry = TomlAdapterRegistry(orch_dir)
        config_store.save(Config(timeout=900))

        dispatch = build_configure_defaults_dispatch(
            config_store, adapter_registry, input_fn=lambda prompt: "0"
        )
        outcome = dispatch(_node("configure.defaults.timeout"))

        assert outcome.long_running is False
        assert config_store.load() == Config(timeout=900)
        err = capsys.readouterr().err
        assert "positive integer" in err

    def test_non_numeric_timeout_rejected(self, tmp_path: Path, capsys) -> None:
        orch_dir = _orch_dir(tmp_path)
        config_store = TomlConfigStore(orch_dir)
        adapter_registry = TomlAdapterRegistry(orch_dir)

        dispatch = build_configure_defaults_dispatch(
            config_store, adapter_registry, input_fn=lambda prompt: "soon"
        )
        outcome = dispatch(_node("configure.defaults.timeout"))

        assert outcome.long_running is False
        assert config_store.load() is None
        assert "positive integer" in capsys.readouterr().err

    def test_timeout_persist_preserves_other_previously_set_fields(
        self, tmp_path: Path
    ) -> None:
        """A partial Config().save() must not wipe other persisted keys —
        _persist_default() must merge, not overwrite (see cli.py's
        _persist_default docstring)."""
        orch_dir = _orch_dir(tmp_path)
        config_store = TomlConfigStore(orch_dir)
        adapter_registry = TomlAdapterRegistry(orch_dir)
        config_store.save(
            Config(adapter="copilot", timeout=1800, cap=3, auto_approve=True)
        )

        dispatch = build_configure_defaults_dispatch(
            config_store, adapter_registry, input_fn=lambda prompt: "600"
        )
        dispatch(_node("configure.defaults.timeout"))

        assert config_store.load() == Config(
            adapter="copilot", timeout=600, cap=3, auto_approve=True
        )


# --- cap: valid persist, invalid rejection ----------------------------------


class TestCapLeaf:
    def test_valid_cap_persists(self, tmp_path: Path) -> None:
        orch_dir = _orch_dir(tmp_path)
        config_store = TomlConfigStore(orch_dir)
        adapter_registry = TomlAdapterRegistry(orch_dir)

        dispatch = build_configure_defaults_dispatch(
            config_store, adapter_registry, input_fn=lambda prompt: "5"
        )
        outcome = dispatch(_node("configure.defaults.cap"))

        assert outcome.long_running is False
        assert config_store.load() == Config(cap=5)

    def test_cap_zero_rejected_and_prior_value_unchanged(
        self, tmp_path: Path, capsys
    ) -> None:
        """UC-09 Gherkin: 'Rejecting an invalid submitted value' — cap=0."""
        orch_dir = _orch_dir(tmp_path)
        config_store = TomlConfigStore(orch_dir)
        adapter_registry = TomlAdapterRegistry(orch_dir)
        config_store.save(Config(cap=3))

        dispatch = build_configure_defaults_dispatch(
            config_store, adapter_registry, input_fn=lambda prompt: "0"
        )
        outcome = dispatch(_node("configure.defaults.cap"))

        assert outcome.long_running is False
        assert config_store.load() == Config(cap=3)
        err = capsys.readouterr().err
        assert "cap" in err
        assert "1" in err

    def test_negative_cap_rejected(self, tmp_path: Path, capsys) -> None:
        orch_dir = _orch_dir(tmp_path)
        config_store = TomlConfigStore(orch_dir)
        adapter_registry = TomlAdapterRegistry(orch_dir)

        dispatch = build_configure_defaults_dispatch(
            config_store, adapter_registry, input_fn=lambda prompt: "-1"
        )
        outcome = dispatch(_node("configure.defaults.cap"))

        assert outcome.long_running is False
        assert config_store.load() is None


# --- auto-approve: toggle, no free-text validation needed -------------------


class TestAutoApproveLeaf:
    def test_toggle_from_unset_flips_builtin_default_false_to_true(
        self, tmp_path: Path, capsys
    ) -> None:
        orch_dir = _orch_dir(tmp_path)
        config_store = TomlConfigStore(orch_dir)
        adapter_registry = TomlAdapterRegistry(orch_dir)

        dispatch = build_configure_defaults_dispatch(config_store, adapter_registry)
        outcome = dispatch(_node("configure.defaults.auto-approve"))

        assert outcome.long_running is False
        assert config_store.load() == Config(auto_approve=True)
        assert "on" in capsys.readouterr().out

    def test_toggle_flips_persisted_true_to_false(self, tmp_path: Path) -> None:
        orch_dir = _orch_dir(tmp_path)
        config_store = TomlConfigStore(orch_dir)
        adapter_registry = TomlAdapterRegistry(orch_dir)
        config_store.save(Config(auto_approve=True))

        dispatch = build_configure_defaults_dispatch(config_store, adapter_registry)
        dispatch(_node("configure.defaults.auto-approve"))

        assert config_store.load() == Config(auto_approve=False)


# --- adapter: valid persist, invalid rejection ------------------------------


class TestAdapterLeaf:
    def test_valid_registered_adapter_persists(self, tmp_path: Path, capsys) -> None:
        orch_dir = _orch_dir(tmp_path)
        config_store = TomlConfigStore(orch_dir)
        adapter_registry = TomlAdapterRegistry(orch_dir)
        _register(adapter_registry, "copilot")

        dispatch = build_configure_defaults_dispatch(config_store, adapter_registry)
        outcome = dispatch(_node("configure.defaults.adapter.copilot"))

        assert outcome.long_running is False
        assert config_store.load() == Config(adapter="copilot")
        assert "copilot" in capsys.readouterr().out

    def test_unregistered_adapter_rejected_and_prior_value_unchanged(
        self, tmp_path: Path, capsys
    ) -> None:
        orch_dir = _orch_dir(tmp_path)
        config_store = TomlConfigStore(orch_dir)
        adapter_registry = TomlAdapterRegistry(orch_dir)
        _register(adapter_registry, "copilot")
        config_store.save(Config(adapter="copilot"))

        dispatch = build_configure_defaults_dispatch(config_store, adapter_registry)
        outcome = dispatch(_node("configure.defaults.adapter.ghost"))

        assert outcome.long_running is False
        assert config_store.load() == Config(adapter="copilot")
        err = capsys.readouterr().err
        assert "registered" in err

    def test_no_adapters_registered_rejects_any_selection(
        self, tmp_path: Path, capsys
    ) -> None:
        """UC-09 extension 4a: no adapter can be chosen; default unchanged."""
        orch_dir = _orch_dir(tmp_path)
        config_store = TomlConfigStore(orch_dir)
        adapter_registry = TomlAdapterRegistry(orch_dir)

        dispatch = build_configure_defaults_dispatch(config_store, adapter_registry)
        outcome = dispatch(_node("configure.defaults.adapter.copilot"))

        assert outcome.long_running is False
        assert config_store.load() is None
        assert "registered" in capsys.readouterr().err


# --- malformed config.toml: refuse cleanly, report file/key (BR-041) -------


def _write_malformed(orch_dir: Path) -> Path:
    """Append a malformed `[defaults]` table, preserving any `[adapters]`
    table a prior `_register()` call in the same test already wrote."""
    orch_dir.mkdir(parents=True, exist_ok=True)
    config_path = orch_dir / "config.toml"
    existing = config_path.read_text(encoding="utf-8") if config_path.exists() else ""
    if existing and not existing.endswith("\n"):
        existing += "\n"
    config_path.write_text(existing + "[defaults]\ntimeout = 0\n", encoding="utf-8")
    return config_path


class TestMalformedConfigRefusal:
    def test_timeout_leaf_refuses_on_malformed_file(
        self, tmp_path: Path, capsys
    ) -> None:
        orch_dir = _orch_dir(tmp_path)
        config_path = _write_malformed(orch_dir)
        adapter_registry = TomlAdapterRegistry(orch_dir)
        config_store = TomlConfigStore(orch_dir)

        dispatch = build_configure_defaults_dispatch(
            config_store, adapter_registry, input_fn=lambda prompt: "900"
        )
        outcome = dispatch(_node("configure.defaults.timeout"))

        assert outcome.long_running is False
        err = capsys.readouterr().err
        assert str(config_path) in err
        assert "timeout" in err
        # File left byte-for-byte intact — no persist attempted.
        assert config_path.read_text(encoding="utf-8") == "[defaults]\ntimeout = 0\n"

    def test_cap_leaf_refuses_on_malformed_file(self, tmp_path: Path, capsys) -> None:
        orch_dir = _orch_dir(tmp_path)
        config_path = _write_malformed(orch_dir)
        adapter_registry = TomlAdapterRegistry(orch_dir)
        config_store = TomlConfigStore(orch_dir)

        dispatch = build_configure_defaults_dispatch(
            config_store, adapter_registry, input_fn=lambda prompt: "5"
        )
        outcome = dispatch(_node("configure.defaults.cap"))

        assert outcome.long_running is False
        assert str(config_path) in capsys.readouterr().err

    def test_auto_approve_leaf_refuses_on_malformed_file(
        self, tmp_path: Path, capsys
    ) -> None:
        orch_dir = _orch_dir(tmp_path)
        config_path = _write_malformed(orch_dir)
        adapter_registry = TomlAdapterRegistry(orch_dir)
        config_store = TomlConfigStore(orch_dir)

        dispatch = build_configure_defaults_dispatch(config_store, adapter_registry)
        outcome = dispatch(_node("configure.defaults.auto-approve"))

        assert outcome.long_running is False
        assert str(config_path) in capsys.readouterr().err

    def test_adapter_leaf_refuses_on_malformed_file(
        self, tmp_path: Path, capsys
    ) -> None:
        orch_dir = _orch_dir(tmp_path)
        config_path = _write_malformed(orch_dir)
        adapter_registry = TomlAdapterRegistry(orch_dir)
        _register(adapter_registry, "copilot")
        config_store = TomlConfigStore(orch_dir)

        dispatch = build_configure_defaults_dispatch(config_store, adapter_registry)
        outcome = dispatch(_node("configure.defaults.adapter.copilot"))

        assert outcome.long_running is False
        assert str(config_path) in capsys.readouterr().err


# --- build_configure_defaults_adapter_menu: runtime-populated submenu ------


class TestConfigureDefaultsAdapterMenu:
    def test_one_leaf_per_registered_adapter(self, tmp_path: Path) -> None:
        orch_dir = _orch_dir(tmp_path)
        adapter_registry = TomlAdapterRegistry(orch_dir)
        config_store = TomlConfigStore(orch_dir)
        _register(adapter_registry, "copilot")
        _register(adapter_registry, "claude", "/bin/cat")

        menu = build_configure_defaults_adapter_menu(adapter_registry, config_store)

        assert menu.id == "configure.defaults.adapter"
        assert menu.type == MenuNodeType.MENU
        assert sorted(child.label for child in menu.children) == ["claude", "copilot"]
        for child in menu.children:
            assert child.type == MenuNodeType.FUNCTION
            assert child.id == f"configure.defaults.adapter.{child.label}"

    def test_persisted_default_is_marked_with_is_default(self, tmp_path: Path) -> None:
        orch_dir = _orch_dir(tmp_path)
        adapter_registry = TomlAdapterRegistry(orch_dir)
        config_store = TomlConfigStore(orch_dir)
        _register(adapter_registry, "copilot")
        _register(adapter_registry, "claude", "/bin/cat")
        config_store.save(Config(adapter="claude"))

        menu = build_configure_defaults_adapter_menu(adapter_registry, config_store)

        marked = [c for c in menu.children if c.is_default]
        assert [c.label for c in marked] == ["claude"]

    def test_falls_back_to_builtin_default_when_unset(self, tmp_path: Path) -> None:
        """copilot is the built-in default (BUILTIN_DEFAULTS['adapter']) when
        no config.toml exists at all (BR-037/BR-040)."""
        orch_dir = _orch_dir(tmp_path)
        adapter_registry = TomlAdapterRegistry(orch_dir)
        config_store = TomlConfigStore(orch_dir)
        _register(adapter_registry, "copilot")
        _register(adapter_registry, "claude", "/bin/cat")

        menu = build_configure_defaults_adapter_menu(adapter_registry, config_store)

        marked = [c for c in menu.children if c.is_default]
        assert [c.label for c in marked] == ["copilot"]

    def test_no_registered_adapters_yields_no_children(self, tmp_path: Path) -> None:
        orch_dir = _orch_dir(tmp_path)
        adapter_registry = TomlAdapterRegistry(orch_dir)
        config_store = TomlConfigStore(orch_dir)

        menu = build_configure_defaults_adapter_menu(adapter_registry, config_store)

        assert menu.children == []

    def test_malformed_config_degrades_to_no_default_marked(
        self, tmp_path: Path
    ) -> None:
        """BR-041, degraded gracefully: menu-tree construction runs eagerly,
        before any operator action, so it cannot itself "refuse an action" —
        it just shows the adapter list with no ★. Actually persisting a new
        default still refuses and reports the malformed file
        (see TestMalformedConfigRefusal.test_adapter_leaf_refuses_on_malformed_file).
        """
        orch_dir = _orch_dir(tmp_path)
        adapter_registry = TomlAdapterRegistry(orch_dir)
        _register(adapter_registry, "copilot")
        _write_malformed(orch_dir)
        config_store = TomlConfigStore(orch_dir)

        menu = build_configure_defaults_adapter_menu(adapter_registry, config_store)

        assert [c.label for c in menu.children] == ["copilot"]
        assert all(not c.is_default for c in menu.children)
