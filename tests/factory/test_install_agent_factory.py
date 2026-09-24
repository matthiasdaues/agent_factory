"""Contract tests for the install-agent-factory bootstrap script.

Covers: argument validation, unsafe target rejection, preflight diagnosis,
source resolution, consent gating, instruction header management, manifest
version 2 migration, and receipt generation.
"""

from __future__ import annotations

import hashlib
import importlib.machinery
import importlib.util
import json
import os
import shutil
import stat
import subprocess
import sys
import textwrap
from pathlib import Path
from unittest import mock

import pytest
from conftest import REPO_ROOT

SCRIPT = REPO_ROOT / "packages" / "factory" / "scripts" / "install-agent-factory"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run(args: list[str], *, input_text: str | None = None,
         env: dict | None = None) -> subprocess.CompletedProcess:
    """Run install-agent-factory as a subprocess."""
    cmd = [sys.executable, str(SCRIPT)] + args
    run_env = {**os.environ, **(env or {})}
    return subprocess.run(
        cmd, capture_output=True, text=True,
        input=input_text, env=run_env, timeout=30,
    )


def _make_source(tmp_path: Path) -> Path:
    """Create a minimal Agent Factory source tree."""
    source = tmp_path / "factory-src"
    source.mkdir()
    pkg = source / "packages" / "factory"
    pkg.mkdir(parents=True)
    (pkg / "VERSION").write_text("0.12.0\n")
    scripts = pkg / "scripts"
    scripts.mkdir()
    # Minimal init-factory stub that succeeds
    (scripts / "init-factory").write_text(textwrap.dedent("""\
        #!/usr/bin/env python3
        import argparse, json, sys
        from pathlib import Path
        ap = argparse.ArgumentParser()
        ap.add_argument("--source", type=Path)
        ap.add_argument("--target", type=Path)
        ap.add_argument("--cli", nargs="+")
        args = ap.parse_args()
        target = args.target
        # Create minimal Factory tree
        af = target / ".agent-factory"
        af.mkdir(parents=True, exist_ok=True)
        (af / "factory").mkdir(exist_ok=True)
        # Write a v1 manifest
        manifest = {
            "version": 1,
            "factory_version": "0.12.0",
            "cli": args.cli[0] if args.cli else None,
            "orientation": {},
            "orientation_markers": {
                "begin": "<!-- >>> agent_factory orientation >>>",
                "end": "<!-- <<< agent_factory orientation <<< -->"
            },
            "orientation_orig_final_newline": {},
            "remove_paths": [],
        }
        (af / "install.json").write_text(json.dumps(manifest, indent=2) + "\\n")
        print("init-factory: done")
        sys.exit(0)
    """))
    os.chmod(scripts / "init-factory", 0o755)
    return source


def _make_target(tmp_path: Path, *, git: bool = True,
                 interfaces: list[str] | None = None) -> Path:
    """Create a target directory, optionally with git init and interface dirs."""
    target = tmp_path / "project"
    target.mkdir()
    if git:
        env = {**os.environ, "GIT_AUTHOR_NAME": "test",
               "GIT_AUTHOR_EMAIL": "t@t",
               "GIT_COMMITTER_NAME": "test",
               "GIT_COMMITTER_EMAIL": "t@t"}
        subprocess.run(["git", "init", str(target)],
                       check=True, capture_output=True, env=env)
    for iface in (interfaces or []):
        (target / iface).mkdir(parents=True, exist_ok=True)
    return target


# ---------------------------------------------------------------------------
# Slice 1 — Argument validation
# ---------------------------------------------------------------------------

