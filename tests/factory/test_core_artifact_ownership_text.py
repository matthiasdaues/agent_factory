"""Text checks for the core-artifact-ownership rulebook changes.

CAO-16 (Rule: Owner receives every finding it acts on next): the finding
format defines `owner:`, lists the ARCH and QA tags, drops RECON, and routes
each open finding to its owner or, without one, to the artifact's producer.
"""

from __future__ import annotations

import re

import pytest
from conftest import REPO_ROOT, load_script

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


ARCHITECTURE_AGENT = AGENTS / "architecture-agent.md"
MAINTAIN_ARCHITECTURE = SKILLS / "maintain-architecture" / "SKILL.md"
RUN_STEP = SKILLS / "run-step" / "SKILL.md"

DEPENDENCY_RULES = "docs/spec/dependency-rules.dsl"
ARCH_FINDINGS = "docs/findings/ARCH-*.md"
STATE_MACHINES = "docs/spec/state-machines.md"


@pytest.mark.spec("CAO-07-LN-01")
class TestSt0353ArchitectureAgentDefinition:
    """CAO-07-LN-01: outputs, context inputs, and the read check of Step 5."""

    def test_st_0353_declares_dependency_rules_with_its_review(self):
        decl = _declarations(_frontmatter(ARCHITECTURE_AGENT))[DEPENDENCY_RULES]
        assert decl["reviewed_by"] == ["architecture-review-agent"]
        assert decl["required"] is False

    def test_st_0353_declares_arch_findings(self):
        assert ARCH_FINDINGS in _declarations(_frontmatter(ARCHITECTURE_AGENT))

    def test_st_0353_declares_no_state_machines(self):
        assert STATE_MACHINES not in _declarations(_frontmatter(ARCHITECTURE_AGENT))

    def test_st_0353_context_inputs_include_the_domain_structure(self):
        context = _frontmatter(ARCHITECTURE_AGENT)["inputs"]["context"]
        assert {ENTITY_MODEL, STATE_MACHINES} <= set(context)

    def test_st_0353_workflow_runs_the_read_check_instead_of_writing(self):
        workflow = _flat(_section(ARCHITECTURE_AGENT.read_text(encoding="utf-8"), "Workflow"))
        assert "→ state machines per" not in workflow
        assert "the read check of Step 5" in workflow


def _step_5() -> str:
    text = MAINTAIN_ARCHITECTURE.read_text(encoding="utf-8")
    match = re.search(r"^## Step 5 — (.*?)(?=^## |\Z)", text, re.M | re.S)
    assert match, "no Step 5"
    return _flat(match.group(0))


@pytest.mark.spec("CAO-07-LN-01")
class TestSt0353MaintainArchitectureStep5IsAReadCheck:
    """CAO-07-LN-01: Step 5 compares, skips, files ARCH, and writes nothing."""

    def test_st_0353_step_5_is_a_read_check(self):
        assert "Step 5 — Check the components against the state machines" in _step_5()

    def test_st_0353_step_5_skipped_without_state_machines(self):
        assert "When `docs/spec/state-machines.md` does not exist, skip this step." in _step_5()

    def test_st_0353_contradiction_files_arch_finding_for_domain_modeling(self):
        step = _step_5()
        assert "`docs/findings/ARCH-NNNN.md`" in step
        assert "`owner: domain-modeling-agent`" in step

    def test_st_0353_step_5_never_writes_state_machines(self):
        assert "Never write `docs/spec/state-machines.md`." in _step_5()


@pytest.mark.spec("CAO-07-LN-01")
class TestSt0353RunStepDoneRule:
    """CAO-07-LN-01: run-step counts a step as done from its outputs alone."""

    def test_st_0353_changed_input_does_not_restart_a_done_step(self):
        text = _flat(RUN_STEP.read_text(encoding="utf-8"))
        assert "A changed input never restarts a step that is done." in text
        assert "The producer of the changed file starts the next pass in its handoff." in text


CORE_LIST = REPO_ROOT / "packages" / "factory" / "rulebooks" / "core-artifacts.yaml"
STRUCTURE_FILES = [
    "entity-model.md",
    "interface-contracts.md",
    "state-machines.md",
    "validation-rules.md",
]
KEPT_SKILLS = [
    "capture-vision",
    "clarify-requirements",
    "grill-me",
    "grill-with-docs",
    "reverse-map",
    "derive-feature",
]


def _core_outputs(agent: dict) -> set[str]:
    """Return the core list patterns whose sample path a declaration matches."""
    import yaml

    il = load_script("index-lint")
    entries = yaml.safe_load(CORE_LIST.read_text(encoding="utf-8"))["entries"]
    return {
        entry["path_pattern"]
        for entry in entries
        for pattern in _declarations(agent)
        if il.pattern_matches(pattern, entry["sample_path"])
    }


