"""Regression tests for install-agent-factory instruction headers.

Covers BUG-0077 (header written through a link into the installed factory)
and BUG-0078 (Claude include paths that point outside the project).
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

from conftest import REPO_ROOT

SCRIPT = REPO_ROOT / "packages" / "factory" / "scripts" / "install-agent-factory"

BEGIN = "<!-- >>> agent_factory orientation >>>"

# init-factory stub that links the root AGENTS.md into the installed
# factory, the way the real init-factory does for Codex, Pi, and Copilot.
_LINKING_INIT_FACTORY = textwrap.dedent("""\
    #!/usr/bin/env python3
    import argparse, json, os
    from pathlib import Path
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path)
    ap.add_argument("--target", type=Path)
    ap.add_argument("--cli", nargs="+")
    ap.add_argument("--project-name")
    args = ap.parse_args()
    target = args.target
    config = target / ".agent-factory" / "factory" / "config"
    config.mkdir(parents=True, exist_ok=True)
    (config / "AGENTS.md").write_text("# Factory routing\\n")
    (config / "AGENTS.codex.md").write_text("# Codex orientation\\n")
    os.symlink(".agent-factory/factory/config/AGENTS.md",
               target / "AGENTS.md")
    manifest = {
        "version": 1,
        "orientation": {"AGENTS.md": "linked"},
        "orientation_orig_final_newline": {},
        "remove_paths": ["AGENTS.md"],
    }
    (target / ".agent-factory" / "install.json").write_text(
        json.dumps(manifest, indent=2) + "\\n")
    print("init-factory: done")
""")


def _load_module():
    loader = importlib.machinery.SourceFileLoader(
        "install_agent_factory_bootstrap", str(SCRIPT))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


# init-factory stub that installs the Codex orientation and links nothing.
_PLAIN_INIT_FACTORY = textwrap.dedent("""\
    #!/usr/bin/env python3
    import argparse, json
    from pathlib import Path
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path)
    ap.add_argument("--target", type=Path)
    ap.add_argument("--cli", nargs="+")
    ap.add_argument("--project-name")
    args = ap.parse_args()
    config = args.target / ".agent-factory" / "factory" / "config"
    config.mkdir(parents=True, exist_ok=True)
    (config / "AGENTS.codex.md").write_text("# Codex orientation\\n")
    manifest = {"version": 1, "orientation": {},
                "orientation_orig_final_newline": {}}
    (args.target / ".agent-factory" / "install.json").write_text(
        json.dumps(manifest, indent=2) + "\\n")
    print("init-factory: done")
