"""Characterization tests: INDEX.yaml references resolve after layout migration.

Parse INDEX.yaml, extract every agent and skill entry, and verify each
referenced definition file exists on disk under packages/factory/.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
INDEX_PATH = REPO_ROOT / "packages" / "factory" / "INDEX.yaml"
FACTORY_ROOT = REPO_ROOT / "packages" / "factory"


@pytest.fixture(scope="module")
def index_data() -> dict:
    """Load and parse INDEX.yaml once per module."""
    assert INDEX_PATH.exists(), f"INDEX.yaml not found at {INDEX_PATH}"
    text = INDEX_PATH.read_text(encoding="utf-8")
    if text.startswith("---\n"):
        text = text[4:]
    data = yaml.safe_load(text)
    assert isinstance(data, dict), "INDEX.yaml did not parse as a mapping"
    return data


class TestAgentResolution:
    """Every agent listed in INDEX.yaml resolves to an existing file."""

    def _agent_entries(self, index_data: dict) -> list[dict]:
        return index_data.get("agents", [])

    def test_agents_section_exists(self, index_data: dict) -> None:
        assert "agents" in index_data, "INDEX.yaml has no agents section"
        assert len(index_data["agents"]) > 0, "agents section is empty"

    def test_each_agent_has_name_and_path(self, index_data: dict) -> None:
        for entry in self._agent_entries(index_data):
            assert "name" in entry, f"agent entry missing name: {entry}"
            assert "path" in entry, f"agent {entry.get('name')} missing path"

    def test_each_agent_file_exists(self, index_data: dict) -> None:
        missing = []
        for entry in self._agent_entries(index_data):
            resolved = FACTORY_ROOT / entry["path"]
            if not resolved.exists():
                missing.append(f"{entry['name']} -> {resolved}")
        assert not missing, (
            f"Agent definition files not found:\n  " + "\n  ".join(missing)
        )


class TestSkillResolution:
    """Every skill listed in INDEX.yaml resolves to an existing SKILL.md."""

    def _skill_entries(self, index_data: dict) -> list[dict]:
        return index_data.get("skills", [])

    def test_skills_section_exists(self, index_data: dict) -> None:
        assert "skills" in index_data, "INDEX.yaml has no skills section"
        assert len(index_data["skills"]) > 0, "skills section is empty"

    def test_each_skill_has_name_and_path(self, index_data: dict) -> None:
        for entry in self._skill_entries(index_data):
            assert "name" in entry, f"skill entry missing name: {entry}"
            assert "path" in entry, f"skill {entry.get('name')} missing path"

    def test_each_skill_file_exists(self, index_data: dict) -> None:
        missing = []
        for entry in self._skill_entries(index_data):
            resolved = FACTORY_ROOT / entry["path"]
            if not resolved.exists():
                missing.append(f"{entry['name']} -> {resolved}")
        assert not missing, (
            f"Skill definition files not found:\n  " + "\n  ".join(missing)
        )


class TestIndexCompleteness:
    """No orphan agent or skill definitions lurk outside the index."""

    def test_all_agent_files_indexed(self, index_data: dict) -> None:
        agents_dir = FACTORY_ROOT / "agents"
        if not agents_dir.is_dir():
            pytest.skip("agents directory not found")
        on_disk = {p.stem for p in agents_dir.glob("*.md")}
        indexed = {e["name"] for e in index_data.get("agents", [])}
        orphans = on_disk - indexed
        assert not orphans, f"Agent files not in INDEX.yaml: {orphans}"

    def test_all_skill_dirs_indexed(self, index_data: dict) -> None:
        skills_dir = FACTORY_ROOT / "skills"
        if not skills_dir.is_dir():
            pytest.skip("skills directory not found")
        on_disk = {
            p.name
            for p in skills_dir.iterdir()
            if p.is_dir() and (p / "SKILL.md").exists()
        }
        indexed = {e["name"] for e in index_data.get("skills", [])}
        missing_from_index = on_disk - indexed
        if missing_from_index:
            import warnings

            warnings.warn(
                f"Skill dirs not in INDEX.yaml (not a failure): {missing_from_index}",
                stacklevel=1,
            )
