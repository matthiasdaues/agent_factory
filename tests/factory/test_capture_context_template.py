"""The capture-context template passes concern-lint in a fresh install (BUG-0047).

The greenfield and brownfield planning gates run concern-lint on the file
this template produces, so every default Read: path must resolve.
"""

from __future__ import annotations

import json
import re
import subprocess

from conftest import REPO_ROOT, SOURCE_SCRIPTS_DIR

SKILL = REPO_ROOT / "packages" / "factory" / "skills" / "capture-context" / "SKILL.md"


def _cross_cutting_template() -> str:
    text = SKILL.read_text(encoding="utf-8")
    block = re.search(r"```markdown\n(# Agent Context\n.*?)```", text, re.S).group(1)
    return block.split("## Technical concerns")[0]


def test_default_read_paths_resolve_in_an_installed_project(tmp_path):
    (tmp_path / ".agent-factory").mkdir()
    (tmp_path / ".agent-factory" / "factory").symlink_to(REPO_ROOT / "packages" / "factory")
    (tmp_path / ".pre-commit-config.yaml").write_text("repos: []\n")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "agent-context.md").write_text(_cross_cutting_template())

    result = subprocess.run(
        [str(SOURCE_SCRIPTS_DIR / "concern-lint"), "--root", str(tmp_path), "--format", "json"],
        capture_output=True, text=True, check=False,
    )

    output = result.stdout or result.stderr
    findings = json.loads(output) if output.strip().startswith(("[", "{")) else output
    assert "CTX-PATHS" not in json.dumps(findings), findings
