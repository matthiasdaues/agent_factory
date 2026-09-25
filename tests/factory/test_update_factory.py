"""Contract tests for update-factory script.

Focus: hook-regenerated files (currently INDEX.yaml) must be excluded from
checksum computation and modification detection, so a pre-commit hook
regenerating INDEX.yaml never forces a user through `--force`. The
exclusion list is shared with init-factory so a fresh install and a
later update agree on what counts as a checksummed path.

Also covers `--check` (ST-0284): reports installed/candidate versions,
source, digest, local modifications, and planned instruction header
changes without writing anything.

ST-0285 extends this with the ADR-0023 seven-step transaction: approval,
download-and-verify, staging, application, rollback, and the receipt.
"""

from __future__ import annotations

import hashlib
import io
import json
import tarfile
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


def _make_candidate_source(root: Path, version: str = "1.1.0") -> Path:
    """A local candidate source tree with a marker file distinct from the
    installed factory/, so a real staged swap is observable."""
    source = root / "candidate-source"
    factory = source / "packages" / "factory"
    factory.mkdir(parents=True)
    (factory / "VERSION").write_text(f"{version}\n")
    (factory / "MARKER").write_text("candidate\n")
    (factory / "scripts").mkdir()
    (factory / "scripts" / "step-guard").write_text("candidate pass\n")
    return source


def _make_archive_bytes(files: dict[str, str]) -> bytes:
    """Build an in-memory tar.gz whose members are the given relative
    path -> content pairs, matching the release archive layout (paths
    relative to the factory/ root, not prefixed with packages/factory/)."""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tf:
        for rel, content in files.items():
            data = content.encode("utf-8")
            info = tarfile.TarInfo(name=rel)
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))
    return buf.getvalue()


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
        monkeypatch.setattr(uf, "get_update_consent", lambda *a, **kw: True)

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


# ---------------------------------------------------------------------------
# ST-0285: approval, download/verify, staging, application, and rollback
# ---------------------------------------------------------------------------


class TestGetUpdateConsent:
    """Blank, declined, or cancelled input is never treated as consent."""

    def test_blank_input_is_not_consent(self):
        assert uf.get_update_consent(input_func=lambda _: "") is False

    def test_declining_input_is_not_consent(self):
        assert uf.get_update_consent(input_func=lambda _: "no") is False

    def test_yes_is_consent(self):
        assert uf.get_update_consent(input_func=lambda _: "yes") is True

    def test_eof_is_not_consent(self):
        def _raise(_):
            raise EOFError

        assert uf.get_update_consent(input_func=_raise) is False


class TestApprovalGate:
    """A normal update requires affirmative consent before any download or
    mutation (VFO-023 approval step); blank input stops with no changes."""

    def test_declined_consent_makes_no_changes(self, tmp_path, capsys, monkeypatch):
        target = tmp_path / "target"
        target.mkdir()
        factory = _make_installed_factory(target)
        source = _make_candidate_source(tmp_path)
        _write_manifest(
            target, factory_version="1.0.0", source_selector="local",
            factory_source=str(source),
        )

        manifest_before = (target / uf.MANIFEST_PATH).read_bytes()
        tree_before = sorted(
            p.relative_to(target).as_posix() for p in target.rglob("*")
        )

        monkeypatch.setattr(uf, "get_update_consent", lambda *a, **kw: False)

        def _fail_if_called(*_a, **_kw):
            raise AssertionError("declined consent must never invoke _run_init")

        monkeypatch.setattr(uf, "_run_init", _fail_if_called)

        code = uf.main(["--target", str(target)])
        capsys.readouterr()

        assert code != 0
        assert (target / uf.MANIFEST_PATH).read_bytes() == manifest_before
        tree_after = sorted(
            p.relative_to(target).as_posix() for p in target.rglob("*")
        )
        assert tree_after == tree_before
        assert (factory / "MARKER").exists() is False


