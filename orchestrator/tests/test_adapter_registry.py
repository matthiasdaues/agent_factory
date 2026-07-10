"""Tests for AdapterEntry, ModelDictionary, and AdapterRegistry port (ST-0045, UC-10)."""

from __future__ import annotations

from typing import List, Optional

import pytest

from orchestrator.entities import AdapterEntry, ModelDictionary, Tier
from orchestrator.ports import AdapterRegistry


class FakeAdapterRegistry:
    """Fake implementation of AdapterRegistry for testing (satisfies the protocol).

    Stores adapters in memory and creates a ModelDictionary for each.
    """

    def __init__(self):
        self._adapters: dict[str, AdapterEntry] = {}
        self._dictionaries: dict[str, ModelDictionary] = {}

    def list_adapters(self) -> List[AdapterEntry]:
        """Return all registered adapters."""
        return list(self._adapters.values())

    def get_adapter(self, name: str) -> AdapterEntry:
        """Retrieve a single adapter by name."""
        if name not in self._adapters:
            raise KeyError(f"Adapter '{name}' not registered.")
        return self._adapters[name]

    def register(self, name: str, binary_path: str) -> None:
        """Register a new adapter and create its model dictionary."""
        if name in self._adapters:
            raise ValueError(f"Adapter '{name}' is already registered.")
        self._adapters[name] = AdapterEntry(name=name, binary_path=binary_path)
        self._dictionaries[name] = ModelDictionary()

    def unregister(self, name: str) -> None:
        """Remove an adapter and its model dictionary (BR-044)."""
        if name not in self._adapters:
            raise KeyError(f"Adapter '{name}' not registered.")
        del self._adapters[name]
        del self._dictionaries[name]

    def get_model(self, adapter: str, tier: str) -> Optional[str]:
        """Retrieve a model_id for an adapter and tier."""
        if adapter not in self._dictionaries:
            raise KeyError(f"Adapter '{adapter}' not registered.")
        return self._dictionaries[adapter].get_model(tier)

    def set_model(self, adapter: str, tier: str, model_id: str) -> None:
        """Set a tier-to-model mapping in an adapter's dictionary."""
        if adapter not in self._dictionaries:
            raise KeyError(f"Adapter '{adapter}' not registered.")
        self._dictionaries[adapter].set_model(tier, model_id)

    def remove_model(self, adapter: str, tier: str) -> None:
        """Unmap a tier in an adapter's dictionary."""
        if adapter not in self._dictionaries:
            raise KeyError(f"Adapter '{adapter}' not registered.")
        self._dictionaries[adapter].remove_model(tier)

    def list_models(self, adapter: str) -> List[tuple[str, str]]:
        """List all tier-to-model mappings for an adapter."""
        if adapter not in self._dictionaries:
            raise KeyError(f"Adapter '{adapter}' not registered.")
        return self._dictionaries[adapter].list_models()


# --- Tier Enum Tests -------------------------------------------------------


def test_tier_has_economy():
    """Tier enum includes economy."""
    assert Tier.ECONOMY.value == "economy"


def test_tier_has_standard():
    """Tier enum includes standard."""
    assert Tier.STANDARD.value == "standard"


def test_tier_has_strong():
    """Tier enum includes strong."""
    assert Tier.STRONG.value == "strong"


def test_tier_vocabulary_is_fixed():
    """Tier has exactly three values."""
    tiers = {t.value for t in Tier}
    assert tiers == {"economy", "standard", "strong"}


# --- AdapterEntry Tests ----------------------------------------------------


def test_adapter_entry_immutable():
    """AdapterEntry is frozen (immutable)."""
    entry = AdapterEntry(name="copilot", binary_path="/usr/bin/copilot")
    with pytest.raises(Exception):  # dataclass frozen raises AttributeError
        entry.name = "claude"


def test_adapter_entry_with_name_and_path():
    """AdapterEntry holds name and binary_path."""
    entry = AdapterEntry(name="copilot", binary_path="/usr/bin/copilot")
    assert entry.name == "copilot"
    assert entry.binary_path == "/usr/bin/copilot"


