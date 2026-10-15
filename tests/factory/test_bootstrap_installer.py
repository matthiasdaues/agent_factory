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


def _make_source(tmp_path: Path) -> Path:
    source = tmp_path / "factory-src"
    scripts = source / "packages" / "factory" / "scripts"
    scripts.mkdir(parents=True)
    (source / "packages" / "factory" / "VERSION").write_text("0.12.0\n")
    init = scripts / "init-factory"
    init.write_text(_LINKING_INIT_FACTORY)
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
