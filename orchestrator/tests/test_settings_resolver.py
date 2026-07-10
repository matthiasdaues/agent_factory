"""Tests for SettingsResolver four-layer precedence (ST-0043, UC-09, ADR-0017).

Precedence: menu selection > CLI flag > config.toml > built-in default.
A ``None`` at any layer means "continue to the next layer," never "stop with
null" (BR-040, VR-034) — never short-circuit on falsy-but-not-None values
such as ``auto_approve=False``.
"""

from __future__ import annotations

from typing import Optional

import pytest

from orchestrator.entities import Config
from orchestrator.settings_resolver import SettingsResolver


class FakeConfigStore:
    """Minimal ConfigStore fake (mirrors tests/test_config_store.py)."""

    def __init__(self, config: Optional[Config] = None):
        self._data = config

    def load(self) -> Optional[Config]:
        return self._data

    def save(self, config: Config) -> None:
        self._data = config


BUILTIN_DEFAULTS = {
    "adapter": "copilot",
    "timeout": 1800,
    "cap": 3,
    "auto_approve": False,
}


# --- layer-by-layer winners --------------------------------------------------


def test_menu_layer_wins_when_present():
    config = Config(adapter="claude", timeout=900, cap=5, auto_approve=True)
    resolver = SettingsResolver(config)

    assert (
        resolver.resolve("adapter", menu_value="gemini", cli_flag="copilot") == "gemini"
    )
    assert resolver.resolve("timeout", menu_value=120, cli_flag=300) == 120
    assert resolver.resolve("cap", menu_value=7, cli_flag=2) == 7
    assert resolver.resolve("auto_approve", menu_value=True, cli_flag=False) is True


def test_cli_flag_wins_when_menu_absent():
    config = Config(adapter="claude", timeout=900, cap=5, auto_approve=True)
    resolver = SettingsResolver(config)

    assert resolver.resolve("adapter", menu_value=None, cli_flag="gemini") == "gemini"
    assert resolver.resolve("timeout", menu_value=None, cli_flag=300) == 300
    assert resolver.resolve("cap", menu_value=None, cli_flag=2) == 2
    assert resolver.resolve("auto_approve", menu_value=None, cli_flag=False) is False


def test_config_layer_wins_when_menu_and_cli_absent():
    config = Config(adapter="claude", timeout=900, cap=5, auto_approve=True)
    resolver = SettingsResolver(config)

    assert resolver.resolve("adapter", menu_value=None, cli_flag=None) == "claude"
    assert resolver.resolve("timeout", menu_value=None, cli_flag=None) == 900
    assert resolver.resolve("cap", menu_value=None, cli_flag=None) == 5
    assert resolver.resolve("auto_approve", menu_value=None, cli_flag=None) is True


def test_builtin_default_wins_when_all_layers_absent():
    resolver = SettingsResolver(Config())

    assert resolver.resolve("adapter", menu_value=None, cli_flag=None) == "copilot"
    assert resolver.resolve("timeout", menu_value=None, cli_flag=None) == 1800
    assert resolver.resolve("cap", menu_value=None, cli_flag=None) == 3
    assert resolver.resolve("auto_approve", menu_value=None, cli_flag=None) is False


def test_builtin_default_wins_when_config_source_is_none():
    """No Config and no ConfigStore at all — resolver still falls back cleanly."""
    resolver = SettingsResolver(None)

    assert resolver.resolve("adapter", menu_value=None, cli_flag=None) == "copilot"
    assert resolver.resolve("timeout", menu_value=None, cli_flag=None) == 1800
    assert resolver.resolve("cap", menu_value=None, cli_flag=None) == 3
    assert resolver.resolve("auto_approve", menu_value=None, cli_flag=None) is False


def test_builtin_default_wins_when_config_store_reports_absent_file():
    """BR-037: an absent config.toml (store.load() -> None) means built-in defaults."""
    store = FakeConfigStore(config=None)
    resolver = SettingsResolver(store)

    assert resolver.resolve("adapter", menu_value=None, cli_flag=None) == "copilot"
    assert resolver.resolve("timeout", menu_value=None, cli_flag=None) == 1800
    assert resolver.resolve("cap", menu_value=None, cli_flag=None) == 3
    assert resolver.resolve("auto_approve", menu_value=None, cli_flag=None) is False


# --- constructor accepts either a loaded Config or a ConfigStore ------------


def test_resolver_accepts_a_config_store_and_reads_through_it():
    store = FakeConfigStore(Config(timeout=900))
    resolver = SettingsResolver(store)

    assert resolver.resolve("timeout", menu_value=None, cli_flag=None) == 900
    # Keys the store didn't set still fall through to built-in default.
    assert resolver.resolve("adapter", menu_value=None, cli_flag=None) == "copilot"


def test_resolver_accepts_an_already_loaded_config_directly():
    config = Config(cap=9)
    resolver = SettingsResolver(config)

    assert resolver.resolve("cap", menu_value=None, cli_flag=None) == 9


# --- no short-circuiting on falsy-but-not-None values -----------------------


def test_none_at_any_layer_falls_through_not_stops():
    """A None anywhere continues to the next layer; only non-None values stop."""
    config = Config(timeout=900)
    resolver = SettingsResolver(config)

    # menu_value is None -> falls through to cli_flag, which is present.
    assert resolver.resolve("timeout", menu_value=None, cli_flag=300) == 300
    # both menu_value and cli_flag are None -> falls through to config.
    assert resolver.resolve("timeout", menu_value=None, cli_flag=None) == 900


