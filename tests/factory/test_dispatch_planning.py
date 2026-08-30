"""Contract tests for dispatch plan — wave planning (Layer 2a).

Covers: dependency graph, file-overlap detection, serial chains, wave
assignment, and conservative fallback for zero-expansion globs.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parent.parent.parent / "factory" / "scripts")
)

from dispatch_lib import (
    StoryMeta,
    compute_wave_plan,
    suggest_tier,
)

# ---------------------------------------------------------------------------
# Dependency graph → wave assignment
# ---------------------------------------------------------------------------


class TestDependencyWaves:
    def test_no_deps_all_wave_1(self, tmp_path: Path) -> None:
        stories = [
            StoryMeta(id="ST-001", outputs=["a.py"]),
            StoryMeta(id="ST-002", outputs=["b.py"]),
        ]
        # Create files so globs expand
        (tmp_path / "a.py").touch()
        (tmp_path / "b.py").touch()
        plan = compute_wave_plan(stories, tmp_path)
        assert len(plan.waves) == 1
        assert plan.waves[0]["wave"] == 1
        ids = [s["id"] for s in plan.waves[0]["stories"]]
        assert "ST-001" in ids
        assert "ST-002" in ids

    def test_dependency_chain_sequential_waves(self, tmp_path: Path) -> None:
        stories = [
            StoryMeta(id="ST-001", outputs=["a.py"]),
            StoryMeta(id="ST-002", deps=["ST-001"], outputs=["b.py"]),
        ]
        (tmp_path / "a.py").touch()
        (tmp_path / "b.py").touch()
        plan = compute_wave_plan(stories, tmp_path)
        assert len(plan.waves) == 2
        assert plan.waves[0]["stories"][0]["id"] == "ST-001"
        assert plan.waves[1]["stories"][0]["id"] == "ST-002"

    def test_deep_dependency_chain(self, tmp_path: Path) -> None:
        stories = [
            StoryMeta(id="ST-001", outputs=["a.py"]),
            StoryMeta(id="ST-002", deps=["ST-001"], outputs=["b.py"]),
            StoryMeta(id="ST-003", deps=["ST-002"], outputs=["c.py"]),
        ]
        (tmp_path / "a.py").touch()
        (tmp_path / "b.py").touch()
        (tmp_path / "c.py").touch()
        plan = compute_wave_plan(stories, tmp_path)
        assert len(plan.waves) == 3

    def test_external_dep_assumed_done(self, tmp_path: Path) -> None:
        """A dep on a story not in the plan is treated as already done."""
        stories = [
            StoryMeta(id="ST-002", deps=["ST-001"], outputs=["b.py"]),
        ]
        (tmp_path / "b.py").touch()
        plan = compute_wave_plan(stories, tmp_path)
        assert len(plan.waves) == 1
        assert plan.waves[0]["stories"][0]["id"] == "ST-002"


# ---------------------------------------------------------------------------
# File-overlap detection
# ---------------------------------------------------------------------------


class TestFileOverlap:
    def test_disjoint_outputs_are_parallel(self, tmp_path: Path) -> None:
        (tmp_path / "src" / "module_a").mkdir(parents=True)
        (tmp_path / "src" / "module_b").mkdir(parents=True)
        (tmp_path / "src" / "module_a" / "x.py").touch()
        (tmp_path / "src" / "module_b" / "y.py").touch()

        stories = [
            StoryMeta(id="ST-001", outputs=["src/module_a/**/*.py"]),
            StoryMeta(id="ST-002", outputs=["src/module_b/**/*.py"]),
        ]
        plan = compute_wave_plan(stories, tmp_path)
        assert len(plan.waves) == 1
        # Both should be parallel
        groups = [s["group"] for s in plan.waves[0]["stories"]]
        assert all(g == "parallel" for g in groups)

    def test_overlapping_outputs_are_serial(self, tmp_path: Path) -> None:
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "shared.py").touch()

        stories = [
            StoryMeta(id="ST-001", outputs=["src/*.py"]),
            StoryMeta(id="ST-002", outputs=["src/*.py"]),
        ]
        plan = compute_wave_plan(stories, tmp_path)
        assert len(plan.waves) == 1
        groups = [s["group"] for s in plan.waves[0]["stories"]]
        assert all(g == "serial" for g in groups)
        assert "serial_chains" in plan.waves[0]

    def test_zero_expansion_conservative_prefix(self, tmp_path: Path) -> None:
        """Glob matching zero files uses directory prefix for conservative serialization."""
        # src/new_module/ does not exist
        stories = [
            StoryMeta(id="ST-003", outputs=["src/new_module/**/*.py"]),
            StoryMeta(id="ST-004", outputs=["src/new_module/config.py"]),
        ]
        plan = compute_wave_plan(stories, tmp_path)
        assert len(plan.waves) == 1
        groups = [s["group"] for s in plan.waves[0]["stories"]]
        assert all(g == "serial" for g in groups)


# ---------------------------------------------------------------------------
# Serial chains and parallel sets within a wave
# ---------------------------------------------------------------------------


class TestWaveStructure:
    def test_mixed_parallel_and_serial(self, tmp_path: Path) -> None:
        (tmp_path / "a.py").touch()
        (tmp_path / "shared.py").touch()
        (tmp_path / "c.py").touch()

        stories = [
            StoryMeta(id="ST-001", outputs=["a.py"]),
            StoryMeta(id="ST-002", outputs=["shared.py"]),
            StoryMeta(id="ST-003", outputs=["shared.py", "c.py"]),
        ]
        plan = compute_wave_plan(stories, tmp_path)
        assert len(plan.waves) == 1
        wave = plan.waves[0]
        parallel = [s for s in wave["stories"] if s["group"] == "parallel"]
        serial = [s for s in wave["stories"] if s["group"] == "serial"]
        assert len(parallel) == 1
        assert parallel[0]["id"] == "ST-001"
        assert len(serial) == 2

    def test_tier_carried_through(self, tmp_path: Path) -> None:
        (tmp_path / "x.py").touch()
        stories = [StoryMeta(id="ST-001", outputs=["x.py"], tier="standard")]
        plan = compute_wave_plan(stories, tmp_path)
        assert plan.waves[0]["stories"][0]["tier"] == "standard"


# ---------------------------------------------------------------------------
# Filter by story IDs
# ---------------------------------------------------------------------------


class TestFilterIds:
    def test_filter_selects_subset(self, tmp_path: Path) -> None:
        (tmp_path / "a.py").touch()
        (tmp_path / "b.py").touch()
        stories = [
            StoryMeta(id="ST-001", outputs=["a.py"]),
            StoryMeta(id="ST-002", outputs=["b.py"]),
        ]
        plan = compute_wave_plan(stories, tmp_path, filter_ids=["ST-001"])
        all_ids = [s["id"] for w in plan.waves for s in w["stories"]]
        assert all_ids == ["ST-001"]


# ---------------------------------------------------------------------------
# YAML output
# ---------------------------------------------------------------------------


class TestPlanOutput:
    def test_output_is_yaml(self, tmp_path: Path) -> None:
        (tmp_path / "x.py").touch()
        stories = [StoryMeta(id="ST-001", outputs=["x.py"])]
        plan = compute_wave_plan(stories, tmp_path)
        output = plan.to_yaml()
        assert "waves:" in output
        assert "ST-001" in output


# ---------------------------------------------------------------------------
# Tier rubric (first-match-wins)
# ---------------------------------------------------------------------------


class TestTierRubric:
    def test_security_risk_domain_suggests_strong(self) -> None:
        fm = {"risk_domains": ["security"], "outputs": ["src/a.py"]}
        assert suggest_tier(fm, {}) == "strong"

    def test_privacy_risk_domain_suggests_strong(self) -> None:
        fm = {"risk_domains": ["privacy"], "outputs": ["src/a.py"]}
        assert suggest_tier(fm, {}) == "strong"

    def test_data_integrity_risk_domain_suggests_strong(self) -> None:
        fm = {"risk_domains": ["data_integrity"], "outputs": ["src/a.py"]}
        assert suggest_tier(fm, {}) == "strong"

    def test_safety_critical_paths_suggests_strong(self) -> None:
        fm = {"outputs": ["factory/scripts/dispatch"]}
        project_config = {"safety_critical_paths": ["factory/scripts/*"]}
        assert suggest_tier(fm, project_config) == "strong"

    def test_multi_directory_outputs_suggests_standard(self) -> None:
        fm = {"outputs": ["src/a.py", "tests/test_a.py"]}
        assert suggest_tier(fm, {}) == "standard"

    def test_three_deps_suggests_standard(self) -> None:
        fm = {
            "outputs": ["src/a.py"],
            "deps": ["ST-001", "ST-002", "ST-003"],
        }
        assert suggest_tier(fm, {}) == "standard"

    def test_single_dir_with_tests_suggests_economy(self) -> None:
        fm = {
            "outputs": ["src/a.py"],
            "tests": ["tests/test_a.py"],
        }
        assert suggest_tier(fm, {}) == "economy"

    def test_no_match_defaults_standard(self) -> None:
        fm = {"outputs": ["src/a.py"]}
        assert suggest_tier(fm, {}) == "standard"

    def test_first_match_wins(self) -> None:
        fm = {
            "risk_domains": ["security"],
            "outputs": ["src/a.py", "tests/test_a.py"],
        }
        assert suggest_tier(fm, {}) == "strong"
