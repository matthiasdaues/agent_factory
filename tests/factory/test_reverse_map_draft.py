"""spec-lint refuses a scope map that reverse-map wrote as a draft (BUG-0096).

Unattended reverse-map marks its scope map with `status: draft` in the
frontmatter. The brownfield Stage 1 exit must not pass until a stakeholder
has confirmed the map, so spec-lint reports the marker as an error.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

from conftest import REPO_ROOT, SOURCE_SCRIPTS_DIR, load_script

sl = load_script("spec-lint")

BODY = (
    "# Scope Map\n\n"
    "| Rule | Status | Confidence | Sources | Feature Link |\n"
    "| ---- | ------ | ---------- | ------- | ------------ |\n"
)


def _spec_dir(tmp_path: Path, frontmatter: str) -> Path:
    spec = tmp_path / "spec"
    supp = spec / "supplementary_specs"
    supp.mkdir(parents=True)
    (supp / "entity-model.md").write_text("# Entity Model\n", encoding="utf-8")
    (spec / "scope-map.md").write_text(frontmatter + BODY, encoding="utf-8")
    return spec


def _codes(spec: Path) -> list[str]:
    findings, _ = sl.run(spec, Path("missing-context.md"), False)
    return [f.code for f in findings if f.severity == "error"]


def test_draft_scope_map_is_reported_and_fails_the_gate(tmp_path):
    spec = _spec_dir(tmp_path, "---\nscope: global\nstatus: draft\n---\n\n")
    assert "SCOPE001" in _codes(spec)
    assert sl.main(["--spec-dir", str(spec), "--context", "none.md"]) == 1


@pytest.mark.parametrize(
    "frontmatter",
    [
        "---\nscope: global\nstatus: confirmed\n---\n\n",
        "---\nscope: global\n---\n\n",
        "",
    ],
    ids=["confirmed", "marker-removed", "no-frontmatter"],
)
def test_confirmed_scope_map_passes(tmp_path, frontmatter):
    spec = _spec_dir(tmp_path, frontmatter)
    assert "SCOPE001" not in _codes(spec)
    assert sl.main(["--spec-dir", str(spec), "--context", "none.md"]) == 0


def test_draft_word_in_body_is_not_the_marker(tmp_path):
    spec = _spec_dir(tmp_path, "---\nscope: global\n---\n\nstatus: draft\n\n")
    assert "SCOPE001" not in _codes(spec)


# --- The documented Stage 1 exit command (review iteration 2) -----------------

PLAYBOOK = REPO_ROOT / "packages" / "factory" / "playbooks" / "brownfield-onboarding.md"
SKILL = REPO_ROOT / "packages" / "factory" / "skills" / "reverse-map" / "SKILL.md"
INSTALLED_SPEC_LINT = ".agent-factory/factory/scripts/spec-lint"


def _stage1_exit_command() -> str:
    """Return the scope-map check command exactly as Step 2.6 documents it."""
    text = PLAYBOOK.read_text(encoding="utf-8")
    section = text.split("### Step 2.6", 1)[1].split("### Stage 1 Exit Point", 1)[0]
    commands = [c for c in re.findall(r"`([^`]+)`", section) if INSTALLED_SPEC_LINT in c]
    assert len(commands) == 1, commands
    return commands[0]


def _stage1_project(tmp_path: Path, frontmatter: str) -> Path:
    """A Stage 1 project: a scope map, but no entity model yet (STRUCT005)."""
    spec = tmp_path / "docs" / "spec"
    spec.mkdir(parents=True)
    (spec / "scope-map.md").write_text(frontmatter + BODY, encoding="utf-8")
    return tmp_path


def _run_exit_check(project: Path, script: Path | None = None) -> subprocess.CompletedProcess:
    script = script or SOURCE_SCRIPTS_DIR / "spec-lint"
    command = _stage1_exit_command().replace(INSTALLED_SPEC_LINT, str(script))
    return subprocess.run(
        ["bash", "-c", command], cwd=project, capture_output=True, text=True, check=False
    )


def test_stage1_exit_command_fails_on_a_draft_scope_map(tmp_path):
    project = _stage1_project(tmp_path, "---\nscope: global\nstatus: draft\n---\n\n")
    assert _run_exit_check(project).returncode != 0


def test_stage1_exit_command_passes_a_confirmed_scope_map_despite_other_errors(tmp_path):
    project = _stage1_project(tmp_path, "---\nscope: global\nstatus: confirmed\n---\n\n")
    spec_dir = project / "docs" / "spec"
    findings, _ = sl.run(spec_dir, Path("missing-context.md"), False)
    assert "STRUCT005" in [f.code for f in findings]
    assert _run_exit_check(project).returncode == 0


def test_stage1_exit_command_fails_when_spec_lint_is_missing(tmp_path):
    project = _stage1_project(tmp_path, "---\nscope: global\nstatus: draft\n---\n\n")
    assert _run_exit_check(project, tmp_path / "no-such-spec-lint").returncode != 0


def test_stage1_exit_command_fails_when_spec_lint_crashes_silently(tmp_path):
    project = _stage1_project(tmp_path, "---\nscope: global\nstatus: draft\n---\n\n")
    crashing = tmp_path / "crashing-spec-lint"
    crashing.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
    crashing.chmod(0o755)
    assert _run_exit_check(project, crashing).returncode != 0


def test_unattended_frontmatter_example_passes_scope_lint(tmp_path):
    text = SKILL.read_text(encoding="utf-8").split("## Unattended mode", 1)[1]
    example = re.search(r"```markdown\n(.*?)```", text, re.S).group(1)
    spec = tmp_path / "docs" / "spec"
    spec.mkdir(parents=True)
    (spec / "scope-map.md").write_text(example + BODY, encoding="utf-8")
    assert load_script("scope-lint").main(["--base-dir", str(tmp_path)]) == 0