def test_falsy_but_non_none_values_are_not_treated_as_absent():
    """auto_approve=False (menu/CLI/config) must win outright, never be skipped."""
    config = Config(auto_approve=True)
    resolver = SettingsResolver(config)

    # CLI flag explicitly False must win over config True — False is not None.
    assert resolver.resolve("auto_approve", menu_value=None, cli_flag=False) is False
    # Menu explicitly False must win over CLI True and config True.
    assert resolver.resolve("auto_approve", menu_value=False, cli_flag=True) is False
    # timeout=0 would be invalid business-wise, but as a resolver-layer
    # mechanism check: a present-but-zero CLI flag still is not None-ish
    # by identity, so it must win over config/built-in.
    assert resolver.resolve("timeout", menu_value=None, cli_flag=0) == 0


# --- full-stack scenario from UC-09 Gherkin (menu wins) ---------------------


def test_full_stack_all_layers_present_menu_wins():
    """UC-09: config.toml timeout=900, CLI --timeout 300, menu selects 120."""
    config = Config(timeout=900)
    resolver = SettingsResolver(config)

    assert resolver.resolve("timeout", menu_value=120, cli_flag=300) == 120


def test_full_stack_without_menu_falls_to_cli():
    config = Config(timeout=900)
    resolver = SettingsResolver(config)

    assert resolver.resolve("timeout", menu_value=None, cli_flag=300) == 300


def test_full_stack_without_menu_or_cli_falls_to_config():
    config = Config(timeout=900)
    resolver = SettingsResolver(config)

    assert resolver.resolve("timeout", menu_value=None, cli_flag=None) == 900


def test_full_stack_with_no_layers_present_falls_to_builtin():
    resolver = SettingsResolver(Config())

    assert resolver.resolve("timeout", menu_value=None, cli_flag=None) == 1800


# --- unknown key -------------------------------------------------------------


def test_unknown_key_raises_value_error():
    resolver = SettingsResolver(Config())

    with pytest.raises(ValueError):
        resolver.resolve("not_a_real_setting", menu_value=None, cli_flag=None)


# --- QS-20 property test: identical results across direct mode and menu mode -


def direct_mode_resolve(resolver: SettingsResolver, key: str, cli_flag):
    """Simulates a direct-mode call site: no menu layer is ever supplied."""
    return resolver.resolve(key, menu_value=None, cli_flag=cli_flag)


def menu_mode_resolve(resolver: SettingsResolver, key: str, menu_value, cli_flag):
    """Simulates a menu-mode call site: menu selection may or may not be set."""
    return resolver.resolve(key, menu_value=menu_value, cli_flag=cli_flag)


def test_property_direct_and_menu_mode_resolve_identically_for_equivalent_inputs():
    """QS-20 (FR-Q3, VR-034): both entry paths share one resolver, so for the
    same effective inputs (no menu override in play) they must agree exactly,
    across every layer-value combination — including None, falsy, and
    all-layers-present sweeps. No entry path may special-case its own
    precedence logic.
    """
    config_variants = [
        Config(),
        Config(adapter="claude"),
        Config(timeout=900, cap=5, auto_approve=True),
        Config(adapter="gemini", timeout=60, cap=1, auto_approve=False),
    ]
    cli_variants = {
        "adapter": [None, "copilot", "gemini"],
        "timeout": [None, 0, 300],
        "cap": [None, 1, 9],
        "auto_approve": [None, True, False],
    }
    menu_variants = {
        "adapter": [None, "claude"],
        "timeout": [None, 120],
        "cap": [None, 7],
        "auto_approve": [None, True],
    }

    for config in config_variants:
        resolver = SettingsResolver(config)
        for key in ("adapter", "timeout", "cap", "auto_approve"):
            for cli_flag in cli_variants[key]:
                # Property 1: direct mode (no menu) is deterministic and
                # matches menu mode called with an explicit None menu value.
                direct_result = direct_mode_resolve(resolver, key, cli_flag)
                menu_result_no_override = menu_mode_resolve(
                    resolver, key, menu_value=None, cli_flag=cli_flag
                )
                assert direct_result == menu_result_no_override

                for menu_value in menu_variants[key]:
                    if menu_value is None:
                        continue
                    # Property 2: whenever menu mode supplies a real
                    # selection, it wins outright regardless of cli_flag.
                    menu_result = menu_mode_resolve(
                        resolver, key, menu_value=menu_value, cli_flag=cli_flag
                    )
                    assert menu_result == menu_value


@pytest.mark.parametrize(
    "key,cli_flag,expected_from_config_or_builtin",
    [
        ("adapter", None, "adapter"),
        ("timeout", None, "timeout"),
        ("cap", None, "cap"),
        ("auto_approve", None, "auto_approve"),
    ],
)
def test_every_key_falls_through_the_full_chain_to_builtin(
    key, cli_flag, expected_from_config_or_builtin
):
    """Sweeps all four settings through the all-absent path to their exact
    built-in default from the specification table."""
    resolver = SettingsResolver(Config())

    resolved = resolver.resolve(key, menu_value=None, cli_flag=cli_flag)

    assert resolved == BUILTIN_DEFAULTS[expected_from_config_or_builtin]