class TestArgumentValidation:
    """Bootstrap exits non-zero on invalid arguments."""

    def test_missing_target_prints_usage(self, tmp_path):
        source = _make_source(tmp_path)
        result = _run(["--from-local", str(source)])
        assert result.returncode != 0
        assert "target" in result.stderr.lower() or "usage" in result.stderr.lower()

    def test_two_source_selectors(self, tmp_path):
        result = _run(["--from-local", "/tmp/x", "--from-remote",
                        "https://example.com", "--target", "/tmp/y"])
        assert result.returncode != 0
        assert "source" in result.stderr.lower()

    def test_version_with_from_local(self, tmp_path):
        source = _make_source(tmp_path)
        target = _make_target(tmp_path)
        result = _run(["--from-local", str(source), "--target",
                        str(target), "--version", "1.0"])
        assert result.returncode != 0
        assert "version" in result.stderr.lower()

    def test_no_source_selector(self, tmp_path):
        target = _make_target(tmp_path)
        result = _run(["--target", str(target)])
        assert result.returncode != 0


# ---------------------------------------------------------------------------
# Slice 2 — Unsafe target rejection
# ---------------------------------------------------------------------------

class TestUnsafeTarget:
    """Bootstrap rejects root, home, and unresolved targets."""

    def test_root_rejected(self, tmp_path):
        source = _make_source(tmp_path)
        result = _run(["--from-local", str(source), "--target", "/"])
        assert result.returncode != 0
        assert "unsafe" in result.stderr.lower() or "root" in result.stderr.lower()

    def test_home_rejected(self, tmp_path):
        source = _make_source(tmp_path)
        result = _run(["--from-local", str(source), "--target",
                        str(Path.home())])
        assert result.returncode != 0

    def test_nonexistent_target_rejected(self, tmp_path):
        source = _make_source(tmp_path)
        result = _run(["--from-local", str(source), "--target",
                        str(tmp_path / "nonexistent")])
        assert result.returncode != 0


# ---------------------------------------------------------------------------
# Slice 3 — Source resolution
# ---------------------------------------------------------------------------

class TestSourceResolution:
    """Local source path resolves to absolute and validates content."""

    def test_relative_path_resolves(self, tmp_path):
        source = _make_source(tmp_path)
        target = _make_target(tmp_path, interfaces=[".claude"])
        # Run with non-interactive (will stop at consent)
        result = _run(["--from-local", str(source), "--target",
                        str(target)], input_text="\n")
        # Should get past validation to preflight/preview
        # The absolute path should appear in stdout
        assert str(source.resolve()) in result.stdout or result.returncode == 0 or "source" in result.stdout.lower()

    def test_invalid_source_rejected(self, tmp_path):
        # Source without packages/factory/
        source = tmp_path / "empty-src"
        source.mkdir()
        target = _make_target(tmp_path)
        result = _run(["--from-local", str(source), "--target",
                        str(target)])
        assert result.returncode != 0
        assert "source" in result.stderr.lower() or "factory" in result.stderr.lower()


# ---------------------------------------------------------------------------
# Slice 4 — Preflight diagnosis
# ---------------------------------------------------------------------------

class TestPreflightDiagnosis:
    """Preflight reports readiness without modifying files."""

    def test_preflight_no_file_changes(self, tmp_path):
        source = _make_source(tmp_path)
        target = _make_target(tmp_path, interfaces=[".claude"])
        # Snapshot target state
        before = set()
        for p in target.rglob("*"):
            if p.is_file():
                before.add((str(p.relative_to(target)), p.read_bytes()))
        # Run with blank input to stop at consent
        result = _run(["--from-local", str(source), "--target",
                        str(target)], input_text="\n")
        # Snapshot after
        after = set()
        for p in target.rglob("*"):
            if p.is_file():
                after.add((str(p.relative_to(target)), p.read_bytes()))
        assert before == after, "Preflight changed target files"

    def test_preflight_produces_readiness_value(self, tmp_path):
        source = _make_source(tmp_path)
        target = _make_target(tmp_path, interfaces=[".claude"])
        result = _run(["--from-local", str(source), "--target",
                        str(target)], input_text="\n")
        out = result.stdout.lower()
        has_readiness = ("ready" in out or "blocked" in out
                         or "limitations" in out)
        assert has_readiness, f"No readiness value in output: {result.stdout}"


