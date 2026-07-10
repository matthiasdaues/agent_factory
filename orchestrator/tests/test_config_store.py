"""Tests for Config entity and ConfigStore port (ST-0041, UC-09)."""

from __future__ import annotations

from typing import Optional


from orchestrator.entities import Config
from orchestrator.ports import ConfigStore


class FakeConfigStore:
    """Fake implementation of ConfigStore for testing (satisfies the protocol)."""

    def __init__(self):
        self._data: Optional[Config] = None

    def load(self) -> Optional[Config]:
        """Load stored config, or None if not yet saved."""
        return self._data

    def save(self, config: Config) -> None:
        """Store config in memory (simulating atomic write)."""
        self._data = config


def test_config_entity_all_fields_optional():
    """All four fields start as None (no override set)."""
    config = Config()
    assert config.adapter is None
    assert config.timeout is None
    assert config.cap is None
    assert config.auto_approve is None


def test_config_entity_with_adapter():
    """Config can hold a single adapter string."""
    config = Config(adapter="copilot")
    assert config.adapter == "copilot"
    assert config.timeout is None
    assert config.cap is None
    assert config.auto_approve is None


def test_config_entity_with_timeout():
    """Config can hold a timeout integer."""
    config = Config(timeout=300)
    assert config.timeout == 300
    assert config.adapter is None
    assert config.cap is None
    assert config.auto_approve is None


def test_config_entity_with_cap():
    """Config can hold a cap integer."""
    config = Config(cap=5)
    assert config.cap == 5
    assert config.adapter is None
    assert config.timeout is None
    assert config.auto_approve is None


def test_config_entity_with_auto_approve():
    """Config can hold an auto_approve boolean."""
    config = Config(auto_approve=True)
    assert config.auto_approve is True
    assert config.adapter is None
    assert config.timeout is None
    assert config.cap is None


def test_config_entity_with_multiple_fields():
    """Config can hold multiple fields at once."""
    config = Config(adapter="claude", timeout=600, cap=10, auto_approve=False)
    assert config.adapter == "claude"
    assert config.timeout == 600
    assert config.cap == 10
    assert config.auto_approve is False


def test_config_store_load_returns_none_when_empty():
    """load() returns None when no config has been saved (file absent)."""
    store: ConfigStore = FakeConfigStore()
    assert store.load() is None


def test_config_store_save_and_load_round_trip():
    """save() persists config; load() retrieves it unchanged."""
    store: ConfigStore = FakeConfigStore()
    config = Config(adapter="copilot", timeout=300, cap=5, auto_approve=True)

    store.save(config)

    loaded = store.load()
    assert loaded is not None
    assert loaded == config
    assert loaded.adapter == "copilot"
    assert loaded.timeout == 300
    assert loaded.cap == 5
    assert loaded.auto_approve is True


def test_config_store_save_partial_config():
    """save() works with a partial config (some fields None)."""
    store: ConfigStore = FakeConfigStore()
    config = Config(adapter="gemini", timeout=None, cap=3, auto_approve=None)

    store.save(config)

    loaded = store.load()
    assert loaded is not None
    assert loaded.adapter == "gemini"
    assert loaded.timeout is None
    assert loaded.cap == 3
    assert loaded.auto_approve is None


def test_config_store_overwrite():
    """save() overwrites prior config."""
    store: ConfigStore = FakeConfigStore()
    config1 = Config(adapter="copilot", timeout=300)
    config2 = Config(adapter="claude", timeout=600)

    store.save(config1)
    assert store.load().adapter == "copilot"

    store.save(config2)

    loaded = store.load()
    assert loaded.adapter == "claude"
    assert loaded.timeout == 600


def test_config_store_preserves_false_and_zero():
    """None is distinguished from False/0 (critical for precedence fallthrough)."""
    store: ConfigStore = FakeConfigStore()
    config = Config(auto_approve=False, timeout=0, cap=1)

    store.save(config)

    loaded = store.load()
    assert loaded is not None
    assert loaded.auto_approve is False  # not None
    assert loaded.timeout == 0  # not None
    assert loaded.cap == 1  # not None


def test_config_store_satisfies_protocol():
    """FakeConfigStore implements ConfigStore protocol."""
    store = FakeConfigStore()
    # Type checker will verify this; runtime we just ensure it works.
    assert hasattr(store, "load")
    assert hasattr(store, "save")
    assert callable(store.load)
    assert callable(store.save)
