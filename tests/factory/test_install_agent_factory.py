"""Contract tests for the install-agent-factory bootstrap script.

Covers: argument validation, unsafe target rejection, preflight diagnosis,
source resolution, consent gating, instruction header management, manifest
version 2 migration, and receipt generation.
"""

from __future__ import annotations

import hashlib
import http.server
import importlib.machinery
import importlib.util
import io
import json
import os
import re
import shutil
import socket
import stat
import subprocess
import sys
import tarfile
import textwrap
import threading
from pathlib import Path
from typing import Dict
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
        ap.add_argument("--project-name")
        args = ap.parse_args()
        target = args.target
        # Create minimal Factory tree
        af = target / ".agent-factory"
        af.mkdir(parents=True, exist_ok=True)
        (af / "factory").mkdir(exist_ok=True)
        # Record the argv this stub was invoked with, so tests can assert
        # on what install-agent-factory passes through to init-factory.
        (af / "_init_factory_argv.json").write_text(json.dumps(sys.argv[1:]))
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
# Remote-release helpers
# ---------------------------------------------------------------------------

_INIT_FACTORY_STUB = textwrap.dedent("""\
    #!/usr/bin/env python3
    import argparse, json, sys
    from pathlib import Path
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path)
    ap.add_argument("--target", type=Path)
    ap.add_argument("--cli", nargs="+")
    ap.add_argument("--project-name")
    args = ap.parse_args()
    target = args.target
    af = target / ".agent-factory"
    af.mkdir(parents=True, exist_ok=True)
    (af / "factory").mkdir(exist_ok=True)
    manifest = {
        "version": 1,
        "factory_version": "1.0.0",
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
""")


def _build_remote_archive(version: str = "1.0.0") -> bytes:
    """Build a gzip tar matching build-release's layout: entries are
    relative to packages/factory/ (no wrapper directory)."""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tf:
        version_bytes = f"{version}\n".encode("utf-8")
        info = tarfile.TarInfo("VERSION")
        info.size = len(version_bytes)
        tf.addfile(info, io.BytesIO(version_bytes))

        init_bytes = _INIT_FACTORY_STUB.encode("utf-8")
        info = tarfile.TarInfo("scripts/init-factory")
        info.size = len(init_bytes)
        info.mode = 0o755
        tf.addfile(info, io.BytesIO(init_bytes))
    return buf.getvalue()


def _sums_line(digest: str) -> bytes:
    return f"{digest}  agent-factory.tar.gz\n".encode("utf-8")


def _load_module(name: str):
    """Load install-agent-factory as a fresh module under `name`.

    Mirrors the loader used throughout this file for unit-level tests that
    call script-internal functions directly.
    """
    loader = importlib.machinery.SourceFileLoader(name, str(SCRIPT))
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


