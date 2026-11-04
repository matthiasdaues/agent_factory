"""Text checks for the core-artifact-ownership rulebook changes.

CAO-16 (Rule: Owner receives every finding it acts on next): the finding
format defines `owner:`, lists the ARCH and QA tags, drops RECON, and routes
each open finding to its owner or, without one, to the artifact's producer.
"""

from __future__ import annotations

import re

import pytest
from conftest import REPO_ROOT

RULEBOOKS = REPO_ROOT / "packages" / "factory" / "rulebooks"
FINDING_FORMAT = RULEBOOKS / "conventions" / "finding-format.md"
FINDING_TEMPLATE = RULEBOOKS / "templates" / "finding.md"


def _section(text: str, heading: str) -> str:
    """Return the body of the `## <heading>` section, up to the next `## `."""
    match = re.search(
        rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", text, re.M | re.S
    )
    assert match, f"section '## {heading}' missing"
    return match.group(1)


def _tag_table_tags(text: str) -> set[str]:
    section = _section(text, "File location and name")
    return set(re.findall(r"^\|[^|\n]+\|\s*`([A-Z]+)`\s*\|$", section, re.M))


@pytest.mark.spec
class TestSt0352FindingFormatDefinesOwner:
    """CAO-16-LN-01: owner field, its definition, tags, routing."""

    def test_st_0352_template_frontmatter_has_owner_line(self):
        template = FINDING_TEMPLATE.read_text(encoding="utf-8")
        frontmatter = _section(template, "Frontmatter")
        assert re.search(r"^owner: \S+", frontmatter, re.M)

    def test_st_0352_format_defines_owner_as_next_actor(self):
        text = FINDING_FORMAT.read_text(encoding="utf-8")
        owner = _section(text, "Owner")
        assert "`owner:`" in owner
        assert "the agent that acts on the finding next" in owner

    def test_st_0352_tag_table_lists_arch_and_qa(self):
        tags = _tag_table_tags(FINDING_FORMAT.read_text(encoding="utf-8"))
        assert {"ARCH", "QA"} <= tags

    def test_st_0352_tag_table_drops_recon(self):
        tags = _tag_table_tags(FINDING_FORMAT.read_text(encoding="utf-8"))
        assert "SPEC" in tags, "tag table not parsed"
        assert "RECON" not in tags

    def test_st_0352_orchestrator_sends_open_finding_to_owner(self):
        text = FINDING_FORMAT.read_text(encoding="utf-8")
        routing = _section(text, "How the orchestrator reads findings")
        assert "sends each open finding to the agent in `owner:`" in routing
        assert "not to the author of the reviewed phase" in routing


@pytest.mark.spec
class TestSt0352FindingWithoutOwnerGoesToProducer:
    """CAO-16-LN-02: fallback to the producer from the output declarations."""

    def test_st_0352_finding_without_owner_goes_to_producer(self):
        text = FINDING_FORMAT.read_text(encoding="utf-8")
        routing = _section(text, "How the orchestrator reads findings")
        assert "without `owner:`" in routing
        assert "producer of the artifact" in routing
        assert "output declarations" in routing