@pytest.mark.spec("CAO-03-LN-01")
class TestSt0349RequirementsAgentKeepsScopeAndBehaviour:
    """CAO-03-LN-01: core outputs, skill list, area spec step, handoff."""

    def test_st_0349_core_outputs_are_scope_map_features_and_areas(self):
        assert _core_outputs(_frontmatter(REQUIREMENTS_AGENT)) == {
            "docs/spec/scope-map.md",
            "docs/spec/features/*.feature",
            "docs/spec/areas/*.md",
        }

    def test_st_0349_area_specs_are_optional_and_reviewed(self):
        decl = _declarations(_frontmatter(REQUIREMENTS_AGENT))[
            "docs/spec/areas/{name}.md"
        ]
        assert decl["required"] is False
        assert decl["reviewed_by"] == ["spec-review-agent"]

    def test_st_0349_skill_list_drops_capture_context(self):
        skills = _frontmatter(REQUIREMENTS_AGENT)["skills"]
        assert "capture-context" not in skills
        assert set(KEPT_SKILLS) <= set(skills)

    def test_st_0349_body_names_no_structure_file(self):
        body = REQUIREMENTS_AGENT.read_text(encoding="utf-8").split("\n---\n", 1)[1]
        assert "Produce supplementary specs" not in body
        assert [f for f in STRUCTURE_FILES if f in body] == []

    def test_st_0349_workflow_writes_an_area_spec_on_request(self):
        workflow = _section(REQUIREMENTS_AGENT.read_text(encoding="utf-8"), "Workflow")
        step = re.search(r"^\s*\w\. \*\*Write area specs\*\*.*$", workflow, re.M)
        assert step, "no area spec step"
        assert "`docs/spec/areas/<area>.md`" in step.group(0)
        assert "the stakeholder says" in step.group(0)

    def test_st_0349_handoff_names_the_domain_modeling_agent(self):
        assert _frontmatter(REQUIREMENTS_AGENT)["handoff-to"] == [
            "domain-modeling-agent"
        ]
        handoff = _section(REQUIREMENTS_AGENT.read_text(encoding="utf-8"), "Handoff")
        assert "domain-modeling-agent" in handoff

    def test_st_0349_spec_review_reads_the_area_specs(self):
        context = _frontmatter(SPEC_REVIEW_AGENT)["inputs"]["context"]
        assert "docs/spec/areas/*.md" in context


ARCHITECTURE_REVIEW_AGENT = AGENTS / "architecture-review-agent.md"
ATAM_REVIEW = SKILLS / "atam-review" / "SKILL.md"


def _rules_check() -> str:
    text = ATAM_REVIEW.read_text(encoding="utf-8")
    match = re.search(
        r"^## Step 1b — Check the dependency rules against the component view\n"
        r"(.*?)(?=^## |\Z)",
        text,
        re.M | re.S,
    )
    assert match, "no Step 1b rules check"
    return _flat(match.group(1))


@pytest.mark.spec("CAO-09-LN-01")
class TestSt0354ArchitectureReviewChecksTheDependencyRules:
    """CAO-09-LN-01: context input, the atam-review rules check, optional rules file."""

    def test_st_0354_rules_file_is_a_context_input(self):
        agent = _frontmatter(ARCHITECTURE_REVIEW_AGENT)
        assert DEPENDENCY_RULES in agent["inputs"]["context"]
        required = {r["path_pattern"] for r in agent["inputs"]["required"]}
        assert DEPENDENCY_RULES not in required

    def test_st_0354_core_list_marks_rules_file_optional(self):
        import yaml

        entries = yaml.safe_load(CORE_LIST.read_text(encoding="utf-8"))["entries"]
        (entry,) = [e for e in entries if e["path_pattern"] == DEPENDENCY_RULES]
        assert entry["optional"] is True

    def test_st_0354_rules_check_reads_the_component_view(self):
        step = _rules_check()
        assert "component view of `docs/spec/architecture.dsl`" in step
        assert "every relationship between them" in step

    def test_st_0354_unknown_component_is_a_mismatch(self):
        assert (
            "A rule that names a module the component view lacks is a mismatch."
            in _rules_check()
        )

    def test_st_0354_forbidden_relationship_is_a_mismatch(self):
        assert (
            "So is a rule that forbids a dependency the component view draws "
            "as a relationship." in _rules_check()
        )

    def test_st_0354_mismatch_files_atam_finding_for_the_architecture_agent(self):
        step = _rules_check()
        assert "`docs/findings/ATAM-NNNN.md`" in step
        assert "`owner: architecture-agent`" in step
        assert "Name the rule and the component view." in step

    def test_st_0354_rules_check_skipped_without_rules_file(self):
        step = _rules_check()
        assert (
            "When `docs/spec/dependency-rules.dsl` does not exist, skip this step"
            in step
        )
        assert "Rules check: skipped" in step

    def test_st_0354_report_carries_the_rules_check(self):
        report = _flat(
            _section(ATAM_REVIEW.read_text(encoding="utf-8"), "Step 4 — Write the review report")
        )
        assert "**Rules check**" in report