class TestStageFactoryTree:
    """Staging places the verified replacement alongside the current
    installation without touching it (ADR-0023 step 4)."""

    def test_staging_copies_candidate_without_touching_live_tree(self, tmp_path):
        target = tmp_path / "target"
        target.mkdir()
        factory = _make_installed_factory(target)
        source = _make_candidate_source(tmp_path)
        source_factory = source / "packages" / "factory"

        staging_dir = uf._stage_factory_tree(target, source_factory)

        assert staging_dir.parent == target / ".agent-factory"
        assert staging_dir.name.startswith(uf.STAGING_DIR_PREFIX)
        assert (staging_dir / "MARKER").read_text() == "candidate\n"
        # The live installation is untouched.
        assert (factory / "MARKER").exists() is False
        assert (factory / "INDEX.yaml").is_file()


class TestRemoteVerificationBeforeStaging:
    """VFO-022: a remote update verifies the archive digest before any
    extraction or staging; a mismatch aborts with no changes."""

    def _write_remote_manifest(self, target: Path, resolved_source: str) -> None:
        _write_manifest(
            target, factory_version="1.0.0", source_selector="remote",
            resolved_source=resolved_source,
        )

    def test_digest_mismatch_aborts_without_changes(
        self, tmp_path, capsys, monkeypatch
    ):
        target = tmp_path / "target"
        target.mkdir()
        _make_installed_factory(target)
        self._write_remote_manifest(
            target, "https://example.com/releases/1.0.0/",
        )

        monkeypatch.setattr(
            uf, "_resolve_remote_candidate",
            lambda resolved_source, timeout=uf.REMOTE_TIMEOUT: (
                None, "1.1.0", "https://example.com/releases/1.1.0/", "deadbeef"
            ),
        )
        monkeypatch.setattr(uf, "get_update_consent", lambda *a, **kw: True)
        monkeypatch.setattr(
            uf, "_download_and_verify_archive",
            lambda url, timeout=uf.REMOTE_TIMEOUT: (
                "digest mismatch", None, None,
            ),
        )

        def _fail_if_called(*_a, **_kw):
            raise AssertionError("a digest mismatch must never reach _run_init")

        monkeypatch.setattr(uf, "_run_init", _fail_if_called)

        manifest_before = (target / uf.MANIFEST_PATH).read_bytes()

        code = uf.main(["--target", str(target)])
        capsys.readouterr()

        assert code != 0
        assert (target / uf.MANIFEST_PATH).read_bytes() == manifest_before
        remote_scratch = list(
            (target / ".agent-factory").glob(f"{uf.REMOTE_SCRATCH_PREFIX}*")
        )
        assert remote_scratch == []

    def test_verified_archive_is_extracted_and_applied(
        self, tmp_path, capsys, monkeypatch
    ):
        target = tmp_path / "target"
        target.mkdir()
        _make_installed_factory(target)
        self._write_remote_manifest(
            target, "https://example.com/releases/1.0.0/",
        )

        archive_bytes = _make_archive_bytes({
            "VERSION": "1.1.0\n",
            "MARKER": "remote-candidate\n",
        })

        monkeypatch.setattr(
            uf, "_resolve_remote_candidate",
            lambda resolved_source, timeout=uf.REMOTE_TIMEOUT: (
                None, "1.1.0", "https://example.com/releases/1.1.0/", "deadbeef"
            ),
        )
        monkeypatch.setattr(uf, "get_update_consent", lambda *a, **kw: True)
        monkeypatch.setattr(
            uf, "_download_and_verify_archive",
            lambda url, timeout=uf.REMOTE_TIMEOUT: (
                None, archive_bytes, "deadbeef",
            ),
        )
        monkeypatch.setattr(uf, "_run_init", lambda src, tgt: 0)

        code = uf.main(["--target", str(target)])
        out = capsys.readouterr().out

        assert code == 0
        target_factory = target / ".agent-factory" / "factory"
        assert (target_factory / "MARKER").read_text() == "remote-candidate\n"
        assert "deadbeef" in out
        manifest = json.loads((target / uf.MANIFEST_PATH).read_text())
        assert manifest["factory_version"] == "1.1.0"
        assert manifest["archive_sha256"] == "deadbeef"
        # The remote extraction scratch directory is cleaned up.
        assert list(
            (target / ".agent-factory").glob(f"{uf.REMOTE_SCRATCH_PREFIX}*")
        ) == []