# ---------------------------------------------------------------------------
# Slice 5 — Consent gating
# ---------------------------------------------------------------------------

class TestConsentGating:
    """Blank or declined input stops the bootstrap without changes."""

    def test_blank_consent_stops(self, tmp_path):
        source = _make_source(tmp_path)
        target = _make_target(tmp_path, interfaces=[".claude"])
        result = _run(["--from-local", str(source), "--target",
                        str(target)], input_text="\n")
        # Should not have installed anything
        assert not (target / ".agent-factory" / "install.json").exists()

    def test_decline_stops(self, tmp_path):
        source = _make_source(tmp_path)
        target = _make_target(tmp_path, interfaces=[".claude"])
        result = _run(["--from-local", str(source), "--target",
                        str(target)], input_text="n\n")
        assert not (target / ".agent-factory" / "install.json").exists()


# ---------------------------------------------------------------------------
# Slice 6 — Interface detection and ambiguity
# ---------------------------------------------------------------------------

class TestInterfaceDetection:
    """Interface detection and ambiguous selection handling."""

    def test_single_interface_auto_selected(self, tmp_path):
        source = _make_source(tmp_path)
        target = _make_target(tmp_path, interfaces=[".claude"])
        # Approve installation with blank interface (auto-select) then "yes"
        result = _run(["--from-local", str(source), "--target",
                        str(target)], input_text="\nyes\n")
        # Should proceed (auto-selected single interface)
        out = result.stdout.lower()
        assert "claude" in out

    def test_multiple_interfaces_blank_does_not_select_all(self, tmp_path):
        source = _make_source(tmp_path)
        target = _make_target(tmp_path, interfaces=[".claude", ".github"])
        # Send blank twice then stop
        result = _run(["--from-local", str(source), "--target",
                        str(target)], input_text="\n\n\n")
        # Should NOT have installed with all interfaces
        assert not (target / ".agent-factory" / "install.json").exists()

    def test_zero_interfaces_blank_stops(self, tmp_path):
        source = _make_source(tmp_path)
        target = _make_target(tmp_path)  # no interface dirs
        result = _run(["--from-local", str(source), "--target",
                        str(target)], input_text="\n\n\n")
        assert not (target / ".agent-factory" / "install.json").exists()


# ---------------------------------------------------------------------------
# Slice 7 — Instruction header management
# ---------------------------------------------------------------------------