def _free_port() -> int:
    """Return a TCP port that is free at the moment of the call."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def _make_release_handler(releases: Dict[str, Dict[str, object]],
                          request_log: list) -> type:
    """Build a BaseHTTPRequestHandler bound to a per-test releases map.

    `releases` shape:
        {
            "latest_version": "1.0.0" | None,
            "assets": {"1.0.0": {"SHA256SUMS": bytes,
                                  "agent-factory.tar.gz": bytes}},
        }
    """

    class Handler(http.server.BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def _handle(self, write_body: bool) -> None:
            request_log.append(self.path)
            if self.path == "/latest":
                latest = releases.get("latest_version")
                if latest is None:
                    self.send_response(404)
                    self.end_headers()
                    return
                self.send_response(302)
                self.send_header("Location", f"/releases/{latest}/")
                self.send_header("Content-Length", "0")
                self.end_headers()
                return

            m = re.match(r"^/releases/([^/]+)/([^/]+)$", self.path)
            if m:
                version, asset = m.groups()
                data = releases.get("assets", {}).get(version, {}).get(asset)
                if data is not None:
                    self.send_response(200)
                    self.send_header("Content-Length", str(len(data)))
                    self.end_headers()
                    if write_body:
                        self.wfile.write(data)
                    return

            self.send_response(404)
            self.send_header("Content-Length", "0")
            self.end_headers()

        def do_GET(self) -> None:
            self._handle(write_body=True)

        def do_HEAD(self) -> None:
            self._handle(write_body=False)

        def log_message(self, format: str, *args) -> None:  # noqa: A002
            pass

    return Handler


@pytest.fixture()
def remote_release_server():
    """Start a local HTTP server standing in for a distribution remote.

    Yields a `start(releases) -> (base_url, request_log)` callable. The
    server is shut down at test teardown.
    """
    state: Dict[str, object] = {}

    def start(releases: Dict[str, Dict[str, object]]):
        request_log: list = []
        handler_cls = _make_release_handler(releases, request_log)
        httpd = http.server.HTTPServer(("127.0.0.1", 0), handler_cls)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        state["httpd"] = httpd
        state["thread"] = thread
        port = httpd.server_address[1]
        return f"http://127.0.0.1:{port}", request_log

    yield start

    httpd = state.get("httpd")
    if httpd is not None:
        httpd.shutdown()
        httpd.server_close()


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


class TestInitFactoryDelegation:
    """install-agent-factory must give init-factory everything it needs to
    run non-interactively. Without --project-name, a fresh target has no
    .agent-factory/config/project.json yet, so init-factory's own project-
    identity step falls back to an interactive `input("Project name: ")`
    prompt that a piped, non-interactive bootstrap can never answer (found
    while building the ST-0293 end-to-end journey test, which runs the
    real init-factory instead of this stub)."""

    def test_passes_project_name_so_init_factory_never_prompts(self, tmp_path):
        source = _make_source(tmp_path)
        target = _make_target(tmp_path, interfaces=[".claude"])
        _run(["--from-local", str(source), "--target",
              str(target)], input_text="\nyes\n")
        argv = json.loads(
            (target / ".agent-factory" / "_init_factory_argv.json").read_text()
        )
        assert "--project-name" in argv
        name_index = argv.index("--project-name") + 1
        assert argv[name_index] == target.name


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


# ---------------------------------------------------------------------------
# Slice 13 — Remote version resolution
# ---------------------------------------------------------------------------

class TestRemoteVersionResolution:
    """Explicit --version bypasses /latest; omitted --version follows it."""

    def test_explicit_version_fetches_releases_dir_without_redirect(
            self, tmp_path, remote_release_server):
        archive = _build_remote_archive("1.0.0")
        digest = hashlib.sha256(archive).hexdigest()
        base_url, request_log = remote_release_server({
            "latest_version": None,
            "assets": {"1.0.0": {
                "SHA256SUMS": _sums_line(digest),
                "agent-factory.tar.gz": archive,
            }},
        })
        target = _make_target(tmp_path, interfaces=[".claude"])
        result = _run(["--from-remote", base_url, "--target", str(target),
                        "--version", "1.0.0"], input_text="\nyes\n")

        assert f"{base_url}/releases/1.0.0/" in result.stdout
        assert not any(p == "/latest" for p in request_log), (
            "explicit --version must not follow the /latest redirect")

    def test_omitted_version_follows_latest_redirect(
            self, tmp_path, remote_release_server):
        archive = _build_remote_archive("2.0.0")
        digest = hashlib.sha256(archive).hexdigest()
        base_url, request_log = remote_release_server({
            "latest_version": "2.0.0",
            "assets": {"2.0.0": {
                "SHA256SUMS": _sums_line(digest),
                "agent-factory.tar.gz": archive,
            }},
        })
        target = _make_target(tmp_path, interfaces=[".claude"])
        result = _run(["--from-remote", base_url, "--target", str(target)],
                       input_text="\nyes\n")

        assert "/latest" in request_log
        assert f"{base_url}/releases/2.0.0/" in result.stdout


# ---------------------------------------------------------------------------
# Slice 14 — Remote digest verification
# ---------------------------------------------------------------------------

class TestRemoteDigestVerification:
    """A verified digest installs; a missing or mismatched one refuses."""

    def test_valid_digest_installs(self, tmp_path, remote_release_server):
        archive = _build_remote_archive("1.0.0")
        digest = hashlib.sha256(archive).hexdigest()
        base_url, _ = remote_release_server({
            "latest_version": None,
            "assets": {"1.0.0": {
                "SHA256SUMS": _sums_line(digest),
                "agent-factory.tar.gz": archive,
            }},
        })
        target = _make_target(tmp_path, interfaces=[".claude"])
        result = _run(["--from-remote", base_url, "--target", str(target),
                        "--version", "1.0.0"], input_text="\nyes\n")

        assert result.returncode == 0, result.stderr
        assert (target / ".agent-factory" / "install.json").exists()

    def test_missing_digest_entry_blocks_extraction(
            self, tmp_path, remote_release_server):
        archive = _build_remote_archive("1.0.0")
        base_url, _ = remote_release_server({
            "latest_version": None,
            "assets": {"1.0.0": {
                # SHA256SUMS present but names a different file.
                "SHA256SUMS": b"deadbeef  some-other-file.tar.gz\n",
                "agent-factory.tar.gz": archive,
            }},
        })
        target = _make_target(tmp_path, interfaces=[".claude"])
        result = _run(["--from-remote", base_url, "--target", str(target),
                        "--version", "1.0.0"], input_text="\nyes\n")

        assert result.returncode != 0
        assert not (target / ".agent-factory").exists()

    def test_mismatched_digest_blocks_extraction(
            self, tmp_path, remote_release_server):
        archive = _build_remote_archive("1.0.0")
        base_url, _ = remote_release_server({
            "latest_version": None,
            "assets": {"1.0.0": {
                "SHA256SUMS": _sums_line("0" * 64),
                "agent-factory.tar.gz": archive,
            }},
        })
        target = _make_target(tmp_path, interfaces=[".claude"])
        result = _run(["--from-remote", base_url, "--target", str(target),
                        "--version", "1.0.0"], input_text="\nyes\n")

        assert result.returncode != 0
        assert not (target / ".agent-factory").exists()
        assert "digest" in (result.stderr + result.stdout).lower()


# ---------------------------------------------------------------------------
# Slice 15 — Remote network failures
# ---------------------------------------------------------------------------

class TestRemoteNetworkFailures:
    """Network failures name the URL and error, then exit non-zero."""

    def test_connection_refused(self, tmp_path):
        port = _free_port()
        base_url = f"http://127.0.0.1:{port}"
        target = _make_target(tmp_path, interfaces=[".claude"])
        result = _run(["--from-remote", base_url, "--target", str(target),
                        "--version", "1.0.0"])

        assert result.returncode != 0
        assert base_url in result.stderr
        assert not (target / ".agent-factory").exists()

    def test_http_404_on_missing_asset(self, tmp_path, remote_release_server):
        base_url, _ = remote_release_server({
            "latest_version": None,
            "assets": {},
        })
        target = _make_target(tmp_path, interfaces=[".claude"])
        result = _run(["--from-remote", base_url, "--target", str(target),
                        "--version", "1.0.0"])

        assert result.returncode != 0
        assert base_url in result.stderr
        assert not (target / ".agent-factory").exists()


# ---------------------------------------------------------------------------
# Slice 16 — Remote preview and receipt content
# ---------------------------------------------------------------------------

class TestRemotePreviewAndReceipt:
    """Remote preview and receipt show the resolved URL and digest."""

    def test_preview_shows_resolved_url_and_digest(
            self, tmp_path, remote_release_server):
        archive = _build_remote_archive("1.0.0")
        digest = hashlib.sha256(archive).hexdigest()
        base_url, _ = remote_release_server({
            "latest_version": None,
            "assets": {"1.0.0": {
                "SHA256SUMS": _sums_line(digest),
                "agent-factory.tar.gz": archive,
            }},
        })
        target = _make_target(tmp_path, interfaces=[".claude"])
        # Stop at consent so the receipt path is not reached.
        result = _run(["--from-remote", base_url, "--target", str(target),
                        "--version", "1.0.0"], input_text="\n\n")

        assert f"{base_url}/releases/1.0.0/" in result.stdout
        assert digest in result.stdout

    def test_receipt_confirms_remote_source_and_digest(
            self, tmp_path, remote_release_server):
        archive = _build_remote_archive("1.0.0")
        digest = hashlib.sha256(archive).hexdigest()
        base_url, _ = remote_release_server({
            "latest_version": None,
            "assets": {"1.0.0": {
                "SHA256SUMS": _sums_line(digest),
                "agent-factory.tar.gz": archive,
            }},
        })
        target = _make_target(tmp_path, interfaces=[".claude"])
        result = _run(["--from-remote", base_url, "--target", str(target),
                        "--version", "1.0.0"], input_text="\nyes\n")

        assert digest in result.stdout
        assert f"{base_url}/releases/1.0.0/" in result.stdout


# ---------------------------------------------------------------------------
# Slice 17 — Remote manifest fields
# ---------------------------------------------------------------------------

class TestRemoteManifest:
    """The manifest records source_selector, resolved_source, and digest."""

    def test_manifest_records_remote_fields(
            self, tmp_path, remote_release_server):
        archive = _build_remote_archive("1.0.0")
        digest = hashlib.sha256(archive).hexdigest()
        base_url, _ = remote_release_server({
            "latest_version": None,
            "assets": {"1.0.0": {
                "SHA256SUMS": _sums_line(digest),
                "agent-factory.tar.gz": archive,
            }},
        })
        target = _make_target(tmp_path, interfaces=[".claude"])
        result = _run(["--from-remote", base_url, "--target", str(target),
                        "--version", "1.0.0"], input_text="\nyes\n")

        assert result.returncode == 0, result.stderr
        manifest = json.loads(
            (target / ".agent-factory" / "install.json").read_text())
        assert manifest["version"] == 2
        assert manifest["source_selector"] == "remote"
        assert manifest["resolved_source"] == f"{base_url}/releases/1.0.0/"
        assert manifest["archive_sha256"] == digest


# ---------------------------------------------------------------------------
# Slice 18 — Prerequisite fix loop (ST-0283)
# ---------------------------------------------------------------------------

class TestFixableChecksContract:
    """uv and managed-Python checks carry the decided fix contract."""

    def test_uv_fix_matches_decided_contract(self, monkeypatch):
        """VFO-011: uv fix -> exact command/scope/reversal/verification."""
        mod = _load_module("install_agent_factory_uvfix")
        monkeypatch.setattr("shutil.which", lambda x: None)

        result = mod.check_uv()
        assert not result.passed
        assert result.fixable is True
        assert result.purpose
        assert result.fix == "curl -LsSf https://astral.sh/uv/install.sh | sh"
        assert "~/.local/bin" in result.scope
        assert result.reversal == "uv self uninstall"
        assert result.verification == "uv --version"

    def test_managed_python_fix_matches_decided_contract(self, monkeypatch):
        """VFO-011: managed Python fix -> exact command/scope/reversal/verification."""
        mod = _load_module("install_agent_factory_pyfix")

        def fake_run(cmd, **kwargs):
            raise FileNotFoundError("uv not found")
        monkeypatch.setattr("subprocess.run", fake_run)

        result = mod.check_managed_python()
        assert not result.passed
        assert result.fixable is True
        assert result.purpose
        assert result.fix == "uv python install 3.10"
        assert "~/.local/share/uv/python" in result.scope
        assert result.reversal == "uv python uninstall 3.10"
        assert result.verification == "uv python list | grep 3.10"

    def test_managed_python_passes_when_verification_succeeds(self, monkeypatch):
        mod = _load_module("install_agent_factory_pyok")

        class FakeCompleted:
            returncode = 0

        monkeypatch.setattr("subprocess.run", lambda *a, **kw: FakeCompleted())

        result = mod.check_managed_python()
        assert result.passed

    def test_git_and_shell_checks_are_not_fixable(self, monkeypatch):
        """Unsupported prerequisites carry guidance only, never fixable."""
        mod = _load_module("install_agent_factory_unsupported")
        monkeypatch.setattr("shutil.which", lambda x: None)

        def fake_run(cmd, **kwargs):
            raise FileNotFoundError("git not found")
        monkeypatch.setattr("subprocess.run", fake_run)

        git_result = mod.check_git()
        shell_result = mod.check_shell()
        assert git_result.fixable is False
        assert shell_result.fixable is False


class TestFixConsent:
    """VFO-012: blank input, decline, and cancellation are never consent."""

    def _check(self, mod):
        return mod.PreflightCheck(
            "uv", False, False, "uv is not installed.",
            purpose="p", fix="f", scope="s", reversal="r",
            verification="v", fixable=True,
        )

    def test_blank_input_is_not_consent(self):
        mod = _load_module("install_agent_factory_consent_blank")
        check = self._check(mod)
        assert mod.get_fix_consent(check, input_func=lambda p: "") is False

    def test_declined_input_is_not_consent(self):
        mod = _load_module("install_agent_factory_consent_decline")
        check = self._check(mod)
        assert mod.get_fix_consent(check, input_func=lambda p: "n") is False

    def test_cancelled_input_is_not_consent(self):
        mod = _load_module("install_agent_factory_consent_cancel")
        check = self._check(mod)

        def raise_eof(prompt):
            raise EOFError()
        assert mod.get_fix_consent(check, input_func=raise_eof) is False

    def test_affirmative_input_is_consent(self):
        mod = _load_module("install_agent_factory_consent_yes")
        check = self._check(mod)
        assert mod.get_fix_consent(check, input_func=lambda p: "yes") is True


class TestFixLoop:
    """VFO-012/VFO-013: the fix loop orchestrates consent, run, and verify."""

    def _fixable(self, mod, name, passed=False):
        return mod.PreflightCheck(
            name, passed, False, f"{name} is not installed.",
            purpose=f"purpose-{name}", fix=f"fix-{name}",
            scope=f"scope-{name}", reversal=f"reversal-{name}",
            verification=f"verify-{name}", fixable=True,
        )

    def _unfixable(self, mod, name):
        return mod.PreflightCheck(
            name, False, True, f"{name} is missing.",
            purpose=f"purpose-{name}", fix=f"fix-{name}",
            scope=f"scope-{name}", reversal=f"reversal-{name}",
            verification=f"verify-{name}", fixable=False,
        )

    def test_confirmed_fix_runs_and_verifies_alone(self):
        mod = _load_module("install_agent_factory_loop_confirm")
        check = self._fixable(mod, "uv")
        run_fix_calls = []
        run_verify_calls = []

        completed = mod.run_fix_loop(
            [check],
            input_func=lambda p: "yes",
            run_fix=lambda cmd: run_fix_calls.append(cmd) or (True, ""),
            run_verify=lambda cmd: run_verify_calls.append(cmd) or True,
        )

        assert run_fix_calls == ["fix-uv"]
        assert run_verify_calls == ["verify-uv"]
        assert completed == [{"name": "uv", "reversal": "reversal-uv"}]

    def test_fix_stops_on_decline_and_reports_reversal(self, capsys):
        mod = _load_module("install_agent_factory_loop_decline")
        uv_check = self._fixable(mod, "uv")
        py_check = self._fixable(mod, "managed_python")
        answers = iter(["yes", "n"])
        run_fix_calls = []

        completed = mod.run_fix_loop(
            [uv_check, py_check],
            input_func=lambda p: next(answers),
            run_fix=lambda cmd: run_fix_calls.append(cmd) or (True, ""),
            run_verify=lambda cmd: True,
        )

        assert run_fix_calls == ["fix-uv"]
        assert completed == [{"name": "uv", "reversal": "reversal-uv"}]
        out = capsys.readouterr().out
        assert "reversal-uv" in out

    def test_blank_input_stops_and_skips_fix(self):
        mod = _load_module("install_agent_factory_loop_blank")
        check = self._fixable(mod, "uv")
        run_fix_calls = []

        completed = mod.run_fix_loop(
            [check],
            input_func=lambda p: "",
            run_fix=lambda cmd: run_fix_calls.append(cmd) or (True, ""),
            run_verify=lambda cmd: True,
        )

        assert run_fix_calls == []
        assert completed == []

    def test_cancelled_input_stops_and_skips_fix(self):
        mod = _load_module("install_agent_factory_loop_cancel")
        check = self._fixable(mod, "uv")
        run_fix_calls = []

        def raise_eof(prompt):
            raise EOFError()

        completed = mod.run_fix_loop(
            [check],
            input_func=raise_eof,
            run_fix=lambda cmd: run_fix_calls.append(cmd) or (True, ""),
            run_verify=lambda cmd: True,
        )

        assert run_fix_calls == []
        assert completed == []

    def test_failed_verification_stops_sequence(self, capsys):
        mod = _load_module("install_agent_factory_loop_failverify")
        uv_check = self._fixable(mod, "uv")
        py_check = self._fixable(mod, "managed_python")
        run_fix_calls = []

        completed = mod.run_fix_loop(
            [uv_check, py_check],
            input_func=lambda p: "yes",
            run_fix=lambda cmd: run_fix_calls.append(cmd) or (True, ""),
            run_verify=lambda cmd: False,
        )

        assert run_fix_calls == ["fix-uv"]
        assert completed == []
        out = capsys.readouterr().out
        assert "verification failed" in out.lower()

    def test_unsupported_check_never_offered_fix(self):
        mod = _load_module("install_agent_factory_loop_unsupported")
        check = self._unfixable(mod, "git")
        prompted = []

        def spy_input(prompt):
            prompted.append(prompt)
            return "yes"

        completed = mod.run_fix_loop(
            [check],
            input_func=spy_input,
            run_fix=lambda cmd: (_ for _ in ()).throw(
                AssertionError("run_fix should not be called")),
            run_verify=lambda cmd: True,
        )

        assert prompted == []
        assert completed == []

    def test_passed_checks_are_skipped(self):
        mod = _load_module("install_agent_factory_loop_passed")
        check = self._fixable(mod, "uv", passed=True)
        prompted = []

        completed = mod.run_fix_loop(
            [check],
            input_func=lambda p: prompted.append(p) or "yes",
            run_fix=lambda cmd: (_ for _ in ()).throw(
                AssertionError("run_fix should not be called")),
            run_verify=lambda cmd: True,
        )

        assert prompted == []
        assert completed == []

    def test_uv_recovery_guidance_names_restart_and_reversal(self, capsys):
        """Recovery guidance is per-prerequisite (uv)."""
        mod = _load_module("install_agent_factory_loop_recover_uv")
        check = self._fixable(mod, "uv")

        mod.run_fix_loop(
            [check], input_func=lambda p: "yes",
            run_fix=lambda cmd: (True, ""), run_verify=lambda cmd: False,
        )
        out = capsys.readouterr().out
        assert "Restart your shell" in out
        assert "uv self uninstall" in out

    def test_managed_python_recovery_guidance_names_manual_install(self, capsys):
        """Recovery guidance is per-prerequisite (managed Python)."""
        mod = _load_module("install_agent_factory_loop_recover_py")
        check = self._fixable(mod, "managed_python")

        mod.run_fix_loop(
            [check], input_func=lambda p: "yes",
            run_fix=lambda cmd: (True, ""), run_verify=lambda cmd: False,
        )
        out = capsys.readouterr().out
        assert "uv python install 3.10" in out
        assert "uv python uninstall 3.10" in out


class TestFixLoopIntegration:
    """End-to-end: the fix loop is wired into the real bootstrap CLI."""

    def _path_without_uv(self) -> str:
        """PATH covering git/bash/python3 but not uv, so preflight reports
        uv (and managed Python, which shells out through uv) missing."""
        return "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

    def test_missing_uv_offers_fix_then_blank_stops_without_running_it(
            self, tmp_path):
        source = _make_source(tmp_path)
        target = _make_target(tmp_path, interfaces=[".claude"])
        result = _run(
            ["--from-local", str(source), "--target", str(target)],
            input_text="\n",
            env={"PATH": self._path_without_uv()},
        )

        out = result.stdout
        assert "Ready with limitations" in out
        assert "Fix available for uv" in out
        assert "curl -LsSf https://astral.sh/uv/install.sh | sh" in out
        assert "Purpose" in out and "Reversal" in out and "Verification" in out
        # Declined at the first fix prompt: nothing installed.
        assert not (target / ".agent-factory" / "install.json").exists()
