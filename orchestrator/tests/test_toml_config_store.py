"""Tests for TomlConfigStore (ST-0042).

Exercises the concrete .orchestrator/config.toml adapter against real
temp-directory files (not mocks) so the atomic-write guarantee (VR-032) is
observed end to end rather than assumed from mocked calls.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest

from orchestrator.adapters.config_store import ConfigStoreError, TomlConfigStore
from orchestrator.entities import Config


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
    # Best-effort cleanup; restore write perms in case a permission test left
    # the directory locked down.
    root.chmod(0o700)
    shutil.rmtree(root, ignore_errors=True)


# --- absent file (FR-Q5) ------------------------------------------------


def test_load_returns_none_when_file_absent(orch_dir: Path) -> None:
    store = TomlConfigStore(orch_dir)

    result = store.load()

    assert result is None


def test_load_does_not_create_the_file(orch_dir: Path) -> None:
    store = TomlConfigStore(orch_dir)

    store.load()

    assert not (orch_dir / "config.toml").exists()


# --- valid round-trip (FR-Q1, FR-Q5) ------------------------------------


def test_save_creates_file_only_on_first_persist(orch_dir: Path) -> None:
    store = TomlConfigStore(orch_dir)
    config_path = orch_dir / "config.toml"
    assert not config_path.exists()

    store.save(Config(adapter="copilot", timeout=900, cap=3, auto_approve=True))

    assert config_path.exists()


def test_valid_round_trip_all_fields_set(orch_dir: Path) -> None:
    store = TomlConfigStore(orch_dir)
    original = Config(adapter="copilot", timeout=900, cap=3, auto_approve=True)

    store.save(original)
    loaded = store.load()

    assert loaded == original


def test_valid_round_trip_partial_fields(orch_dir: Path) -> None:
    store = TomlConfigStore(orch_dir)
    original = Config(adapter=None, timeout=120, cap=None, auto_approve=False)

    store.save(original)
    loaded = store.load()

    assert loaded == original


def test_save_overwrites_prior_persisted_value(orch_dir: Path) -> None:
    store = TomlConfigStore(orch_dir)
    store.save(Config(adapter="copilot", timeout=900, cap=3, auto_approve=True))

    store.save(Config(adapter="claude", timeout=60, cap=1, auto_approve=False))
    loaded = store.load()

    assert loaded == Config(adapter="claude", timeout=60, cap=1, auto_approve=False)


def test_save_leaves_no_leftover_temp_files(orch_dir: Path) -> None:
    store = TomlConfigStore(orch_dir)

    store.save(Config(adapter="copilot", timeout=900, cap=3, auto_approve=True))

    assert [p.name for p in orch_dir.iterdir()] == ["config.toml"]


def test_save_preserves_unrelated_toml_sections(orch_dir: Path) -> None:
    """The adapter registry (ADR-0017, ST-0046) shares this file; a
    ConfigStore.save() must not clobber sections it does not own."""
    config_path = orch_dir / "config.toml"
    config_path.write_text(
        '[adapters]\ncopilot = "/usr/local/bin/copilot"\n\n'
        "[defaults]\n"
        'adapter = "copilot"\n',
        encoding="utf-8",
    )
    store = TomlConfigStore(orch_dir)

    store.save(Config(adapter="claude", timeout=None, cap=None, auto_approve=None))

    text = config_path.read_text(encoding="utf-8")
    assert '[adapters]\ncopilot = "/usr/local/bin/copilot"' in text
    loaded = store.load()
    assert loaded == Config(adapter="claude", timeout=None, cap=None, auto_approve=None)


# --- malformed file / invalid value (FR-Q6) -----------------------------


def test_malformed_syntax_raises_error_naming_file_and_line(orch_dir: Path) -> None:
    config_path = orch_dir / "config.toml"
    config_path.write_text("[defaults]\nthis is not valid\n", encoding="utf-8")
    store = TomlConfigStore(orch_dir)

    with pytest.raises(ConfigStoreError) as excinfo:
        store.load()

    message = str(excinfo.value)
    assert str(config_path) in message


def test_unparsable_value_raises_error_naming_key(orch_dir: Path) -> None:
    config_path = orch_dir / "config.toml"
    config_path.write_text("[defaults]\ntimeout = %%%\n", encoding="utf-8")
    store = TomlConfigStore(orch_dir)

    with pytest.raises(ConfigStoreError) as excinfo:
        store.load()

    message = str(excinfo.value)
    assert "timeout" in message
    assert str(config_path) in message


def test_wrong_type_raises_error_naming_key(orch_dir: Path) -> None:
    config_path = orch_dir / "config.toml"
    config_path.write_text('[defaults]\ntimeout = "soon"\n', encoding="utf-8")
    store = TomlConfigStore(orch_dir)

    with pytest.raises(ConfigStoreError) as excinfo:
        store.load()

    assert "timeout" in str(excinfo.value)


def test_non_positive_timeout_raises_error(orch_dir: Path) -> None:
    config_path = orch_dir / "config.toml"
    config_path.write_text("[defaults]\ntimeout = 0\n", encoding="utf-8")
    store = TomlConfigStore(orch_dir)

    with pytest.raises(ConfigStoreError) as excinfo:
        store.load()

    assert "timeout" in str(excinfo.value)


def test_cap_below_one_raises_error(orch_dir: Path) -> None:
    config_path = orch_dir / "config.toml"
    config_path.write_text("[defaults]\ncap = 0\n", encoding="utf-8")
    store = TomlConfigStore(orch_dir)

    with pytest.raises(ConfigStoreError) as excinfo:
        store.load()

    assert "cap" in str(excinfo.value)


def test_unknown_key_raises_error(orch_dir: Path) -> None:
    config_path = orch_dir / "config.toml"
    config_path.write_text('[defaults]\nbogus = "x"\n', encoding="utf-8")
    store = TomlConfigStore(orch_dir)

    with pytest.raises(ConfigStoreError) as excinfo:
        store.load()

    assert "bogus" in str(excinfo.value)


# --- failed write leaves prior file intact (VR-032, BR-038) -------------


def test_failed_write_leaves_prior_config_intact(orch_dir: Path) -> None:
    store = TomlConfigStore(orch_dir)
    store.save(Config(adapter="copilot", timeout=900, cap=3, auto_approve=True))
    config_path = orch_dir / "config.toml"
    original_bytes = config_path.read_bytes()

    # Real filesystem failure: strip write permission on the directory so
    # neither the temp-file write nor the rename can complete.
    orch_dir.chmod(0o500)
    try:
        with pytest.raises(OSError):
            store.save(Config(adapter="claude", timeout=60, cap=1, auto_approve=False))
    finally:
        orch_dir.chmod(0o700)

    assert config_path.read_bytes() == original_bytes
    assert store.load() == Config(
        adapter="copilot", timeout=900, cap=3, auto_approve=True
    )
