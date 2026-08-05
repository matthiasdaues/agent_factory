"""Tests for `factory/scripts/update-factory`: refreshing an installed
factory/ to the current state of the referenced agent_factory checkout.

init-factory and update-factory are extensionless scripts loaded via
importlib against the real files, the same way test_remove_factory.py loads
init-factory. Every test builds a complete, isolated source checkout by copying
this repo's own `factory/` into `tmp_path`, then uses it as `--source`. That
keeps the tests hermetic without ever mutating this checkout, and lets them
mutate the synthetic source freely to prove update picks changes up and drops
stale files.

init-factory's network/pre-commit steps (usage-runtime provisioning, lifecycle
initialization, `pre-commit install`) are isolated so the install round trip
stays fast and offline. update-factory's delegation to the sourced init-factory
is stubbed with a plain mirror-copy of `factory/` so the tests exercise
update-factory's own contract — validation, source resolution, removal, the
delegation boundary — rather than re-running the full install.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]


def _load(name: str):
    script = _ROOT / "factory" / "scripts" / name
    loader = SourceFileLoader(name.replace("-", "_"), str(script))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    sys.modules[loader.name] = module
    loader.exec_module(module)
    return module


init_factory = _load("init-factory")
update_factory = _load("update-factory")

MANIFEST = ".agent-factory/factory-install.json"


@pytest.fixture(autouse=True)
def _isolate_install(monkeypatch):
    """Keep the init-factory round trip fast/offline in every test."""
    monkeypatch.setattr(
        init_factory, "provision_usage_runtime", lambda _target, _report: True
    )
    monkeypatch.setattr(
        init_factory,
        "initialize_usage_lifecycle",
        lambda _target, _report, _retention: None,
    )
    monkeypatch.setattr(
        init_factory, "pre_commit_install", lambda _target, _report: None
    )

    # update-factory delegates the reinstall to the sourced init-factory; stub
    # that seam with a fast mirror-copy so update's own logic is what runs.
    def fake_run_init(source: Path, target: Path) -> int:
        dest = target / "factory"
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(source / "factory", dest)
        return 0

    monkeypatch.setattr(update_factory, "_run_init", fake_run_init)


def _make_source(tmp_path: Path) -> Path:
    """A complete, isolated factory checkout (a copy of this repo's factory/)."""
    src = tmp_path / "source"
    src.mkdir(parents=True)
    shutil.copytree(_ROOT / "factory", src / "factory")
    return src


def _install(target: Path, source: Path) -> int:
    return init_factory.main(
        [
            "--target",
            str(target),
            "--source",
            str(source),
            "--project-name",
            "Test Project",
        ]
    )


class TestManifestRecordsSource:
    def test_init_records_factory_source(self, tmp_path):
        src = _make_source(tmp_path)
        target = tmp_path / "proj"
        assert _install(target, src) == 0
        manifest = json.loads((target / MANIFEST).read_text(encoding="utf-8"))
        assert manifest["factory_source"] == str(src.resolve())


class TestUpdateRefresh:
    def test_update_brings_factory_to_current_source(self, tmp_path):
        src = _make_source(tmp_path)
        target = tmp_path / "proj"
        assert _install(target, src) == 0

        (src / "factory" / "agents" / "new-agent.md").write_text("new agent\n")

        assert update_factory.main(["--target", str(target), "--source", str(src)]) == 0
        assert (target / "factory/agents/new-agent.md").read_text() == "new agent\n"

    def test_update_drops_files_absent_from_source(self, tmp_path):
        src = _make_source(tmp_path)
        target = tmp_path / "proj"
        assert _install(target, src) == 0

        stale = target / "factory" / "skills" / "stale-skill" / "SKILL.md"
        stale.parent.mkdir(parents=True)
        stale.write_text("stale\n")
        assert (target / "factory/skills/stale-skill").exists()

        assert update_factory.main(["--target", str(target), "--source", str(src)]) == 0
        assert not (target / "factory/skills/stale-skill").exists()

    def test_update_uses_recorded_source_without_flag(self, tmp_path):
        src = _make_source(tmp_path)
        target = tmp_path / "proj"
        assert _install(target, src) == 0

        (src / "factory" / "agents" / "from-manifest.md").write_text("x\n")
        assert update_factory.main(["--target", str(target)]) == 0
        assert (target / "factory/agents/from-manifest.md").exists()

    def test_source_flag_overrides_recorded_source(self, tmp_path):
        src_a = _make_source(tmp_path)
        src_b = _make_source(tmp_path / "other")
        target = tmp_path / "proj"
        assert _install(target, src_a) == 0

        (src_b / "factory" / "agents" / "from-override.md").write_text("y\n")
        assert (
            update_factory.main(["--target", str(target), "--source", str(src_b)]) == 0
        )
        assert (target / "factory/agents/from-override.md").exists()
        assert not (target / "factory/agents/from-manifest.md").exists()

    def test_delegates_reinstall_to_sourced_init_factory(self, tmp_path, monkeypatch):
        src = _make_source(tmp_path)
        target = tmp_path / "proj"
        assert _install(target, src) == 0

        calls: list[tuple[Path, Path]] = []

        def record(source: Path, target: Path) -> int:
            calls.append((source, target))
            return 0

        monkeypatch.setattr(update_factory, "_run_init", record)
        assert update_factory.main(["--target", str(target), "--source", str(src)]) == 0
        assert calls == [(src.resolve(), target.resolve())]

    def test_update_without_existing_factory_reinstalls(self, tmp_path):
        src = _make_source(tmp_path)
        target = tmp_path / "proj"
        assert _install(target, src) == 0

        shutil.rmtree(target / "factory")
        assert not (target / "factory").exists()

        (src / "factory" / "agents" / "fresh.md").write_text("f\n")
        assert update_factory.main(["--target", str(target), "--source", str(src)]) == 0
        assert (target / "factory/agents/fresh.md").exists()


class TestUpdatePreservesMachineState:
    def test_agent_factory_usage_tracking_survives_update(self, tmp_path):
        """The user-facing guarantee: update replaces only factory/ and never
        removes .agent-factory/ usage transcripts or lifecycle state."""
        src = _make_source(tmp_path)
        target = tmp_path / "proj"
        assert _install(target, src) == 0

        usage_dir = target / ".agent-factory" / "usage" / "transcripts"
        usage_dir.mkdir(parents=True)
        transcript = usage_dir / "record.jsonl"
        transcript.write_text('{"seq": 1}\n', encoding="utf-8")
        state = target / ".agent-factory/usage-control/state.json"
        state.parent.mkdir(parents=True)
        state.write_text('{"mode": "active"}\n', encoding="utf-8")

        (src / "factory" / "agents" / "new-agent.md").write_text("new agent\n")
        assert update_factory.main(["--target", str(target), "--source", str(src)]) == 0

        assert transcript.read_text(encoding="utf-8") == '{"seq": 1}\n'
        assert state.read_text(encoding="utf-8") == '{"mode": "active"}\n'


class TestUpdateErrors:
    def test_non_install_target_fails(self, tmp_path):
        target = tmp_path / "not-an-install"
        target.mkdir()
        assert update_factory.main(["--target", str(target)]) == 1

    def test_missing_source_without_flag_fails(self, tmp_path):
        src = _make_source(tmp_path)
        target = tmp_path / "proj"
        assert _install(target, src) == 0

        manifest_path = target / MANIFEST
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest.pop("factory_source", None)
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        assert update_factory.main(["--target", str(target)]) == 1

    def test_source_without_factory_fails(self, tmp_path):
        src = _make_source(tmp_path)
        target = tmp_path / "proj"
        assert _install(target, src) == 0

        assert (
            update_factory.main(
                ["--target", str(target), "--source", str(tmp_path / "nope")]
            )
            == 1
        )