class TestApplicationAndRollback:
    """VFO-05-IT-02: application failure restores the previous Factory
    tree, manifest, and checksums exactly."""

    def _install(self, target: Path) -> Path:
        return _make_installed_factory(target)

    def test_successful_update_swaps_staged_tree_into_place(
        self, tmp_path, capsys, monkeypatch
    ):
        target = tmp_path / "target"
        target.mkdir()
        self._install(target)
        source = _make_candidate_source(tmp_path)
        _write_manifest(
            target, factory_version="1.0.0", source_selector="local",
            factory_source=str(source),
        )

        monkeypatch.setattr(uf, "get_update_consent", lambda *a, **kw: True)
        monkeypatch.setattr(uf, "_run_init", lambda src, tgt: 0)

        code = uf.main(["--target", str(target)])
        out = capsys.readouterr().out

        assert code == 0
        target_factory = target / ".agent-factory" / "factory"
        assert (target_factory / "MARKER").read_text() == "candidate\n"
        assert "Update Receipt" in out
        assert ".agent-factory/factory/" in out
        # No leftover staging or backup directories.
        leftovers = list((target / ".agent-factory").glob(f"{uf.STAGING_DIR_PREFIX}*"))
        leftovers += list((target / ".agent-factory").glob(f"{uf.BACKUP_DIR_PREFIX}*"))
        assert leftovers == []

    def test_run_init_failure_restores_previous_tree_manifest_and_checksums(
        self, tmp_path, capsys, monkeypatch
    ):
        target = tmp_path / "target"
        target.mkdir()
        self._install(target)
        source = _make_candidate_source(tmp_path)
        _write_manifest(
            target, factory_version="1.0.0", source_selector="local",
            factory_source=str(source),
        )

        manifest_before = (target / uf.MANIFEST_PATH).read_bytes()
        checksums_before = (target / uf.CHECKSUMS_PATH).read_bytes()

        monkeypatch.setattr(uf, "get_update_consent", lambda *a, **kw: True)
        monkeypatch.setattr(uf, "_run_init", lambda src, tgt: 1)

        code = uf.main(["--target", str(target)])
        out_err = capsys.readouterr().err

        assert code != 0
        assert "restored" in out_err.lower()
        target_factory = target / ".agent-factory" / "factory"
        # The previous tree is back — the candidate marker is absent, the
        # original installed content is present again.
        assert (target_factory / "MARKER").exists() is False
        assert (target_factory / "INDEX.yaml").read_text() == "agents: []\n"
        assert (target / uf.MANIFEST_PATH).read_bytes() == manifest_before
        assert (target / uf.CHECKSUMS_PATH).read_bytes() == checksums_before
        leftovers = list((target / ".agent-factory").glob(f"{uf.STAGING_DIR_PREFIX}*"))
        leftovers += list((target / ".agent-factory").glob(f"{uf.BACKUP_DIR_PREFIX}*"))
        assert leftovers == []

    def test_exception_during_application_also_rolls_back(
        self, tmp_path, monkeypatch
    ):
        target = tmp_path / "target"
        target.mkdir()
        self._install(target)
        source = _make_candidate_source(tmp_path)
        _write_manifest(
            target, factory_version="1.0.0", source_selector="local",
            factory_source=str(source),
        )

        manifest_before = (target / uf.MANIFEST_PATH).read_bytes()

        monkeypatch.setattr(uf, "get_update_consent", lambda *a, **kw: True)

        def _boom(*_a, **_kw):
            raise RuntimeError("boom")

        monkeypatch.setattr(uf, "_apply_header_changes", _boom)

        code = uf.main(["--target", str(target)])

        assert code != 0
        target_factory = target / ".agent-factory" / "factory"
        assert (target_factory / "MARKER").exists() is False
        assert (target / uf.MANIFEST_PATH).read_bytes() == manifest_before