def test_adapter_entry_equality():
    """Two AdapterEntry objects with same name and path are equal."""
    entry1 = AdapterEntry(name="copilot", binary_path="/usr/bin/copilot")
    entry2 = AdapterEntry(name="copilot", binary_path="/usr/bin/copilot")
    assert entry1 == entry2


def test_adapter_entry_different_names():
    """Two AdapterEntry objects with different names are not equal."""
    entry1 = AdapterEntry(name="copilot", binary_path="/usr/bin/copilot")
    entry2 = AdapterEntry(name="claude", binary_path="/usr/bin/copilot")
    assert entry1 != entry2


# --- ModelDictionary Tests -------------------------------------------------


def test_model_dictionary_empty_on_init():
    """ModelDictionary starts empty."""
    md = ModelDictionary()
    assert md.list_models() == []


def test_model_dictionary_get_model_unmapped():
    """get_model returns None for unmapped tier."""
    md = ModelDictionary()
    assert md.get_model("economy") is None


def test_model_dictionary_set_and_get_model():
    """set_model and get_model round-trip correctly."""
    md = ModelDictionary()
    md.set_model("economy", "gpt-4-mini")
    assert md.get_model("economy") == "gpt-4-mini"


def test_model_dictionary_set_multiple_tiers():
    """ModelDictionary can hold mappings for all three tiers."""
    md = ModelDictionary()
    md.set_model("economy", "gpt-4-mini")
    md.set_model("standard", "gpt-4")
    md.set_model("strong", "gpt-4-turbo")

    assert md.get_model("economy") == "gpt-4-mini"
    assert md.get_model("standard") == "gpt-4"
    assert md.get_model("strong") == "gpt-4-turbo"


def test_model_dictionary_set_replaces_prior():
    """set_model replaces prior mapping for a tier."""
    md = ModelDictionary()
    md.set_model("economy", "old-model")
    assert md.get_model("economy") == "old-model"

    md.set_model("economy", "new-model")
    assert md.get_model("economy") == "new-model"


def test_model_dictionary_set_invalid_tier():
    """set_model rejects tier outside {economy, standard, strong}."""
    md = ModelDictionary()
    with pytest.raises(ValueError) as exc_info:
        md.set_model("invalid", "some-model")
    assert "Invalid tier" in str(exc_info.value)
    assert "invalid" in str(exc_info.value)


def test_model_dictionary_remove_model():
    """remove_model deletes a tier mapping."""
    md = ModelDictionary()
    md.set_model("economy", "gpt-4-mini")
    md.set_model("standard", "gpt-4")

    md.remove_model("economy")

    assert md.get_model("economy") is None
    assert md.get_model("standard") == "gpt-4"


def test_model_dictionary_remove_unmapped_tier():
    """remove_model on unmapped tier is idempotent (no-op)."""
    md = ModelDictionary()
    # Should not raise
    md.remove_model("economy")
    assert md.get_model("economy") is None


def test_model_dictionary_remove_invalid_tier():
    """remove_model rejects tier outside {economy, standard, strong}."""
    md = ModelDictionary()
    with pytest.raises(ValueError) as exc_info:
        md.remove_model("invalid")
    assert "Invalid tier" in str(exc_info.value)


def test_model_dictionary_list_models_empty():
    """list_models returns empty list when no mappings."""
    md = ModelDictionary()
    assert md.list_models() == []


def test_model_dictionary_list_models_single():
    """list_models returns all current mappings as tuples."""
    md = ModelDictionary()
    md.set_model("economy", "gpt-4-mini")

    models = md.list_models()
    assert len(models) == 1
    assert ("economy", "gpt-4-mini") in models


def test_model_dictionary_list_models_multiple():
    """list_models returns all current mappings."""
    md = ModelDictionary()
    md.set_model("economy", "gpt-4-mini")
    md.set_model("standard", "gpt-4")
    md.set_model("strong", "gpt-4-turbo")

    models = md.list_models()
    assert len(models) == 3
    assert ("economy", "gpt-4-mini") in models
    assert ("standard", "gpt-4") in models
    assert ("strong", "gpt-4-turbo") in models


