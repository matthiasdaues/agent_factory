"""Tests for index-lint — generates factory/INDEX.yaml from agent, skill,
and playbook frontmatter.

Loaded via importlib against the real extensionless script, same idiom as
test_transition_lint.py/test_phase_advance.py. Each test builds a small
fixture tree of agents/skills/playbooks under tmp_path rather than reading
the real factory/ content, so these tests don't drift when real agents or
playbooks are added or reworded.
"""

from __future__ import annotations

import importlib.util
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _ROOT / "factory" / "scripts" / "index-lint"
_loader = SourceFileLoader("index_lint", str(_SCRIPT))
_spec = importlib.util.spec_from_loader("index_lint", _loader)
index_lint = importlib.util.module_from_spec(_spec)
sys.modules["index_lint"] = index_lint
_loader.exec_module(index_lint)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _make_tree(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    agents_dir = tmp_path / "agents"
    skills_dir = tmp_path / "skills"
    playbooks_dir = tmp_path / "playbooks"
    out = tmp_path / "INDEX.yaml"

    _write(
        agents_dir / "requirements-agent.md",
        """---
name: requirements-agent
title: Requirements Agent
phase: 1
phase-name: Requirements
description: >-
  Capture a project vision and produce a complete specification.
---
""",
    )
    _write(
        agents_dir / "developer-agent.md",
        """---
name: developer-agent
title: Developer Agent
description: Implement a single backlog story using TDD.
---
""",
    )
    _write(
        skills_dir / "write-prd" / "SKILL.md",
        """---
name: write-prd
category: requirements
description: Synthesise a PRD from clarified requirements.
---
""",
    )
    _write(
        playbooks_dir / "bug-fix.md",
        """---
title: Bug Fix Playbook
category: orchestration
---

# Bug Fix Playbook

Operational procedure for **fixing defects** in production or development.

## Step 1

**Agent**: `developer-agent`

## Step 2

**Agent**: `qa-agent`
""",
    )
    _write(
        playbooks_dir / "poc-spike.md",
        """---
title: Proof-of-Concept Spike Playbook
category: orchestration
---

# Proof-of-Concept Spike Playbook

Operational procedure for **getting from an idea to something you can look at and see run**.

No agent chain here.
""",
    )

    return agents_dir, skills_dir, playbooks_dir, out


class TestRenderIndex:
    def test_agents_grouped_and_sorted_by_phase(self, tmp_path):
        agents_dir, skills_dir, playbooks_dir, out = _make_tree(tmp_path)

        content, warnings = index_lint.render_index(
            agents_dir, skills_dir, playbooks_dir, out
        )

        assert "name: requirements-agent" in content
        assert "phase: 1" in content
        assert "phase_name: Requirements" in content
        assert "name: developer-agent" in content
        assert warnings == []

    def test_playbook_agent_sequence_derived_from_agent_lines(self, tmp_path):
        agents_dir, skills_dir, playbooks_dir, out = _make_tree(tmp_path)

        content, _ = index_lint.render_index(agents_dir, skills_dir, playbooks_dir, out)

        bug_fix_start = content.index("name: bug-fix")
        bug_fix_block = content[bug_fix_start : bug_fix_start + 400]
        assert "agents:" in bug_fix_block
        assert "- developer-agent" in bug_fix_block
        assert "- qa-agent" in bug_fix_block

    def test_playbook_description_derived_from_first_paragraph(self, tmp_path):
        agents_dir, skills_dir, playbooks_dir, out = _make_tree(tmp_path)

        content, _ = index_lint.render_index(agents_dir, skills_dir, playbooks_dir, out)

        assert (
            "description: Operational procedure for fixing defects in production or development."
            in content
        )

    def test_playbook_with_no_agent_lines_has_no_agents_key(self, tmp_path):
        agents_dir, skills_dir, playbooks_dir, out = _make_tree(tmp_path)

        content, _ = index_lint.render_index(agents_dir, skills_dir, playbooks_dir, out)

        poc_start = content.index("name: poc-spike")
        poc_block = content[poc_start:]
        # poc-spike is the last playbook in this fixture — nothing after it
        # should introduce an "agents:" key for its own entry.
        assert "agents:" not in poc_block

    def test_fsm_companion_detected_when_present(self, tmp_path):
        agents_dir, skills_dir, playbooks_dir, out = _make_tree(tmp_path)
        _write(playbooks_dir / "bug-fix.fsm.yml", "version: 1.0.0\n")

        content, _ = index_lint.render_index(agents_dir, skills_dir, playbooks_dir, out)

        bug_fix_start = content.index("name: bug-fix")
        bug_fix_block = content[bug_fix_start : bug_fix_start + 400]
        assert "fsm: playbooks/bug-fix.fsm.yml" in bug_fix_block

    def test_skill_without_category_warns(self, tmp_path):
        agents_dir, skills_dir, playbooks_dir, out = _make_tree(tmp_path)
        _write(
            skills_dir / "uncategorised-skill" / "SKILL.md",
            "---\nname: uncategorised-skill\ndescription: No category set.\n---\n",
        )

        _, warnings = index_lint.render_index(
            agents_dir, skills_dir, playbooks_dir, out
        )

        assert any("uncategorised-skill" in w for w in warnings)

    def test_description_with_colon_is_quoted(self, tmp_path):
        agents_dir, skills_dir, playbooks_dir, out = _make_tree(tmp_path)
        _write(
            agents_dir / "colon-agent.md",
            '---\nname: colon-agent\ntitle: "Colon: Agent"\ndescription: "Has a colon: right here."\n---\n',
        )

        content, _ = index_lint.render_index(agents_dir, skills_dir, playbooks_dir, out)

        assert 'description: "Has a colon: right here."' in content


class TestMainCLI:
    def test_writes_then_check_mode_passes(self, tmp_path, capsys):
        agents_dir, skills_dir, playbooks_dir, out = _make_tree(tmp_path)

        rc = index_lint.main(
            [
                "--agents-dir",
                str(agents_dir),
                "--skills-dir",
                str(skills_dir),
                "--playbooks-dir",
                str(playbooks_dir),
                "--out",
                str(out),
            ]
        )
        assert rc == 0
        assert out.exists()

        rc_check = index_lint.main(
            [
                "--agents-dir",
                str(agents_dir),
                "--skills-dir",
                str(skills_dir),
                "--playbooks-dir",
                str(playbooks_dir),
                "--out",
                str(out),
                "--check",
            ]
        )
        assert rc_check == 0

    def test_check_mode_fails_when_stale(self, tmp_path):
        agents_dir, skills_dir, playbooks_dir, out = _make_tree(tmp_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("stale content\n", encoding="utf-8")

        rc = index_lint.main(
            [
                "--agents-dir",
                str(agents_dir),
                "--skills-dir",
                str(skills_dir),
                "--playbooks-dir",
                str(playbooks_dir),
                "--out",
                str(out),
                "--check",
            ]
        )
        assert rc == 1

    def test_second_write_is_noop(self, tmp_path):
        agents_dir, skills_dir, playbooks_dir, out = _make_tree(tmp_path)
        argv = [
            "--agents-dir",
            str(agents_dir),
            "--skills-dir",
            str(skills_dir),
            "--playbooks-dir",
            str(playbooks_dir),
            "--out",
            str(out),
        ]

        assert index_lint.main(argv) == 0
        first_content = out.read_text(encoding="utf-8")
        assert index_lint.main(argv) == 0
        assert out.read_text(encoding="utf-8") == first_content


class TestRealFactoryIndex:
    """Sanity check against the real factory/ tree, proving the checked-in
    factory/INDEX.yaml actually matches what index-lint would generate."""

    def test_real_index_is_up_to_date(self):
        real_agents = _ROOT / "factory" / "agents"
        real_skills = _ROOT / "factory" / "skills"
        real_playbooks = _ROOT / "factory" / "playbooks"
        real_out = _ROOT / "factory" / "INDEX.yaml"

        rc = index_lint.main(
            [
                "--agents-dir",
                str(real_agents),
                "--skills-dir",
                str(real_skills),
                "--playbooks-dir",
                str(real_playbooks),
                "--out",
                str(real_out),
                "--check",
            ]
        )
        assert rc == 0