class TestForceReceipt:
    """VFO-024/VFO-025: --force preserves modified files and the receipt
    records the preservation path and the preserved files."""

    def test_force_preserves_modified_files_and_receipt_records_them(
        self, tmp_path, capsys, monkeypatch
    ):
        target = tmp_path / "target"
        target.mkdir()
        factory = _make_installed_factory(target)
        source = _make_candidate_source(tmp_path)
        _write_manifest(
            target, factory_version="1.0.0", source_selector="local",
            factory_source=str(source),
        )

        (factory / "scripts" / "step-guard").write_text("user-modified\n")

        monkeypatch.setattr(uf, "get_update_consent", lambda *a, **kw: True)
        monkeypatch.setattr(uf, "_run_init", lambda src, tgt: 0)

        code = uf.main(["--target", str(target), "--force"])
        out = capsys.readouterr().out

        assert code == 0
        assert "Preserved user changes" in out
        assert "scripts/step-guard" in out
        preserved_root = target / uf.USER_CHANGES_DIR
        preserved_files = list(preserved_root.rglob("step-guard"))
        assert len(preserved_files) == 1
        assert preserved_files[0].read_text() == "user-modified\n"


class TestHeaderApplyAndRollback:
    """Instruction headers are updated during application and restored
    exactly on rollback (ADR-0023 staging includes header edits)."""

    def _setup(self, tmp_path):
        target = tmp_path / "target"
        target.mkdir()
        _make_installed_factory(target)
        source = _make_candidate_source(tmp_path)
        (source / "packages" / "factory" / "config").mkdir()
        (source / "packages" / "factory" / "config" / "AGENTS.codex.md").write_text(
            "new instructions\n"
        )

        old_block = f"{uf.ORIENTATION_BEGIN}\nold instructions\n{uf.ORIENTATION_END}\n"
        old_digest = hashlib.sha256(old_block.encode("utf-8")).hexdigest()
        original_content = old_block + "\nproject instructions\n"
        (target / "AGENTS.md").write_text(original_content)

        _write_manifest(
            target, factory_version="1.0.0", source_selector="local",
            factory_source=str(source), cli="codex",
            orientation={
                "AGENTS.md": {"status": "injected", "block_digest": old_digest},
            },
        )
        return target, source, original_content

    def test_changed_header_is_updated_on_successful_apply(
        self, tmp_path, capsys, monkeypatch
    ):
        target, _source, _original = self._setup(tmp_path)

        monkeypatch.setattr(uf, "get_update_consent", lambda *a, **kw: True)
        monkeypatch.setattr(uf, "_run_init", lambda src, tgt: 0)

        code = uf.main(["--target", str(target)])
        out = capsys.readouterr().out

        assert code == 0
        updated = (target / "AGENTS.md").read_text()
        assert "new instructions" in updated
        assert "old instructions" not in updated
        assert "project instructions" in updated
        assert "AGENTS.md" in out
        manifest = json.loads((target / uf.MANIFEST_PATH).read_text())
        assert manifest["orientation"]["AGENTS.md"]["block_digest"] != hashlib.sha256(
            f"{uf.ORIENTATION_BEGIN}\nold instructions\n{uf.ORIENTATION_END}\n".encode()
        ).hexdigest()

    def test_header_change_is_restored_on_rollback(self, tmp_path, monkeypatch):
        target, _source, original_content = self._setup(tmp_path)

        monkeypatch.setattr(uf, "get_update_consent", lambda *a, **kw: True)
        monkeypatch.setattr(uf, "_run_init", lambda src, tgt: 1)

        code = uf.main(["--target", str(target)])

        assert code != 0
        assert (target / "AGENTS.md").read_text() == original_content


# ---------------------------------------------------------------------------
# ST-0286: source-boundary consent for --from-remote / --from-local
# ---------------------------------------------------------------------------


def _write_remote_manifest(
    target: Path, resolved_source: str = "https://releases.example.com/releases/1.0.0/",
) -> dict:
    return _write_manifest(
        target, factory_version="1.0.0", source_selector="remote",
        resolved_source=resolved_source,
    )


