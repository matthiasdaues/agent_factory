"""Contract tests for the intent select command."""

from __future__ import annotations

import os
import shutil

import pytest
from conftest import REPO_ROOT, load_script

intent = load_script("intent")


def _write_agent(tmp_path, name, inputs_required=None, description=""):
    """Write a minimal agent .md file with structured frontmatter."""
    lines = [
        "---",
        f"name: {name}",
        f"description: {description}" if description else f"name: {name}",
    ]

    if inputs_required is not None:
        lines.append("inputs:")
        lines.append("  required:")
        for req in inputs_required:
            lines.append(f"    - type: {req['type']}")
            lines.append(f'      path_pattern: "{req["path_pattern"]}"')
            if "conditions" in req:
                cond = req["conditions"]
                lines.append("      conditions:")
                for k, v in cond.items():
                    lines.append(f"        {k}: {v}")
        lines.append("  context: []")
    else:
        lines.append("inputs:")
        lines.append("  context: []")

    lines.append("---")
    lines.append(f"# {name}")

    agents_dir = tmp_path / "agents"
    agents_dir.mkdir(exist_ok=True)
    (agents_dir / f"{name}.md").write_text("\n".join(lines))
    return agents_dir


class TestSelectListsAllAgents:
    def test_lists_all_agents(self, tmp_path, capsys):
        agents_dir = _write_agent(tmp_path, "alpha-agent")
        _write_agent(tmp_path, "beta-agent")

        result = intent.main(["select", "--agents-dir", str(agents_dir)])

        assert result == 0
        out = capsys.readouterr().out
        assert "alpha-agent" in out
        assert "beta-agent" in out

    def test_no_agents_found(self, tmp_path, capsys):
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()

        result = intent.main(["select", "--agents-dir", str(agents_dir)])

        assert result == 0
        out = capsys.readouterr().out
        assert "no agent definitions found" in out


class TestSelectSatisfiedEvidence:
    def test_shows_satisfied_input(self, tmp_path, capsys):
        target = tmp_path / "docs"
        target.mkdir()
        proposal = target / "my-proposal.md"
        proposal.write_text("---\nstatus: accepted\n---\n# Proposal\n")

        agents_dir = _write_agent(
            tmp_path,
            "test-agent",
            inputs_required=[
                {
                    "type": "proposal",
                    "path_pattern": str(target / "*.md"),
                }
            ],
        )

        os.chdir(tmp_path)
        result = intent.main(["select", "--agents-dir", str(agents_dir)])

        assert result == 0
        out = capsys.readouterr().out
        assert "✓" in out
        assert "proposal" in out


class TestSelectUnsatisfiedEvidence:
    def test_shows_unsatisfied_input(self, tmp_path, capsys):
        agents_dir = _write_agent(
            tmp_path,
            "test-agent",
            inputs_required=[
                {
                    "type": "story",
                    "path_pattern": str(tmp_path / "nonexistent/*.md"),
                }
            ],
        )

        result = intent.main(["select", "--agents-dir", str(agents_dir)])

        assert result == 0
        out = capsys.readouterr().out
        assert "✗" in out
        assert "story" in out


class TestSelectNoRequiredInputs:
    def test_no_required_inputs_marked(self, tmp_path, capsys):
        agents_dir = _write_agent(tmp_path, "free-agent")

        result = intent.main(["select", "--agents-dir", str(agents_dir)])

        assert result == 0
        out = capsys.readouterr().out
        assert "○" in out
        assert "always eligible" in out


class TestSelectWorkstreamFlag:
    def test_workstream_flag_accepted(self, tmp_path, capsys):
        agents_dir = _write_agent(tmp_path, "scoped-agent")

        result = intent.main(
            [
                "select",
                "--agents-dir",
                str(agents_dir),
                "--workstream",
                "my-workstream",
            ]
        )

        assert result == 0


class TestSelectExitCode:
    def test_exit_code_zero_on_success(self, tmp_path):
        agents_dir = _write_agent(tmp_path, "test-agent")
        result = intent.main(["select", "--agents-dir", str(agents_dir)])
        assert result == 0


class TestSelectReadOnly:
    def test_no_files_written(self, tmp_path):
        agents_dir = _write_agent(tmp_path, "test-agent")
        before = set(tmp_path.rglob("*"))

        intent.main(["select", "--agents-dir", str(agents_dir)])

        after = set(tmp_path.rglob("*"))
        assert before == after


ROUTING_INPUTS = [
    {"type": "feature", "path_pattern": "docs/spec/features/*.feature"},
    {"type": "scope-map", "path_pattern": "docs/spec/scope-map.md"},
]


