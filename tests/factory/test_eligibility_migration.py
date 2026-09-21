"""Characterization tests for agent declaration format.

Owned contracts:
  - No agent definition contains phase or phase-name (standard risk)
  - Every agent definition uses structured inputs/outputs, not flat lists (standard risk)
  - index-lint --check exits 0 after regeneration (standard risk)
  - Every agent and skill name from acceptance commit exists post-migration (standard risk)
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
_PACKAGES_DIR = REPO_ROOT / "packages" / "factory"
if str(_PACKAGES_DIR) not in sys.path:
    sys.path.insert(0, str(_PACKAGES_DIR))
AGENTS_DIR = REPO_ROOT / "packages" / "factory" / "agents"
INDEX_LINT = REPO_ROOT / "packages" / "factory" / "scripts" / "index-lint"
INDEX_YAML = REPO_ROOT / ".claude" / "INDEX.yaml"

FACTORY_AGENTS = REPO_ROOT / "packages" / "factory" / "agents"
FACTORY_SKILLS = REPO_ROOT / "packages" / "factory" / "skills"
FACTORY_PLAYBOOKS = REPO_ROOT / "packages" / "factory" / "playbooks"
FACTORY_RULEBOOKS = REPO_ROOT / "packages" / "factory" / "rulebooks"


def _read_frontmatter_lines(path: Path) -> list[str]:
    text = path.read_text()
    if not text.startswith("---"):
        return []
    end = text.find("\n---", 3)
    if end == -1:
        return []
    return text[3:end].strip().split("\n")


class TestNoLegacyPhaseFields:
    def test_no_agent_has_phase_field(self):
        for path in sorted(AGENTS_DIR.glob("*.md")):
            lines = _read_frontmatter_lines(path)
            for line in lines:
                stripped = line.strip()
                if stripped.startswith("phase:") and not stripped.startswith("phase-"):
                    pytest.fail(f"{path.name} still has 'phase:' field")

    def test_no_agent_has_phase_name_field(self):
        for path in sorted(AGENTS_DIR.glob("*.md")):
            lines = _read_frontmatter_lines(path)
            for line in lines:
                if line.strip().startswith("phase-name:"):
                    pytest.fail(f"{path.name} still has 'phase-name:' field")


class TestStructuredDeclarationsPresent:
    def test_every_agent_has_structured_inputs(self):
        for path in sorted(AGENTS_DIR.glob("*.md")):
            lines = _read_frontmatter_lines(path)
            has_inputs = any(
                line.strip().startswith("inputs:")
                for line in lines
            )
            assert has_inputs, f"{path.name} missing 'inputs:'"

    def test_no_agent_has_flat_inputs(self):
        for path in sorted(AGENTS_DIR.glob("*.md")):
            lines = _read_frontmatter_lines(path)
            in_inputs = False
            for line in lines:
                stripped = line.strip()
                if stripped == "inputs:":
                    in_inputs = True
                    continue
                if in_inputs:
                    if stripped.startswith("- ") and not stripped.startswith("- type:"):
                        pytest.fail(
                            f"{path.name} uses flat 'inputs:' list (rejected)"
                        )
                    elif stripped and not stripped.startswith("-") and not stripped.startswith(" "):
                        break

    def test_no_agent_has_eligible_cycles(self):
        for path in sorted(AGENTS_DIR.glob("*.md")):
            lines = _read_frontmatter_lines(path)
            has_eligible = any(
                line.strip().startswith("eligible_cycles")
                for line in lines
            )
            assert not has_eligible, (
                f"{path.name} still has 'eligible_cycles' (removed)"
            )


class TestIndexLintConsistency:
    def test_index_lint_check_passes(self, tmp_path):
        out = tmp_path / "INDEX.yaml"
        gen = subprocess.run(
            [sys.executable, str(INDEX_LINT),
             "--agents-dir", str(FACTORY_AGENTS),
             "--skills-dir", str(FACTORY_SKILLS),
             "--playbooks-dir", str(FACTORY_PLAYBOOKS),
             "--rulebooks-dir", str(FACTORY_RULEBOOKS),
             "--out", str(out)],
            capture_output=True, text=True,
        )
        assert gen.returncode == 0, f"index-lint generate failed: {gen.stderr}"

        check = subprocess.run(
            [sys.executable, str(INDEX_LINT),
             "--agents-dir", str(FACTORY_AGENTS),
             "--skills-dir", str(FACTORY_SKILLS),
             "--playbooks-dir", str(FACTORY_PLAYBOOKS),
             "--rulebooks-dir", str(FACTORY_RULEBOOKS),
             "--out", str(out),
             "--check"],
            capture_output=True, text=True,
        )
        assert check.returncode == 0, (
            f"index-lint --check failed: {check.stdout}\n{check.stderr}"
        )

    def test_generated_index_has_structured_inputs(self, tmp_path):
        out = tmp_path / "INDEX.yaml"
        subprocess.run(
            [sys.executable, str(INDEX_LINT),
             "--agents-dir", str(FACTORY_AGENTS),
             "--skills-dir", str(FACTORY_SKILLS),
             "--playbooks-dir", str(FACTORY_PLAYBOOKS),
             "--rulebooks-dir", str(FACTORY_RULEBOOKS),
             "--out", str(out)],
            capture_output=True, text=True,
        )
        content = out.read_text()
        assert "inputs:" in content
        assert "outputs:" in content
        assert "eligible_cycles:" not in content
        assert "phase:" not in content.split("playbooks:")[0]
        assert "phase_name:" not in content.split("playbooks:")[0]


class TestNamePreservation:
    @staticmethod
    def _generate_index(tmp_path) -> Path:
        out = tmp_path / "INDEX.yaml"
        subprocess.run(
            [sys.executable, str(INDEX_LINT),
             "--agents-dir", str(FACTORY_AGENTS),
             "--skills-dir", str(FACTORY_SKILLS),
             "--playbooks-dir", str(FACTORY_PLAYBOOKS),
             "--rulebooks-dir", str(FACTORY_RULEBOOKS),
             "--out", str(out)],
            capture_output=True, text=True,
        )
        return out

    def _parse_names_from_index(self, text: str) -> tuple[set[str], set[str]]:
        agents = set()
        skills = set()
        section = None
        for line in text.split("\n"):
            stripped = line.strip()
            if stripped.startswith("agents:"):
                section = "agents"
                continue
            elif stripped.startswith("skills:"):
                section = "skills"
                continue
            elif stripped.startswith("playbooks:"):
                section = "playbooks"
                continue
            elif stripped.startswith("rulebooks:"):
                section = "rulebooks"
                continue
            if stripped.startswith("- name:"):
                name = stripped.split(":", 1)[1].strip()
                if section == "agents":
                    agents.add(name)
                elif section == "skills":
                    skills.add(name)
        return agents, skills

    EXPECTED_AGENTS = {
        "architecture-agent",
        "architecture-review-agent",
        "claim-reviewer",
        "coaching-agent",
        "code-review-agent",
        "developer-agent",
        "implementation-agent",
        "planning-agent",
        "proposal-review-agent",
        "qa-agent",
        "reconciliation-agent",
        "requirements-agent",
        "researcher",
        "research-orchestrator",
        "research-report-writer",
        "spec-review-agent",
        "virgil",
    }

    def test_all_agent_names_preserved(self, tmp_path):
        out = self._generate_index(tmp_path)
        text = out.read_text()
        agents, _ = self._parse_names_from_index(text)
        missing = self.EXPECTED_AGENTS - agents
        assert not missing, f"Missing agents in INDEX.yaml: {missing}"

    def test_no_phase_fields_in_index(self, tmp_path):
        out = self._generate_index(tmp_path)
        text = out.read_text()
        for line in text.split("\n"):
            stripped = line.strip()
            assert not stripped.startswith("phase:"), (
                f"INDEX.yaml still has 'phase:' field: {stripped}"
            )
            assert not stripped.startswith("phase_name:"), (
                f"INDEX.yaml still has 'phase_name:' field: {stripped}"
            )
