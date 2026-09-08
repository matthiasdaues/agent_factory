"""Contract tests for update-factory script.

Focus: hook-regenerated files (currently INDEX.yaml) must be excluded from
checksum computation and modification detection, so a pre-commit hook
regenerating INDEX.yaml never forces a user through `--force`. The
exclusion list is shared with init-factory so a fresh install and a
later update agree on what counts as a checksummed path.
"""

from __future__ import annotations

import json
from pathlib import Path

from conftest import load_script

uf = load_script("update-factory")
inf = load_script("init-factory")


class TestHookRegeneratedPathsConstant:
    """Both scripts must declare and share the same exclusion list."""

    def test_update_factory_declares_constant(self):
        assert hasattr(uf, "HOOK_REGENERATED_PATHS")
        assert uf.HOOK_REGENERATED_PATHS

    def test_init_factory_declares_constant(self):
        assert hasattr(inf, "HOOK_REGENERATED_PATHS")
        assert inf.HOOK_REGENERATED_PATHS

    def test_constants_match_between_scripts(self):
        assert uf.HOOK_REGENERATED_PATHS == inf.HOOK_REGENERATED_PATHS


class TestShouldChecksumExcludesHookRegeneratedPaths:
    def test_update_factory_excludes_index_yaml(self):
        assert uf._should_checksum("INDEX.yaml") is False

    def test_update_factory_excludes_nested_index_yaml(self):
        assert uf._should_checksum("skills/init-factory/INDEX.yaml") is False

    def test_update_factory_still_checksums_other_files(self):
        assert uf._should_checksum("scripts/step-guard") is True
        assert uf._should_checksum("skills/tdd/SKILL.md") is True

    def test_init_factory_excludes_index_yaml(self):
        assert inf._should_checksum("INDEX.yaml") is False

    def test_init_factory_still_checksums_other_files(self):
        assert inf._should_checksum("scripts/step-guard") is True


class TestComputeChecksumsExcludesIndexYaml:
    def _make_factory(self, root: Path) -> Path:
        factory = root / "factory"
        factory.mkdir()
        (factory / "INDEX.yaml").write_text("agents: []\n")
        (factory / "scripts").mkdir()
        (factory / "scripts" / "step-guard").write_text("pass\n")
        return factory

    def test_update_factory_compute_checksums_skips_index_yaml(self, tmp_path):
        factory = self._make_factory(tmp_path)
        checksums = uf._compute_checksums(factory)
        assert "INDEX.yaml" not in checksums
        assert "scripts/step-guard" in checksums

    def test_init_factory_compute_checksums_skips_index_yaml(self, tmp_path):
        factory = self._make_factory(tmp_path)
        checksums = inf.compute_factory_checksums(factory)
        assert "INDEX.yaml" not in checksums
        assert "scripts/step-guard" in checksums


class TestDetectModificationsIgnoresIndexYamlChanges:
    """A hook-regenerated INDEX.yaml must never surface as a user change."""

    def _make_factory(self, root: Path) -> Path:
        factory = root / "factory"
        factory.mkdir()
        (factory / "INDEX.yaml").write_text("agents: []\n")
        (factory / "scripts").mkdir()
        (factory / "scripts" / "step-guard").write_text("pass\n")
        return factory

    def test_index_yaml_change_alone_is_not_detected(self, tmp_path):
        factory = self._make_factory(tmp_path)
        uf._write_checksums(tmp_path, factory)

        (factory / "INDEX.yaml").write_text("agents: [regenerated]\n")

        modified, added, removed = uf._detect_modifications(tmp_path)
        assert modified == []
        assert added == []
        assert removed == []

    def test_index_yaml_removal_is_not_detected(self, tmp_path):
        factory = self._make_factory(tmp_path)
        uf._write_checksums(tmp_path, factory)

        (factory / "INDEX.yaml").unlink()

        modified, added, removed = uf._detect_modifications(tmp_path)
        assert modified == []
        assert added == []
        assert removed == []

    def test_genuine_user_change_is_still_detected(self, tmp_path):
        factory = self._make_factory(tmp_path)
        uf._write_checksums(tmp_path, factory)

        (factory / "scripts" / "step-guard").write_text("changed\n")

        modified, _added, _removed = uf._detect_modifications(tmp_path)
        assert "scripts/step-guard" in modified


class TestMainSkipsForceGateForIndexYamlOnlyChanges:
    """update-factory's --force gate must not trip on a hook-regenerated
    INDEX.yaml. The gate itself is exercised via main(); the actual
    factory/ refresh (_run_init) is stubbed out since it shells out to a
    real init-factory checkout -- out of scope for this contract test."""

    def _install(self, target: Path, source: Path) -> Path:
        factory = target / "factory"
        factory.mkdir()
        (factory / "INDEX.yaml").write_text("agents: []\n")
        (factory / "scripts").mkdir()
        (factory / "scripts" / "step-guard").write_text("pass\n")
        uf._write_checksums(target, factory)

        manifest_path = target / uf.MANIFEST_PATH
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps({"factory_source": str(source)}), encoding="utf-8"
        )
        (source / "packages" / "factory").mkdir(parents=True)
        return factory

    def test_index_yaml_only_change_proceeds_without_force(
        self, tmp_path, monkeypatch
    ):
        target = tmp_path / "target"
        target.mkdir()
        source = tmp_path / "source"
        factory = self._install(target, source)

        # Simulate the pre-commit hook regenerating INDEX.yaml.
        (factory / "INDEX.yaml").write_text("agents: [regenerated]\n")

        calls: list[tuple[Path, Path]] = []
        monkeypatch.setattr(
            uf, "_run_init", lambda src, tgt: calls.append((src, tgt)) or 0
        )

        code = uf.main(["--target", str(target)])

        assert code == 0
        assert calls, "expected _run_init to run — the force gate must not block"

    def test_genuine_user_change_without_force_still_blocks(
        self, tmp_path, monkeypatch
    ):
        target = tmp_path / "target"
        target.mkdir()
        source = tmp_path / "source"
        factory = self._install(target, source)

        (factory / "scripts" / "step-guard").write_text("changed\n")

        calls: list[tuple[Path, Path]] = []
        monkeypatch.setattr(
            uf, "_run_init", lambda src, tgt: calls.append((src, tgt)) or 0
        )

        code = uf.main(["--target", str(target)])

        assert code == 2
        assert not calls, "a real user change must still require --force"