@pytest.mark.spec
class TestSt0346IndexLintHookWatchesCoreList:
    """A commit that changes only the core list still runs index-lint (BR-059)."""

    def test_st_0346_index_lint_hook_matches_core_list(self):
        import yaml

        config = yaml.safe_load(
            (REPO_ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
        )
        hooks = [h for repo in config["repos"] for h in repo.get("hooks", [])]
        (hook,) = [h for h in hooks if h["id"] == "index-lint"]
        assert re.search(hook["files"], "packages/factory/rulebooks/core-artifacts.yaml")


AGENTS = REPO_ROOT / "packages" / "factory" / "agents"
DOMAIN_MODELING_AGENT = AGENTS / "domain-modeling-agent.md"
SPEC_REVIEW_AGENT = AGENTS / "spec-review-agent.md"

GLOSSARY = "docs/spec/glossary.md"
ENTITY_MODEL = "docs/spec/entity-model.md"
OPTIONAL_STRUCTURE = [
    "docs/spec/state-machines.md",
    "docs/spec/validation-rules.md",
    "docs/spec/interface-contracts.md",
    "docs/spec/schemas/*",
]


def _frontmatter(path) -> dict:
    import yaml

    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert match, f"{path.name}: no frontmatter"
    return yaml.safe_load(match.group(1))


def _declarations(agent: dict) -> dict[str, dict]:
    return {d["path_pattern"]: d for d in agent["outputs"]["declarations"]}


@pytest.mark.spec("CAO-04-LN-01")
class TestSt0348DomainModelingAgentDefinition:
    """CAO-04-LN-01: tier, inputs, six outputs, optional files, schema step, handoff."""

    def test_st_0348_tier_is_strong(self):
        assert _frontmatter(DOMAIN_MODELING_AGENT)["tier"] == "strong"

    def test_st_0348_required_inputs_are_scope_map_and_feature_files(self):
        required = _frontmatter(DOMAIN_MODELING_AGENT)["inputs"]["required"]
        assert {r["path_pattern"] for r in required} == {
            "docs/spec/scope-map.md",
            "docs/spec/features/*.feature",
        }

    def test_st_0348_context_inputs(self):
        context = _frontmatter(DOMAIN_MODELING_AGENT)["inputs"]["context"]
        assert {
            GLOSSARY,
            "docs/spec/work/term-candidates.md",
            "src/**/*",
            "docs/agent-context.md",
        } <= set(context)

    def test_st_0348_glossary_and_entity_model_are_required_outputs(self):
        decls = _declarations(_frontmatter(DOMAIN_MODELING_AGENT))
        assert decls[GLOSSARY]["required"] is True
        assert decls[GLOSSARY]["reviewed_by"] == ["spec-review-agent", "stakeholder"]
        assert decls[ENTITY_MODEL]["required"] is True
        assert decls[ENTITY_MODEL]["reviewed_by"] == ["spec-review-agent"]

    @pytest.mark.parametrize("pattern", OPTIONAL_STRUCTURE)
    def test_st_0348_optional_structure_output_is_reviewed(self, pattern):
        decl = _declarations(_frontmatter(DOMAIN_MODELING_AGENT))[pattern]
        assert decl["required"] is False
        assert decl["reviewed_by"] == ["spec-review-agent"]

    def test_st_0348_optional_files_only_when_the_domain_needs_them(self):
        text = DOMAIN_MODELING_AGENT.read_text(encoding="utf-8")
        assert (
            "only when the domain has state machines, rules, contracts, "
            "or structured payloads" in " ".join(text.split())
        )

    def test_st_0348_workflow_has_schema_step(self):
        workflow = _section(
            DOMAIN_MODELING_AGENT.read_text(encoding="utf-8"), "Workflow"
        )
        step = re.search(r"^\d+\. \*\*Write schemas\*\*.*$", workflow, re.M)
        assert step, "no schema step"
        assert "`docs/spec/schemas/`" in step.group(0)
        assert "payload column" in step.group(0)

    def test_st_0348_workflow_has_state_machine_step(self):
        workflow = _section(
            DOMAIN_MODELING_AGENT.read_text(encoding="utf-8"), "Workflow"
        )
        step = re.search(r"^\d+\. \*\*Write state machines\*\*.*$", workflow, re.M)
        assert step, "no state machine step"
        assert "pseudocode" in step.group(0)
        assert "statemachine-lint" in step.group(0)

    def test_st_0348_handoff_names_spec_review_in_a_new_session(self):
        handoff = _section(DOMAIN_MODELING_AGENT.read_text(encoding="utf-8"), "Handoff")
        assert "spec-review-agent" in handoff
        assert "new session" in handoff

    def test_st_0348_handoff_names_architecture_only_after_its_files_change(self):
        handoff = " ".join(
            _section(DOMAIN_MODELING_AGENT.read_text(encoding="utf-8"), "Handoff").split()
        )
        assert (
            "only when this run wrote or changed `docs/spec/entity-model.md` "
            "or `docs/spec/state-machines.md`" in handoff
        )
        assert "architecture-agent" in handoff

    def test_st_0348_handoff_targets_in_frontmatter(self):
        assert _frontmatter(DOMAIN_MODELING_AGENT)["handoff-to"] == [
            "spec-review-agent",
            "architecture-agent",
        ]


@pytest.mark.spec("CAO-04-LN-01")
class TestSt0348SpecReviewReadsTheStructureFamily:
    """The spec-review agent reads every file it reviews (BR-059)."""

    def test_st_0348_glossary_and_entity_model_are_required_inputs(self):
        required = _frontmatter(SPEC_REVIEW_AGENT)["inputs"]["required"]
        assert {GLOSSARY, ENTITY_MODEL} <= {r["path_pattern"] for r in required}

    def test_st_0348_optional_structure_files_are_context_inputs(self):
        context = _frontmatter(SPEC_REVIEW_AGENT)["inputs"]["context"]
        assert set(OPTIONAL_STRUCTURE) <= set(context)
        assert GLOSSARY not in context


TEST_STRATEGY_AGENT = AGENTS / "test-strategy-agent.md"
REQUIREMENTS_AGENT = AGENTS / "requirements-agent.md"
VIRGIL = AGENTS / "virgil.md"
PLANNING_AGENT = AGENTS / "planning-agent.md"
SKILLS = REPO_ROOT / "packages" / "factory" / "skills"

TESTING_YAML = "docs/testing.yaml"
QA_STRATEGY = "docs/spec/work/{name}-qa-strategy.md"


def _flat(text: str) -> str:
    return " ".join(text.split())


def _subsection(text: str, heading: str) -> str:
    """Return the body of the `### <heading>` section, up to the next heading."""
    match = re.search(
        rf"^### {re.escape(heading)}\n(.*?)(?=^##+ |\Z)", text, re.M | re.S
    )
    assert match, f"section '### {heading}' missing"
    return match.group(1)


@pytest.mark.spec("CAO-10-LN-01")
class TestSt0357TestStrategyAgentDefinition:
    """CAO-10-LN-01: tier, skills, inputs, outputs, workflow, handoff."""

    def test_st_0357_tier_is_strong(self):
        assert _frontmatter(TEST_STRATEGY_AGENT)["tier"] == "strong"

    def test_st_0357_skills_are_the_four_test_practice_skills(self):
        assert _frontmatter(TEST_STRATEGY_AGENT)["skills"] == [
            "detect-test-regime",
            "qa-strategy-from-spec",
            "crap-score",
            "mutation-testing",
        ]

    def test_st_0357_declares_no_required_input(self):
        inputs = _frontmatter(TEST_STRATEGY_AGENT)["inputs"]
        assert not inputs.get("required")

    def test_st_0357_context_inputs(self):
        context = _frontmatter(TEST_STRATEGY_AGENT)["inputs"]["context"]
        assert {
            "docs/spec/features/*.feature",
            "docs/spec/interface-contracts.md",
            ENTITY_MODEL,
            TESTING_YAML,
        } <= set(context)

    def test_st_0357_outputs_are_testing_yaml_and_qa_strategies(self):
        decls = _declarations(_frontmatter(TEST_STRATEGY_AGENT))
        assert decls[TESTING_YAML]["reviewed_by"] == ["stakeholder"]
        assert QA_STRATEGY in decls

    def test_st_0357_writes_testing_yaml_without_a_feature_file(self):
        workflow = _flat(_section(TEST_STRATEGY_AGENT.read_text(encoding="utf-8"), "Workflow"))
        assert "also in a project without a feature file" in workflow

    def test_st_0357_qa_strategy_only_when_its_inputs_exist(self):
        workflow = _flat(_section(TEST_STRATEGY_AGENT.read_text(encoding="utf-8"), "Workflow"))
        assert (
            "only when the feature file, `docs/spec/interface-contracts.md`, "
            "and `docs/spec/entity-model.md` exist" in workflow
        )
        assert "names the missing input" in workflow

    def test_st_0357_every_testing_yaml_change_waits_for_the_stakeholder(self):
        workflow = _flat(_section(TEST_STRATEGY_AGENT.read_text(encoding="utf-8"), "Workflow"))
        assert (
            "**Pause point:** every change to `docs/testing.yaml` waits for "
            "the stakeholder's confirmation" in workflow
        )
        assert "writes nothing before the stakeholder confirms" in workflow

    def test_st_0357_mutation_testing_records_only_enabled_and_command(self):
        workflow = _flat(_section(TEST_STRATEGY_AGENT.read_text(encoding="utf-8"), "Workflow"))
        assert (
            "only `gates.mutation_testing.enabled` and "
            "`gates.mutation_testing.command`" in workflow
        )
        assert "writes no configuration file of the mutation tool" in workflow

    def test_st_0357_never_runs_a_gate(self):
        text = _flat(TEST_STRATEGY_AGENT.read_text(encoding="utf-8"))
        assert "The agent never runs a gate." in text

    def test_st_0357_handoff_names_the_planning_agent(self):
        assert _frontmatter(TEST_STRATEGY_AGENT)["handoff-to"] == ["planning-agent"]
        handoff = _section(TEST_STRATEGY_AGENT.read_text(encoding="utf-8"), "Handoff")
        assert "planning-agent" in handoff


@pytest.mark.spec("CAO-10-LN-01")
class TestSt0357OtherAgentsGiveUpTheTestPractice:
    """CAO-10-LN-01: requirements agent, Virgil, and planning agent."""

    def test_st_0357_requirements_agent_drops_the_qa_strategy(self):
        agent = _frontmatter(REQUIREMENTS_AGENT)
        assert "qa-strategy-from-spec" not in agent["skills"]
        assert QA_STRATEGY not in _declarations(agent)
        assert "qa-strategy-from-spec" not in REQUIREMENTS_AGENT.read_text(
            encoding="utf-8"
        )

    def test_st_0357_virgil_declares_no_testing_yaml(self):
        assert TESTING_YAML not in _declarations(_frontmatter(VIRGIL))

    def test_st_0357_fitting_step_2b_takes_the_test_strategy_role(self):
        step = _flat(
            _subsection(VIRGIL.read_text(encoding="utf-8"), "2b. Detect test regime")
        )
        assert "the session takes the test-strategy agent's role" in step
        assert "test-strategy-agent.md" in step

    def test_st_0357_planning_preflight_stops_and_names_the_test_strategy_agent(self):
        preflight = _flat(
            _subsection(
                PLANNING_AGENT.read_text(encoding="utf-8"),
                "Pre-flight — Concern registry and testing regime",
            )
        )
        assert "stop the pre-flight" in preflight
        assert "test-strategy-agent" in preflight

    def test_st_0357_planning_agent_does_not_run_detect_test_regime(self):
        assert "detect-test-regime" not in PLANNING_AGENT.read_text(encoding="utf-8")


@pytest.mark.spec("CAO-10-LN-01")
class TestSt0357SkillsNameTheirCaller:
    """The two test practice skills name the test-strategy agent and the pause point."""

    def test_st_0357_detect_test_regime_names_caller_and_pause_point(self):
        text = _flat((SKILLS / "detect-test-regime" / "SKILL.md").read_text(encoding="utf-8"))
        assert "The test-strategy agent invokes this skill" in text
        assert "Write nothing before the stakeholder confirms" in text
        assert "planning agent detects" not in text

    def test_st_0357_qa_strategy_from_spec_names_its_caller(self):
        text = _flat(
            (SKILLS / "qa-strategy-from-spec" / "SKILL.md").read_text(encoding="utf-8")
        )
        assert "The test-strategy agent invokes this skill" in text