class TestDetectSourceBoundaryChange:
    """VFO-005: a boundary change is a source-kind flip or a different
    remote base URL. A different local path under the same "local" kind
    is not a boundary change — that is the pre-existing --source override."""

    def test_no_flags_given_returns_none(self):
        manifest = {"source_selector": "local", "factory_source": "/a/b"}
        assert uf._detect_source_boundary_change(manifest, None, None) is None

    def test_remote_to_local_kind_change_is_a_boundary(self, tmp_path):
        manifest = {
            "source_selector": "remote",
            "resolved_source": "https://releases.example.com/releases/1.0.0/",
        }
        changed, current_desc, requested_desc = uf._detect_source_boundary_change(
            manifest, None, tmp_path / "factory-src",
        )
        assert changed is True
        assert current_desc.startswith("remote `https://releases.example.com`")
        assert requested_desc.startswith("local `")

    def test_local_to_remote_kind_change_is_a_boundary(self):
        manifest = {"source_selector": "local", "factory_source": "/checkout"}
        changed, current_desc, requested_desc = uf._detect_source_boundary_change(
            manifest, "https://other.example.com", None,
        )
        assert changed is True
        assert current_desc == "local `/checkout`"
        assert requested_desc == "remote `https://other.example.com`"

    def test_same_remote_url_is_not_a_boundary(self):
        manifest = {
            "source_selector": "remote",
            "resolved_source": "https://releases.example.com/releases/1.0.0/",
        }
        changed, _current, _requested = uf._detect_source_boundary_change(
            manifest, "https://releases.example.com", None,
        )
        assert changed is False

    def test_different_remote_url_is_a_boundary(self):
        manifest = {
            "source_selector": "remote",
            "resolved_source": "https://releases.example.com/releases/1.0.0/",
        }
        changed, _current, requested_desc = uf._detect_source_boundary_change(
            manifest, "https://other.example.com", None,
        )
        assert changed is True
        assert requested_desc == "remote `https://other.example.com`"

    def test_different_local_path_same_kind_is_not_a_boundary(self, tmp_path):
        source = tmp_path / "checkout"
        manifest = {"source_selector": "local", "factory_source": str(source)}
        other = tmp_path / "other-checkout"
        changed, _current, _requested = uf._detect_source_boundary_change(
            manifest, None, other,
        )
        assert changed is False


class TestGetSourceBoundaryConsent:
    """Blank, declined, or cancelled input is never treated as consent."""

    def test_blank_input_is_not_consent(self):
        assert uf.get_source_boundary_consent("msg", input_func=lambda _: "") is False

    def test_declining_input_is_not_consent(self):
        assert uf.get_source_boundary_consent(
            "msg", input_func=lambda _: "no",
        ) is False

    def test_yes_is_consent(self):
        assert uf.get_source_boundary_consent(
            "msg", input_func=lambda _: "yes",
        ) is True

    def test_eof_is_not_consent(self):
        def _raise(_):
            raise EOFError

        assert uf.get_source_boundary_consent("msg", input_func=_raise) is False