TERM_CANDIDATES = "docs/spec/work/term-candidates.md"
WRITE_GLOSSARY = "`--write-glossary`"
CANDIDATE_HEADER = (
    "| Term | Domain area | Source | Proposed definition | Status | Note |"
)
REVERSE_MAP = SKILLS / "reverse-map" / "SKILL.md"
GRILLING = SKILLS / "grilling" / "SKILL.md"
DOMAIN_MODELING = SKILLS / "domain-modeling" / "SKILL.md"
RECONCILE_SPEC = SKILLS / "reconcile-spec" / "SKILL.md"
TERM_WRITERS = [REVERSE_MAP, GRILLING, DOMAIN_MODELING, RECONCILE_SPEC]
WRITE_VERB = re.compile(r"\b(writes?|seeds?|updates?|adds?|creates?)\b", re.I)
NEGATION = re.compile(r"\b(never|neither|not|no|unchanged)\b", re.I)


def _blocks(text: str) -> list[str]:
    """Split a Markdown body into paragraphs and list items, without headings."""
    body = text.split("\n---\n", 1)[1]
    parts = re.split(r"\n\s*\n|\n(?=\s*(?:[-*]|\d+\.) )", body)
    return [_flat(p) for p in parts if p.strip() and not p.lstrip().startswith("#")]


def _glossary_writes(path) -> list[str]:
    """Return the blocks that name a write to the glossary without the argument."""
    return [
        block
        for block in _blocks(path.read_text(encoding="utf-8"))
        if "glossary.md" in block
        and WRITE_VERB.search(block)
        and WRITE_GLOSSARY not in block
        and not NEGATION.search(block)
    ]


@pytest.mark.spec("CAO-06-LN-01")
class TestSt0350TermsBecomeCandidates:
    """CAO-06-LN-01: term candidates or a report row, and one glossary producer."""

    @pytest.mark.parametrize("path", TERM_WRITERS, ids=lambda p: p.parent.name)
    def test_st_0350_skill_writes_no_glossary_without_the_argument(self, path):
        assert _glossary_writes(path) == []

    def test_st_0350_reverse_map_records_found_names_as_candidates(self):
        text = REVERSE_MAP.read_text(encoding="utf-8")
        step = _flat(_section(text, "Record term candidates"))
        assert f"`{TERM_CANDIDATES}`" in step
        assert CANDIDATE_HEADER in text
        assert "status `candidate`" in step
        assert "Source names the code path" in step
        assert "never writes `docs/spec/glossary.md`" in step

    def test_st_0350_reverse_map_writes_only_scope_map_and_candidates(self):
        boundaries = _flat(_section(REVERSE_MAP.read_text(encoding="utf-8"), "Boundaries"))
        assert (
            f"It writes only `docs/spec/scope-map.md` and `{TERM_CANDIDATES}`."
            in boundaries
        )

    def test_st_0350_reverse_map_unattended_mode_records_candidates(self):
        unattended = _flat(
            _section(REVERSE_MAP.read_text(encoding="utf-8"), "Unattended mode")
        )
        assert "Record term candidates as in the attended mode." in unattended
        assert "Seed" not in unattended

    def test_st_0350_domain_modeling_routes_a_settled_term(self):
        route = _flat(
            _section(DOMAIN_MODELING.read_text(encoding="utf-8"), "Where a settled term goes")
        )
        assert f"Only the domain-modeling agent passes {WRITE_GLOSSARY}." in route
        assert f"`{TERM_CANDIDATES}`" in route
        assert "status `confirmed`" in route
        assert "the settled definition" in route
        assert "`docs/spec/glossary.md` stays unchanged" in route

    def test_st_0350_glossary_update_needs_the_argument(self):
        text = DOMAIN_MODELING.read_text(encoding="utf-8")
        update = _flat(_subsection(text, f"Update {GLOSSARY} inline"))
        assert f"Only with {WRITE_GLOSSARY}" in update

    def test_st_0350_grilling_passes_the_argument_on_only_when_received(self):
        mode = _flat(_section(GRILLING.read_text(encoding="utf-8"), "Settled terms"))
        assert f"`{TERM_CANDIDATES}`" in mode
        assert "status `confirmed`" in mode
        assert f"Pass {WRITE_GLOSSARY} on only when this run received it." in mode

    def test_st_0350_reconcile_spec_reports_terminology_drift_as_a_row(self):
        text = _flat(RECONCILE_SPEC.read_text(encoding="utf-8"))
        assert "Artifact `docs/spec/glossary.md`" in text
        assert "Owner `domain-modeling-agent`" in text
        assert "Status `open`" in text
        assert (
            f"It changes neither `docs/spec/glossary.md` nor `{TERM_CANDIDATES}`."
            in text
        )