""")


def _make_source(tmp_path: Path, init_script: str = _LINKING_INIT_FACTORY
                 ) -> Path:
    source = tmp_path / "factory-src"
    scripts = source / "packages" / "factory" / "scripts"
    scripts.mkdir(parents=True)
    (source / "packages" / "factory" / "VERSION").write_text("0.12.0\n")
    init = scripts / "init-factory"
    init.write_text(init_script)
    os.chmod(init, 0o755)
    return source


def _make_target(tmp_path: Path, dot_dir: str) -> Path:
    target = tmp_path / "project"
    target.mkdir()
    subprocess.run(["git", "init", str(target)], check=True,
                   capture_output=True)
    (target / dot_dir).mkdir()
    return target


def _install(source: Path, target: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--from-local", str(source),
         "--target", str(target)],
        capture_output=True, text=True, input="\nyes\n", timeout=60,
    )


class TestLinkedInstructionFiles:
    """BUG-0077: links that init-factory created stay untouched."""

    def test_BUG_0077_header_not_written_through_factory_link(self, tmp_path):
        source = _make_source(tmp_path)
        target = _make_target(tmp_path, ".codex")

        result = _install(source, target)

        assert result.returncode == 0, result.stderr
        routing = target / ".agent-factory" / "factory" / "config" / "AGENTS.md"
        assert (target / "AGENTS.md").is_symlink()
        assert routing.read_text() == "# Factory routing\n"
        manifest = json.loads(
            (target / ".agent-factory" / "install.json").read_text())
        assert manifest["orientation"]["AGENTS.md"]["status"] == "linked"

    def test_BUG_0077_discovery_skips_links_inside_target(self, tmp_path):
        mod = _load_module()
        target = tmp_path / "project"
        (target / "docs").mkdir(parents=True)
        real = target / "docs" / "AGENTS.md"
        real.write_text("# Docs\n")
        (target / "AGENTS.md").symlink_to("docs/AGENTS.md")

        found = mod.discover_instruction_files(target)

        assert found == [real]


class TestClaudeIncludePaths:
    """BUG-0078: each include path is relative to the file it sits in."""

    def _block(self, tmp_path: Path, rel: str) -> str:
        mod = _load_module()
        target = tmp_path / "project"
        filepath = target / rel
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text("# Agents\n")
        return mod._build_orientation_block(target, filepath, "claude")

    def test_BUG_0078_root_agents_md_includes_resolve_inside_project(
            self, tmp_path):
        block = self._block(tmp_path, "AGENTS.md")

        assert "@.agent-factory/factory/config/AGENTS.claude.md\n" in block
        assert "@docs/agent-context.md\n" in block
        assert "@../" not in block

    def test_BUG_0078_nested_agents_md_includes_climb_to_project_root(
            self, tmp_path):
        block = self._block(tmp_path, "packages/web/AGENTS.md")

        assert ("@../../.agent-factory/factory/config/AGENTS.claude.md\n"
                in block)
        assert "@../../docs/agent-context.md\n" in block


def _load_update_factory():
    from conftest import load_script
    return load_script("update-factory")


class TestUpdateKeepsClaudeIncludePaths:
    """BUG-0078: update-factory builds the same per-file block as the
    installer, so an update never writes the old broken includes back."""

    def test_BUG_0078_update_and_installer_share_include_list(self):
        inst = _load_module()
        uf = _load_update_factory()

        assert uf.ORIENTATION_INCLUDE == inst.ORIENTATION_INCLUDE

    def test_BUG_0078_update_builds_the_installer_block_per_file(
            self, tmp_path):
        inst = _load_module()
        uf = _load_update_factory()
        target = tmp_path / "project"
        source = tmp_path / "source"
        for rel in ("AGENTS.md", "packages/web/AGENTS.md",
                    "a/b/c/AGENTS.md"):
            filepath = target / rel
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.write_text("# Agents\n")

            installed = inst._build_orientation_block(
                target, filepath, "claude")
            candidate = uf._candidate_orientation_block(
                source, "claude", target=target, rel=rel)

            assert candidate == installed, rel

    def test_BUG_0078_install_then_update_leaves_header_unchanged(
            self, tmp_path, monkeypatch):
        inst = _load_module()
        uf = _load_update_factory()
        target = tmp_path / "project"
        factory = target / ".agent-factory" / "factory"
        (factory / "scripts").mkdir(parents=True)
        (factory / "scripts" / "step-guard").write_text("pass\n")
        uf._write_checksums(target, factory)
        source = tmp_path / "source"
        (source / "packages" / "factory").mkdir(parents=True)
        (source / "packages" / "factory" / "VERSION").write_text("1.1.0\n")

        orientation = {}
        before = {}
        for rel in ("AGENTS.md", "packages/web/AGENTS.md"):
            filepath = target / rel
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.write_text("# mine\n")
            injection = inst.inject_header(filepath, target, "claude")
            orientation[rel] = {
                "status": "injected",
                "block_digest": injection["block_digest"],
                "orig_final_newline": True,
            }
            before[rel] = filepath.read_bytes()
        (target / uf.MANIFEST_PATH).write_text(json.dumps({
            "factory_version": "1.0.0", "cli": "claude",
            "source_selector": "local", "factory_source": str(source),
            "orientation": orientation,
        }))
        monkeypatch.setattr(uf, "get_update_consent", lambda *a, **kw: True)
        monkeypatch.setattr(uf, "_run_init", lambda src, tgt: 0)

        assert uf.main(["--target", str(target)]) == 0

        for rel, content in before.items():
            assert (target / rel).read_bytes() == content, rel


class TestDeveloperLinkedInstructionFiles:
    """BUG-0077: a developer's own link inside the project keeps its header;
    only links out of the project or into the installed factory are
    skipped."""

    def test_BUG_0077_discovery_keeps_developer_link(self, tmp_path):
        mod = _load_module()
        target = tmp_path / "project"
        target.mkdir()
        (target / "CLAUDE.md").write_text("# mine\n")
        (target / "AGENTS.md").symlink_to("CLAUDE.md")

        found = mod.discover_instruction_files(target)

        assert found == [target / "AGENTS.md"]

    def test_BUG_0077_discovery_skips_link_out_of_project(self, tmp_path):
        mod = _load_module()
        outside = tmp_path / "elsewhere.md"
        outside.write_text("# not ours\n")
        target = tmp_path / "project"
        target.mkdir()
        (target / "AGENTS.md").symlink_to(outside)

        assert mod.discover_instruction_files(target) == []

    def test_BUG_0077_install_writes_header_through_developer_link(
            self, tmp_path):
        source = _make_source(tmp_path, _PLAIN_INIT_FACTORY)
        target = _make_target(tmp_path, ".codex")
        (target / "CLAUDE.md").write_text("# mine\n")
        (target / "AGENTS.md").symlink_to("CLAUDE.md")

        result = _install(source, target)

        assert result.returncode == 0, result.stderr
        assert "Instruction files to update:" in result.stdout
        assert "    AGENTS.md\n" in result.stdout
        assert (target / "AGENTS.md").is_symlink()
        content = (target / "CLAUDE.md").read_text()
        assert content.startswith(BEGIN)
        assert content.endswith("# mine\n")

    def test_BUG_0077_update_discovery_matches_installer(self, tmp_path):
        inst = _load_module()
        uf = _load_update_factory()
        target = tmp_path / "project"
        (target / "docs").mkdir(parents=True)
        (target / "web").mkdir()
        (target / ".agent-factory" / "factory" / "config").mkdir(parents=True)
        (target / ".agent-factory" / "factory" / "config" / "AGENTS.md"
         ).write_text("# Factory routing\n")
        outside = tmp_path / "elsewhere.md"
        outside.write_text("# not ours\n")
        (target / "CLAUDE.md").write_text("# mine\n")
        (target / "docs" / "AGENTS.md").write_text("# Docs\n")
        (target / "AGENTS.md").symlink_to("CLAUDE.md")
        (target / "web" / "AGENTS.md").symlink_to("../docs/AGENTS.md")
        (target / "docs" / "copilot-instructions.md").symlink_to(outside)
        (target / "web" / "copilot-instructions.md").symlink_to(
            "../.agent-factory/factory/config/AGENTS.md")

        expected = [p.relative_to(target).as_posix()
                    for p in inst.discover_instruction_files(target)]

        assert expected == ["AGENTS.md", "docs/AGENTS.md"]
        assert uf._discover_instruction_files(target) == expected