class TestSourceBoundaryConsentInMain:
    """The source-boundary prompt is separate from the normal update
    approval; both must pass, and --force never bypasses source consent."""

    def test_from_remote_new_url_triggers_prompt_and_proceeds(
        self, tmp_path, capsys, monkeypatch
    ):
        target = tmp_path / "target"
        target.mkdir()
        _make_installed_factory(target)
        _write_remote_manifest(target)

        archive_bytes = _make_archive_bytes({"VERSION": "2.0.0\n", "MARKER": "other\n"})

        monkeypatch.setattr(
            uf, "_resolve_release_base_url",
            lambda base_url, timeout=uf.REMOTE_TIMEOUT: (
                None, "https://other.example.com/releases/2.0.0/"
            ),
        )
        monkeypatch.setattr(
            uf, "_fetch_candidate_digest",
            lambda url, timeout=uf.REMOTE_TIMEOUT: (None, "cafebabe"),
        )
        monkeypatch.setattr(
            uf, "_download_and_verify_archive",
            lambda url, timeout=uf.REMOTE_TIMEOUT: (None, archive_bytes, "cafebabe"),
        )
        monkeypatch.setattr(uf, "_run_init", lambda src, tgt: 0)
        seen_messages: list[str] = []
        monkeypatch.setattr(
            uf, "get_source_boundary_consent",
            lambda message, *a, **kw: seen_messages.append(message) or True,
        )
        monkeypatch.setattr(uf, "get_update_consent", lambda *a, **kw: True)

        code = uf.main([
            "--target", str(target), "--from-remote", "https://other.example.com",
        ])
        capsys.readouterr()

        assert code == 0
        assert len(seen_messages) == 1
        assert "Current source: remote `https://releases.example.com`" in seen_messages[0]
        assert "Requested source: remote `https://other.example.com`" in seen_messages[0]
        manifest = json.loads((target / uf.MANIFEST_PATH).read_text())
        assert manifest["source_selector"] == "remote"
        assert manifest["resolved_source"] == "https://other.example.com/releases/2.0.0/"

    def test_from_remote_same_url_skips_boundary_prompt(
        self, tmp_path, capsys, monkeypatch
    ):
        target = tmp_path / "target"
        target.mkdir()
        _make_installed_factory(target)
        _write_remote_manifest(target)

        calls: list[str] = []
        monkeypatch.setattr(
            uf, "get_source_boundary_consent",
            lambda *a, **kw: calls.append("called") or True,
        )
        monkeypatch.setattr(
            uf, "_resolve_release_base_url",
            lambda base_url, timeout=uf.REMOTE_TIMEOUT: (
                None, "https://releases.example.com/releases/1.0.0/"
            ),
        )
        monkeypatch.setattr(
            uf, "_fetch_candidate_digest",
            lambda url, timeout=uf.REMOTE_TIMEOUT: (None, "deadbeef"),
        )
        monkeypatch.setattr(
            uf, "_download_and_verify_archive",
            lambda url, timeout=uf.REMOTE_TIMEOUT: (
                None, _make_archive_bytes({"VERSION": "1.0.0\n"}), "deadbeef",
            ),
        )
        monkeypatch.setattr(uf, "_run_init", lambda src, tgt: 0)
        monkeypatch.setattr(uf, "get_update_consent", lambda *a, **kw: True)

        code = uf.main([
            "--target", str(target), "--from-remote", "https://releases.example.com",
        ])
        capsys.readouterr()

        assert code == 0
        assert calls == []

    def test_declined_source_boundary_consent_stops_without_changes(
        self, tmp_path, capsys, monkeypatch
    ):
        target = tmp_path / "target"
        target.mkdir()
        _make_installed_factory(target)
        _write_remote_manifest(target)
        manifest_before = (target / uf.MANIFEST_PATH).read_bytes()

        monkeypatch.setattr(uf, "get_source_boundary_consent", lambda *a, **kw: False)

        def _fail_if_called(*_a, **_kw):
            raise AssertionError("declined source consent must never reach _run_init")

        monkeypatch.setattr(uf, "_run_init", _fail_if_called)

        code = uf.main([
            "--target", str(target), "--from-remote", "https://other.example.com",
        ])
        capsys.readouterr()

        assert code != 0
        assert (target / uf.MANIFEST_PATH).read_bytes() == manifest_before

    def test_force_does_not_bypass_source_boundary_consent(
        self, tmp_path, capsys, monkeypatch
    ):
        target = tmp_path / "target"
        target.mkdir()
        _make_installed_factory(target)
        _write_remote_manifest(target)

        monkeypatch.setattr(uf, "get_source_boundary_consent", lambda *a, **kw: False)

        def _fail_if_called(*_a, **_kw):
            raise AssertionError("--force must not bypass source-boundary consent")

        monkeypatch.setattr(uf, "_run_init", _fail_if_called)

        code = uf.main([
            "--target", str(target), "--from-remote", "https://other.example.com",
            "--force",
        ])
        capsys.readouterr()

        assert code != 0

    def test_from_local_kind_change_triggers_prompt_and_proceeds(
        self, tmp_path, capsys, monkeypatch
    ):
        target = tmp_path / "target"
        target.mkdir()
        _make_installed_factory(target)
        _write_remote_manifest(target)
        source = _make_candidate_source(tmp_path)

        seen_messages: list[str] = []
        monkeypatch.setattr(
            uf, "get_source_boundary_consent",
            lambda message, *a, **kw: seen_messages.append(message) or True,
        )
        monkeypatch.setattr(uf, "get_update_consent", lambda *a, **kw: True)
        monkeypatch.setattr(uf, "_run_init", lambda src, tgt: 0)

        code = uf.main(["--target", str(target), "--from-local", str(source)])
        capsys.readouterr()

        assert code == 0
        assert len(seen_messages) == 1
        assert "Current source: remote" in seen_messages[0]
        assert "Requested source: local" in seen_messages[0]
        manifest = json.loads((target / uf.MANIFEST_PATH).read_text())
        assert manifest["source_selector"] == "local"
        assert manifest["factory_source"] == str(source.resolve())
        target_factory = target / ".agent-factory" / "factory"
        assert (target_factory / "MARKER").read_text() == "candidate\n"