# --- AdapterRegistry Tests -------------------------------------------------


def test_adapter_registry_empty_on_init():
    """AdapterRegistry starts with no adapters."""
    registry: AdapterRegistry = FakeAdapterRegistry()
    assert registry.list_adapters() == []


def test_adapter_registry_register_and_list():
    """register() adds adapter; list_adapters() returns it."""
    registry: AdapterRegistry = FakeAdapterRegistry()
    registry.register("copilot", "/usr/bin/copilot")

    adapters = registry.list_adapters()
    assert len(adapters) == 1
    assert adapters[0].name == "copilot"
    assert adapters[0].binary_path == "/usr/bin/copilot"


def test_adapter_registry_get_adapter():
    """get_adapter() retrieves a registered adapter."""
    registry: AdapterRegistry = FakeAdapterRegistry()
    registry.register("copilot", "/usr/bin/copilot")

    entry = registry.get_adapter("copilot")
    assert entry.name == "copilot"
    assert entry.binary_path == "/usr/bin/copilot"


def test_adapter_registry_get_nonexistent_adapter():
    """get_adapter() raises KeyError for unregistered adapter."""
    registry: AdapterRegistry = FakeAdapterRegistry()
    with pytest.raises(KeyError):
        registry.get_adapter("copilot")


def test_adapter_registry_register_duplicate_name():
    """register() rejects duplicate adapter names."""
    registry: AdapterRegistry = FakeAdapterRegistry()
    registry.register("copilot", "/usr/bin/copilot")

    with pytest.raises(ValueError):
        registry.register("copilot", "/usr/bin/copilot-2")


def test_adapter_registry_register_creates_empty_dictionary():
    """register() creates an empty model dictionary for the adapter."""
    registry: AdapterRegistry = FakeAdapterRegistry()
    registry.register("copilot", "/usr/bin/copilot")

    models = registry.list_models("copilot")
    assert models == []


def test_adapter_registry_unregister_removes_adapter():
    """unregister() removes the adapter."""
    registry: AdapterRegistry = FakeAdapterRegistry()
    registry.register("copilot", "/usr/bin/copilot")
    registry.unregister("copilot")

    assert registry.list_adapters() == []


def test_adapter_registry_unregister_removes_dictionary():
    """unregister() removes the adapter's model dictionary (BR-044)."""
    registry: AdapterRegistry = FakeAdapterRegistry()
    registry.register("copilot", "/usr/bin/copilot")
    registry.set_model("copilot", "economy", "gpt-4-mini")

    registry.unregister("copilot")

    # Retrieving the dictionary should now fail
    with pytest.raises(KeyError):
        registry.list_models("copilot")


def test_adapter_registry_unregister_nonexistent_adapter():
    """unregister() raises KeyError for unregistered adapter."""
    registry: AdapterRegistry = FakeAdapterRegistry()
    with pytest.raises(KeyError):
        registry.unregister("copilot")


def test_adapter_registry_set_and_get_model():
    """set_model() and get_model() store and retrieve tier mappings."""
    registry: AdapterRegistry = FakeAdapterRegistry()
    registry.register("copilot", "/usr/bin/copilot")
    registry.set_model("copilot", "economy", "gpt-4-mini")

    assert registry.get_model("copilot", "economy") == "gpt-4-mini"


def test_adapter_registry_get_model_unmapped():
    """get_model() returns None for unmapped tier."""
    registry: AdapterRegistry = FakeAdapterRegistry()
    registry.register("copilot", "/usr/bin/copilot")

    assert registry.get_model("copilot", "economy") is None


def test_adapter_registry_set_model_invalid_tier():
    """set_model() rejects tier outside {economy, standard, strong}."""
    registry: AdapterRegistry = FakeAdapterRegistry()
    registry.register("copilot", "/usr/bin/copilot")

    with pytest.raises(ValueError):
        registry.set_model("copilot", "invalid", "some-model")


def test_adapter_registry_set_model_nonexistent_adapter():
    """set_model() raises KeyError for unregistered adapter."""
    registry: AdapterRegistry = FakeAdapterRegistry()

    with pytest.raises(KeyError):
        registry.set_model("copilot", "economy", "gpt-4-mini")