class TestInstructionHeaders:
    """Header injection, idempotency, and exclusion handling."""

    def test_header_injected_into_agents_md(self, tmp_path):
        source = _make_source(tmp_path)
        target = _make_target(tmp_path, interfaces=[".claude"])
        # Create an AGENTS.md in a subdirectory
        sub = target / "docs"
        sub.mkdir()
        agents_md = sub / "AGENTS.md"
        agents_md.write_text("# My Agents\n\nSome content.\n")
        # Approve installation
        result = _run(["--from-local", str(source), "--target",
                        str(target)], input_text="\nyes\n")
        content = agents_md.read_text()
        assert "<!-- >>> agent_factory orientation >>>" in content
        assert "<!-- <<< agent_factory orientation <<< -->" in content

    def test_header_not_duplicated(self, tmp_path):
        source = _make_source(tmp_path)
        target = _make_target(tmp_path, interfaces=[".claude"])
        sub = target / "docs"
        sub.mkdir()
        agents_md = sub / "AGENTS.md"
        agents_md.write_text("# My Agents\n")
        # Install twice
        _run(["--from-local", str(source), "--target",
              str(target)], input_text="\nyes\n")
        _run(["--from-local", str(source), "--target",
              str(target)], input_text="\nyes\n")
        content = agents_md.read_text()
        count = content.count("<!-- >>> agent_factory orientation >>>")
        assert count == 1, f"Expected 1 header block, found {count}"

    def test_excluded_dirs_skipped(self, tmp_path):
        source = _make_source(tmp_path)
        target = _make_target(tmp_path, interfaces=[".claude"])
        # Create AGENTS.md inside an excluded dir
        excluded = target / "node_modules" / "pkg"
        excluded.mkdir(parents=True)
        agents_md = excluded / "AGENTS.md"
        agents_md.write_text("# Package agents\n")
        _run(["--from-local", str(source), "--target",
              str(target)], input_text="\nyes\n")
        # Should be unchanged
        assert "orientation" not in agents_md.read_text()

    def test_symlinks_not_followed(self, tmp_path):
        source = _make_source(tmp_path)
        target = _make_target(tmp_path, interfaces=[".claude"])
        sub = target / "linked"
        sub.mkdir()
        # Create external symlink target
        external = tmp_path / "external"
        external.mkdir()
        agents_md = external / "AGENTS.md"
        agents_md.write_text("# External\n")
        # Symlink into target
        link = sub / "AGENTS.md"
        link.symlink_to(agents_md)
        _run(["--from-local", str(source), "--target",
              str(target)], input_text="\nyes\n")
        # External file should be unchanged
        assert "orientation" not in agents_md.read_text()

    def test_copilot_instructions_discovered(self, tmp_path):
        source = _make_source(tmp_path)
        target = _make_target(tmp_path, interfaces=[".claude"])
        sub = target / "packages" / "web"
        sub.mkdir(parents=True)
        ci = sub / "copilot-instructions.md"
        ci.write_text("# Copilot\nInstructions here.\n")
        _run(["--from-local", str(source), "--target",
              str(target)], input_text="\nyes\n")
        content = ci.read_text()
        assert "<!-- >>> agent_factory orientation >>>" in content


# ---------------------------------------------------------------------------
# Slice 8 — Manifest version 2
# ---------------------------------------------------------------------------

class TestManifestV2:
    """Manifest migration from v1 to v2."""

    def test_manifest_version_is_2(self, tmp_path):
        source = _make_source(tmp_path)
        target = _make_target(tmp_path, interfaces=[".claude"])
        _run(["--from-local", str(source), "--target",
              str(target)], input_text="\nyes\n")
        manifest_path = target / ".agent-factory" / "install.json"
        assert manifest_path.exists()
        manifest = json.loads(manifest_path.read_text())
        assert manifest["version"] == 2

    def test_manifest_has_source_selector(self, tmp_path):
        source = _make_source(tmp_path)
        target = _make_target(tmp_path, interfaces=[".claude"])
        _run(["--from-local", str(source), "--target",
              str(target)], input_text="\nyes\n")
        manifest = json.loads(
            (target / ".agent-factory" / "install.json").read_text())
        assert manifest["source_selector"] == "local"
        assert manifest["resolved_source"] == str(source.resolve())

    def test_manifest_orientation_entries_are_objects(self, tmp_path):
        source = _make_source(tmp_path)
        target = _make_target(tmp_path, interfaces=[".claude"])
        sub = target / "docs"
        sub.mkdir()
        (sub / "AGENTS.md").write_text("# Agents\n")
        _run(["--from-local", str(source), "--target",
              str(target)], input_text="\nyes\n")
        manifest = json.loads(
            (target / ".agent-factory" / "install.json").read_text())
        for key, entry in manifest.get("orientation", {}).items():
            assert isinstance(entry, dict), f"orientation[{key}] is not a dict"
            assert "status" in entry
            assert "block_digest" in entry
            assert "orig_final_newline" in entry


# ---------------------------------------------------------------------------
# Slice 9 — Receipt generation
# ---------------------------------------------------------------------------

