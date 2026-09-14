"""Integration tests for ST-0249 — component lifecycle operations.

Tests cover install, update (compatible and incompatible), remove,
idempotency, raw-evidence preservation, and manifest management for
the usage-analysis component.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from conftest import load_script

inf = load_script("init-factory")


@pytest.fixture()
def source_root(tmp_path: Path) -> Path:
    """Mock monorepo root with a packages/usage/ subtree."""
    pkg = tmp_path / "source" / "packages" / "usage"
    (pkg / "src" / "usage").mkdir(parents=True)
    (pkg / "src" / "usage" / "__init__.py").write_text("# usage\n")
    (pkg / "src" / "usage" / "cli.py").write_text("# cli\n")
    (pkg / "contracts").mkdir()
    (pkg / "contracts" / "contract.yaml").write_text(
        "owner: factory\nschema: v1.schema.json\n"
    )
    (pkg / "contracts" / "v1.schema.json").write_text("{}\n")
    (pkg / "sql").mkdir()
    (pkg / "sql" / "bootstrap-v1.sql").write_text("-- bootstrap\n")
    (pkg / "docs").mkdir()
    (pkg / "docs" / "ui-exploration.md").write_text("# UI\n")
    (pkg / "pyproject.toml").write_text(
        '[project]\nname = "usage"\nversion = "0.1.0"\n'
    )
    return tmp_path / "source"


@pytest.fixture()
def target(tmp_path: Path) -> Path:
    """Minimal target project with .agent-factory/ and a manifest."""
    t = tmp_path / "project"
    t.mkdir()
    af = t / ".agent-factory"
    af.mkdir()
    (af / "usage").mkdir()
    (af / "usage" / "evidence.jsonl").write_text('{"row": 1}\n')
    manifest = {
        "version": 1,
        "installed_components": {},
        "remove_paths": [],
    }
    (af / "factory-install.json").write_text(
        json.dumps(manifest, indent=2) + "\n"
    )
    return t


def _make_install_dict() -> dict:
    return {"installed_components": {}}


class TestUsagePackageSource:
    def test_finds_existing_package(self, source_root: Path) -> None:
        result = inf._usage_package_source(source_root)
        assert result is not None
        assert result.name == "usage"

    def test_returns_none_when_absent(self, tmp_path: Path) -> None:
        assert inf._usage_package_source(tmp_path) is None


class TestExtractContractMajor:
    def test_extracts_v1(self, source_root: Path) -> None:
        pkg = source_root / "packages" / "usage"
        assert inf._extract_contract_major(pkg) == "1"

    def test_returns_none_when_missing(self, tmp_path: Path) -> None:
        assert inf._extract_contract_major(tmp_path) is None


class TestReadPackageVersion:
    def test_reads_version(self, source_root: Path) -> None:
        pkg = source_root / "packages" / "usage"
        version = inf._read_package_version(pkg)
        assert isinstance(version, str)
        assert version in ("0.1.0", "0.0.0")

    def test_defaults_when_missing(self, tmp_path: Path) -> None:
        assert inf._read_package_version(tmp_path) == "0.0.0"


class TestInstallUsageComponent:
    def test_installs_component(
        self, target: Path, source_root: Path
    ) -> None:
        install = _make_install_dict()
        report: list[str] = []
        inf.install_usage_component(target, source_root, install, report)

        dest = target / inf.COMPONENT_INSTALL_DIR
        assert dest.is_dir()
        assert (dest / "src" / "usage" / "__init__.py").exists()
        assert (dest / "src" / "usage" / "cli.py").exists()
        assert (dest / "pyproject.toml").exists()
        assert (dest / "contracts" / "contract.yaml").exists()
        assert (dest / "sql" / "bootstrap-v1.sql").exists()
        assert (dest / "docs" / "ui-exploration.md").exists()

        meta = json.loads((dest / "component.json").read_text())
        assert meta["component"] == "usage"
        assert meta["contract_version"] == "v1"
        assert isinstance(meta["package_version"], str)

        assert "usage" in install["installed_components"]

    def test_idempotent_skip(
        self, target: Path, source_root: Path
    ) -> None:
        install = _make_install_dict()
        report: list[str] = []
        inf.install_usage_component(target, source_root, install, report)

        report2: list[str] = []
        install2 = _make_install_dict()
        inf.install_usage_component(target, source_root, install2, report2)
        assert any("already installed" in r for r in report2)

    def test_raises_when_no_source(self, target: Path, tmp_path: Path) -> None:
        install = _make_install_dict()
        report: list[str] = []
        with pytest.raises(inf.Collision, match="packages/usage/ not found"):
            inf.install_usage_component(target, tmp_path, install, report)


class TestDoUpdateComponent:
    def test_compatible_update(
        self, target: Path, source_root: Path
    ) -> None:
        install = _make_install_dict()
        report: list[str] = []
        inf.install_usage_component(target, source_root, install, report)

        manifest_path = target / inf.MANIFEST_PATH
        manifest = json.loads(manifest_path.read_text())
        manifest["installed_components"] = install["installed_components"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

        (source_root / "packages" / "usage" / "src" / "usage" / "new.py").write_text(
            "# new\n"
        )
        (source_root / "packages" / "usage" / "pyproject.toml").write_text(
            '[project]\nname = "usage"\nversion = "0.2.0"\n'
        )

        rc = inf.do_update_component(target, source_root, "usage")
        assert rc == 0

        dest = target / inf.COMPONENT_INSTALL_DIR
        assert (dest / "src" / "usage" / "new.py").exists()
        meta = json.loads((dest / "component.json").read_text())
        assert isinstance(meta["package_version"], str)

    def test_incompatible_update_rejected(
        self, target: Path, source_root: Path
    ) -> None:
        install = _make_install_dict()
        report: list[str] = []
        inf.install_usage_component(target, source_root, install, report)

        manifest_path = target / inf.MANIFEST_PATH
        manifest = json.loads(manifest_path.read_text())
        manifest["installed_components"] = install["installed_components"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

        (source_root / "packages" / "usage" / "contracts" / "contract.yaml").write_text(
            "owner: factory\nschema: v2.schema.json\n"
        )

        rc = inf.do_update_component(target, source_root, "usage")
        assert rc == 1

        meta = json.loads(
            (target / inf.COMPONENT_INSTALL_DIR / "component.json").read_text()
        )
        assert meta["contract_version"] == "v1"

    def test_update_not_installed(
        self, target: Path, source_root: Path
    ) -> None:
        rc = inf.do_update_component(target, source_root, "usage")
        assert rc == 1

    def test_unknown_component(
        self, target: Path, source_root: Path
    ) -> None:
        rc = inf.do_update_component(target, source_root, "bogus")
        assert rc == 1


class TestDoRemoveComponent:
    def test_removes_component(
        self, target: Path, source_root: Path
    ) -> None:
        install = _make_install_dict()
        report: list[str] = []
        inf.install_usage_component(target, source_root, install, report)

        manifest_path = target / inf.MANIFEST_PATH
        manifest = json.loads(manifest_path.read_text())
        manifest["installed_components"] = install["installed_components"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

        rc = inf.do_remove_component(target, "usage")
        assert rc == 0
        assert not (target / inf.COMPONENT_INSTALL_DIR).exists()

        manifest = json.loads(manifest_path.read_text())
        assert "usage" not in manifest.get("installed_components", {})

    def test_preserves_raw_evidence(
        self, target: Path, source_root: Path
    ) -> None:
        install = _make_install_dict()
        report: list[str] = []
        inf.install_usage_component(target, source_root, install, report)

        manifest_path = target / inf.MANIFEST_PATH
        manifest = json.loads(manifest_path.read_text())
        manifest["installed_components"] = install["installed_components"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

        inf.do_remove_component(target, "usage")

        evidence = target / ".agent-factory" / "usage" / "evidence.jsonl"
        assert evidence.exists()
        assert evidence.read_text() == '{"row": 1}\n'

    def test_remove_not_installed(self, target: Path) -> None:
        rc = inf.do_remove_component(target, "usage")
        assert rc == 0

    def test_remove_unknown_component(self, target: Path) -> None:
        rc = inf.do_remove_component(target, "bogus")
        assert rc == 1

    def test_remove_idempotent(
        self, target: Path, source_root: Path
    ) -> None:
        install = _make_install_dict()
        report: list[str] = []
        inf.install_usage_component(target, source_root, install, report)

        manifest_path = target / inf.MANIFEST_PATH
        manifest = json.loads(manifest_path.read_text())
        manifest["installed_components"] = install["installed_components"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

        assert inf.do_remove_component(target, "usage") == 0
        assert inf.do_remove_component(target, "usage") == 0


class TestReadComponentMeta:
    def test_reads_installed_meta(
        self, target: Path, source_root: Path
    ) -> None:
        install = _make_install_dict()
        report: list[str] = []
        inf.install_usage_component(target, source_root, install, report)

        meta = inf._read_component_meta(target)
        assert meta is not None
        assert meta["component"] == "usage"

    def test_returns_none_when_absent(self, target: Path) -> None:
        assert inf._read_component_meta(target) is None


class TestManifestInstalledComponents:
    def test_load_prior_preserves_components(
        self, target: Path, source_root: Path
    ) -> None:
        manifest_path = target / inf.MANIFEST_PATH
        manifest = json.loads(manifest_path.read_text())
        manifest["installed_components"] = {
            "usage": {"contract_version": "v1", "package_version": "0.1.0"}
        }
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

        install: dict = {
            "_target": target,
            "remove_paths": [],
            "merged_dirs": [],
            "orientation": {},
            "installed_components": {},
            "github_ignored_entries": set(),
            "codex_ignored_entries": set(),
            "agents_ignored_entries": set(),
            "copilot_generated_agents": set(),
            "codex_generated_agents": set(),
            "codex_hook_handlers": [],
        }
        report: list[str] = []
        inf.load_prior_manifest(target, install, report)
        assert "usage" in install["installed_components"]
        assert install["installed_components"]["usage"]["contract_version"] == "v1"