IMPLEMENTATION_AGENT = AGENTS / "implementation-agent.md"
MUTATION_TESTING = SKILLS / "mutation-testing" / "SKILL.md"
QA_FINDINGS = "docs/findings/QA-*.md"


def _resolve_qa_step() -> str:
    workflow = _section(TEST_STRATEGY_AGENT.read_text(encoding="utf-8"), "Workflow")
    match = re.search(
        r"^\d+\. \*\*Resolve the QA findings\*\*.*?(?=^\d+\. \*\*|^\*\*Pause point|\Z)",
        workflow,
        re.M | re.S,
    )
    assert match, "no step 'Resolve the QA findings'"
    return _flat(match.group(0))


def _post_wave_step() -> str:
    workflow = _section(
        IMPLEMENTATION_AGENT.read_text(encoding="utf-8"), "Workflow — Automated Mode"
    )
    match = re.search(
        r"^\d+\. \*\*Route the QA findings\*\*.*?(?=^\d+\. \*\*|\Z)",
        workflow,
        re.M | re.S,
    )
    assert match, "no step 'Route the QA findings'"
    return _flat(match.group(0))


@pytest.mark.spec("CAO-12-LN-01")
class TestSt0358MutationTestingFilesAQaFinding:
    """CAO-12-LN-01: an unresolved mutant becomes a QA finding with its owner."""

    def test_st_0358_file_qa_finding_names_path_and_owner(self):
        text = _flat(MUTATION_TESTING.read_text(encoding="utf-8"))
        assert "`docs/findings/QA-NNNN.md`" in text
        assert "`owner: test-strategy-agent`" in text
        assert "`status: open`" in text


@pytest.mark.spec("CAO-12-LN-01")
class TestSt0358TestStrategyAgentResolvesQaFindings:
    """CAO-12-LN-01: owned-only rule and the two resolutions."""

    def test_st_0358_declares_qa_findings_as_output_and_context(self):
        agent = _frontmatter(TEST_STRATEGY_AGENT)
        assert QA_FINDINGS in _declarations(agent)
        assert QA_FINDINGS in agent["inputs"]["context"]

    def test_st_0358_works_only_on_open_findings_it_owns(self):
        step = _resolve_qa_step()
        assert "only on open `QA` findings with `owner: test-strategy-agent`" in step
        assert "leaves every other finding unchanged" in step

    def test_st_0358_wrong_layer_changes_the_table_and_resolves(self):
        step = _resolve_qa_step()
        assert "changes the contract-owner table of the QA strategy" in step
        assert "sets `status: resolved`" in step

    def test_st_0358_missing_test_moves_owner_and_stays_open(self):
        step = _resolve_qa_step()
        assert "records in the finding which test is missing" in step
        assert "moves `owner:` to `planning-agent`" in step
        assert "status stays `open`" in step


@pytest.mark.spec("CAO-12-LN-01")
class TestSt0358ImplementationAgentRoutesQaFindings:
    """CAO-12-LN-01: dispatch after the wave, resolution on merge."""

    def test_st_0358_dispatches_test_strategy_agent_for_its_findings(self):
        step = _post_wave_step()
        assert "after `close-wave`" in step
        assert (
            "dispatches the test-strategy agent for each open `QA` finding "
            "with `owner: test-strategy-agent`" in step
        )

    def test_st_0358_no_dispatch_for_planning_agent_findings(self):
        step = _post_wave_step()
        assert (
            "does not dispatch the test-strategy agent for a finding "
            "with `owner: planning-agent`" in step
        )

    def test_st_0358_merge_of_the_story_resolves_the_finding(self):
        step = _post_wave_step()
        assert "a merged story names an open `QA` finding" in step
        assert "sets its `status: resolved`" in step

    def test_st_0358_declares_qa_findings(self):
        assert QA_FINDINGS in _declarations(_frontmatter(IMPLEMENTATION_AGENT))


@pytest.mark.spec("CAO-12-LN-01")
class TestSt0358PlanningAgentReadsQaFindings:
    """CAO-12-LN-01: the planning agent's context input."""

    def test_st_0358_qa_findings_are_a_context_input(self):
        assert QA_FINDINGS in _frontmatter(PLANNING_AGENT)["inputs"]["context"]

    def test_st_0358_adds_the_missing_test_to_a_story_that_names_the_finding(self):
        text = _flat(PLANNING_AGENT.read_text(encoding="utf-8"))
        assert (
            "reads each open `QA` finding with `owner: planning-agent`" in text
        )
        assert "adds the missing test to a story that names the finding" in text