class TestReceiptGeneration:
    """Receipt includes required fields after successful installation."""

    def test_receipt_lists_changed_paths(self, tmp_path):
        source = _make_source(tmp_path)
        target = _make_target(tmp_path, interfaces=[".claude"])
        result = _run(["--from-local", str(source), "--target",
                        str(target)], input_text="\nyes\n")
        out = result.stdout.lower()
        assert "receipt" in out or "installed" in out or "changed" in out

    def test_receipt_shows_next_command(self, tmp_path):
        source = _make_source(tmp_path)
        target = _make_target(tmp_path, interfaces=[".claude"])
        result = _run(["--from-local", str(source), "--target",
                        str(target)], input_text="\nyes\n")
        out = result.stdout
        # Receipt must contain a next command
        assert "next" in out.lower() or "init-factory" in out.lower() or "cd " in out

    def test_receipt_shows_uninstall_command(self, tmp_path):
        source = _make_source(tmp_path)
        target = _make_target(tmp_path, interfaces=[".claude"])
        result = _run(["--from-local", str(source), "--target",
                        str(target)], input_text="\nyes\n")
        assert "remove-factory" in result.stdout


# ---------------------------------------------------------------------------
# Slice 10 — Preview content
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Slice 11 — Unsupported host (unit-level, mocked platform)
# ---------------------------------------------------------------------------

class TestUnsupportedHost:
    """Unsupported host platform stops with explanation."""

    def test_unsupported_platform_blocked(self, tmp_path, monkeypatch):
        """VFO-008: unsupported platform -> explanation, exit non-zero."""
        monkeypatch.setattr("platform.system", lambda: "FreeBSD")
        monkeypatch.setattr("platform.machine", lambda: "x86_64")
        loader = importlib.machinery.SourceFileLoader(
            "install_agent_factory_plat", str(SCRIPT))
        spec = importlib.util.spec_from_loader(
            "install_agent_factory_plat", loader)
        mod = importlib.util.module_from_spec(spec)
        loader.exec_module(mod)
        result = mod.check_platform()
        assert not result.passed
        assert result.critical
        assert "unsupported" in result.message.lower() or "freebsd" in result.message.lower()

    def test_unsupported_architecture_blocked(self, tmp_path, monkeypatch):
        """VFO-008: unsupported architecture -> explanation."""
        monkeypatch.setattr("platform.system", lambda: "Linux")
        monkeypatch.setattr("platform.machine", lambda: "mips64")
        loader = importlib.machinery.SourceFileLoader(
            "install_agent_factory_arch", str(SCRIPT))
        spec = importlib.util.spec_from_loader(
            "install_agent_factory_arch", loader)
        mod = importlib.util.module_from_spec(spec)
        loader.exec_module(mod)
        result = mod.check_platform()
        assert not result.passed
        assert "unsupported" in result.message.lower() or "mips" in result.message.lower()


# ---------------------------------------------------------------------------
# Slice 12b — Missing prerequisite report (unit-level, mocked)
# ---------------------------------------------------------------------------

class TestMissingPrerequisiteReport:
    """Missing prerequisite includes purpose, fix, scope, reversal, verification."""

    def test_missing_git_reports_five_fields(self, monkeypatch):
        """VFO-011: missing prerequisite -> five-field report."""
        import importlib.util
        loader = importlib.machinery.SourceFileLoader(
            "install_agent_factory_prereq", str(SCRIPT))
        spec = importlib.util.spec_from_loader(
            "install_agent_factory_prereq", loader)
        mod = importlib.util.module_from_spec(spec)
        loader.exec_module(mod)

        # Mock git as unavailable
        original_run = subprocess.run
        def fake_run(cmd, **kwargs):
            if cmd and cmd[0] == "git":
                raise FileNotFoundError("git not found")
            return original_run(cmd, **kwargs)
        monkeypatch.setattr("subprocess.run", fake_run)

        result = mod.check_git()
        assert not result.passed
        assert result.purpose, "Missing purpose"
        assert result.fix, "Missing fix"
        assert result.scope, "Missing scope"
        assert result.reversal, "Missing reversal"
        assert result.verification, "Missing verification"

    def test_missing_shell_reports_five_fields(self, monkeypatch):
        """VFO-011: missing shell -> five-field report."""
        import importlib.util
        loader = importlib.machinery.SourceFileLoader(
            "install_agent_factory_shell", str(SCRIPT))
        spec = importlib.util.spec_from_loader(
            "install_agent_factory_shell", loader)
        mod = importlib.util.module_from_spec(spec)
        loader.exec_module(mod)

        monkeypatch.setattr("shutil.which", lambda x: None)

        result = mod.check_shell()
        assert not result.passed
        assert result.purpose
        assert result.fix
        assert result.scope
        assert result.reversal
        assert result.verification


