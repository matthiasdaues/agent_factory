"""Tests for TomlAdapterRegistry (ST-0046).

NOTE on filename: ST-0046's frontmatter names this file
`tests/test_adapter_registry.py`, but that path already holds ST-0045's
tests for the abstract `AdapterEntry`/`ModelDictionary`/`AdapterRegistry`
port contract (a `FakeAdapterRegistry`-driven test suite). This file targets
the *concrete* TOML-backed adapter instead, so it lives at
`tests/test_toml_adapter_registry.py` to avoid clobbering ST-0045's tests —
see the "Analysis" section of backlog/ST-0046.md for the full rationale.

Exercises the concrete .orchestrator/config.toml adapter against real
temp-directory files (not mocks), mirroring tests/test_toml_config_store.py's
approach so the atomic-write guarantee (BR-048) is observed end to end.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

import pytest

from orchestrator.adapters.adapter_registry import TomlAdapterRegistry
from orchestrator.entities import AdapterEntry


@pytest.fixture
def orch_dir(request) -> Path:
    root = (
        Path(__file__).resolve().parent
        / ".scratch"
        / f"{request.node.name}-{os.getpid()}"
    )
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    yield root
    root.chmod(0o700)
    shutil.rmtree(root, ignore_errors=True)


@pytest.fixture
def executable(tmp_path) -> str:
    """A real executable file path, guaranteed to exist on this machine."""
    return sys.executable


@pytest.fixture
def other_executable(tmp_path) -> str:
    """A second, distinct real executable path (different from `executable`)."""
    return "/bin/cat"


@pytest.fixture
def non_executable(tmp_path) -> str:
    """A real file that exists but is not executable."""
    path = tmp_path / "not-executable"
    path.write_text("not a binary\n", encoding="utf-8")
    path.chmod(0o644)
    return str(path)


# --- register (BR-042, BR-043) ------------------------------------------


def test_register_accepts_valid_executable_path(
    orch_dir: Path, executable: str
) -> None:
    registry = TomlAdapterRegistry(orch_dir)

    registry.register("copilot", executable)

    assert registry.get_adapter("copilot") == AdapterEntry(
        name="copilot", binary_path=executable
    )


def test_register_creates_file_only_on_first_persist(
    orch_dir: Path, executable: str
) -> None:
    config_path = orch_dir / "config.toml"
    registry = TomlAdapterRegistry(orch_dir)
    assert not config_path.exists()

    registry.register("copilot", executable)

    assert config_path.exists()


def test_register_persists_across_new_instance(orch_dir: Path, executable: str) -> None:
    TomlAdapterRegistry(orch_dir).register("copilot", executable)

    reloaded = TomlAdapterRegistry(orch_dir)
    assert reloaded.list_adapters() == [
        AdapterEntry(name="copilot", binary_path=executable)
    ]


def test_register_creates_empty_model_dictionary(
    orch_dir: Path, executable: str
) -> None:
    registry = TomlAdapterRegistry(orch_dir)

    registry.register("copilot", executable)

    assert registry.list_models("copilot") == []


def test_register_rejects_duplicate_name(orch_dir: Path, executable: str) -> None:
    registry = TomlAdapterRegistry(orch_dir)
    registry.register("copilot", executable)

    with pytest.raises(ValueError):
        registry.register("copilot", executable)


def test_register_duplicate_name_leaves_registry_unchanged(
    orch_dir: Path, executable: str
) -> None:
    registry = TomlAdapterRegistry(orch_dir)
    registry.register("copilot", executable)

    with pytest.raises(ValueError):
        registry.register("copilot", "/some/other/path")

    assert registry.get_adapter("copilot").binary_path == executable


def test_register_rejects_duplicate_binary_path_under_new_name(
    orch_dir: Path, executable: str
) -> None:
    """BR-043: the same executable path may not be registered twice under
    different names."""
    registry = TomlAdapterRegistry(orch_dir)
    registry.register("copilot", executable)

    with pytest.raises(ValueError):
        registry.register("copilot-2", executable)

    assert [a.name for a in registry.list_adapters()] == ["copilot"]


def test_register_rejects_missing_path(orch_dir: Path) -> None:
    registry = TomlAdapterRegistry(orch_dir)

    with pytest.raises(ValueError):
        registry.register("copilot", "/no/such/binary/exists")

    assert registry.list_adapters() == []


def test_register_rejects_non_executable_path(
    orch_dir: Path, non_executable: str
) -> None:
    registry = TomlAdapterRegistry(orch_dir)

    with pytest.raises(ValueError):
        registry.register("copilot", non_executable)

    assert registry.list_adapters() == []


def test_register_invalid_path_does_not_create_file(
    orch_dir: Path, non_executable: str
) -> None:
    registry = TomlAdapterRegistry(orch_dir)
    config_path = orch_dir / "config.toml"

    with pytest.raises(ValueError):
        registry.register("copilot", non_executable)

    assert not config_path.exists()


def test_register_multiple_adapters(
    orch_dir: Path, executable: str, other_executable: str
) -> None:
    registry = TomlAdapterRegistry(orch_dir)
    registry.register("copilot", executable)
    registry.register("claude", other_executable)

    names = sorted(a.name for a in registry.list_adapters())
    assert names == ["claude", "copilot"]


def test_get_adapter_raises_for_unregistered(orch_dir: Path) -> None:
    registry = TomlAdapterRegistry(orch_dir)

    with pytest.raises(KeyError):
        registry.get_adapter("copilot")


# --- unregister / cascade delete (BR-044) -------------------------------


def test_unregister_removes_adapter(orch_dir: Path, executable: str) -> None:
    registry = TomlAdapterRegistry(orch_dir)
    registry.register("copilot", executable)

    registry.unregister("copilot")

    assert registry.list_adapters() == []


def test_unregister_cascades_model_dictionary(orch_dir: Path, executable: str) -> None:
    registry = TomlAdapterRegistry(orch_dir)
    registry.register("copilot", executable)
    registry.set_model("copilot", "economy", "gpt-4-mini")

    registry.unregister("copilot")

    with pytest.raises(KeyError):
        registry.list_models("copilot")


def test_unregister_cascade_persists_after_reload(
    orch_dir: Path, executable: str
) -> None:
    registry = TomlAdapterRegistry(orch_dir)
    registry.register("copilot", executable)
    registry.set_model("copilot", "economy", "gpt-4-mini")
    registry.unregister("copilot")

    reloaded = TomlAdapterRegistry(orch_dir)
    assert reloaded.list_adapters() == []
    with pytest.raises(KeyError):
        reloaded.list_models("copilot")


def test_unregister_raises_for_unregistered(orch_dir: Path) -> None:
    registry = TomlAdapterRegistry(orch_dir)

    with pytest.raises(KeyError):
        registry.unregister("copilot")


def test_unregister_one_leaves_other_adapters_intact(
    orch_dir: Path, executable: str, other_executable: str
) -> None:
    registry = TomlAdapterRegistry(orch_dir)
    registry.register("copilot", executable)
    registry.register("claude", other_executable)
    registry.set_model("claude", "standard", "claude-sonnet")

    registry.unregister("copilot")

    assert [a.name for a in registry.list_adapters()] == ["claude"]
    assert registry.get_model("claude", "standard") == "claude-sonnet"


# --- model dictionary CRUD (BR-045) -------------------------------------


def test_set_and_get_model(orch_dir: Path, executable: str) -> None:
    registry = TomlAdapterRegistry(orch_dir)
    registry.register("copilot", executable)

    registry.set_model("copilot", "economy", "gpt-4-mini")

    assert registry.get_model("copilot", "economy") == "gpt-4-mini"


def test_set_model_persists_across_new_instance(
    orch_dir: Path, executable: str
) -> None:
    registry = TomlAdapterRegistry(orch_dir)
    registry.register("copilot", executable)
    registry.set_model("copilot", "economy", "gpt-4-mini")

    reloaded = TomlAdapterRegistry(orch_dir)
    assert reloaded.get_model("copilot", "economy") == "gpt-4-mini"


def test_get_model_unmapped_tier_returns_none(orch_dir: Path, executable: str) -> None:
    registry = TomlAdapterRegistry(orch_dir)
    registry.register("copilot", executable)

    assert registry.get_model("copilot", "economy") is None


def test_set_model_replaces_prior_mapping(orch_dir: Path, executable: str) -> None:
    registry = TomlAdapterRegistry(orch_dir)
    registry.register("copilot", executable)
    registry.set_model("copilot", "economy", "old-model")

    registry.set_model("copilot", "economy", "new-model")

    assert registry.get_model("copilot", "economy") == "new-model"


def test_set_model_rejects_invalid_tier(orch_dir: Path, executable: str) -> None:
    registry = TomlAdapterRegistry(orch_dir)
    registry.register("copilot", executable)

    with pytest.raises(ValueError):
        registry.set_model("copilot", "invalid", "some-model")


def test_set_model_invalid_tier_leaves_dictionary_unchanged(
    orch_dir: Path, executable: str
) -> None:
    registry = TomlAdapterRegistry(orch_dir)
    registry.register("copilot", executable)
    registry.set_model("copilot", "economy", "gpt-4-mini")

    with pytest.raises(ValueError):
        registry.set_model("copilot", "bogus-tier", "some-model")

    assert registry.list_models("copilot") == [("economy", "gpt-4-mini")]


def test_set_model_raises_for_unregistered_adapter(orch_dir: Path) -> None:
    registry = TomlAdapterRegistry(orch_dir)

    with pytest.raises(KeyError):
        registry.set_model("copilot", "economy", "gpt-4-mini")


def test_remove_model(orch_dir: Path, executable: str) -> None:
    registry = TomlAdapterRegistry(orch_dir)
    registry.register("copilot", executable)
    registry.set_model("copilot", "economy", "gpt-4-mini")
    registry.set_model("copilot", "standard", "gpt-4")

    registry.remove_model("copilot", "economy")

    assert registry.get_model("copilot", "economy") is None
    assert registry.get_model("copilot", "standard") == "gpt-4"


def test_remove_model_is_idempotent(orch_dir: Path, executable: str) -> None:
    registry = TomlAdapterRegistry(orch_dir)
    registry.register("copilot", executable)

    registry.remove_model("copilot", "economy")  # should not raise

    assert registry.get_model("copilot", "economy") is None


def test_remove_model_rejects_invalid_tier(orch_dir: Path, executable: str) -> None:
    registry = TomlAdapterRegistry(orch_dir)
    registry.register("copilot", executable)

    with pytest.raises(ValueError):
        registry.remove_model("copilot", "invalid")


def test_remove_model_raises_for_unregistered_adapter(orch_dir: Path) -> None:
    registry = TomlAdapterRegistry(orch_dir)

    with pytest.raises(KeyError):
        registry.remove_model("copilot", "economy")


def test_list_models_multiple_tiers(orch_dir: Path, executable: str) -> None:
    registry = TomlAdapterRegistry(orch_dir)
    registry.register("copilot", executable)
    registry.set_model("copilot", "economy", "gpt-4-mini")
    registry.set_model("copilot", "standard", "gpt-4")
    registry.set_model("copilot", "strong", "gpt-4-turbo")

    models = registry.list_models("copilot")

    assert len(models) == 3
    assert ("economy", "gpt-4-mini") in models
    assert ("standard", "gpt-4") in models
    assert ("strong", "gpt-4-turbo") in models


def test_list_models_raises_for_unregistered_adapter(orch_dir: Path) -> None:
    registry = TomlAdapterRegistry(orch_dir)

    with pytest.raises(KeyError):
        registry.list_models("copilot")


def test_two_adapters_have_independent_dictionaries(
    orch_dir: Path, executable: str, other_executable: str
) -> None:
    registry = TomlAdapterRegistry(orch_dir)
    registry.register("copilot", executable)
    registry.register("claude", other_executable)

    registry.set_model("copilot", "economy", "copilot-mini")
    registry.set_model("claude", "economy", "claude-haiku")

    assert registry.get_model("copilot", "economy") == "copilot-mini"
    assert registry.get_model("claude", "economy") == "claude-haiku"


# --- coexistence with TomlConfigStore's [defaults] table (ADR-0017) -----


def test_save_preserves_foreign_defaults_table(orch_dir: Path, executable: str) -> None:
    config_path = orch_dir / "config.toml"
    config_path.write_text(
        '[defaults]\nadapter = "copilot"\ntimeout = 900\n', encoding="utf-8"
    )
    registry = TomlAdapterRegistry(orch_dir)

    registry.register("copilot", executable)

    text = config_path.read_text(encoding="utf-8")
    assert '[defaults]\nadapter = "copilot"\ntimeout = 900' in text


def test_defaults_table_is_untouched_by_unregister(
    orch_dir: Path, executable: str
) -> None:
    config_path = orch_dir / "config.toml"
    registry = TomlAdapterRegistry(orch_dir)
    registry.register("copilot", executable)
    config_path.write_text(
        config_path.read_text(encoding="utf-8") + '[defaults]\nadapter = "copilot"\n',
        encoding="utf-8",
    )

    registry.unregister("copilot")

    text = config_path.read_text(encoding="utf-8")
    assert '[defaults]\nadapter = "copilot"' in text
    assert "[adapters]" not in text


def test_loading_registry_ignores_defaults_table(
    orch_dir: Path, executable: str
) -> None:
    config_path = orch_dir / "config.toml"
    config_path.write_text(
        '[defaults]\nadapter = "copilot"\ntimeout = 900\n', encoding="utf-8"
    )
    registry = TomlAdapterRegistry(orch_dir)

    assert registry.list_adapters() == []


# --- failed write leaves prior state intact (BR-048) --------------------


def test_failed_write_leaves_prior_registry_intact(
    orch_dir: Path, executable: str, other_executable: str
) -> None:
    registry = TomlAdapterRegistry(orch_dir)
    registry.register("copilot", executable)
    config_path = orch_dir / "config.toml"
    original_bytes = config_path.read_bytes()

    orch_dir.chmod(0o500)
    try:
        with pytest.raises(OSError):
            registry.register("claude", other_executable)
    finally:
        orch_dir.chmod(0o700)

    assert config_path.read_bytes() == original_bytes
    assert [a.name for a in registry.list_adapters()] == ["copilot"]


def test_failed_write_leaves_no_leftover_temp_files(
    orch_dir: Path, executable: str, other_executable: str
) -> None:
    registry = TomlAdapterRegistry(orch_dir)
    registry.register("copilot", executable)

    orch_dir.chmod(0o500)
    try:
        with pytest.raises(OSError):
            registry.register("claude", other_executable)
    finally:
        orch_dir.chmod(0o700)

    assert [p.name for p in orch_dir.iterdir()] == ["config.toml"]


def test_successful_write_leaves_no_leftover_temp_files(
    orch_dir: Path, executable: str
) -> None:
    registry = TomlAdapterRegistry(orch_dir)

    registry.register("copilot", executable)

    assert [p.name for p in orch_dir.iterdir()] == ["config.toml"]