class TestCheckReportsSourceBoundary:
    """--check reports a detected source-boundary change as information,
    without prompting (VFO-021: check performs no writes and no prompts)."""

    def test_check_reports_detected_source_change(self, tmp_path, capsys, monkeypatch):
        target = tmp_path / "target"
        target.mkdir()
        _make_installed_factory(target)
        _write_remote_manifest(target)

        calls: list[str] = []
        monkeypatch.setattr(
            uf, "get_source_boundary_consent",
            lambda *a, **kw: calls.append("called") or True,
        )
        monkeypatch.setattr(
            uf, "_resolve_remote_candidate",
            lambda resolved_source, timeout=uf.REMOTE_TIMEOUT: (
                None, "1.0.0", "https://releases.example.com/releases/1.0.0/", "deadbeef"
            ),
        )

        code = uf.main([
            "--target", str(target), "--check",
            "--from-remote", "https://other.example.com",
        ])
        out = capsys.readouterr().out

        assert code == 0
        assert calls == []
        assert "Source change detected: current remote" in out
        assert "requested remote `https://other.example.com`" in out
        assert "separate source-boundary consent" in out

    def test_check_same_source_reports_no_boundary_change(
        self, tmp_path, capsys, monkeypatch
    ):
        target = tmp_path / "target"
        target.mkdir()
        _make_installed_factory(target)
        _write_remote_manifest(target)

        monkeypatch.setattr(
            uf, "_resolve_remote_candidate",
            lambda resolved_source, timeout=uf.REMOTE_TIMEOUT: (
                None, "1.0.0", "https://releases.example.com/releases/1.0.0/", "deadbeef"
            ),
        )

        code = uf.main([
            "--target", str(target), "--check",
            "--from-remote", "https://releases.example.com",
        ])
        out = capsys.readouterr().out

        assert code == 0
        assert "Source change detected" not in out

    def test_check_without_from_flags_reports_nothing_extra(
        self, tmp_path, capsys, monkeypatch
    ):
        target = tmp_path / "target"
        target.mkdir()
        _make_installed_factory(target)
        _write_remote_manifest(target)

        monkeypatch.setattr(
            uf, "_resolve_remote_candidate",
            lambda resolved_source, timeout=uf.REMOTE_TIMEOUT: (
                None, "1.0.0", "https://releases.example.com/releases/1.0.0/", "deadbeef"
            ),
        )

        code = uf.main(["--target", str(target), "--check"])
        out = capsys.readouterr().out

        assert code == 0
        assert "Source change detected" not in out


class TestMutuallyExclusiveFromFlags:
    def test_from_remote_and_from_local_together_is_an_error(self, tmp_path):
        target = tmp_path / "target"
        target.mkdir()

        try:
            uf.main([
                "--target", str(target),
                "--from-remote", "https://other.example.com",
                "--from-local", str(tmp_path / "src"),
            ])
        except SystemExit as exc:
            assert exc.code != 0
        else:
            raise AssertionError("expected argparse to reject both flags together")
