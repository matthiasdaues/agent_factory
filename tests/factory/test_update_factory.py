"""Contract tests for update-factory script.

Focus: hook-regenerated files (currently INDEX.yaml) must be excluded from
checksum computation and modification detection, so a pre-commit hook
regenerating INDEX.yaml never forces a user through `--force`. The
exclusion list is shared with init-factory so a fresh install and a
later update agree on what counts as a checksummed path.

Also covers `--check` (ST-0284): reports installed/candidate versions,
source, digest, local modifications, and planned instruction header
changes without writing anything.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from conftest import load_script

uf = load_script("update-factory")
inf = load_script("init-factory")


# ---------------------------------------------------------------------------
# Check-mode fixtures
# ---------------------------------------------------------------------------


def _write_manifest(target: Path, **overrides) -> dict:
    manifest = {
        "factory_version": "1.0.0",
        "cli": "codex",
        "source_selector": "local",
        "orientation": {},
    }
    manifest.update(overrides)
    manifest_path = target / uf.MANIFEST_PATH
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def _make_installed_factory(target: Path) -> Path:
    """A minimal installed .agent-factory/factory/ tree with a checksum
    baseline, so _detect_modifications has something to compare against."""
    factory = target / ".agent-factory" / "factory"
    factory.mkdir(parents=True)
    (factory / "INDEX.yaml").write_text("agents: []\n")
    (factory / "scripts").mkdir()
    (factory / "scripts" / "step-guard").write_text("pass\n")
    uf._write_checksums(target, factory)
    return factory


def _make_local_source(root: Path, version: str = "1.0.0") -> Path:
    source = root / "source"
    (source / "packages" / "factory").mkdir(parents=True)
    (source / "packages" / "factory" / "VERSION").write_text(f"{version}\n")
    return source


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
        factory = root / ".agent-factory" / "factory"
        factory.mkdir(parents=True)
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
        factory = target / ".agent-factory" / "factory"
        factory.mkdir(parents=True)
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

    def test_index_yaml_only_change_proceeds_without_force(self, tmp_path, monkeypatch):
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


class TestCheckMissingManifest:
    def test_no_manifest_is_an_error(self, tmp_path, capsys):
        target = tmp_path / "target"
        target.mkdir()

        code = uf.main(["--target", str(target), "--check"])

        assert code == 1
        assert "install.json" in capsys.readouterr().err


class TestCheckReportsVersionsSourceAndDigest:
    """update-factory --check reports installed and candidate versions and
    the source, without writing (VFO-021)."""

    def test_local_candidate_newer_than_installed(self, tmp_path, capsys):
        target = tmp_path / "target"
        target.mkdir()
        _make_installed_factory(target)
        source = _make_local_source(tmp_path, version="1.1.0")
        _write_manifest(
            target, factory_version="1.0.0", source_selector="local",
            factory_source=str(source),
        )

        code = uf.main(["--target", str(target), "--check"])
        out = capsys.readouterr().out

        assert code == 0
        assert "Installed version:  1.0.0" in out
        assert "Candidate version:  1.1.0" in out
        assert str(source) in out

    def test_installed_and_candidate_versions_equal(self, tmp_path, capsys):
        target = tmp_path / "target"
        target.mkdir()
        _make_installed_factory(target)
        source = _make_local_source(tmp_path, version="1.0.0")
        _write_manifest(
            target, factory_version="1.0.0", source_selector="local",
            factory_source=str(source),
        )

        code = uf.main(["--target", str(target), "--check"])
        out = capsys.readouterr().out

        assert code == 0
        assert "Candidate version:  1.0.0" in out
        assert "equal" in out

    def test_source_override_takes_precedence_over_manifest(self, tmp_path, capsys):
        target = tmp_path / "target"
        target.mkdir()
        _make_installed_factory(target)
        manifest_source = _make_local_source(tmp_path / "manifest-source", version="1.0.0")
        override_source = _make_local_source(tmp_path / "override-source", version="2.0.0")
        _write_manifest(
            target, factory_version="1.0.0", source_selector="local",
            factory_source=str(manifest_source),
        )

        code = uf.main([
            "--target", str(target), "--check", "--source", str(override_source),
        ])
        out = capsys.readouterr().out

        assert code == 0
        assert "Candidate version:  2.0.0" in out
        assert str(override_source) in out

    def test_missing_local_source_reports_unavailable_candidate(self, tmp_path, capsys):
        target = tmp_path / "target"
        target.mkdir()
        _make_installed_factory(target)
        _write_manifest(
            target, factory_version="1.0.0", source_selector="local",
            factory_source=str(tmp_path / "does-not-exist"),
        )

        code = uf.main(["--target", str(target), "--check"])
        out = capsys.readouterr().out

        assert code == 0
        assert "Candidate version:  unavailable" in out


class TestCheckReportsLocalModifications:
    def test_no_modifications_reports_clean(self, tmp_path, capsys):
        target = tmp_path / "target"
        target.mkdir()
        _make_installed_factory(target)
        source = _make_local_source(tmp_path, version="1.0.0")
        _write_manifest(
            target, factory_version="1.0.0", source_selector="local",
            factory_source=str(source),
        )

        code = uf.main(["--target", str(target), "--check"])
        out = capsys.readouterr().out

        assert code == 0
        assert "No local modifications detected." in out

    def test_modified_file_is_listed(self, tmp_path, capsys):
        target = tmp_path / "target"
        target.mkdir()
        factory = _make_installed_factory(target)
        source = _make_local_source(tmp_path, version="1.0.0")
        _write_manifest(
            target, factory_version="1.0.0", source_selector="local",
            factory_source=str(source),
        )

        (factory / "scripts" / "step-guard").write_text("changed\n")

        code = uf.main(["--target", str(target), "--check"])
        out = capsys.readouterr().out

        assert code == 0
        assert "scripts/step-guard" in out

    def test_legacy_install_without_checksums_reports_unavailable(self, tmp_path, capsys):
        target = tmp_path / "target"
        target.mkdir()
        (target / ".agent-factory" / "factory").mkdir(parents=True)
        source = _make_local_source(tmp_path, version="1.0.0")
        _write_manifest(
            target, factory_version="1.0.0", source_selector="local",
            factory_source=str(source),
        )

        code = uf.main(["--target", str(target), "--check"])
        out = capsys.readouterr().out

        assert code == 0
        assert "cannot detect modifications" in out


class TestCheckReportsHeaderChanges:
    def test_new_instruction_file_is_reported_as_added(self, tmp_path, capsys):
        target = tmp_path / "target"
        target.mkdir()
        _make_installed_factory(target)
        source = _make_local_source(tmp_path, version="1.0.0")
        _write_manifest(
            target, factory_version="1.0.0", source_selector="local",
            factory_source=str(source), orientation={},
        )
        (target / "AGENTS.md").write_text("hello\n")

        code = uf.main(["--target", str(target), "--check"])
        out = capsys.readouterr().out

        assert code == 0
        assert "Planned instruction header changes:" in out
        assert "A  AGENTS.md" in out

    def test_deleted_instruction_file_is_reported_as_removed(self, tmp_path, capsys):
        target = tmp_path / "target"
        target.mkdir()
        _make_installed_factory(target)
        source = _make_local_source(tmp_path, version="1.0.0")
        _write_manifest(
            target, factory_version="1.0.0", source_selector="local",
            factory_source=str(source),
            orientation={"AGENTS.md": {"status": "injected", "block_digest": "abc"}},
        )
        # AGENTS.md is not created — it was removed since the last update.

        code = uf.main(["--target", str(target), "--check"])
        out = capsys.readouterr().out

        assert code == 0
        assert "D  AGENTS.md" in out

    def test_linked_orientation_entries_are_not_reported_as_removed(self, tmp_path, capsys):
        """Only 'injected' entries are header content — 'linked' entries are
        symlink bookkeeping and must not be treated as missing headers."""
        target = tmp_path / "target"
        target.mkdir()
        _make_installed_factory(target)
        source = _make_local_source(tmp_path, version="1.0.0")
        _write_manifest(
            target, factory_version="1.0.0", source_selector="local",
            factory_source=str(source),
            orientation={".claude/CLAUDE.md": {"status": "linked"}},
        )

        code = uf.main(["--target", str(target), "--check"])
        out = capsys.readouterr().out

        assert code == 0
        assert "No planned instruction header changes." in out

    def test_content_change_detected_against_local_candidate(self, tmp_path, capsys):
        target = tmp_path / "target"
        target.mkdir()
        _make_installed_factory(target)
        source = _make_local_source(tmp_path, version="1.0.0")
        (source / "packages" / "factory" / "config").mkdir()
        (source / "packages" / "factory" / "config" / "AGENTS.codex.md").write_text(
            "new instructions\n"
        )

        old_block = (
            f"{uf.ORIENTATION_BEGIN}\nold instructions\n{uf.ORIENTATION_END}\n"
        )
        old_digest = hashlib.sha256(old_block.encode("utf-8")).hexdigest()

        _write_manifest(
            target, factory_version="1.0.0", source_selector="local",
            factory_source=str(source), cli="codex",
            orientation={
                "AGENTS.md": {"status": "injected", "block_digest": old_digest},
            },
        )
        (target / "AGENTS.md").write_text("project instructions\n")

        code = uf.main(["--target", str(target), "--check"])
        out = capsys.readouterr().out

        assert code == 0
        assert "M  AGENTS.md" in out

    def test_no_content_diff_for_remote_candidate(self, tmp_path, capsys, monkeypatch):
        """A remote candidate's header content is not diffed — that would
        require downloading the archive, which --check must not do."""
        target = tmp_path / "target"
        target.mkdir()
        _make_installed_factory(target)
        monkeypatch.setattr(
            uf, "_resolve_remote_candidate",
            lambda resolved_source, timeout=uf.REMOTE_TIMEOUT: (
                None, "1.1.0", "https://example.com/releases/1.1.0/", "deadbeef"
            ),
        )
        _write_manifest(
            target, factory_version="1.0.0", source_selector="remote",
            resolved_source="https://example.com/releases/1.0.0/", cli="codex",
            orientation={
                "AGENTS.md": {"status": "injected", "block_digest": "anything"},
            },
        )
        (target / "AGENTS.md").write_text("project instructions\n")

        code = uf.main(["--target", str(target), "--check"])
        out = capsys.readouterr().out

        assert code == 0
        assert "No planned instruction header changes." in out


class TestCheckResolvesRemoteCandidate:
    def test_reports_remote_version_source_and_digest(self, tmp_path, capsys, monkeypatch):
        target = tmp_path / "target"
        target.mkdir()
        _make_installed_factory(target)
        monkeypatch.setattr(
            uf, "_resolve_remote_candidate",
            lambda resolved_source, timeout=uf.REMOTE_TIMEOUT: (
                None, "1.2.0", "https://example.com/releases/1.2.0/", "deadbeef"
            ),
        )
        _write_manifest(
            target, factory_version="1.0.0", source_selector="remote",
            resolved_source="https://example.com/releases/1.1.0/",
        )

        code = uf.main(["--target", str(target), "--check"])
        out = capsys.readouterr().out

        assert code == 0
        assert "Candidate version:  1.2.0" in out
        assert "https://example.com/releases/1.2.0/" in out
        assert "Candidate digest:   deadbeef" in out

    def test_resolution_error_reports_unavailable_without_raising(
        self, tmp_path, capsys, monkeypatch
    ):
        target = tmp_path / "target"
        target.mkdir()
        _make_installed_factory(target)
        monkeypatch.setattr(
            uf, "_resolve_remote_candidate",
            lambda resolved_source, timeout=uf.REMOTE_TIMEOUT: (
                "network unreachable", None, None, None
            ),
        )
        _write_manifest(
            target, factory_version="1.0.0", source_selector="remote",
            resolved_source="https://example.com/releases/1.1.0/",
        )

        code = uf.main(["--target", str(target), "--check"])
        out = capsys.readouterr().out

        assert code == 0
        assert "Candidate version:  unavailable (network unreachable)" in out

    def test_derive_remote_base_url_strips_release_segment(self):
        assert uf._derive_remote_base_url(
            "https://example.com/dist/releases/1.1.0/"
        ) == "https://example.com/dist"

    def test_derive_remote_base_url_returns_none_for_unrecognized_shape(self):
        assert uf._derive_remote_base_url("https://example.com/dist/") is None

    def test_resolve_remote_candidate_composes_resolution_and_digest(
        self, monkeypatch
    ):
        monkeypatch.setattr(
            uf, "_resolve_release_base_url",
            lambda base_url, timeout=uf.REMOTE_TIMEOUT: (
                None, "https://example.com/releases/1.2.0/"
            ),
        )
        monkeypatch.setattr(
            uf, "_fetch_candidate_digest",
            lambda resolved_url, timeout=uf.REMOTE_TIMEOUT: (None, "deadbeef"),
        )

        error, version, resolved_url, digest = uf._resolve_remote_candidate(
            "https://example.com/releases/1.1.0/"
        )

        assert error is None
        assert version == "1.2.0"
        assert resolved_url == "https://example.com/releases/1.2.0/"
        assert digest == "deadbeef"


class TestCheckPerformsNoWrites:
    """VFO-021: --check creates no files, directories, staging areas, or
    manifest updates."""

    def test_no_filesystem_changes_after_check(self, tmp_path, capsys, monkeypatch):
        target = tmp_path / "target"
        target.mkdir()
        _make_installed_factory(target)
        source = _make_local_source(tmp_path, version="1.1.0")
        _write_manifest(
            target, factory_version="1.0.0", source_selector="local",
            factory_source=str(source),
        )

        manifest_path = target / uf.MANIFEST_PATH
        checksums_path = target / uf.CHECKSUMS_PATH
        manifest_before = manifest_path.read_bytes()
        checksums_before = checksums_path.read_bytes()
        tree_before = sorted(
            p.relative_to(target).as_posix() for p in target.rglob("*")
        )

        def _fail_if_called(*_a, **_kw):
            raise AssertionError("--check must never invoke _run_init")

        monkeypatch.setattr(uf, "_run_init", _fail_if_called)

        code = uf.main(["--target", str(target), "--check"])
        capsys.readouterr()

        assert code == 0
        assert manifest_path.read_bytes() == manifest_before
        assert checksums_path.read_bytes() == checksums_before
        tree_after = sorted(
            p.relative_to(target).as_posix() for p in target.rglob("*")
        )
        assert tree_after == tree_before