def test_adapter_registry_remove_model():
    """remove_model() deletes a tier mapping."""
    registry: AdapterRegistry = FakeAdapterRegistry()
    registry.register("copilot", "/usr/bin/copilot")
    registry.set_model("copilot", "economy", "gpt-4-mini")
    registry.set_model("copilot", "standard", "gpt-4")

    registry.remove_model("copilot", "economy")

    assert registry.get_model("copilot", "economy") is None
    assert registry.get_model("copilot", "standard") == "gpt-4"


def test_adapter_registry_remove_model_invalid_tier():
    """remove_model() rejects tier outside {economy, standard, strong}."""
    registry: AdapterRegistry = FakeAdapterRegistry()
    registry.register("copilot", "/usr/bin/copilot")

    with pytest.raises(ValueError):
        registry.remove_model("copilot", "invalid")


def test_adapter_registry_remove_model_nonexistent_adapter():
    """remove_model() raises KeyError for unregistered adapter."""
    registry: AdapterRegistry = FakeAdapterRegistry()

    with pytest.raises(KeyError):
        registry.remove_model("copilot", "economy")


def test_adapter_registry_list_models():
    """list_models() returns all tier-to-model mappings for an adapter."""
    registry: AdapterRegistry = FakeAdapterRegistry()
    registry.register("copilot", "/usr/bin/copilot")
    registry.set_model("copilot", "economy", "gpt-4-mini")
    registry.set_model("copilot", "standard", "gpt-4")
    registry.set_model("copilot", "strong", "gpt-4-turbo")

    models = registry.list_models("copilot")
    assert len(models) == 3
    assert ("economy", "gpt-4-mini") in models
    assert ("standard", "gpt-4") in models
    assert ("strong", "gpt-4-turbo") in models


def test_adapter_registry_list_models_nonexistent_adapter():
    """list_models() raises KeyError for unregistered adapter."""
    registry: AdapterRegistry = FakeAdapterRegistry()

    with pytest.raises(KeyError):
        registry.list_models("copilot")


def test_adapter_registry_multiple_adapters():
    """AdapterRegistry can manage multiple adapters and their separate dictionaries."""
    registry: AdapterRegistry = FakeAdapterRegistry()
    registry.register("copilot", "/usr/bin/copilot")
    registry.register("claude", "/usr/bin/claude")

    registry.set_model("copilot", "economy", "copilot-mini")
    registry.set_model("claude", "economy", "claude-haiku")

    assert registry.get_model("copilot", "economy") == "copilot-mini"
    assert registry.get_model("claude", "economy") == "claude-haiku"


def test_adapter_registry_unregister_one_doesnt_affect_other():
    """Unregistering one adapter doesn't affect others."""
    registry: AdapterRegistry = FakeAdapterRegistry()
    registry.register("copilot", "/usr/bin/copilot")
    registry.register("claude", "/usr/bin/claude")
    registry.set_model("claude", "standard", "claude-sonnet")

    registry.unregister("copilot")

    assert len(registry.list_adapters()) == 1
    assert registry.get_adapter("claude").name == "claude"
    assert registry.get_model("claude", "standard") == "claude-sonnet"


def test_adapter_registry_satisfies_protocol():
    """FakeAdapterRegistry implements AdapterRegistry protocol."""
    registry = FakeAdapterRegistry()
    # Type checker will verify this; runtime we just ensure methods exist.
    assert hasattr(registry, "list_adapters")
    assert hasattr(registry, "get_adapter")
    assert hasattr(registry, "register")
    assert hasattr(registry, "unregister")
    assert hasattr(registry, "get_model")
    assert hasattr(registry, "set_model")
    assert hasattr(registry, "remove_model")
    assert hasattr(registry, "list_models")
    assert all(
        callable(getattr(registry, method))
        for method in [
            "list_adapters",
            "get_adapter",
            "register",
            "unregister",
            "get_model",
            "set_model",
            "remove_model",
            "list_models",
        ]
    )