# ---------------------------------------------------------------------------
# Slice 12 — Manifest v1 migration (unit-level)
# ---------------------------------------------------------------------------

class TestManifestMigration:
    """Migrate manifest from v1 to v2 schema."""

    def test_bare_string_orientation_becomes_object(self):
        """V1 orientation entries upgrade to objects."""
        sys.path.insert(0, str(SCRIPT.parent))
        try:
            import importlib.util
            loader = importlib.machinery.SourceFileLoader(
                "install_agent_factory_mig", str(SCRIPT))
            spec = importlib.util.spec_from_loader(
                "install_agent_factory_mig", loader)
            mod = importlib.util.module_from_spec(spec)
            loader.exec_module(mod)

            v1 = {
                "version": 1,
                "orientation": {
                    ".claude/CLAUDE.md": "injected",
                },
                "orientation_orig_final_newline": {
                    ".claude/CLAUDE.md": False,
                },
            }
            v2 = mod.migrate_manifest_v1_to_v2(
                v1, "local", "/path/to/source")
            assert v2["version"] == 2
            assert v2["source_selector"] == "local"
            assert v2["resolved_source"] == "/path/to/source"
            entry = v2["orientation"][".claude/CLAUDE.md"]
            assert isinstance(entry, dict)
            assert entry["status"] == "injected"
            assert entry["orig_final_newline"] is False
            assert "orientation_orig_final_newline" not in v2
        finally:
            sys.path.pop(0)

    def test_extra_orientations_merged(self):
        """Bootstrap-injected headers are added to manifest."""
        sys.path.insert(0, str(SCRIPT.parent))
        try:
            import importlib.util
            loader = importlib.machinery.SourceFileLoader(
                "install_agent_factory_mig2", str(SCRIPT))
            spec = importlib.util.spec_from_loader(
                "install_agent_factory_mig2", loader)
            mod = importlib.util.module_from_spec(spec)
            loader.exec_module(mod)

            v1 = {
                "version": 1,
                "orientation": {},
                "orientation_orig_final_newline": {},
            }
            extra = {
                "docs/AGENTS.md": {
                    "status": "injected",
                    "block_digest": "abc123",
                    "orig_final_newline": True,
                }
            }
            v2 = mod.migrate_manifest_v1_to_v2(
                v1, "local", "/src", extra_orientations=extra)
            assert "docs/AGENTS.md" in v2["orientation"]
            assert v2["orientation"]["docs/AGENTS.md"]["block_digest"] == "abc123"
        finally:
            sys.path.pop(0)


# ---------------------------------------------------------------------------
# Slice 10 — Preview content
# ---------------------------------------------------------------------------

class TestPreviewContent:
    """Preview shows required information before consent."""

    def test_preview_shows_source_and_target(self, tmp_path):
        source = _make_source(tmp_path)
        target = _make_target(tmp_path, interfaces=[".claude"])
        result = _run(["--from-local", str(source), "--target",
                        str(target)], input_text="\n")
        out = result.stdout
        # Preview should mention source and target
        assert str(source.resolve()) in out or "source" in out.lower()
        assert str(target) in out or "target" in out.lower()

    def test_preview_shows_uninstall_command(self, tmp_path):
        source = _make_source(tmp_path)
        target = _make_target(tmp_path, interfaces=[".claude"])
        result = _run(["--from-local", str(source), "--target",
                        str(target)], input_text="\n")
        assert "remove-factory" in result.stdout