def _build_project(root, feature_dir):
    """Build a project with a scope map, an accepted proposal, and payments.feature in feature_dir."""
    spec = root / "docs" / "spec"
    spec.mkdir(parents=True)
    (spec / "scope-map.md").write_text("# Scope Map\n")
    proposals = root / "docs" / "proposals"
    proposals.mkdir(parents=True)
    (proposals / "payments.md").write_text("---\nstatus: accepted\n---\n# Payments\n")
    (root / feature_dir).mkdir(parents=True, exist_ok=True)
    (root / feature_dir / "payments.feature").write_text("Feature: Payments\n")


class TestSelectRoutesByFeatureFolder:
    def test_feature_in_features_folder_completes_requirements(
        self, tmp_path, capsys, monkeypatch
    ):
        project = tmp_path / "routed-project"
        _build_project(project, "docs/spec/features")
        agents_dir = _write_agent(
            tmp_path, "planning-agent", inputs_required=ROUTING_INPUTS
        )
        monkeypatch.chdir(project)

        result = intent.main(["select", "--agents-dir", str(agents_dir)])

        assert result == 0
        out = capsys.readouterr().out
        assert "✓ planning-agent" in out
        assert "✓ feature: docs/spec/features/payments.feature" in out

    def test_feature_at_top_of_spec_leaves_requirements_open(
        self, tmp_path, capsys, monkeypatch
    ):
        project = tmp_path / "top-level-project"
        _build_project(project, "docs/spec")
        agents_dir = _write_agent(
            tmp_path, "planning-agent", inputs_required=ROUTING_INPUTS
        )
        monkeypatch.chdir(project)

        result = intent.main(["select", "--agents-dir", str(agents_dir)])

        assert result == 0
        out = capsys.readouterr().out
        assert "✗ planning-agent" in out
        assert "✗ feature: no file matching docs/spec/features/*.feature" in out


DOMAIN_MODELING_AGENT = (
    REPO_ROOT / "packages" / "factory" / "agents" / "domain-modeling-agent.md"
)


def _build_domain_fixture(root, with_feature):
    """Build `scope-only` or `scope-and-feature` (ST-0348 Demo Data)."""
    spec = root / "docs" / "spec"
    spec.mkdir(parents=True)
    (spec / "scope-map.md").write_text("# Scope Map\n")
    if with_feature:
        (spec / "features").mkdir()
        (spec / "features" / "payments.feature").write_text("Feature: Payments\n")


def _select_domain_modeling_agent(tmp_path, project, monkeypatch, capsys):
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    shutil.copy(DOMAIN_MODELING_AGENT, agents_dir / DOMAIN_MODELING_AGENT.name)
    monkeypatch.chdir(project)
    assert intent.main(["select", "--agents-dir", str(agents_dir)]) == 0
    return capsys.readouterr().out


@pytest.mark.spec("CAO-04-IT-01")
class TestSt0348DomainModelingAgentEligibility:
    def test_st_0348_scope_only_is_not_eligible_and_names_the_feature_files(
        self, tmp_path, capsys, monkeypatch
    ):
        project = tmp_path / "scope-only"
        _build_domain_fixture(project, with_feature=False)

        out = _select_domain_modeling_agent(tmp_path, project, monkeypatch, capsys)

        assert "✗ domain-modeling-agent" in out
        assert "✗ feature: no file matching docs/spec/features/*.feature" in out

    def test_st_0348_scope_and_feature_is_eligible(
        self, tmp_path, capsys, monkeypatch
    ):
        project = tmp_path / "scope-and-feature"
        _build_domain_fixture(project, with_feature=True)
        assert not (project / "docs" / "spec" / "entity-model.md").exists()

        out = _select_domain_modeling_agent(tmp_path, project, monkeypatch, capsys)

        assert "✓ domain-modeling-agent" in out
        assert "✓ feature: docs/spec/features/payments.feature" in out


TEST_STRATEGY_AGENT = (
    REPO_ROOT / "packages" / "factory" / "agents" / "test-strategy-agent.md"
)


def _build_suite_no_feature(root):
    """Build `suite-no-feature` (ST-0357 Demo Data)."""
    (root / "tests").mkdir(parents=True)
    (root / "pyproject.toml").write_text(
        '[project]\nname = "example"\n\n[tool.pytest.ini_options]\ntestpaths = ["tests"]\n'
    )
    (root / "tests" / "test_example.py").write_text(
        "def test_example():\n    assert True\n"
    )


@pytest.mark.spec("CAO-10-IT-01")
class TestSt0357TestStrategyAgentEligibility:
    def test_st_0357_suite_no_feature_is_eligible(
        self, tmp_path, capsys, monkeypatch
    ):
        project = tmp_path / "suite-no-feature"
        _build_suite_no_feature(project)
        assert not (project / "docs" / "spec").exists()
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        shutil.copy(TEST_STRATEGY_AGENT, agents_dir / TEST_STRATEGY_AGENT.name)
        monkeypatch.chdir(project)

        assert intent.main(["select", "--agents-dir", str(agents_dir)]) == 0

        out = capsys.readouterr().out
        assert "○ test-strategy-agent" in out
        assert "(no required inputs — always eligible)" in out
